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
                self.material_color = self.__GetColorJson(materialDefinition.diffuse[0])
                # material_color['normal'] = materialDefinition.normal[1]
                # material_color['metallic'] = materialDefinition.metallic[1]
                # material_color['roughness'] = materialDefinition.roughness[1]
                # material_color['ao'] = materialDefinition.ao[1]
                # material_color['opacity'] = materialDefinition.opacity[1]
        except:
            pass

    def Get(self):
        return self.material_color

    def __GetColorJson(self, color):
        color_json = {}
        color_json['r'] = int(round(color.r*255))
        color_json['g'] = int(round(color.g*255))
        color_json['b'] = int(round(color.b*255))
        return color_json