using BCloudServiceUtilities;
using BCommonUtilities;
using ServiceUtilities.Process.Procedure;
using ServiceUtilities.Process.RandomAccessFile;
using Newtonsoft.Json;
using PixyzWorkerProcess.Processing.Models;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace PixyzWorkerProcess.Processing
{
    public class BatchProcessingService
    {
        private const string FAILED_STATE = "Failed";
        private const string RUNNING_STATE = "Running";
        private const string SUCCESS_STATE = "Succeeded";
        public static BatchProcessingService Instance { get; private set; }

        private string InternalState = "Waiting";
        private object LockObject = new object();

        public string State
        {
            get
            {
                return InternalState;
            }
            //Don't accidentally override a failed state with something else
            private set
            {
                lock (LockObject)
                {
                    if (InternalState != FAILED_STATE)
                    {
                        InternalState = value;
                    }
                }
            }
        }

        private IBMemoryServiceInterface MemoryService;
        private readonly HttpClient Client = new HttpClient();
        //Upload Requests
        List<HttpWebRequest> WebRequests = new List<HttpWebRequest>();

        private ConcurrentQueue<Node> NodesToWriteAndCompress = new ConcurrentQueue<Node>();
        private ConcurrentQueue<Node> NodesToWrite = new ConcurrentQueue<Node>();

        private bool QueueComplete = false;
        

        private Dictionary<EProcessedFileType, string> UploadUrls = new Dictionary<EProcessedFileType, string>();

        private string NotifyDoneUrl = "";

        private static void LogError(string _Message)
        {
            Console.WriteLine(_Message);
        }

        public static bool Initialize(IBMemoryServiceInterface MemoryService, Action<string> _ErrorMessageAction = null)
        {
            try
            {
                Instance = new BatchProcessingService();
                Instance.MemoryService = MemoryService;
                return Instance.SubscribeToPubSub(MemoryService.GetPubSubService(), LogError);
            }
            catch(Exception ex)
            {
                _ErrorMessageAction?.Invoke($"{ex.Message}\n{ex.StackTrace}");
                return false;
            }
        }

        public void SetUploadUrls(string _HierarchyCompressed, string _HierarchyUncompressed, string _MetadataCompressed, string _MetadataUncompressed, string _GeometryCompressed, string _GeometryUncompressed, string _NotifyDoneUrl)
        {
            UploadUrls.Add(EProcessedFileType.HIERARCHY_RAF, _HierarchyUncompressed);
            UploadUrls.Add(EProcessedFileType.HIERARCHY_CF, _HierarchyCompressed);

            UploadUrls.Add(EProcessedFileType.GEOMETRY_RAF, _GeometryUncompressed);
            UploadUrls.Add(EProcessedFileType.GEOMETRY_CF, _GeometryCompressed);

            UploadUrls.Add(EProcessedFileType.METADATA_RAF, _MetadataUncompressed);
            UploadUrls.Add(EProcessedFileType.METADATA_CF, _MetadataCompressed);

            NotifyDoneUrl = _NotifyDoneUrl;
        }

        public void AddItemToQueues(Node Item, Node ItemCompress)
        {
            NodesToWriteAndCompress.Enqueue(ItemCompress);
            NodesToWrite.Enqueue(Item);
        }

        public void StartProcessingBatchData(string _Filename, Action<string> _ErrorMessageAction = null)
        {
            State = RUNNING_STATE;
            ManualResetEvent WaitCompressedFiles = new ManualResetEvent(false);
            ManualResetEvent WaitUnCompressedFiles = new ManualResetEvent(false);

            ProcessQueue(_Filename, _ErrorMessageAction, WaitCompressedFiles, NodesToWriteAndCompress, EDeflateCompression.Compress);
            ProcessQueue(_Filename, _ErrorMessageAction, WaitUnCompressedFiles, NodesToWrite, EDeflateCompression.DoNotCompress);

            BTaskWrapper.Run(() =>
            {
                try
                {
                    WaitCompressedFiles.WaitOne();
                    WaitUnCompressedFiles.WaitOne();

                    if (State != FAILED_STATE)
                    {
                        EndProcessingBatchData(_ErrorMessageAction);
                    }
                    else
                    {
                        _ErrorMessageAction?.Invoke("Write Failed");
                    }
                }
                catch (Exception ex)
                {
                    _ErrorMessageAction?.Invoke($"{ex.Message}\n{ex.StackTrace}");
                    //Just set the state, health checker should see this and take action
                    State = FAILED_STATE;
                }
            });
        }

        private void ProcessQueue(string _Filename, Action<string> _ErrorMessageAction, ManualResetEvent ProcessQueueWait, ConcurrentQueue<Node> ProcessQueue, EDeflateCompression QueueCompressMode)
        {
            BTaskWrapper.Run(() =>
            {
                try
                {
                    _ErrorMessageAction?.Invoke("Start processing Queue");
                    Dictionary<ENodeType, StreamStruct> WriteStreams = CreateStreams(_Filename, QueueCompressMode);
                    using (XStreamWriter Writer = new XStreamWriter(WriteStreams))
                    {
                        while (!QueueComplete || ProcessQueue.Count > 0)
                        {
                            if (ProcessQueue.TryDequeue(out Node WriteNode))
                            {
                                if (WriteNode.GetNodeType() == ENodeType.Hierarchy)
                                {
                                    HierarchyNode CurrentHierarchyNode = (HierarchyNode)WriteNode;

                                    //Need to check that lists are not null
                                    CheckHierarchyNode(CurrentHierarchyNode);

                                    Writer.Write(CurrentHierarchyNode);
                                }

                                if (WriteNode.GetNodeType() == ENodeType.Geometry)
                                {
                                    GeometryNode CurrentGeometry = (GeometryNode)WriteNode;
                                    CheckGeometry(CurrentGeometry);

                                    Writer.Write((GeometryNode)WriteNode);
                                }

                                if (WriteNode.GetNodeType() == ENodeType.Metadata)
                                {
                                    Writer.Write((MetadataNode)WriteNode);
                                }
                            }
                            else
                            {
                                Thread.Sleep(10);
                            }
                        }
                        _ErrorMessageAction?.Invoke("Closing Stream");
                    }
                    _ErrorMessageAction?.Invoke("Closed Stream");
                }
                catch (Exception ex)
                {
                    _ErrorMessageAction?.Invoke($"{ex.Message}\n{ex.StackTrace}");
                    State = FAILED_STATE;
                }

                ProcessQueueWait.Set();
            });
        }

        private static void CheckGeometry(GeometryNode CurrentGeometry)
        {
            if (CurrentGeometry.LODs != null)
            {
                for (int i = 0; i < CurrentGeometry.LODs.Count; ++i)
                {
                    if (CurrentGeometry.LODs[i].Indexes != null)
                    {
                        CurrentGeometry.LODs[i].Indexes.Reverse();
                    }
                }
            }
        }

        private static void CheckHierarchyNode(HierarchyNode CurrentHierarchyNode)
        {
            if (CurrentHierarchyNode.ChildNodes == null)
            {
                CurrentHierarchyNode.ChildNodes = new List<ulong>();
            }

            if (CurrentHierarchyNode.GeometryParts == null)
            {
                CurrentHierarchyNode.GeometryParts = new List<HierarchyNode.GeometryPart>();
            }
        }

        /// <summary>
        /// Call after nothing more will be added to the queue for this run
        /// </summary>
        public void SignalQueuingComplete()
        {
            QueueComplete = true;
        }

        public void EndProcessingBatchData(Action<string> _ErrorMessageAction)
        {
            //Upload files and change status to completed
            State = UploadAllFiles(LogError);

            //Call out to cad process to let it know it can destroy the pod
            try
            {
                if (State == SUCCESS_STATE)
                {
                    _ErrorMessageAction?.Invoke($"Ending Pod : {NotifyDoneUrl}");

                    Thread.Sleep(30000);
                    Task<HttpResponseMessage> ResponseTask = Client.GetAsync(NotifyDoneUrl);
                    ResponseTask.Wait();

                    if(ResponseTask.Result.StatusCode != HttpStatusCode.OK)
                    {
                        State = FAILED_STATE;
                        Task<string> ContentReadTask = ResponseTask.Result.Content.ReadAsStringAsync();
                        ContentReadTask.Wait();

                        _ErrorMessageAction?.Invoke($"{ContentReadTask.Result}");
                    }
                }
            }
            catch(Exception ex)
            {
                _ErrorMessageAction?.Invoke($"Failed to end pod : {ex.Message}\n{ex.StackTrace}");
                State = FAILED_STATE;
            }
        }

        private int ExpectedMessageCount = -1;
        private int QueuedMessageCount = 0;
        private bool SubscribeToPubSub(IBPubSubServiceInterface _PubSub, Action<string> _ErrorMessageAction = null)
        {
            return _PubSub.CustomSubscribe("models", (Message, Json) =>
            {
                //make two copies so that writers don't interfere with each other
                NodeMessage MessageReceived = JsonConvert.DeserializeObject<NodeMessage>(Json);
                NodeMessage MessageReceivedCompressCopy = JsonConvert.DeserializeObject<NodeMessage>(Json);

                try
                {
                    if (!MessageReceived.Done)
                    {
                        if (MessageReceived.Errors != null && MessageReceived.Errors.Length > 0)
                        {
                            for (int i = 0; i < MessageReceived.Errors.Length; ++i)
                            {
                                _ErrorMessageAction?.Invoke(MessageReceived.Errors[i]);
                            }
                        }

                        if (MessageReceived.HierarchyNode != null)
                        {
                            AddItemToQueues(MessageReceived.HierarchyNode, MessageReceivedCompressCopy.HierarchyNode);
                        }

                        if (MessageReceived.GeometryNode != null)
                        {
                            AddItemToQueues(MessageReceived.GeometryNode, MessageReceivedCompressCopy.GeometryNode);
                        }

                        if (MessageReceived.MetadataNode != null)
                        {
                            AddItemToQueues(MessageReceived.MetadataNode, MessageReceivedCompressCopy.MetadataNode);
                        }

                        Interlocked.Increment(ref QueuedMessageCount);
                        

                    }
                    else
                    {
                        ExpectedMessageCount = MessageReceived.MessageCount;
                    }
                    //Check if Expected message count has been set
                    if(ExpectedMessageCount != -1 && QueuedMessageCount >= ExpectedMessageCount)
                    {
                        _ErrorMessageAction?.Invoke($"Received End signal for {ExpectedMessageCount} messages");
                        SignalQueuingComplete();
                    }
                }
                catch(Exception ex)
                {
                    _ErrorMessageAction?.Invoke($"{ex.Message}\n{ex.StackTrace}");
                }

            });
        }

        private string UploadAllFiles(Action<string> _ErrorMessageAction = null)
        {
            _ErrorMessageAction?.Invoke("Uploading files");
            Task[] Tasks = new Task[WebRequests.Count];
            try
            {
                for(int i = 0; i < WebRequests.Count; ++i)
                {
                    Tasks[i] = WebRequests[i].GetResponseAsync();
                }

                Task.WaitAll(Tasks);

                foreach (var CompletedTask in Tasks) CompletedTask.Dispose();

                return SUCCESS_STATE;
            }
            catch (Exception ex)
            {
                _ErrorMessageAction?.Invoke($"{ex.Message}\n{ex.StackTrace}");
                return FAILED_STATE;
            }
        }
        
        private static HttpWebRequest CreateWebRequest(string _UploadUrl)
        {
            HttpWebRequest Request = (HttpWebRequest)HttpWebRequest.Create(_UploadUrl);

            //Do not buffer everything on client side before sending
            Request.Method = "PUT";
            Request.AllowWriteStreamBuffering = false;
            Request.AllowReadStreamBuffering = false;
            Request.ContentType = "application/octet-stream";

            return Request;
        }

        private Dictionary<ENodeType, StreamStruct> CreateStreams(string _Name, EDeflateCompression CompressMode)
        {
            Dictionary<ENodeType, StreamStruct> Streams = new Dictionary<ENodeType, StreamStruct>();

            EProcessedFileType HierarchyFileType = EProcessedFileType.HIERARCHY_RAF;
            if (CompressMode == EDeflateCompression.Compress)
            {
                HierarchyFileType = EProcessedFileType.HIERARCHY_CF;
            }

            HttpWebRequest HierarchyRequest = CreateWebRequest(UploadUrls[HierarchyFileType]);
            lock (WebRequests)
            {
                WebRequests.Add(HierarchyRequest);
            }
            Stream WriteHierarchyStream = HierarchyRequest.GetRequestStream();
            StreamStruct HierarchyStreamStruct = new StreamStruct(WriteHierarchyStream, CompressMode);


            EProcessedFileType GeometryFileType = EProcessedFileType.GEOMETRY_RAF;
            if (CompressMode == EDeflateCompression.Compress)
            {
                GeometryFileType = EProcessedFileType.GEOMETRY_CF;
            }

            HttpWebRequest GeometryRequest = CreateWebRequest(UploadUrls[GeometryFileType]);
            lock (WebRequests)
            {
                WebRequests.Add(GeometryRequest);
            }
            Stream WriteGeometryStream = GeometryRequest.GetRequestStream();
            StreamStruct GeometryStreamStruct = new StreamStruct(WriteGeometryStream, CompressMode);


            EProcessedFileType MetadateFileType = EProcessedFileType.METADATA_RAF;
            if (CompressMode == EDeflateCompression.Compress)
            {
                MetadateFileType = EProcessedFileType.METADATA_CF;
            }

            HttpWebRequest MetadataRequest = CreateWebRequest(UploadUrls[MetadateFileType]);
            lock(WebRequests)
            {
                WebRequests.Add(MetadataRequest);
            }
            Stream WriteMetadataStream = MetadataRequest.GetRequestStream();
            StreamStruct MetadataStreamStruct = new StreamStruct(WriteMetadataStream, CompressMode);


            Streams.Add(ENodeType.Hierarchy, HierarchyStreamStruct);
            Streams.Add(ENodeType.Geometry, GeometryStreamStruct);
            Streams.Add(ENodeType.Metadata, MetadataStreamStruct);
            return Streams;
        }
    }
}
