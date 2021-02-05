
from .PB.protob_messages_pb2 import PGeometryPart
class Vector3:
    def __init__(self, proto: PGeometryPart, x, y, z):
        self.proto = proto
        self.x = x
        self.y = y
        self.z = z

    def SetLocation(self):
        self.proto.Location.X = float(format(self.x, 'f'))
        self.proto.Location.Y = float(format(self.y, 'f'))
        self.proto.Location.Z = float(format(self.z, 'f'))
    
    def SetRotation(self):
        self.proto.Rotation.X = float(format(self.x, 'f'))
        self.proto.Rotation.Y = float(format(self.y, 'f'))
        self.proto.Rotation.Z = float(format(self.z, 'f'))
    
    def SetScale(self):
        self.proto.Scale.X = float(format(self.x, 'f'))
        self.proto.Scale.Y = float(format(self.y, 'f'))
        self.proto.Scale.Z = float(format(self.z, 'f'))