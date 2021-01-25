import math
from .utils import Utils
from .geometry_mesh import GeometryMesh
from .pixyz_algorithms import PixyzAlgorithms
from .logger import Logger

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class GeometryNode:
    def __init__(self, thread_lock, occurrence, decimate_target_strategy = "ratio", lod_levels = [100, 90, 80, 60, 20, 10], small_object_threshold = 50, scale_factor = 1000):
        #Parameters
        self.thread_lock = thread_lock
        self.occurrence = occurrence
        self.decimate_target_strategy = decimate_target_strategy
        self.lod_levels = lod_levels
        self.small_object_threshold = small_object_threshold
        self.scale_factor = scale_factor
        
        #Returns
        self.geometry_nodes = []
        self.error_messages = []

        if self.__IsPrototypePart() == True:
            occurrence_id = core.getProperty(self.occurrence, "Id")
            part = scene.getComponent(self.occurrence, scene.ComponentType.Part, False)
            targetTriangleCounts = []

            if len(self.lod_levels) <= 0:
                self.lod_levels = [100]

            if self.decimate_target_strategy == "ratio":
                for current_lod in range(len(self.lod_levels)):
                    triangle_count = scene.getPolygonCount([self.occurrence], True, False, False)
                    decimate_value = triangle_count
                    if current_lod > 0:
                        decimate_value = int(math.floor(triangle_count * (lod_levels[current_lod] / 100)))
                    targetTriangleCounts.append(decimate_value)

            for current_lod in range(len(self.lod_levels)):
                try:
                    if current_lod > 0:
                        # if target_strategy == triangleCount: use that value directly, otherwise convert to ratio based calculation
                        decimate_value = self.lod_levels[current_lod]

                        if self.decimate_target_strategy == "ratio":
                            decimate_value = targetTriangleCounts[current_lod]

                        self.thread_lock.acquire()
                        PixyzAlgorithms(verbose=False).DecimateTarget([self.occurrence], ["triangleCount", decimate_value])
                        self.thread_lock.release()
                except Exception as e:
                    Logger().Error(f"=====> LOD Decimate Error, LOD{current_lod} -TargetStrategy: {self.decimate_target_strategy} -Error: {e}")
                
                try:
                    lod_mesh = scene.getPartMesh(part)
                    
                    lod, error_message_lod = GeometryMesh(current_lod, lod_mesh, self.small_object_threshold, self.scale_factor).Get()

                    geometry_node = {}
                    geometry_node['id'] = occurrence_id
                    geometry_node['lodNumber'] = current_lod
                    geometry_node['lod'] = lod
                    self.geometry_nodes.append(geometry_node)

                    if error_message_lod:
                        self.error_messages.append(error_message_lod)
                except Exception as e:
                    Logger().Error(f"=====> GeometryMesh Error, LOD{current_lod} -TargetStrategy: {self.lod_target_strategy} -Error: {e}")
                    self.error_messages.append(e)

    def __IsPrototypePart(self):
        partOccurrenceList = scene.getPartOccurrences(scene.getRoot())
        prototype = scene.getPrototype(self.occurrence)

        # if Utils().BisectSearch(partOccurrenceList, self.occurrence) and prototype == 0:
        #     return True
        for item in partOccurrenceList:
            if item == self.occurrence and prototype == 0:
                return True
        return False

    def Get(self):
        return [self.geometry_nodes, self.error_messages]