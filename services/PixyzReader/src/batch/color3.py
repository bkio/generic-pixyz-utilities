from .protobuf_messages_pb2 import *

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import material
except: pass

class Color3:
    """Getting Color3(r,g,b) information from Pixyz with materialDefinition"""
    def __init__(self, component):

        self.material_color = None
        try:
            for partMaterial in scene.listPartSubMaterials(component):
                materialDefinition = material.getMaterialDefinition(partMaterial)
                self.material_color = self.__GetColorInfo(materialDefinition.diffuse[0])
                # material_color['normal'] = materialDefinition.normal[1]
                # material_color['metallic'] = materialDefinition.metallic[1]
                # material_color['roughness'] = materialDefinition.roughness[1]
                # material_color['ao'] = materialDefinition.ao[1]
                # material_color['opacity'] = materialDefinition.opacity[1]
        except:
            self.material_color = PColorRGB()

    def Get(self):
        return self.material_color

    def __GetColorInfo(self, color):
        ColorData = PColorRGB()
        ColorData.R = int(round(color.r*255))
        ColorData.G = int(round(color.g*255))
        ColorData.B = int(round(color.b*255))
        return ColorData