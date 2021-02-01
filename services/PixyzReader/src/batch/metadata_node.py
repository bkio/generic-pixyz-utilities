import json
from .logger import Logger
from .protobuf_messages_pb2 import *

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class MetadataNode:
    def __init__(self, proto: PMetadataNode, occurrence, metadata_id):
        self.proto = proto
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
        self.proto.UniqueID = int(self.metadata_id)
        self.proto.Metadata = json.dumps(self.metadata_obj)
        return self.metadata_obj