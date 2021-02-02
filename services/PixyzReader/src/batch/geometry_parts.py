from .protobuf_messages_pb2 import PHierarchyNode
from .matrix4x4 import Matrix4x4
from .vector3 import Vector3
from .color3 import Color3

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
    from pxz import geom
except: pass

class GeometryParts:
    def __init__(self, proto: PHierarchyNode, occurrence, scale_factor = 1000):
        self.proto = proto
        
        for component in scene.listComponents(occurrence, True):
            # geometry_part = {}
            GeometryPartData = self.proto.GeometryParts.add()

            # get transform informations
            matrix = scene.getGlobalMatrix(occurrence)
            vectorList = geom.toTRS(matrix)
            
            prototype = scene.getPrototype(occurrence)
            if prototype == 0:
                GeometryPartData.GeometryID = int(core.getProperty(occurrence, "Id"))
            else:
                GeometryPartData.GeometryID = int(prototype)
            
            Vector3(GeometryPartData, vectorList[0].x/scale_factor, vectorList[0].y/scale_factor, vectorList[0].z/scale_factor).SetLocation()
            Vector3(GeometryPartData, vectorList[1].x, vectorList[1].y, vectorList[1].z).SetRotation()
            Vector3(GeometryPartData, vectorList[2].x, vectorList[2].y, vectorList[2].z).SetScale()
            Color3(GeometryPartData, component)
