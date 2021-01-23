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
        self.scale_factor = scale_factor
        
        if self.__IsPartOccurrence(occurrence) == True:
            for component in scene.listComponents(occurrence, True):
                geometry_part = {}

                # get transform informations
                matrix = scene.getGlobalMatrix(occurrence)
                part_matrix = scene.getPartsTransforms([component])[0]
                _Matrix4x4 = Matrix4x4(matrix, part_matrix, self.scale_factor)
                vectorList = geom.toTRS(matrix)
                
                prototype = scene.getPrototype(occurrence)
                if prototype == 0:
                    geometry_part['geometryId'] = core.getProperty(occurrence, "Id")
                else:
                    geometry_part['geometryId'] = prototype
                
                geometry_part['location'] = Vector3(vectorList[0].x/self.scale_factor, vectorList[0].y/self.scale_factor, vectorList[0].z/self.scale_factor).Get()
                # geometry_part['location'] = _Matrix4x4.GetTranslation()
                geometry_part['rotation'] = Vector3(vectorList[1].x, vectorList[1].y, vectorList[1].z).Get()
                # geometry_part['rotation'] = _Matrix4x4.GetEulerRotation()
                geometry_part['scale'] = Vector3(vectorList[2].x, vectorList[2].y, vectorList[2].z).Get()
                # geometry_part['scale'] = _Matrix4x4.GetScale()
                geometry_part['color'] = Color3(component).Get()
                
                self.geometry_parts.append(geometry_part)

        if len(self.geometry_parts) == 0:
            self.geometry_parts = None

    def __IsPartOccurrence(self, occurrence):
        partOccurrenceList = scene.getPartOccurrences(scene.getRoot())
        for item in partOccurrenceList:
            if item == occurrence:
                return True
        return False
    
    def Get(self):
        return self.geometry_parts
