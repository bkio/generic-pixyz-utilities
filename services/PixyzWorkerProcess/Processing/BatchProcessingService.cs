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
using System.IO.Compression;
using System.Linq;

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
        List<Stream> WriteStreams = new List<Stream>();

        private ConcurrentQueue<Node> NodesToWriteAndCompress = new ConcurrentQueue<Node>();
        private ConcurrentQueue<Node> NodesToWrite = new ConcurrentQueue<Node>();

        private bool QueueComplete = false;


        private Dictionary<EProcessedFileType, string> UploadUrls = new Dictionary<EProcessedFileType, string>();
        private bool IsFileWrite = false;


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
            catch (Exception ex)
            {
                _ErrorMessageAction?.Invoke($"{ex.Message}\n{ex.StackTrace}");
                return false;
            }
        }

        public void SetUploadUrls(string _HierarchyCompressed, string _HierarchyUncompressed, string _MetadataCompressed, string _MetadataUncompressed, string _GeometryCompressed, string _GeometryUncompressed, string _NotifyDoneUrl, bool _IsFileWrite = false)
        {
            UploadUrls.Add(EProcessedFileType.HIERARCHY_RAF, _HierarchyUncompressed);
            UploadUrls.Add(EProcessedFileType.HIERARCHY_CF, _HierarchyCompressed);

            UploadUrls.Add(EProcessedFileType.GEOMETRY_RAF, _GeometryUncompressed);
            UploadUrls.Add(EProcessedFileType.GEOMETRY_CF, _GeometryCompressed);

            UploadUrls.Add(EProcessedFileType.METADATA_RAF, _MetadataUncompressed);
            UploadUrls.Add(EProcessedFileType.METADATA_CF, _MetadataCompressed);

            NotifyDoneUrl = _NotifyDoneUrl;

            IsFileWrite = _IsFileWrite;
        }

        public void AddItemToQueues(Node Item, Node ItemCompress)
        {
            NodesToWriteAndCompress.Enqueue(ItemCompress);
            NodesToWrite.Enqueue(Item);
        }

        public void StartProcessingBatchData(Action<string> _ErrorMessageAction = null)
        {
            State = RUNNING_STATE;
            ManualResetEvent WaitCompressedFiles = new ManualResetEvent(false);
            ManualResetEvent WaitUnCompressedFiles = new ManualResetEvent(false);

            ProcessQueue(_ErrorMessageAction, WaitCompressedFiles, NodesToWriteAndCompress, EDeflateCompression.Compress);
            ProcessQueue(_ErrorMessageAction, WaitUnCompressedFiles, NodesToWrite, EDeflateCompression.DoNotCompress);

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

        private void ProcessQueue(Action<string> _ErrorMessageAction, ManualResetEvent ProcessQueueWait, ConcurrentQueue<Node> ProcessQueue, EDeflateCompression QueueCompressMode)
        {
            BTaskWrapper.Run(() =>
            {
                try
                {
                    _ErrorMessageAction?.Invoke("Start processing Queue");
                    Dictionary<ENodeType, StreamStruct> WriteStreams = CreateStreams(QueueCompressMode);
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

            if (CurrentHierarchyNode.GeometryParts.Count > 0)
            {
                for (int i = 0; i < CurrentHierarchyNode.GeometryParts.Count; ++i)
                {
                    if (CurrentHierarchyNode.GeometryParts[i].Color == null)
                    {
                        CurrentHierarchyNode.GeometryParts[i].Color = new ServiceUtilities.Process.Geometry.Color();
                    }
                }
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
            if (!IsFileWrite)
            {
                //Upload files and change status to completed
                State = UploadAllFiles(LogError);
            }
            else
            {
                State = CompleteWrites(LogError);
            }

            //Call out to cad process to let it know it can destroy the pod
            try
            {
                if (State == SUCCESS_STATE && !IsFileWrite)
                {
                    _ErrorMessageAction?.Invoke($"Ending Pod : {NotifyDoneUrl}");

                    Thread.Sleep(30000);
                    Task<HttpResponseMessage> ResponseTask = Client.GetAsync(NotifyDoneUrl);
                    ResponseTask.Wait();

                    if (ResponseTask.Result.StatusCode != HttpStatusCode.OK)
                    {
                        State = FAILED_STATE;
                        Task<string> ContentReadTask = ResponseTask.Result.Content.ReadAsStringAsync();
                        ContentReadTask.Wait();

                        _ErrorMessageAction?.Invoke($"{ContentReadTask.Result}");
                    }
                }
            }
            catch (Exception ex)
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

                try
                {
                    byte[] MessageBytes = Convert.FromBase64String(Json);
                    MemoryStream InputStream = new MemoryStream(MessageBytes);
                    MemoryStream OutputStream = new MemoryStream();
                    using (DeflateStream decompressionStream = new DeflateStream(InputStream, CompressionMode.Decompress))
                    {
                        decompressionStream.CopyTo(OutputStream);
                    }

                    string DecompressedMessage = Encoding.UTF8.GetString(OutputStream.ToArray());

                    NodeMessage MessageReceived = JsonConvert.DeserializeObject<NodeMessage>(DecompressedMessage);
                    NodeMessage MessageReceivedCompressCopy = JsonConvert.DeserializeObject<NodeMessage>(DecompressedMessage);

                    AddMessage(MessageReceived, MessageReceivedCompressCopy, _ErrorMessageAction);
                }
                catch (Exception ex)
                {
                    _ErrorMessageAction?.Invoke($"{ex.Message}\n{ex.StackTrace}");
                }

            });
        }

        private ConcurrentDictionary<ulong, LodMessage> GeometryNodeToAssemblePlain = new ConcurrentDictionary<ulong, LodMessage>();
        private ConcurrentDictionary<ulong, LodMessage> GeometryNodeToAssembleCompressed = new ConcurrentDictionary<ulong, LodMessage>();

        private static void MergeGeometry(ConcurrentDictionary<ulong, LodMessage> _GeometryStore, LodMessage NewMessage)
        {
                _GeometryStore.AddOrUpdate(NewMessage.UniqueID, NewMessage, (K, V) =>
                {
                    V.LODs.Add(NewMessage.LODs[0]);
                    return V;
                });
            
        }

        private static void CompleteMerge(ConcurrentDictionary<ulong, LodMessage> _GeometryStore)
        {
            Parallel.ForEach(_GeometryStore, (Node) => 
            {
                Node.Value.LODs = Node.Value.LODs.OrderByDescending(x => x.Indexes.Count).ToList();
            });

        }

        public void AddMessage(NodeMessage Message, NodeMessage MessageCompressCopy, Action<string> _ErrorMessageAction = null)
        {
            if (!Message.Done)
            {
                if (Message.Errors != null && Message.Errors.Length > 0)
                {
                    for (int i = 0; i < Message.Errors.Length; ++i)
                    {
                        _ErrorMessageAction?.Invoke(Message.Errors[i]);
                    }
                }

                if (Message.HierarchyNode != null)
                {
                    AddItemToQueues(Message.HierarchyNode, MessageCompressCopy.HierarchyNode);
                }

                if (Message.GeometryNode != null)
                {

                    //AddItemToQueues(Message.GeometryNode, MessageCompressCopy.GeometryNode);

                    MergeGeometry(GeometryNodeToAssemblePlain, Message.GeometryNode);
                    MergeGeometry(GeometryNodeToAssembleCompressed, MessageCompressCopy.GeometryNode);
                }

                if (Message.MetadataNode != null)
                {
                    AddItemToQueues(Message.MetadataNode, MessageCompressCopy.MetadataNode);
                }

                Interlocked.Increment(ref QueuedMessageCount);
            }
            else
            {
                ExpectedMessageCount = Message.MessageCount;
            }


            _ErrorMessageAction?.Invoke($"Message Count: {QueuedMessageCount}");
            //Check if Expected message count has been set
            if (ExpectedMessageCount != -1 && QueuedMessageCount >= ExpectedMessageCount)
            {
                _ErrorMessageAction?.Invoke($"Received End signal for {ExpectedMessageCount} messages");
                CompleteMerge(GeometryNodeToAssemblePlain);
                CompleteMerge(GeometryNodeToAssembleCompressed);

                foreach(var Node in GeometryNodeToAssemblePlain)
                {
                    //There should exist a copy of each message
                    LodMessage Copy = GeometryNodeToAssembleCompressed[Node.Key];
                    AddItemToQueues(Node.Value, Copy);
                }

                SignalQueuingComplete();
            }
        }

        private string CompleteWrites(Action<string> _ErrorMessageAction = null)
        {
            _ErrorMessageAction?.Invoke("Writing files");

            try
            {
                for (int i = 0; i < WriteStreams.Count; ++i)
                {
                    try
                    {
                        WriteStreams[i].Dispose();
                    }
                    catch (Exception ex)
                    {
                        _ErrorMessageAction?.Invoke($"{ex.Message}\n{ex.StackTrace}");
                    }
                }
                return SUCCESS_STATE;
            }
            catch (Exception ex)
            {
                _ErrorMessageAction?.Invoke($"{ex.Message}\n{ex.StackTrace}");
                return FAILED_STATE;
            }
        }

        private string UploadAllFiles(Action<string> _ErrorMessageAction = null)
        {
            _ErrorMessageAction?.Invoke("Uploading files");
            Task[] Tasks = new Task[WebRequests.Count];
            try
            {
                for (int i = 0; i < WebRequests.Count; ++i)
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

        private Dictionary<ENodeType, StreamStruct> CreateFileStreams(EDeflateCompression CompressMode)
        {
            Dictionary<ENodeType, StreamStruct> Streams = new Dictionary<ENodeType, StreamStruct>();

            EProcessedFileType HierarchyFileType = EProcessedFileType.HIERARCHY_RAF;
            if (CompressMode == EDeflateCompression.Compress)
            {
                HierarchyFileType = EProcessedFileType.HIERARCHY_CF;
            }

            Stream WriteHierarchyStream = new FileStream(UploadUrls[HierarchyFileType], FileMode.Create);
            lock (WriteStreams)
            {
                WriteStreams.Add(WriteHierarchyStream);
            }
            StreamStruct HierarchyStreamStruct = new StreamStruct(WriteHierarchyStream, CompressMode);


            EProcessedFileType GeometryFileType = EProcessedFileType.GEOMETRY_RAF;
            if (CompressMode == EDeflateCompression.Compress)
            {
                GeometryFileType = EProcessedFileType.GEOMETRY_CF;
            }

            Stream WriteGeometryStream = new FileStream(UploadUrls[GeometryFileType], FileMode.Create);
            lock (WriteStreams)
            {
                WriteStreams.Add(WriteGeometryStream);
            }
            StreamStruct GeometryStreamStruct = new StreamStruct(WriteGeometryStream, CompressMode);

            EProcessedFileType MetadateFileType = EProcessedFileType.METADATA_RAF;
            if (CompressMode == EDeflateCompression.Compress)
            {
                MetadateFileType = EProcessedFileType.METADATA_CF;
            }

            Stream WriteMetadataStream = new FileStream(UploadUrls[MetadateFileType], FileMode.Create);
            lock (WriteStreams)
            {
                WriteStreams.Add(WriteMetadataStream);
            }
            StreamStruct MetadataStreamStruct = new StreamStruct(WriteMetadataStream, CompressMode);

            Streams.Add(ENodeType.Hierarchy, HierarchyStreamStruct);
            Streams.Add(ENodeType.Geometry, GeometryStreamStruct);
            Streams.Add(ENodeType.Metadata, MetadataStreamStruct);

            return Streams;
        }

        private Dictionary<ENodeType, StreamStruct> CreateStreams(EDeflateCompression CompressMode)
        {
            if (IsFileWrite)
            {
                return CreateFileStreams(CompressMode);
            }

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
            lock (WebRequests)
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
