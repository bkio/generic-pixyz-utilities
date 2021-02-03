import capnpy
import json
from .logger import Logger

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class MetadataNode:
    def __init__(self, capnproto, occurrence, metadata_id):
        self.capnproto = capnproto
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
        except:
            self.metadata_obj = None
            Logger().Warning("=====> No metadata component found")

    def Get(self):
        if self.metadata_obj != None:
            metadata_node = {}
            metadata_node["unique_id"] = int(self.metadata_id)
            metadata_str = json.dumps(self.metadata_obj)
            metadata_node["metadata"] = bytes(metadata_str, 'utf-8')
            return self.capnproto.CPMetadataNode(**metadata_node)
        else:
            return self.capnproto.CPMetadataNode()