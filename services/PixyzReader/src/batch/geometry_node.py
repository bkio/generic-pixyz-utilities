from .utils import Utils
from .geometry_mesh import GeometryMesh
from .logger import Logger

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class GeometryNode:
    def __init__(self, occurrence, current_lod_level=0, small_object_threshold = 50, scale_factor = 1000):
        #Parameters
        self.occurrence = occurrence
        self.current_lod_level = current_lod_level
        self.small_object_threshold = small_object_threshold
        self.scale_factor = scale_factor
        
        #Returns
        self.geometry_node = None
        self.error_messages = []

        occurrence_id = core.getProperty(self.occurrence, "Id")
        part = scene.getComponent(self.occurrence, scene.ComponentType.Part, False)
        lod_mesh = scene.getPartMesh(part)

        try:
            lod, error_message_lod = GeometryMesh(occurrence, lod_mesh, self.small_object_threshold, self.scale_factor).Get()

            if lod == None:
                self.geometry_node = None
            else:
                self.geometry_node = {}
                self.geometry_node['id'] = occurrence_id
                self.geometry_node['lodNumber'] = current_lod_level
                self.geometry_node['lod'] = lod

            if error_message_lod != None:
                self.error_messages.append(error_message_lod)
        except Exception as e:
            Logger().Error(f"=====> GeometryMesh Error {e}")
            self.error_messages.append(e)
        
    def Get(self):
        return [self.geometry_node, self.error_messages]