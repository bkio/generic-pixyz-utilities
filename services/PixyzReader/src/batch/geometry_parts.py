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
        self.geometry_part = {}

        # get transform information
        matrix = scene.getGlobalMatrix(occurrence)
        vectorList = geom.toTRS(matrix)
        
        prototype = scene.getPrototype(occurrence)
        if prototype == 0:
            self.geometry_part['geometryId'] = core.getProperty(occurrence, "Id")
        else:
            self.geometry_part['geometryId'] = prototype
        
        self.geometry_part['location'] = Vector3(vectorList[0].x/scale_factor, vectorList[0].y/scale_factor, vectorList[0].z/scale_factor).Get()
        self.geometry_part['rotation'] = Vector3(vectorList[1].x, vectorList[1].y, vectorList[1].z).Get()
        self.geometry_part['scale'] = Vector3(vectorList[2].x, vectorList[2].y, vectorList[2].z).Get()
        self.geometry_part['color'] = Color3(occurrence).Get()
    
    def Get(self):
        return self.geometry_part
