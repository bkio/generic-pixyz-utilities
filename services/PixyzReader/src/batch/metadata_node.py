import json
from .logger import Logger
from .protobuf_messages_pb2 import *

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class MetadataNode:
    def __init__(self, occurrence, metadata_id):
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
        if self.metadata_obj == None:
            return None
        else:
            metadata_message = PMetadataNode()
            metadata_message.UniqueID = int(self.metadata_id)
            metadata_message.Metadata = json.dumps(self.metadata_obj)
            return metadata_message