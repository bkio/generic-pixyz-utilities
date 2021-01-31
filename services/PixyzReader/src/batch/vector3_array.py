from .protobuf_messages_pb2 import *
class Vector3Array:
    def __init__(self, array = [], divider = 1):
        self.vector3_array = []
        for item in array:
            VectorData = PVector3D()
            VectorData.X = item.x / divider
            VectorData.Y = item.y / divider
            VectorData.Z = item.z / divider
            self.vector3_array.append(VectorData)

    def Get(self):
        return self.vector3_array