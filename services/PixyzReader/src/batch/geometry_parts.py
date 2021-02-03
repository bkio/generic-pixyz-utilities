import capnpy
from .vector3 import Vector3
from .color3 import Color3

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
    from pxz import geom
except: pass

class GeometryParts:
    def __init__(self, capnproto, occurrence, scale_factor = 1000):
        self.capnproto = capnproto
        self.geometryParts = []
        
        for component in scene.listComponents(occurrence, True):
            GeometryPartData = {}

            # get transform informations
            matrix = scene.getGlobalMatrix(occurrence)
            vectorList = geom.toTRS(matrix)
            
            prototype = scene.getPrototype(occurrence)
            if prototype == 0:
                GeometryPartData["geometry_id"] = int(core.getProperty(occurrence, "Id"))
            else:
                GeometryPartData["geometry_id"] = int(prototype)
            
            location = Vector3(vectorList[0].x/scale_factor, vectorList[0].y/scale_factor, vectorList[0].z/scale_factor).Get()
            rotation = Vector3(vectorList[1].x, vectorList[1].y, vectorList[1].z).Get()
            scale = Vector3(vectorList[2].x, vectorList[2].y, vectorList[2].z).Get()
            color = Color3(component).Get()

            GeometryPartData["location"] = self.capnproto.CPVector3D(**location)
            GeometryPartData["rotation"] = self.capnproto.CPVector3D(**rotation)
            GeometryPartData["scale"] = self.capnproto.CPVector3D(**scale)
            if(color != None):
                GeometryPartData["color"] = self.capnproto.CPColor(**color)
            else:
                GeometryPartData["color"] = self.capnproto.CPColor()

            self.geometryParts.append(self.capnproto.CPGeometryPart(**GeometryPartData))

    def Get(self):
        return self.geometryParts
