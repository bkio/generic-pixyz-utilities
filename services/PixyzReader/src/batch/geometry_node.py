from .pixyz_algorithms import PixyzAlgorithms
from .geometry_mesh import GeometryMesh
from .logger import Logger
from .PB.protob_messages_pb2 import PGeometryNode

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class GeometryNode:
    def __init__(self, proto: PGeometryNode, thread_lock, occurrence, current_lod_level = 0, small_object_threshold = 50, scale_factor = 1000):
        #Parameters
        self.proto = proto
        self.thread_lock = thread_lock
        self.occurrence = occurrence
        self.current_lod_level = current_lod_level
        self.small_object_threshold = small_object_threshold
        self.scale_factor = scale_factor
        
        #Returns
        self.has_geometry_node = False
        self.error_messages = []

        occurrence_id = core.getProperty(self.occurrence, "Id")
        part = scene.getComponent(self.occurrence, scene.ComponentType.Part, False)
        lod_mesh = scene.getPartMesh(part)
        
        self.proto.UniqueID = int(occurrence_id)
        self.proto.LodNumber = int(current_lod_level)

        try:
            has_lod, error_message_lod = GeometryMesh(self.proto.LOD, self.occurrence, lod_mesh, self.small_object_threshold, self.scale_factor).Get()

            if error_message_lod != None:
                self.error_messages.append(error_message_lod)

            self.has_geometry_node = has_lod

            if has_lod == False:
                self.proto = None
        except Exception as e:
            self.has_geometry_node = False
            self.error_messages.append(e)
            Logger().Error(f"=====> GeometryMesh Error {e}")
        
    def Get(self):
        return [self.has_geometry_node, self.error_messages]