from .protobuf_messages_pb2 import *
from .geometry_parts import GeometryParts
from .logger import Logger
from .utils import Utils

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class HierarchyNode:
    def __init__(self, part_occurrences, occurrence, parent_id, hierarchy_id, metadata_id, scale_factor = 1000):
        self.parent_id = parent_id
        self.hierarchy_id = hierarchy_id
        self.metadata_id = metadata_id
        
        if Utils().BisectSearch(part_occurrences, occurrence):
            self.geometryParts = GeometryParts(occurrence, scale_factor).Get()
        else:
            self.geometryParts = []

        self.childNodes = []
        for child in scene.getChildren(occurrence):
            child_hierarchy_id = core.getProperty(child, "hierarchy_id")
            self.childNodes.append(int(child_hierarchy_id))
    
    def Get(self):
        HierarchyNodeData = PHierarchyNode()
        HierarchyNodeData.UniqueID = int(self.hierarchy_id)
        HierarchyNodeData.ParentID = int(self.parent_id)
        HierarchyNodeData.MetadataID = int(self.metadata_id)
        HierarchyNodeData.GeometryParts.extend(self.geometryParts)
        HierarchyNodeData.ChildNodes.extend(self.childNodes)
        return HierarchyNodeData