
from .protobuf_messages_pb2 import *
class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def Get(self):
        VectorData = PVector3D()
        VectorData.X = float(format(self.x, 'f'))
        VectorData.Y = float(format(self.y, 'f'))
        VectorData.Z = float(format(self.z, 'f'))
        return VectorData