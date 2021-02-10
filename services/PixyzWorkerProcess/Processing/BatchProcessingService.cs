﻿using BCloudServiceUtilities;
using BCommonUtilities;
using ServiceUtilities.Process.Procedure;
using ServiceUtilities.Process.RandomAccessFile;
using PixyzWorkerProcess.Processing.Models;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using System.IO.Compression;
using System.Linq;
using FlatBuffers;
using FB;

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
                _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] {ex.Message}\n{ex.StackTrace}");
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

        public void AddItemToQueues(Node Item)
        {
            NodesToWrite.Enqueue(Item);
        }

        public void StartProcessingBatchData(Action<string> _ErrorMessageAction = null)
        {
            State = RUNNING_STATE;
            ManualResetEvent WaitFiles = new ManualResetEvent(false);

            ProcessQueue(_ErrorMessageAction, WaitFiles, NodesToWrite, EDeflateCompression.Compress);

            BTaskWrapper.Run(() =>
            {
                try
                {
                    WaitFiles.WaitOne();

                    if (State != FAILED_STATE)
                    {
                        EndProcessingBatchData(_ErrorMessageAction);
                    }
                    else
                    {
                        _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] Write Failed");
                    }
                }
                catch (Exception ex)
                {
                    _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] {ex.Message}\n{ex.StackTrace}");
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
                    _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] Start processing Queue");
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
                        _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] Closing Stream");
                    }
                    _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] Closed Stream");
                }
                catch (Exception ex)
                {
                    _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] {ex.Message}\n{ex.StackTrace}");
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
                if (State == SUCCESS_STATE)
                {
                    _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] Files are successfully written.");
                }
            }

            //Call out to cad process to let it know it can destroy the pod
            try
            {
                if (State == SUCCESS_STATE && !IsFileWrite)
                {
                    _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] Ending Pod : {NotifyDoneUrl}");

                    Thread.Sleep(30000);
                    Task<HttpResponseMessage> ResponseTask = Client.GetAsync(NotifyDoneUrl);
                    ResponseTask.Wait();

                    if (ResponseTask.Result.StatusCode != HttpStatusCode.OK)
                    {
                        State = FAILED_STATE;
                        Task<string> ContentReadTask = ResponseTask.Result.Content.ReadAsStringAsync();
                        ContentReadTask.Wait();

                        _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] {ContentReadTask.Result}");
                    }
                }
            }
            catch (Exception ex)
            {
                _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] Failed to end pod : {ex.Message}\n{ex.StackTrace}");
                State = FAILED_STATE;
            }
        }

        private int ExpectedMessageCount = -1;
        private int QueuedMessageCount = 0;
        private bool SubscribeToPubSub(IBPubSubServiceInterface _PubSub, Action<string> _ErrorMessageAction = null)
        {
            return _PubSub.CustomSubscribe("models", (Message, Json) =>
            {
                try
                {
                    byte[] MessageBytes = Convert.FromBase64String(Json);
                    MemoryStream InputStream = new MemoryStream(MessageBytes);
                    MemoryStream OutputStream = new MemoryStream();

                    using (DeflateStream decompressionStream = new DeflateStream(InputStream, CompressionMode.Decompress))
                    {
                        decompressionStream.CopyTo(OutputStream);
                    }

                    //string DecompressedMessage = Encoding.UTF8.GetString(OutputStream.ToArray());
                    byte[] DecompressedArray = OutputStream.ToArray();
                    var buf = new ByteBuffer(DecompressedArray);

                    var FlatNodeMessage = FBNodeMessage.GetRootAsFBNodeMessage(buf);

                    NodeMessage MessageReceived = ConvertNodeMessage(FlatNodeMessage);

                    AddMessage(MessageReceived, _ErrorMessageAction);
                }
                catch (Exception ex)
                {
                    _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] {ex.Message}\n{ex.StackTrace}");
                }

            });
        }

        public NodeMessage ConvertNodeMessage(FBNodeMessage FlatBufferMessage)
        {
            NodeMessage _Message = new NodeMessage();
            _Message.Done = FlatBufferMessage.Done;
            _Message.ModelID = FlatBufferMessage.ModelID;
            _Message.MessageCount = FlatBufferMessage.MessageCount;
            _Message.Errors = FlatBufferMessage.Errors;
            if (FlatBufferMessage.HierarchyNode != null)
            {
                _Message.HierarchyNode = ConvertNodeH(FlatBufferMessage.HierarchyNode);
            }
            if (FlatBufferMessage.GeometryNode != null)
            {
                _Message.GeometryNode = ConvertNodeG(FlatBufferMessage.GeometryNode);
            }
            if (FlatBufferMessage.MetadataNode != null)
            {
                _Message.MetadataNode = ConvertNodeM(FlatBufferMessage.MetadataNode);
            }
            return _Message;
        }

        public HierarchyNode ConvertNodeH(FBHierarchyNode? FlatBufferMessage)
        {
            HierarchyNode _Node = new HierarchyNode();
            _Node.UniqueID = FlatBufferMessage.Value.UniqueID;
            _Node.ParentID = FlatBufferMessage.Value.ParentID;
            _Node.MetadataID = FlatBufferMessage.Value.MetadataID;
            _Node.GeometryParts = new List<HierarchyNode.GeometryPart>();
            for (int i = 0; i < FlatBufferMessage.Value.GeometryPartsLength; i++)
            {
                var CurrentPart = FlatBufferMessage.Value.GeometryParts(i);
                var Part = new HierarchyNode.GeometryPart();
                Part.GeometryID = CurrentPart.Value.GeometryID;
                Part.Location = new ServiceUtilities.Process.Geometry.Vector3D();
                Part.Rotation = new ServiceUtilities.Process.Geometry.Vector3D();
                Part.Scale = new ServiceUtilities.Process.Geometry.Vector3D();
                Part.Color = new ServiceUtilities.Process.Geometry.Color();
                if (CurrentPart.HasValue)
                {
                    Part.Location = new ServiceUtilities.Process.Geometry.Vector3D(CurrentPart.Value.Location.X, CurrentPart.Value.Location.Y, CurrentPart.Value.Location.Z);
                    Part.Rotation = new ServiceUtilities.Process.Geometry.Vector3D(CurrentPart.Value.Rotation.X, CurrentPart.Value.Rotation.Y, CurrentPart.Value.Rotation.Z);
                    Part.Scale = new ServiceUtilities.Process.Geometry.Vector3D(CurrentPart.Value.Scale.X, CurrentPart.Value.Scale.Y, CurrentPart.Value.Scale.Z);
                    if (!CurrentPart.Value.Color.NoColor)
                    {
                        Part.Color = new ServiceUtilities.Process.Geometry.Color(CurrentPart.Value.Color.R, CurrentPart.Value.Color.G, CurrentPart.Value.Color.B);
                    }
                }
                _Node.GeometryParts.Add(Part);
            }
            for (int i = 0; i < FlatBufferMessage.Value.ChildNodesLength; i++)
            {
                _Node.ChildNodes.Add(FlatBufferMessage.Value.ChildNodes(i));
            }
            return _Node;
        }

        public LodMessage ConvertNodeG(FBGeometryNode? FlatBufferMessage)
        {
            LodMessage _Node = new LodMessage();
            _Node.UniqueID = FlatBufferMessage.Value.UniqueID;
            _Node.LodNumber = FlatBufferMessage.Value.LodNumber;

            if (FlatBufferMessage.Value.LOD != null)
            {
                var CurrentFlatLOD = FlatBufferMessage.Value.LOD;
                ServiceUtilities.Process.Geometry.LOD CurrentLOD = new ServiceUtilities.Process.Geometry.LOD();
                CurrentLOD.VertexNormalTangentList = new List<ServiceUtilities.Process.Geometry.VertexNormalTangent>();
                
                for (int i=0; i < CurrentFlatLOD.Value.VertexNormalTangentListLength; i++)
                {
                    var Item = CurrentFlatLOD.Value.VertexNormalTangentList(i);
                    var VertNormTang = new ServiceUtilities.Process.Geometry.VertexNormalTangent();
                    VertNormTang.Vertex = new ServiceUtilities.Process.Geometry.Vector3D();
                    VertNormTang.Normal = new ServiceUtilities.Process.Geometry.Vector3D();
                    VertNormTang.Tangent = new ServiceUtilities.Process.Geometry.Vector3D();
                    if (Item.HasValue)
                    {
                        VertNormTang.Vertex = new ServiceUtilities.Process.Geometry.Vector3D(Item.Value.Vertex.X, Item.Value.Vertex.Y, Item.Value.Vertex.Z);
                        VertNormTang.Normal = new ServiceUtilities.Process.Geometry.Vector3D(Item.Value.Normal.X, Item.Value.Normal.Y, Item.Value.Normal.Z);
                        VertNormTang.Tangent = new ServiceUtilities.Process.Geometry.Vector3D(Item.Value.Tangent.X, Item.Value.Tangent.Y, Item.Value.Tangent.Z);
                    }
                    CurrentLOD.VertexNormalTangentList.Add(VertNormTang);
                }
                CurrentLOD.Indexes = new List<uint>();
                for (int i = 0; i < CurrentFlatLOD.Value.IndexesLength; i++)
                {
                    CurrentLOD.Indexes.Add(CurrentFlatLOD.Value.Indexes(i));
                }
                _Node.LODs.Add(CurrentLOD);
            }
            return _Node;
        }

        public MetadataNode ConvertNodeM(FBMetadataNode? FlatBufferMessage)
        {
            MetadataNode _Node = new MetadataNode();
            if(FlatBufferMessage.HasValue)
            {
                _Node.UniqueID = FlatBufferMessage.Value.UniqueID;
                _Node.Metadata = FlatBufferMessage.Value.Metadata;
            }
            return _Node;
        }

        private ConcurrentDictionary<ulong, LodMessage> GeometryNodeToAssemble = new ConcurrentDictionary<ulong, LodMessage>();

        private static void MergeGeometry(ConcurrentDictionary<ulong, LodMessage> _GeometryStore, LodMessage NewMessage)
        {
            _GeometryStore.AddOrUpdate(NewMessage.UniqueID, NewMessage, (K, V) =>
            {
                for (int i = 0; i < NewMessage.LODs.Count; ++i)
                {
                    if (NewMessage.LODs[i] != null)
                    {
                        V.LODs.Add(NewMessage.LODs[i]);
                    }
                }
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

        public void AddMessage(NodeMessage Message, Action<string> _ErrorMessageAction = null)
        {
            if (!Message.Done)
            {
                if (Message.Errors != null && Message.Errors.Length > 2)
                {
                    _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] Message Errors: {Message.Errors}");
                }

                if (Message.HierarchyNode != null)
                {
                    if(Message.HierarchyNode.ParentID == Message.HierarchyNode.UniqueID)
                    {
                        Message.HierarchyNode.ParentID = Node.UNDEFINED_ID;
                    }
                    AddItemToQueues(Message.HierarchyNode/*, MessageCompressCopy.HierarchyNode*/);
                }

                if (Message.GeometryNode != null)
                {

                    //AddItemToQueues(Message.GeometryNode, MessageCompressCopy.GeometryNode);

                    MergeGeometry(GeometryNodeToAssemble, Message.GeometryNode);
                }

                if (Message.MetadataNode != null)
                {
                    AddItemToQueues(Message.MetadataNode/*, MessageCompressCopy.MetadataNode*/);
                }

                Interlocked.Increment(ref QueuedMessageCount);
            }
            else
            {
                ExpectedMessageCount = Message.MessageCount;
            }


            _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] Message Count: {QueuedMessageCount}");
            //Check if Expected message count has been set
            if (ExpectedMessageCount != -1 && QueuedMessageCount >= ExpectedMessageCount)
            {
                lock (LockObject)
                {
                    if (!QueueComplete)
                    {
                        _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] Received End signal for {ExpectedMessageCount} messages");
                        CompleteMerge(GeometryNodeToAssemble);

                        foreach (var Node in GeometryNodeToAssemble)
                        {
                            AddItemToQueues(Node.Value);
                        }

                        SignalQueuingComplete();
                    }
                }
            }
        }

        private string CompleteWrites(Action<string> _ErrorMessageAction = null)
        {
            _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] Writing files");

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
                        _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] {ex.Message}\n{ex.StackTrace}");
                    }
                }
                return SUCCESS_STATE;
            }
            catch (Exception ex)
            {
                _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] {ex.Message}\n{ex.StackTrace}");
                return FAILED_STATE;
            }
        }

        private string UploadAllFiles(Action<string> _ErrorMessageAction = null)
        {
            _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] Uploading files");
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
                _ErrorMessageAction?.Invoke($"[{DateTime.Now.ToString("yyyy/MM/dd HH:mm:ss.fffff")}] {ex.Message}\n{ex.StackTrace}");
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
