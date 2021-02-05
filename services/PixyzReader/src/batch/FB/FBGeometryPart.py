# automatically generated by the FlatBuffers compiler, do not modify

# namespace: FB

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class FBGeometryPart(object):
    __slots__ = ['_tab']

    # FBGeometryPart
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # FBGeometryPart
    def GeometryID(self): return self._tab.Get(flatbuffers.number_types.Uint64Flags, self._tab.Pos + flatbuffers.number_types.UOffsetTFlags.py_type(0))
    # FBGeometryPart
    def Location(self, obj):
        obj.Init(self._tab.Bytes, self._tab.Pos + 8)
        return obj

    # FBGeometryPart
    def Rotation(self, obj):
        obj.Init(self._tab.Bytes, self._tab.Pos + 20)
        return obj

    # FBGeometryPart
    def Scale(self, obj):
        obj.Init(self._tab.Bytes, self._tab.Pos + 32)
        return obj

    # FBGeometryPart
    def Color(self, obj):
        obj.Init(self._tab.Bytes, self._tab.Pos + 44)
        return obj


def CreateFBGeometryPart(builder, GeometryID, Location_X, Location_Y, Location_Z, Rotation_X, Rotation_Y, Rotation_Z, Scale_X, Scale_Y, Scale_Z, Color_R, Color_G, Color_B, Color_NoColor):
    builder.Prep(8, 48)
    builder.Prep(1, 4)
    builder.PrependBool(Color_NoColor)
    builder.PrependUint8(Color_B)
    builder.PrependUint8(Color_G)
    builder.PrependUint8(Color_R)
    builder.Prep(4, 12)
    builder.PrependFloat32(Scale_Z)
    builder.PrependFloat32(Scale_Y)
    builder.PrependFloat32(Scale_X)
    builder.Prep(4, 12)
    builder.PrependFloat32(Rotation_Z)
    builder.PrependFloat32(Rotation_Y)
    builder.PrependFloat32(Rotation_X)
    builder.Prep(4, 12)
    builder.PrependFloat32(Location_Z)
    builder.PrependFloat32(Location_Y)
    builder.PrependFloat32(Location_X)
    builder.PrependUint64(GeometryID)
    return builder.Offset()