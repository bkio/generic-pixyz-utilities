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

        self.geometryParts = []
        if Utils().ForLoopSearch(part_occurrences, occurrence):
            self.geometryParts = GeometryParts(occurrence, scale_factor).Get()

        self.childNodes = []
        for child in scene.getChildren(occurrence):
            child_hierarchy_id = core.getProperty(child, "hierarchy_id")
            self.childNodes.append(child_hierarchy_id)
    
    def Get(self):
        return {
            'id': self.hierarchy_id, 
            'parentId': self.parent_id, 
            'metadataId': self.metadata_id, 
            'geometryParts': self.geometryParts, 
            'childNodes': self.childNodes
        }