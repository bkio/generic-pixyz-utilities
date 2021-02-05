from .PB.protob_messages_pb2 import PHierarchyNode
from .geometry_parts import GeometryParts
from .logger import Logger
from .utils import Utils

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class HierarchyNode:
    def __init__(self, proto: PHierarchyNode, part_occurrences, occurrence, parent_id, hierarchy_id, metadata_id, scale_factor = 1000):
        self.proto = proto
        self.parent_id = parent_id
        self.hierarchy_id = hierarchy_id
        self.metadata_id = metadata_id
        
        if Utils().ForLoopSearch(part_occurrences, occurrence):
            self.geometryParts = GeometryParts(self.proto, occurrence, scale_factor)

        self.childNodes = []
        for child in scene.getChildren(occurrence):
            child_hierarchy_id = core.getProperty(child, "hierarchy_id")
            self.childNodes.append(int(child_hierarchy_id))

        self.proto.UniqueID = int(self.hierarchy_id)
        self.proto.ParentID = int(self.parent_id)
        self.proto.MetadataID = int(self.metadata_id)
        self.proto.ChildNodes.extend(self.childNodes)