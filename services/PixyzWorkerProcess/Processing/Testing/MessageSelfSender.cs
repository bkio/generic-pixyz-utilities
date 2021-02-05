using BCloudServiceUtilities;
using Google.Protobuf;
using PixyzWorkerProcess.Processing.Models;
using PixyzWorkerProcess.Processing.PB;
using ServiceUtilities.Process.RandomAccessFile;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace PixyzWorkerProcess.Processing.Testing
{
    public class MessageSelfSender
    {
        public static void LoadAndSendData(string _Filename, IBPubSubServiceInterface _PubSub, Action<string> _ErrorMessageAction = null)
        {
            List<HierarchyNode> HierarchyNodes = new List<HierarchyNode>();
            List<GeometryNode> GeometryNodes = new List<GeometryNode>();
            List<MetadataNode> MetadataNodes = new List<MetadataNode>();

            string Ext = "";
            EDeflateCompression CompressEnum;

            bool ExistsP = File.Exists($"{_Filename}.x3dc_h") && File.Exists($"{_Filename}.x3dc_g") && File.Exists($"{_Filename}.x3dc_m");
            bool ExistsC = File.Exists($"{_Filename}.x3dp_h") && File.Exists($"{_Filename}.x3dp_g") && File.Exists($"{_Filename}.x3dp_m");

            if (ExistsP)
            {
                CompressEnum = EDeflateCompression.DoNotCompress;
                Ext = "x3dp_";
            }
            else if (ExistsC)
            {
                CompressEnum = EDeflateCompression.Compress;
                Ext = "x3dc_";
            }
            else
            {
                throw new FileNotFoundException("The specified file could not be found");
            }

            FileStream ReadFileStreamH = new FileStream($"{_Filename}.{Ext}h", FileMode.Open);
            FileStream ReadFileStreamG = new FileStream($"{_Filename}.{Ext}g", FileMode.Open);
            FileStream ReadFileStreamM = new FileStream($"{_Filename}.{Ext}m", FileMode.Open);

            int LodCount = 0;
            ManualResetEvent ResetEvent = new ManualResetEvent(false);
            int DoneCount = 0;

            using (XStreamReader ReaderH = new XStreamReader(ENodeType.Hierarchy, ReadFileStreamH,
                (_Sdk) =>
                {

                },
                (_Node) =>
                {
                    //Convert hierarchy here
                    HierarchyNode HNode = (HierarchyNode)_Node;
                    HierarchyNodes.Add(HNode);

                }, CompressEnum))
            {
                if (!ReaderH.Process(Console.WriteLine))
                {
                    throw new Exception("Failed");
                }

                Interlocked.Increment(ref DoneCount);

                if (DoneCount >= 3)
                {
                    ResetEvent.Set();
                }
            }

            using (XStreamReader ReaderM = new XStreamReader(ENodeType.Metadata, ReadFileStreamM,
            (_Sdk) =>
            {

            },
            (_Node) =>
            {
                //Convert metadata here
                MetadataNode MNode = (MetadataNode)_Node;
                MetadataNodes.Add(MNode);

            }, CompressEnum))
            {
                if (!ReaderM.Process(Console.WriteLine))
                {
                    throw new Exception("Failed");
                }

                Interlocked.Increment(ref DoneCount);

                if (DoneCount >= 3)
                {
                    ResetEvent.Set();
                }
            }

            using (XStreamReader ReaderG = new XStreamReader(ENodeType.Geometry, ReadFileStreamG,
                (_Sdk) =>
                {
                },
                (_Node) =>
                {
                    //Convert geometry here
                    GeometryNode GNode = (GeometryNode)_Node;
                    GeometryNodes.Add(GNode);

                    if (GNode.LODs.Count > LodCount)
                    {
                        LodCount = GNode.LODs.Count;
                    }

                }, CompressEnum))
            {
                if (!ReaderG.Process(Console.WriteLine))
                {
                    throw new Exception("Failed");
                }
                Interlocked.Increment(ref DoneCount);

                if (DoneCount >= 3)
                {
                    ResetEvent.Set();
                }
            }

            ResetEvent.WaitOne();

            int Count = 0;

            Stopwatch sw = new Stopwatch();
            sw.Start();

            Parallel.ForEach(HierarchyNodes, (Node) =>
            {
                NodeMessage SendMessage = new NodeMessage();
                SendMessage.HierarchyNode = Node;

                int CurrentCount = Interlocked.Increment(ref Count);
                
                SendMessage.Done = false;
                SendMessage.ModelID = 0;
                SendMessage.MessageCount = CurrentCount;

                string EncodedMessage = PrepareMessage(SendMessage);
                Publish(EncodedMessage, _PubSub, _ErrorMessageAction);
            });

            Parallel.ForEach(MetadataNodes, (Node) => 
            {
                NodeMessage SendMessage = new NodeMessage();
                SendMessage.MetadataNode = Node;

                int CurrentCount = Interlocked.Increment(ref Count);
                SendMessage.Done = false;
                SendMessage.ModelID = 0;
                SendMessage.MessageCount = CurrentCount;

                string EncodedMessage = PrepareMessage(SendMessage);
                Publish(EncodedMessage, _PubSub, _ErrorMessageAction);
            });

            Parallel.ForEach(GeometryNodes, (Node) => { 
                NodeMessage SendMessage = new NodeMessage();
                SendMessage.GeometryNode = new LodMessage() { LODs = Node.LODs, UniqueID = Node.UniqueID };

                int CurrentCount = Interlocked.Increment(ref Count);
                SendMessage.Done = false;
                SendMessage.ModelID = 0;
                SendMessage.MessageCount = CurrentCount;

                string EncodedMessage = PrepareMessage(SendMessage);
                Publish(EncodedMessage, _PubSub, _ErrorMessageAction);
            });

            NodeMessage LastMessage = new NodeMessage();
            LastMessage.Done = true;
            LastMessage.MessageCount = Count;

            string EncodedLastMessage = PrepareMessage(LastMessage);
            Publish(EncodedLastMessage, _PubSub, _ErrorMessageAction);

            sw.Stop();

            _ErrorMessageAction?.Invoke($"Converted and wrote {Count} messages in {sw.ElapsedMilliseconds} ms");
        }

        public static void Publish(string Message, IBPubSubServiceInterface _PubSub, Action<string> _ErrorMessageAction = null)
        {
            _PubSub.CustomPublish("models", Message, _ErrorMessageAction);
        }

        public static string PrepareMessage(NodeMessage Message)
        {
            PNodeMessage PMessage = ConvertNodeMessage(Message);

            MemoryStream Input = new MemoryStream(PMessage.ToByteArray());
            MemoryStream Output = new MemoryStream();

            using (DeflateStream CompressStream = new DeflateStream(Output, CompressionMode.Compress))
            {
                Input.CopyTo(CompressStream);
            }

            string Result = Convert.ToBase64String(Output.ToArray());
            Input.Close();
            Output.Close();

            return Result;

        }


        public static PNodeMessage ConvertNodeMessage(NodeMessage ProtoMessage)
        {
            PNodeMessage _Message = new PNodeMessage();
            _Message.Done = ProtoMessage.Done;
            _Message.ModelID = ProtoMessage.ModelID;
            _Message.MessageCount = ProtoMessage.MessageCount;
            _Message.Errors = ProtoMessage.Errors;

            if (ProtoMessage.HierarchyNode != null)
            {
                _Message.HierarchyNode = ConvertNodeH(ProtoMessage.HierarchyNode);
            }
            if (ProtoMessage.GeometryNode != null)
            {
                _Message.GeometryNode = ConvertNodeG(ProtoMessage.GeometryNode);
            }
            if (ProtoMessage.MetadataNode != null)
            {
                _Message.MetadataNode = ConvertNodeM(ProtoMessage.MetadataNode);
            }
            return _Message;
        }

        public static PHierarchyNode ConvertNodeH(HierarchyNode ProtoNode)
        {
            PHierarchyNode _Node = new PHierarchyNode();
            _Node.UniqueID = ProtoNode.UniqueID;
            _Node.ParentID = ProtoNode.ParentID;
            _Node.MetadataID = ProtoNode.MetadataID;

            if (ProtoNode.GeometryParts.Count > 0)
            {
                foreach (var Item in ProtoNode.GeometryParts)
                {
                    var Part = new PGeometryPart();
                    Part.GeometryID = Item.GeometryID;
                    Part.Location = new PVector3D();
                    Part.Rotation = new PVector3D();
                    Part.Scale = new PVector3D();
                    Part.Color = new PColorRGB();

                    if (Item.Location != null)
                    {
                        Part.Location = new PVector3D() { X =Item.Location.X, Y = Item.Location.Y, Z = Item.Location.Z };
                    }
                    if (Item.Rotation != null)
                    {
                        Part.Rotation = new PVector3D() { X = Item.Rotation.X, Y = Item.Rotation.Y, Z = Item.Rotation.Z };
                    }
                    if (Item.Scale != null)
                    {
                        Part.Scale = new PVector3D() { X = Item.Scale.X, Y = Item.Scale.Y, Z = Item.Scale.Z };
                    }
                    if (Item.Color != null)
                    {
                        Part.Color = new PColorRGB() { R = Item.Color.R, G = Item.Color.G, B = Item.Color.B };
                    }
                    _Node.GeometryParts.Add(Part);
                }
            }
            if (ProtoNode.ChildNodes.Count > 0)
            {
                _Node.ChildNodes.AddRange(ProtoNode.ChildNodes);
            }
            return _Node;
        }

        public static PGeometryNode ConvertNodeG(LodMessage ProtoNode)
        {
            PGeometryNode _Node = new PGeometryNode();
            _Node.UniqueID = ProtoNode.UniqueID;
            _Node.LodNumber = ProtoNode.LodNumber;
            if (ProtoNode.LODs.Count == 1)
            {
                var CurrentProtoLOD = ProtoNode.LODs[0];
                PLOD CurrentLOD = new PLOD();
                
                foreach (var Item in CurrentProtoLOD.VertexNormalTangentList)
                {
                    var VertNormTang = new PVertexNormalTangent();
                    VertNormTang.Vertex = new PVector3D();
                    VertNormTang.Normal = new PVector3D();
                    VertNormTang.Tangent = new PVector3D();
                    if (Item.Vertex != null)
                    {
                        VertNormTang.Vertex = new PVector3D() { X = Item.Vertex.X, Y = Item.Vertex.Y, Z = Item.Vertex.Z };
                    }
                    if (Item.Normal != null)
                    {
                        VertNormTang.Normal = new PVector3D() { X = Item.Normal.X, Y = Item.Normal.Y, Z = Item.Normal.Z };
                    }
                    if (Item.Tangent != null)
                    {
                        VertNormTang.Tangent = new PVector3D() { X = Item.Tangent.X, Y = Item.Tangent.Y, Z = Item.Tangent.Z };
                    }
                    CurrentLOD.VertexNormalTangentList.Add(VertNormTang);
                }
                
                CurrentLOD.Indexes.AddRange(CurrentProtoLOD.Indexes);
                _Node.LOD = CurrentLOD;
            }
            return _Node;
        }

        public static PMetadataNode ConvertNodeM(MetadataNode ProtoNode)
        {
            PMetadataNode _Node = new PMetadataNode();
            _Node.UniqueID = ProtoNode.UniqueID;
            _Node.Metadata = ProtoNode.Metadata;
            return _Node;
        }
    }
}
