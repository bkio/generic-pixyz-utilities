import json
from .logger import Logger
import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class MetadataNode:
    def __init__(self, occurrence, metadata_id):
        self.metadata_node = None
        self.metadata_obj = {}
        self.metadata_id = metadata_id
        # put name info as metadata before getting actual metadata information
        self.metadata_obj['__hierarchy_name__'] = core.getProperty(occurrence, "Name")

        try:
            metadataComponent = scene.getComponent(occurrence, scene.ComponentType.Metadata)
            metadataDefinitionList = scene.getMetadatasDefinitions([metadataComponent])
            for metadataDefinition in metadataDefinitionList:
                for item in metadataDefinition:
                    self.metadata_obj[item.name] = item.value

            self.metadata_node = {}
            self.metadata_node['id'] = self.metadata_id
            self.metadata_node['metadata'] = json.dumps(self.metadata_obj)
        except:
            Logger().Warning("=====> No metadata component found")

    def Get(self):
        return self.metadata_node