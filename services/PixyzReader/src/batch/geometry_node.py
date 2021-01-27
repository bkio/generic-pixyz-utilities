from .utils import Utils
from .geometry_mesh import GeometryMesh
from .logger import Logger

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class GeometryNode:
    def __init__(self, occurrence, small_object_threshold = 50, scale_factor = 1000):
        #Parameters
        self.occurrence = occurrence
        self.small_object_threshold = small_object_threshold
        self.scale_factor = scale_factor
        
        #Returns
        self.geometry_node = None
        self.error_messages = []

        occurrence_id = core.getProperty(self.occurrence, "Id")
        part = scene.getComponent(self.occurrence, scene.ComponentType.Part, False)
        lod_mesh = scene.getPartMesh(part)

        try:
            lod, error_message_lod = GeometryMesh(lod_mesh, self.small_object_threshold, self.scale_factor).Get()

            self.geometry_node = {}
            self.geometry_node['id'] = occurrence_id
            self.geometry_node['lods'] = [ lod ]

            if error_message_lod:
                self.error_messages.append(error_message_lod)
        except Exception as e:
            Logger().Error(f"=====> GeometryMesh Error {e}")
            self.error_messages.append(e)
        
    def Get(self):
        return [self.geometry_node, self.error_messages]