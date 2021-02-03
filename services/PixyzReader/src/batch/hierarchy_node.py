import capnpy
from .geometry_parts import GeometryParts
from .logger import Logger
from .utils import Utils

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class HierarchyNode:
    def __init__(self, capnproto, part_occurrences, occurrence, parent_id, hierarchy_id, metadata_id, scale_factor = 1000):
        self.capnproto = capnproto

        self.parent_id = parent_id
        self.hierarchy_id = hierarchy_id
        self.metadata_id = metadata_id
        self.geometryParts = []
        
        try:
            if Utils().ForLoopSearch(part_occurrences, occurrence):
                self.geometryParts = GeometryParts(self.capnproto, occurrence, scale_factor).Get()
        except Exception as e:
            Logger().Error(f"=====> GeometryParts Error: {e}")

        self.childNodes = []
        for child in scene.getChildren(occurrence):
            child_hierarchy_id = core.getProperty(child, "hierarchy_id")
            self.childNodes.append(int(child_hierarchy_id))
  
    def Get(self):
        hierarchyNode = {}
        hierarchyNode["unique_id"] = int(self.hierarchy_id)
        hierarchyNode["parent_id"] = int(self.parent_id)
        if(self.metadata_id == None):
            self.metadata_id = 0
        hierarchyNode["metadata_id"] = int(self.metadata_id)
        hierarchyNode["geometry_parts"] = self.geometryParts
        hierarchyNode["child_nodes"] = self.childNodes
        return self.capnproto.CPHierarchyNode(**hierarchyNode)