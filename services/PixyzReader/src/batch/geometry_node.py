from batch.pixyz_algorithms import PixyzAlgorithms
from .geometry_mesh import GeometryMesh
from .logger import Logger
from .protobuf_messages_pb2 import *

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class GeometryNode:
    def __init__(self, proto: PGeometryNode, thread_lock, occurrence, current_lod_level=0, target_strategy="ratio", decimate_value=0, small_object_threshold = 50, scale_factor = 1000):
        #Parameters
        self.proto = proto
        self.occurrence = occurrence
        self.small_object_threshold = small_object_threshold
        self.scale_factor = scale_factor
        self.current_lod_level = current_lod_level
        self.decimate_value = decimate_value
        self.target_strategy = target_strategy
        self.thread_lock = thread_lock
        
        #Returns
        self.geometry_node = None
        self.error_messages = []

        occurrence_id = core.getProperty(self.occurrence, "Id")
        part = scene.getComponent(self.occurrence, scene.ComponentType.Part, False)
        lod_mesh = scene.getPartMesh(part)

        try:
            self.thread_lock.acquire()
            PixyzAlgorithms(verbose=False).DecimateTarget([self.occurrence], [self.target_strategy, self.decimate_value])
            self.thread_lock.release()
        except Exception as e:
            Logger().Error(f"=====> GeometryMesh DecimateTarget Error {e}")

        try:
            self.proto.UniqueID = int(occurrence_id)
            self.proto.LodNumber = self.current_lod_level
            proto_lod = self.proto.LODs.add()
            lod_info, error_message_lod = GeometryMesh(proto_lod, lod_mesh, self.small_object_threshold, self.scale_factor).Get()
            # self.geometry_node.LODs.append(lod_info)

            if error_message_lod:
                self.error_messages.append(error_message_lod)

            if lod_info != None:
                self.geometry_node = 1
        except Exception as e:
            Logger().Error(f"=====> GeometryMesh Error {e}")
            self.error_messages.append(e)
        
    def Get(self):
        return [self.geometry_node, self.error_messages]