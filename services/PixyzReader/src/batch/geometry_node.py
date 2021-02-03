import math
import capnpy
from batch.pixyz_algorithms import PixyzAlgorithms
from .geometry_mesh import GeometryMesh
from .logger import Logger

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class GeometryNode:
    def __init__(self, capnproto, thread_lock, occurrence, current_lod_level = 0, small_object_threshold = 50, scale_factor = 1000):
        #Parameters
        self.capnproto = capnproto
        self.occurrence = occurrence
        self.small_object_threshold = small_object_threshold
        self.scale_factor = scale_factor
        self.current_lod_level = current_lod_level
        self.thread_lock = thread_lock
        
        #Returns
        self.geometry_node = None
        self.error_messages = []

        occurrence_id = core.getProperty(self.occurrence, "Id")
        part = scene.getComponent(self.occurrence, scene.ComponentType.Part, False)
        lod_mesh = scene.getPartMesh(part)

        try:
            if current_lod_level < 5:
                self.small_object_threshold = 0

            lod_info, error_message_lod = GeometryMesh(self.capnproto, lod_mesh, self.small_object_threshold, self.scale_factor).Get()

            if error_message_lod:
                self.error_messages.append(error_message_lod)

            if lod_info != None:
                self.geometry_node = {}
                self.geometry_node["unique_id"] = int(occurrence_id)
                self.geometry_node["lod_number"] = int(self.current_lod_level)
                self.geometry_node["lod"] = lod_info
        except Exception as e:
            Logger().Error(f"=====> GeometryMesh Error {e}")
            self.error_messages.append(e)
        
    def Get(self):
        if self.geometry_node == None:
            return [self.geometry_node, self.error_messages]
        else:
            return [self.capnproto.CPGeometryNode(**self.geometry_node), self.error_messages]