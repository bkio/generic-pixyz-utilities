// <auto-generated>
//  automatically generated by the FlatBuffers compiler, do not modify
// </auto-generated>

namespace FB
{

using global::System;
using global::System.Collections.Generic;
using global::FlatBuffers;

public struct FBLOD : IFlatbufferObject
{
  private Table __p;
  public ByteBuffer ByteBuffer { get { return __p.bb; } }
  public static void ValidateVersion() { FlatBufferConstants.FLATBUFFERS_1_12_0(); }
  public static FBLOD GetRootAsFBLOD(ByteBuffer _bb) { return GetRootAsFBLOD(_bb, new FBLOD()); }
  public static FBLOD GetRootAsFBLOD(ByteBuffer _bb, FBLOD obj) { return (obj.__assign(_bb.GetInt(_bb.Position) + _bb.Position, _bb)); }
  public void __init(int _i, ByteBuffer _bb) { __p = new Table(_i, _bb); }
  public FBLOD __assign(int _i, ByteBuffer _bb) { __init(_i, _bb); return this; }

  public FB.FBVertexNormalTangent? VertexNormalTangentList(int j) { int o = __p.__offset(4); return o != 0 ? (FB.FBVertexNormalTangent?)(new FB.FBVertexNormalTangent()).__assign(__p.__vector(o) + j * 36, __p.bb) : null; }
  public int VertexNormalTangentListLength { get { int o = __p.__offset(4); return o != 0 ? __p.__vector_len(o) : 0; } }
  public uint Indexes(int j) { int o = __p.__offset(6); return o != 0 ? __p.bb.GetUint(__p.__vector(o) + j * 4) : (uint)0; }
  public int IndexesLength { get { int o = __p.__offset(6); return o != 0 ? __p.__vector_len(o) : 0; } }
#if ENABLE_SPAN_T
  public Span<uint> GetIndexesBytes() { return __p.__vector_as_span<uint>(6, 4); }
#else
  public ArraySegment<byte>? GetIndexesBytes() { return __p.__vector_as_arraysegment(6); }
#endif
  public uint[] GetIndexesArray() { return __p.__vector_as_array<uint>(6); }

  public static Offset<FB.FBLOD> CreateFBLOD(FlatBufferBuilder builder,
      VectorOffset VertexNormalTangentListOffset = default(VectorOffset),
      VectorOffset IndexesOffset = default(VectorOffset)) {
    builder.StartTable(2);
    FBLOD.AddIndexes(builder, IndexesOffset);
    FBLOD.AddVertexNormalTangentList(builder, VertexNormalTangentListOffset);
    return FBLOD.EndFBLOD(builder);
  }

  public static void StartFBLOD(FlatBufferBuilder builder) { builder.StartTable(2); }
  public static void AddVertexNormalTangentList(FlatBufferBuilder builder, VectorOffset VertexNormalTangentListOffset) { builder.AddOffset(0, VertexNormalTangentListOffset.Value, 0); }
  public static void StartVertexNormalTangentListVector(FlatBufferBuilder builder, int numElems) { builder.StartVector(36, numElems, 4); }
  public static void AddIndexes(FlatBufferBuilder builder, VectorOffset IndexesOffset) { builder.AddOffset(1, IndexesOffset.Value, 0); }
  public static VectorOffset CreateIndexesVector(FlatBufferBuilder builder, uint[] data) { builder.StartVector(4, data.Length, 4); for (int i = data.Length - 1; i >= 0; i--) builder.AddUint(data[i]); return builder.EndVector(); }
  public static VectorOffset CreateIndexesVectorBlock(FlatBufferBuilder builder, uint[] data) { builder.StartVector(4, data.Length, 4); builder.Add(data); return builder.EndVector(); }
  public static void StartIndexesVector(FlatBufferBuilder builder, int numElems) { builder.StartVector(4, numElems, 4); }
  public static Offset<FB.FBLOD> EndFBLOD(FlatBufferBuilder builder) {
    int o = builder.EndTable();
    return new Offset<FB.FBLOD>(o);
  }
};


}
