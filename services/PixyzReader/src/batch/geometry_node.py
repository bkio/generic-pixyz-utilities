import math
from batch.pixyz_algorithms import PixyzAlgorithms
from .geometry_mesh import GeometryMesh
from .logger import Logger
from .protobuf_messages_pb2 import PGeometryNode

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class GeometryNode:
    def __init__(self, proto: PGeometryNode, thread_lock, occurrence, current_lod_level = 0, small_object_threshold = 50, scale_factor = 1000):
        #Parameters
        self.proto = proto
        self.occurrence = occurrence
        self.small_object_threshold = small_object_threshold
        self.scale_factor = scale_factor
        self.current_lod_level = current_lod_level
        self.thread_lock = thread_lock
        
        #Returns
        self.error_messages = []

        occurrence_id = core.getProperty(self.occurrence, "Id")
        part = scene.getComponent(self.occurrence, scene.ComponentType.Part, False)
        lod_mesh = scene.getPartMesh(part)
        
        self.proto.UniqueID = int(occurrence_id)
        self.proto.LodNumber = int(current_lod_level)

        try:
            if current_lod_level < 5:
                self.small_object_threshold = 0

            proto_lod = self.proto.LODs.add()
            error_message_lod = GeometryMesh(proto_lod, lod_mesh, self.small_object_threshold, self.scale_factor).Get()

            if error_message_lod:
                self.error_messages.append(error_message_lod)

        except Exception as e:
            Logger().Error(f"=====> GeometryMesh Error {e}")
            self.error_messages.append(e)
        
    def Get(self):
        return self.error_messages