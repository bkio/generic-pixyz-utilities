using Capnp;
using Capnp.Rpc;
using System;
using System.CodeDom.Compiler;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace CapnpGen
{
    [System.CodeDom.Compiler.GeneratedCode("capnpc-csharp", "1.3.0.0"), TypeId(0xd87915fcc10ed673UL)]
    public class CPColor : ICapnpSerializable
    {
        public const UInt64 typeId = 0xd87915fcc10ed673UL;
        void ICapnpSerializable.Deserialize(DeserializerState arg_)
        {
            var reader = READER.create(arg_);
            R = reader.R;
            G = reader.G;
            B = reader.B;
            applyDefaults();
        }

        public void serialize(WRITER writer)
        {
            writer.R = R;
            writer.G = G;
            writer.B = B;
        }

        void ICapnpSerializable.Serialize(SerializerState arg_)
        {
            serialize(arg_.Rewrap<WRITER>());
        }

        public void applyDefaults()
        {
        }

        public float R
        {
            get;
            set;
        }

        public float G
        {
            get;
            set;
        }

        public float B
        {
            get;
            set;
        }

        public struct READER
        {
            readonly DeserializerState ctx;
            public READER(DeserializerState ctx)
            {
                this.ctx = ctx;
            }

            public static READER create(DeserializerState ctx) => new READER(ctx);
            public static implicit operator DeserializerState(READER reader) => reader.ctx;
            public static implicit operator READER(DeserializerState ctx) => new READER(ctx);
            public float R => ctx.ReadDataFloat(0UL, 0F);
            public float G => ctx.ReadDataFloat(32UL, 0F);
            public float B => ctx.ReadDataFloat(64UL, 0F);
        }

        public class WRITER : SerializerState
        {
            public WRITER()
            {
                this.SetStruct(2, 0);
            }

            public float R
            {
                get => this.ReadDataFloat(0UL, 0F);
                set => this.WriteData(0UL, value, 0F);
            }

            public float G
            {
                get => this.ReadDataFloat(32UL, 0F);
                set => this.WriteData(32UL, value, 0F);
            }

            public float B
            {
                get => this.ReadDataFloat(64UL, 0F);
                set => this.WriteData(64UL, value, 0F);
            }
        }
    }

    [System.CodeDom.Compiler.GeneratedCode("capnpc-csharp", "1.3.0.0"), TypeId(0xc63a9c7da42e035cUL)]
    public class CPVector3D : ICapnpSerializable
    {
        public const UInt64 typeId = 0xc63a9c7da42e035cUL;
        void ICapnpSerializable.Deserialize(DeserializerState arg_)
        {
            var reader = READER.create(arg_);
            X = reader.X;
            Y = reader.Y;
            Z = reader.Z;
            applyDefaults();
        }

        public void serialize(WRITER writer)
        {
            writer.X = X;
            writer.Y = Y;
            writer.Z = Z;
        }

        void ICapnpSerializable.Serialize(SerializerState arg_)
        {
            serialize(arg_.Rewrap<WRITER>());
        }

        public void applyDefaults()
        {
        }

        public float X
        {
            get;
            set;
        }

        public float Y
        {
            get;
            set;
        }

        public float Z
        {
            get;
            set;
        }

        public struct READER
        {
            readonly DeserializerState ctx;
            public READER(DeserializerState ctx)
            {
                this.ctx = ctx;
            }

            public static READER create(DeserializerState ctx) => new READER(ctx);
            public static implicit operator DeserializerState(READER reader) => reader.ctx;
            public static implicit operator READER(DeserializerState ctx) => new READER(ctx);
            public float X => ctx.ReadDataFloat(0UL, 0F);
            public float Y => ctx.ReadDataFloat(32UL, 0F);
            public float Z => ctx.ReadDataFloat(64UL, 0F);
        }

        public class WRITER : SerializerState
        {
            public WRITER()
            {
                this.SetStruct(2, 0);
            }

            public float X
            {
                get => this.ReadDataFloat(0UL, 0F);
                set => this.WriteData(0UL, value, 0F);
            }

            public float Y
            {
                get => this.ReadDataFloat(32UL, 0F);
                set => this.WriteData(32UL, value, 0F);
            }

            public float Z
            {
                get => this.ReadDataFloat(64UL, 0F);
                set => this.WriteData(64UL, value, 0F);
            }
        }
    }

    [System.CodeDom.Compiler.GeneratedCode("capnpc-csharp", "1.3.0.0"), TypeId(0xdea485e87e4fc92aUL)]
    public class CPVertexNormalTangent : ICapnpSerializable
    {
        public const UInt64 typeId = 0xdea485e87e4fc92aUL;
        void ICapnpSerializable.Deserialize(DeserializerState arg_)
        {
            var reader = READER.create(arg_);
            Vertex = CapnpSerializable.Create<CapnpGen.CPVector3D>(reader.Vertex);
            Normal = CapnpSerializable.Create<CapnpGen.CPVector3D>(reader.Normal);
            Tangent = CapnpSerializable.Create<CapnpGen.CPVector3D>(reader.Tangent);
            applyDefaults();
        }

        public void serialize(WRITER writer)
        {
            Vertex?.serialize(writer.Vertex);
            Normal?.serialize(writer.Normal);
            Tangent?.serialize(writer.Tangent);
        }

        void ICapnpSerializable.Serialize(SerializerState arg_)
        {
            serialize(arg_.Rewrap<WRITER>());
        }

        public void applyDefaults()
        {
        }

        public CapnpGen.CPVector3D Vertex
        {
            get;
            set;
        }

        public CapnpGen.CPVector3D Normal
        {
            get;
            set;
        }

        public CapnpGen.CPVector3D Tangent
        {
            get;
            set;
        }

        public struct READER
        {
            readonly DeserializerState ctx;
            public READER(DeserializerState ctx)
            {
                this.ctx = ctx;
            }

            public static READER create(DeserializerState ctx) => new READER(ctx);
            public static implicit operator DeserializerState(READER reader) => reader.ctx;
            public static implicit operator READER(DeserializerState ctx) => new READER(ctx);
            public CapnpGen.CPVector3D.READER Vertex => ctx.ReadStruct(0, CapnpGen.CPVector3D.READER.create);
            public CapnpGen.CPVector3D.READER Normal => ctx.ReadStruct(1, CapnpGen.CPVector3D.READER.create);
            public CapnpGen.CPVector3D.READER Tangent => ctx.ReadStruct(2, CapnpGen.CPVector3D.READER.create);
        }

        public class WRITER : SerializerState
        {
            public WRITER()
            {
                this.SetStruct(0, 3);
            }

            public CapnpGen.CPVector3D.WRITER Vertex
            {
                get => BuildPointer<CapnpGen.CPVector3D.WRITER>(0);
                set => Link(0, value);
            }

            public CapnpGen.CPVector3D.WRITER Normal
            {
                get => BuildPointer<CapnpGen.CPVector3D.WRITER>(1);
                set => Link(1, value);
            }

            public CapnpGen.CPVector3D.WRITER Tangent
            {
                get => BuildPointer<CapnpGen.CPVector3D.WRITER>(2);
                set => Link(2, value);
            }
        }
    }

    [System.CodeDom.Compiler.GeneratedCode("capnpc-csharp", "1.3.0.0"), TypeId(0xd472d0468f84332fUL)]
    public class CPLOD : ICapnpSerializable
    {
        public const UInt64 typeId = 0xd472d0468f84332fUL;
        void ICapnpSerializable.Deserialize(DeserializerState arg_)
        {
            var reader = READER.create(arg_);
            VertexNormalTangentList = reader.VertexNormalTangentList?.ToReadOnlyList(_ => CapnpSerializable.Create<CapnpGen.CPVertexNormalTangent>(_));
            Indexes = reader.Indexes;
            applyDefaults();
        }

        public void serialize(WRITER writer)
        {
            writer.VertexNormalTangentList.Init(VertexNormalTangentList, (_s1, _v1) => _v1?.serialize(_s1));
            writer.Indexes.Init(Indexes);
        }

        void ICapnpSerializable.Serialize(SerializerState arg_)
        {
            serialize(arg_.Rewrap<WRITER>());
        }

        public void applyDefaults()
        {
        }

        public IReadOnlyList<CapnpGen.CPVertexNormalTangent> VertexNormalTangentList
        {
            get;
            set;
        }

        public IReadOnlyList<uint> Indexes
        {
            get;
            set;
        }

        public struct READER
        {
            readonly DeserializerState ctx;
            public READER(DeserializerState ctx)
            {
                this.ctx = ctx;
            }

            public static READER create(DeserializerState ctx) => new READER(ctx);
            public static implicit operator DeserializerState(READER reader) => reader.ctx;
            public static implicit operator READER(DeserializerState ctx) => new READER(ctx);
            public IReadOnlyList<CapnpGen.CPVertexNormalTangent.READER> VertexNormalTangentList => ctx.ReadList(0).Cast(CapnpGen.CPVertexNormalTangent.READER.create);
            public IReadOnlyList<uint> Indexes => ctx.ReadList(1).CastUInt();
        }

        public class WRITER : SerializerState
        {
            public WRITER()
            {
                this.SetStruct(0, 2);
            }

            public ListOfStructsSerializer<CapnpGen.CPVertexNormalTangent.WRITER> VertexNormalTangentList
            {
                get => BuildPointer<ListOfStructsSerializer<CapnpGen.CPVertexNormalTangent.WRITER>>(0);
                set => Link(0, value);
            }

            public ListOfPrimitivesSerializer<uint> Indexes
            {
                get => BuildPointer<ListOfPrimitivesSerializer<uint>>(1);
                set => Link(1, value);
            }
        }
    }

    [System.CodeDom.Compiler.GeneratedCode("capnpc-csharp", "1.3.0.0"), TypeId(0xdf9b2f1f57745bb5UL)]
    public class CPGeometryPart : ICapnpSerializable
    {
        public const UInt64 typeId = 0xdf9b2f1f57745bb5UL;
        void ICapnpSerializable.Deserialize(DeserializerState arg_)
        {
            var reader = READER.create(arg_);
            GeometryID = reader.GeometryID;
            Location = CapnpSerializable.Create<CapnpGen.CPVector3D>(reader.Location);
            Rotation = CapnpSerializable.Create<CapnpGen.CPVector3D>(reader.Rotation);
            Scale = CapnpSerializable.Create<CapnpGen.CPVector3D>(reader.Scale);
            Color = CapnpSerializable.Create<CapnpGen.CPColor>(reader.Color);
            applyDefaults();
        }

        public void serialize(WRITER writer)
        {
            writer.GeometryID = GeometryID;
            Location?.serialize(writer.Location);
            Rotation?.serialize(writer.Rotation);
            Scale?.serialize(writer.Scale);
            Color?.serialize(writer.Color);
        }

        void ICapnpSerializable.Serialize(SerializerState arg_)
        {
            serialize(arg_.Rewrap<WRITER>());
        }

        public void applyDefaults()
        {
        }

        public ulong GeometryID
        {
            get;
            set;
        }

        public CapnpGen.CPVector3D Location
        {
            get;
            set;
        }

        public CapnpGen.CPVector3D Rotation
        {
            get;
            set;
        }

        public CapnpGen.CPVector3D Scale
        {
            get;
            set;
        }

        public CapnpGen.CPColor Color
        {
            get;
            set;
        }

        public struct READER
        {
            readonly DeserializerState ctx;
            public READER(DeserializerState ctx)
            {
                this.ctx = ctx;
            }

            public static READER create(DeserializerState ctx) => new READER(ctx);
            public static implicit operator DeserializerState(READER reader) => reader.ctx;
            public static implicit operator READER(DeserializerState ctx) => new READER(ctx);
            public ulong GeometryID => ctx.ReadDataULong(0UL, 0UL);
            public CapnpGen.CPVector3D.READER Location => ctx.ReadStruct(0, CapnpGen.CPVector3D.READER.create);
            public CapnpGen.CPVector3D.READER Rotation => ctx.ReadStruct(1, CapnpGen.CPVector3D.READER.create);
            public CapnpGen.CPVector3D.READER Scale => ctx.ReadStruct(2, CapnpGen.CPVector3D.READER.create);
            public CapnpGen.CPColor.READER Color => ctx.ReadStruct(3, CapnpGen.CPColor.READER.create);
        }

        public class WRITER : SerializerState
        {
            public WRITER()
            {
                this.SetStruct(1, 4);
            }

            public ulong GeometryID
            {
                get => this.ReadDataULong(0UL, 0UL);
                set => this.WriteData(0UL, value, 0UL);
            }

            public CapnpGen.CPVector3D.WRITER Location
            {
                get => BuildPointer<CapnpGen.CPVector3D.WRITER>(0);
                set => Link(0, value);
            }

            public CapnpGen.CPVector3D.WRITER Rotation
            {
                get => BuildPointer<CapnpGen.CPVector3D.WRITER>(1);
                set => Link(1, value);
            }

            public CapnpGen.CPVector3D.WRITER Scale
            {
                get => BuildPointer<CapnpGen.CPVector3D.WRITER>(2);
                set => Link(2, value);
            }

            public CapnpGen.CPColor.WRITER Color
            {
                get => BuildPointer<CapnpGen.CPColor.WRITER>(3);
                set => Link(3, value);
            }
        }
    }

    [System.CodeDom.Compiler.GeneratedCode("capnpc-csharp", "1.3.0.0"), TypeId(0xbfb0f8df22582331UL)]
    public class CPHierarchyNode : ICapnpSerializable
    {
        public const UInt64 typeId = 0xbfb0f8df22582331UL;
        void ICapnpSerializable.Deserialize(DeserializerState arg_)
        {
            var reader = READER.create(arg_);
            UniqueID = reader.UniqueID;
            ParentID = reader.ParentID;
            MetadataID = reader.MetadataID;
            GeometryParts = reader.GeometryParts?.ToReadOnlyList(_ => CapnpSerializable.Create<CapnpGen.CPGeometryPart>(_));
            ChildNodes = reader.ChildNodes;
            applyDefaults();
        }

        public void serialize(WRITER writer)
        {
            writer.UniqueID = UniqueID;
            writer.ParentID = ParentID;
            writer.MetadataID = MetadataID;
            writer.GeometryParts.Init(GeometryParts, (_s1, _v1) => _v1?.serialize(_s1));
            writer.ChildNodes.Init(ChildNodes);
        }

        void ICapnpSerializable.Serialize(SerializerState arg_)
        {
            serialize(arg_.Rewrap<WRITER>());
        }

        public void applyDefaults()
        {
        }

        public ulong UniqueID
        {
            get;
            set;
        }

        public ulong ParentID
        {
            get;
            set;
        }

        public ulong MetadataID
        {
            get;
            set;
        }

        public IReadOnlyList<CapnpGen.CPGeometryPart> GeometryParts
        {
            get;
            set;
        }

        public IReadOnlyList<ulong> ChildNodes
        {
            get;
            set;
        }

        public struct READER
        {
            readonly DeserializerState ctx;
            public READER(DeserializerState ctx)
            {
                this.ctx = ctx;
            }

            public static READER create(DeserializerState ctx) => new READER(ctx);
            public static implicit operator DeserializerState(READER reader) => reader.ctx;
            public static implicit operator READER(DeserializerState ctx) => new READER(ctx);
            public ulong UniqueID => ctx.ReadDataULong(0UL, 0UL);
            public ulong ParentID => ctx.ReadDataULong(64UL, 0UL);
            public ulong MetadataID => ctx.ReadDataULong(128UL, 0UL);
            public IReadOnlyList<CapnpGen.CPGeometryPart.READER> GeometryParts => ctx.ReadList(0).Cast(CapnpGen.CPGeometryPart.READER.create);
            public IReadOnlyList<ulong> ChildNodes => ctx.ReadList(1).CastULong();
        }

        public class WRITER : SerializerState
        {
            public WRITER()
            {
                this.SetStruct(3, 2);
            }

            public ulong UniqueID
            {
                get => this.ReadDataULong(0UL, 0UL);
                set => this.WriteData(0UL, value, 0UL);
            }

            public ulong ParentID
            {
                get => this.ReadDataULong(64UL, 0UL);
                set => this.WriteData(64UL, value, 0UL);
            }

            public ulong MetadataID
            {
                get => this.ReadDataULong(128UL, 0UL);
                set => this.WriteData(128UL, value, 0UL);
            }

            public ListOfStructsSerializer<CapnpGen.CPGeometryPart.WRITER> GeometryParts
            {
                get => BuildPointer<ListOfStructsSerializer<CapnpGen.CPGeometryPart.WRITER>>(0);
                set => Link(0, value);
            }

            public ListOfPrimitivesSerializer<ulong> ChildNodes
            {
                get => BuildPointer<ListOfPrimitivesSerializer<ulong>>(1);
                set => Link(1, value);
            }
        }
    }

    [System.CodeDom.Compiler.GeneratedCode("capnpc-csharp", "1.3.0.0"), TypeId(0x97a7915258f1d2e5UL)]
    public class CPMetadataNode : ICapnpSerializable
    {
        public const UInt64 typeId = 0x97a7915258f1d2e5UL;
        void ICapnpSerializable.Deserialize(DeserializerState arg_)
        {
            var reader = READER.create(arg_);
            UniqueID = reader.UniqueID;
            Metadata = reader.Metadata;
            applyDefaults();
        }

        public void serialize(WRITER writer)
        {
            writer.UniqueID = UniqueID;
            writer.Metadata = Metadata;
        }

        void ICapnpSerializable.Serialize(SerializerState arg_)
        {
            serialize(arg_.Rewrap<WRITER>());
        }

        public void applyDefaults()
        {
        }

        public ulong UniqueID
        {
            get;
            set;
        }

        public string Metadata
        {
            get;
            set;
        }

        public struct READER
        {
            readonly DeserializerState ctx;
            public READER(DeserializerState ctx)
            {
                this.ctx = ctx;
            }

            public static READER create(DeserializerState ctx) => new READER(ctx);
            public static implicit operator DeserializerState(READER reader) => reader.ctx;
            public static implicit operator READER(DeserializerState ctx) => new READER(ctx);
            public ulong UniqueID => ctx.ReadDataULong(0UL, 0UL);
            public string Metadata => ctx.ReadText(0, null);
        }

        public class WRITER : SerializerState
        {
            public WRITER()
            {
                this.SetStruct(1, 1);
            }

            public ulong UniqueID
            {
                get => this.ReadDataULong(0UL, 0UL);
                set => this.WriteData(0UL, value, 0UL);
            }

            public string Metadata
            {
                get => this.ReadText(0, null);
                set => this.WriteText(0, value, null);
            }
        }
    }

    [System.CodeDom.Compiler.GeneratedCode("capnpc-csharp", "1.3.0.0"), TypeId(0xf078430ec7081872UL)]
    public class CPGeometryNode : ICapnpSerializable
    {
        public const UInt64 typeId = 0xf078430ec7081872UL;
        void ICapnpSerializable.Deserialize(DeserializerState arg_)
        {
            var reader = READER.create(arg_);
            UniqueID = reader.UniqueID;
            LodNumber = reader.LodNumber;
            Lod = CapnpSerializable.Create<CapnpGen.CPLOD>(reader.Lod);
            applyDefaults();
        }

        public void serialize(WRITER writer)
        {
            writer.UniqueID = UniqueID;
            writer.LodNumber = LodNumber;
            Lod?.serialize(writer.Lod);
        }

        void ICapnpSerializable.Serialize(SerializerState arg_)
        {
            serialize(arg_.Rewrap<WRITER>());
        }

        public void applyDefaults()
        {
        }

        public ulong UniqueID
        {
            get;
            set;
        }

        public int LodNumber
        {
            get;
            set;
        }

        public CapnpGen.CPLOD Lod
        {
            get;
            set;
        }

        public struct READER
        {
            readonly DeserializerState ctx;
            public READER(DeserializerState ctx)
            {
                this.ctx = ctx;
            }

            public static READER create(DeserializerState ctx) => new READER(ctx);
            public static implicit operator DeserializerState(READER reader) => reader.ctx;
            public static implicit operator READER(DeserializerState ctx) => new READER(ctx);
            public ulong UniqueID => ctx.ReadDataULong(0UL, 0UL);
            public int LodNumber => ctx.ReadDataInt(64UL, 0);
            public CapnpGen.CPLOD.READER Lod => ctx.ReadStruct(0, CapnpGen.CPLOD.READER.create);
        }

        public class WRITER : SerializerState
        {
            public WRITER()
            {
                this.SetStruct(2, 1);
            }

            public ulong UniqueID
            {
                get => this.ReadDataULong(0UL, 0UL);
                set => this.WriteData(0UL, value, 0UL);
            }

            public int LodNumber
            {
                get => this.ReadDataInt(64UL, 0);
                set => this.WriteData(64UL, value, 0);
            }

            public CapnpGen.CPLOD.WRITER Lod
            {
                get => BuildPointer<CapnpGen.CPLOD.WRITER>(0);
                set => Link(0, value);
            }
        }
    }

    [System.CodeDom.Compiler.GeneratedCode("capnpc-csharp", "1.3.0.0"), TypeId(0xbe44170a4123aa49UL)]
    public class CPNodeMessage : ICapnpSerializable
    {
        public const UInt64 typeId = 0xbe44170a4123aa49UL;
        void ICapnpSerializable.Deserialize(DeserializerState arg_)
        {
            var reader = READER.create(arg_);
            ModelID = reader.ModelID;
            Errors = reader.Errors;
            HierarchyNode = CapnpSerializable.Create<CapnpGen.CPHierarchyNode>(reader.HierarchyNode);
            MetadataNode = CapnpSerializable.Create<CapnpGen.CPMetadataNode>(reader.MetadataNode);
            GeometryNode = CapnpSerializable.Create<CapnpGen.CPGeometryNode>(reader.GeometryNode);
            Done = reader.Done;
            MessageCount = reader.MessageCount;
            applyDefaults();
        }

        public void serialize(WRITER writer)
        {
            writer.ModelID = ModelID;
            writer.Errors.Init(Errors);
            HierarchyNode?.serialize(writer.HierarchyNode);
            MetadataNode?.serialize(writer.MetadataNode);
            GeometryNode?.serialize(writer.GeometryNode);
            writer.Done = Done;
            writer.MessageCount = MessageCount;
        }

        void ICapnpSerializable.Serialize(SerializerState arg_)
        {
            serialize(arg_.Rewrap<WRITER>());
        }

        public void applyDefaults()
        {
        }

        public ulong ModelID
        {
            get;
            set;
        }

        public IReadOnlyList<string> Errors
        {
            get;
            set;
        }

        public CapnpGen.CPHierarchyNode HierarchyNode
        {
            get;
            set;
        }

        public CapnpGen.CPMetadataNode MetadataNode
        {
            get;
            set;
        }

        public CapnpGen.CPGeometryNode GeometryNode
        {
            get;
            set;
        }

        public bool Done
        {
            get;
            set;
        }

        public int MessageCount
        {
            get;
            set;
        }

        public struct READER
        {
            readonly DeserializerState ctx;
            public READER(DeserializerState ctx)
            {
                this.ctx = ctx;
            }

            public static READER create(DeserializerState ctx) => new READER(ctx);
            public static implicit operator DeserializerState(READER reader) => reader.ctx;
            public static implicit operator READER(DeserializerState ctx) => new READER(ctx);
            public ulong ModelID => ctx.ReadDataULong(0UL, 0UL);
            public IReadOnlyList<string> Errors => ctx.ReadList(0).CastText2();
            public CapnpGen.CPHierarchyNode.READER HierarchyNode => ctx.ReadStruct(1, CapnpGen.CPHierarchyNode.READER.create);
            public CapnpGen.CPMetadataNode.READER MetadataNode => ctx.ReadStruct(2, CapnpGen.CPMetadataNode.READER.create);
            public CapnpGen.CPGeometryNode.READER GeometryNode => ctx.ReadStruct(3, CapnpGen.CPGeometryNode.READER.create);
            public bool Done => ctx.ReadDataBool(64UL, false);
            public int MessageCount => ctx.ReadDataInt(96UL, 0);
        }

        public class WRITER : SerializerState
        {
            public WRITER()
            {
                this.SetStruct(2, 4);
            }

            public ulong ModelID
            {
                get => this.ReadDataULong(0UL, 0UL);
                set => this.WriteData(0UL, value, 0UL);
            }

            public ListOfTextSerializer Errors
            {
                get => BuildPointer<ListOfTextSerializer>(0);
                set => Link(0, value);
            }

            public CapnpGen.CPHierarchyNode.WRITER HierarchyNode
            {
                get => BuildPointer<CapnpGen.CPHierarchyNode.WRITER>(1);
                set => Link(1, value);
            }

            public CapnpGen.CPMetadataNode.WRITER MetadataNode
            {
                get => BuildPointer<CapnpGen.CPMetadataNode.WRITER>(2);
                set => Link(2, value);
            }

            public CapnpGen.CPGeometryNode.WRITER GeometryNode
            {
                get => BuildPointer<CapnpGen.CPGeometryNode.WRITER>(3);
                set => Link(3, value);
            }

            public bool Done
            {
                get => this.ReadDataBool(64UL, false);
                set => this.WriteData(64UL, value, false);
            }

            public int MessageCount
            {
                get => this.ReadDataInt(96UL, 0);
                set => this.WriteData(96UL, value, 0);
            }
        }
    }
}