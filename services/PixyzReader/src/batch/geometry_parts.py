from .protobuf_messages_pb2 import *
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
    def __init__(self, occurrence, scale_factor = 1000):
        self.geometry_parts = []
        
        for component in scene.listComponents(occurrence, True):
            # geometry_part = {}
            GeometryPartData = PGeometryPart()

            # get transform informations
            matrix = scene.getGlobalMatrix(occurrence)
            part_matrix = scene.getPartsTransforms([component])[0]
            # _Matrix4x4 = Matrix4x4(matrix, part_matrix, scale_factor)
            vectorList = geom.toTRS(matrix)
            
            prototype = scene.getPrototype(occurrence)
            if prototype == 0:
                GeometryPartData.GeometryID = int(core.getProperty(occurrence, "Id"))
            else:
                GeometryPartData.GeometryID = int(prototype)
            
            location = Vector3(vectorList[0].x/scale_factor, vectorList[0].y/scale_factor, vectorList[0].z/scale_factor).Get()
            GeometryPartData.Location.X = location.X
            GeometryPartData.Location.Y = location.Y
            GeometryPartData.Location.Z = location.Z
            # geometry_part['location'] = _Matrix4x4.GetTranslation()
            rotation = Vector3(vectorList[1].x, vectorList[1].y, vectorList[1].z).Get()
            GeometryPartData.Rotation.X = rotation.X
            GeometryPartData.Rotation.Y = rotation.Y
            GeometryPartData.Rotation.Z = rotation.Z
            # geometry_part['rotation'] = _Matrix4x4.GetEulerRotation()
            scale = Vector3(vectorList[2].x, vectorList[2].y, vectorList[2].z).Get()
            GeometryPartData.Scale.X = scale.X
            GeometryPartData.Scale.Y = scale.Y
            GeometryPartData.Scale.Z = scale.Z
            # geometry_part['scale'] = _Matrix4x4.GetScale()
            color = Color3(component).Get()
            if color != None:
                GeometryPartData.Color.R = color.R
                GeometryPartData.Color.G = color.G
                GeometryPartData.Color.B = color.B
            
            self.geometry_parts.append(GeometryPartData)
    
    def Get(self):
        return self.geometry_parts
