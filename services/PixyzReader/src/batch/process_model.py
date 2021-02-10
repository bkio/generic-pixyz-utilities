import random
import flatbuffers
from .FB.FBNodeMessage import *
from .FB.FBVertexNormalTangent import *
from .FB.FBGeometryNode import *
from .FB.FBLOD import *
from .FB.FBMetadataNode import *
from .FB.FBHierarchyNode import *
from .FB.FBGeometryPart import *
from .logger import Logger
from .redis_client import RedisClient
from .utils import Utils
from .thread_pool import ThreadPool
from .metadata_node import MetadataNode
from .hierarchy_node import HierarchyNode
from .geometry_node import GeometryNode
from .pixyz_algorithms import PixyzAlgorithms

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class ProcessModel:
    def __init__(self, model_id, redis_client:RedisClient, number_of_thread = 20, decimate_target_strategy = "ratio", lod_decimations = [-1, 90, 88, 75, 35, 50], small_object_threshold = [0, 0, 0, 0, 20, 40], scale_factor = 1000):
        # Parameters
        self.model_id = model_id
        self.redis_client = redis_client
        if number_of_thread <= 0:
            number_of_thread = 1
        self.number_of_thread = number_of_thread
        self.decimate_target_strategy = decimate_target_strategy
        self.lod_decimations = lod_decimations
        self.small_object_threshold = small_object_threshold
        self.scale_factor = scale_factor
        self.custom_informations = []

        self.workerItems = []
        self.root = scene.getRoot()

        self.part_occurrences = []
        self.prototype_parts = []

    def Start(self):
        Logger().Warning("=====> Model processing has been started, please wait processing...")
        self.ApplyCustomInformations(self.root)

        if len(self.lod_decimations) <= 0:
            self.lod_decimations = [-1]
        
        for current_lod in range(len(self.lod_decimations)):
            self.part_occurrences = scene.getPartOccurrences(self.root)
            self.prototype_parts = self.GetPrototypeParts()

            if current_lod == 0:
                self.UpdatePartInformation()
                self.CreateWorkerItems(self.root, '18446744069414584320')
            else:
                self.ApplyDecimateAlgorithms(current_lod)
                self.UpdatePartInformation()
                self.CreateWorkerItemsOnlyGeometry()

            self.StartProcess(current_lod)
        
        Logger().Warning("=====> Process is done. Please wait for done message.")
        self.redis_client.Done()

    def UpdatePartInformation(self):
        self.part_occurrences = scene.getPartOccurrences(self.root)
        self.prototype_parts = self.GetPrototypeParts()

    def ApplyDecimateAlgorithms(self, current_lod_level):
        lod_decimation_value = self.lod_decimations[current_lod_level]
        if type(lod_decimation_value) is list:
            if len(lod_decimation_value) == 3:
                Logger().Warning(f"=====> Applying DecimateToQuality algorithm to LOD{current_lod_level}...")
                PixyzAlgorithms(verbose=True).Decimate([], lod_decimation_value[0], lod_decimation_value[1], lod_decimation_value[2])
            elif len(lod_decimation_value) == 4:
                Logger().Warning(f"=====> Applying HiddenRemoval algorithm to LOD{current_lod_level}...")
                PixyzAlgorithms(verbose=False).IdentifyPatches([], True, True, lod_decimation_value[0])
                PixyzAlgorithms(verbose=False).HiddenRemoval([], 1, lod_decimation_value[1], lod_decimation_value[2], lod_decimation_value[3])
                PixyzAlgorithms(verbose=False).DeletePatches()
                PixyzAlgorithms(verbose=True).DeleteFreeVertices()
            else:
                Logger().Error(f"Wrong LOD information for LOD{current_lod_level}, please to be sure it is a list and contains 3 elements for decimateToQuality or 4 elements for hiddenRemoval algorithms.")
        else:
            Logger().Warning(f"=====> Applying DecimateTarget algorithm with {self.decimate_target_strategy}:{lod_decimation_value} parameters to LOD{current_lod_level}...")
            PixyzAlgorithms(verbose=True).DecimateTarget([], [self.decimate_target_strategy, lod_decimation_value])

    def GetPrototypeParts(self):
        prototypes = []
        for occurrence in self.part_occurrences:
            prototype = scene.getPrototype(occurrence)
            if prototype == 0:
                prototypes.append(occurrence)
        
        return prototypes

    def AddCustomInformation(self, key, value, random):
        customInfo = {}
        customInfo["key"] = key
        customInfo["value"] = value
        customInfo["random"] = random
        self.custom_informations.append(customInfo)

    def ClearCustomInformation(self):
        self.custom_informations = []

    def ApplyCustomInformations(self, occurrence):
        for custom_info in self.custom_informations:
            custom_value = custom_info["value"]
            if custom_info["random"] == True:
                custom_value = str(random.getrandbits(64))
            core.addCustomProperty(occurrence, custom_info["key"], custom_value)

        for child in scene.getChildren(occurrence):
            self.ApplyCustomInformations(child)

    def StartProcess(self, current_lod_level):
        Logger().Warning(f"=====> LOD{current_lod_level} processing is started. LOD{current_lod_level} Worker Count: {len(self.workerItems)}")

        # 1) Init a Thread pool with the desired number of threads
        pool = ThreadPool(self.number_of_thread)

        for worker in self.workerItems:
            # 2) Add the task to the queue
            pool.AddTask(self.GetItemDetails, worker, current_lod_level)

        # 3) Wait for completion
        pool.WaitCompletion()

        Logger().Warning(f"=====> LOD{current_lod_level} processing is completed. Current Message Count : {self.redis_client.GetMessageCount()}")        
        
    def CreateWorkerItems(self, occurrence, parent_id):
        worker = {}
        worker['occurrence'] = occurrence
        worker['parent_id'] = parent_id
        self.workerItems.append(worker)
        
        hierarchy_id = core.getProperty(occurrence, "hierarchy_id")

        # get child information
        for child in scene.getChildren(occurrence):
            self.CreateWorkerItems(child, hierarchy_id)

    def CreateWorkerItemsOnlyGeometry(self):
        self.workerItems = []
        for prototype in self.prototype_parts:
            worker = {}
            worker['occurrence'] = prototype
            worker['parent_id'] = None
            self.workerItems.append(worker)
    
    def GetItemDetails(self, item, current_lod_level):
        occurrence = item['occurrence']
        parent_id = item['parent_id']
        hierarchy_id = core.getProperty(occurrence, "hierarchy_id")

        metadataNode = None
        hierarchyNode = None

        if current_lod_level == 0:
            metadata_id = str(random.getrandbits(64))
            try:
                metadataNode = MetadataNode(occurrence, metadata_id).Get()
                if metadataNode == None:
                    metadata_id = None
            except Exception as e:
                Logger().Error(f"=====> MetadataNode Error {e}")

            try:
                hierarchyNode = HierarchyNode(self.part_occurrences, occurrence, parent_id, hierarchy_id, metadata_id, self.scale_factor).Get()
            except Exception as e:
                Logger().Error(f"=====> HierarchyNode Error {e}")

        geometryNode = None
        error_messages = []

        if Utils().ForLoopSearch(self.prototype_parts, occurrence):
            current_small_object_threshold = self.small_object_threshold[current_lod_level]
            try:
                geometryNode, error_messages = GeometryNode(occurrence, current_lod_level, current_small_object_threshold, self.scale_factor).Get()
            except Exception as e:
                Logger().Error(f"=====> GeometryNode Error {e}")

        if metadataNode == None and hierarchyNode == None and geometryNode == None and len(error_messages) == 0:
            pass
        else:
            try:
                fbbuilder = flatbuffers.Builder(2048)
                metadataNodeFB = None
                if metadataNode != None:
                    metadata_string = fbbuilder.CreateString(metadataNode['metadata'])    
                    FBMetadataNodeStart(fbbuilder)
                    FBMetadataNodeAddUniqueID(fbbuilder, int(metadataNode['id']))
                    FBMetadataNodeAddMetadata(fbbuilder, metadata_string)
                    metadataNodeFB = FBMetadataNodeEnd(fbbuilder)

                hierarchyNodeFB = None
                if hierarchyNode != None:
                    geometryPartVector = None
                    geometryParts = hierarchyNode['geometryParts']
                    geometryPartsLength = len(geometryParts)
                    if geometryPartsLength > 0:
                        FBHierarchyNodeStartGeometryPartsVector(fbbuilder, geometryPartsLength)
                        for i in range(geometryPartsLength):
                            part = geometryParts[i]
                            geometryId = part['geometryId']
                            location = part['location']
                            rotation = part['rotation']
                            scale = part['scale']
                            color = part['color']
                            if color == None:
                                color = { 'r': 0, 'g': 0, 'b': 0, 'no_color': True }
                            else:
                                color['no_color'] = False
                            CreateFBGeometryPart(fbbuilder, int(geometryId), float(location['x']), float(location['y']), float(location['z']), float(rotation['x']), float(rotation['y']), float(rotation['z']), float(scale['x']), float(scale['y']), float(scale['z']), int(color['r']), int(color['g']), int(color['b']), color['no_color'])
                        geometryPartVector = fbbuilder.EndVector(geometryPartsLength)

                    childNodeVector = None
                    childNodes = hierarchyNode['childNodes']
                    childNodesLength = len(childNodes)
                    if childNodesLength > 0:
                        FBHierarchyNodeStartChildNodesVector(fbbuilder, childNodesLength)
                        for child in childNodes:
                            fbbuilder.PrependUint64(int(child))
                        
                        childNodeVector = fbbuilder.EndVector(childNodesLength)
                    FBHierarchyNodeStart(fbbuilder)
                    FBHierarchyNodeAddUniqueID(fbbuilder, int(hierarchyNode['id']))
                    FBHierarchyNodeAddParentID(fbbuilder, int(hierarchyNode['parentId']))
                    FBHierarchyNodeAddMetadataID(fbbuilder, int(hierarchyNode['metadataId']))
                    if geometryPartVector != None:
                        FBHierarchyNodeAddGeometryParts(fbbuilder, geometryPartVector)
                    if childNodeVector != None:
                        FBHierarchyNodeAddChildNodes(fbbuilder, childNodeVector)
                    hierarchyNodeFB = FBHierarchyNodeEnd(fbbuilder)
                
                geometryNodeFB = None
                if geometryNode != None:
                    lod = geometryNode['lod']

                    vertexNormalTangentListVector = None
                    vertexNormalTangentList = lod['vertexNormalTangentList']
                    vertexNormalTangentListLength = len(vertexNormalTangentList)
                    if vertexNormalTangentListLength > 0:
                        FBLODStartVertexNormalTangentListVector(fbbuilder, vertexNormalTangentListLength)
                        for item in vertexNormalTangentList:
                            vertex = item['vertex']
                            normal = item['normal']
                            tangent = item['tangent']
                            CreateFBVertexNormalTangent(fbbuilder, float(vertex['x']), float(vertex['y']), float(vertex['z']), float(normal['x']), float(normal['y']), float(normal['z']), float(tangent['x']), float(tangent['y']), float(tangent['z']))
                        vertexNormalTangentListVector = fbbuilder.EndVector(vertexNormalTangentListLength)

                    indexesVector = None
                    indexes = lod['indexes']
                    indexesLength = len(indexes)
                    if indexesLength > 0:
                        FBLODStartIndexesVector(fbbuilder, indexesLength)
                        for index in indexes:
                            fbbuilder.PrependUint32(index)
                        indexesVector = fbbuilder.EndVector(indexesLength)

                    FBLODStart(fbbuilder)
                    if vertexNormalTangentListVector != None:
                        FBLODAddVertexNormalTangentList(fbbuilder, vertexNormalTangentListVector)
                    if indexesVector != None:
                        FBLODAddIndexes(fbbuilder, indexesVector)
                    lodFB = FBLODEnd(fbbuilder)

                    FBGeometryNodeStart(fbbuilder)
                    FBGeometryNodeAddUniqueID(fbbuilder, int(geometryNode['id']))
                    FBGeometryNodeAddLodNumber(fbbuilder, int(geometryNode['lodNumber']))
                    FBGeometryNodeAddLOD(fbbuilder, lodFB)
                    geometryNodeFB = FBGeometryNodeEnd(fbbuilder)
                
                errors_string = fbbuilder.CreateString(str(error_messages))
                FBNodeMessageStart(fbbuilder)
                FBNodeMessageAddModelID(fbbuilder, int(self.model_id))
                FBNodeMessageAddDone(fbbuilder, False)
                FBNodeMessageAddMessageCount(fbbuilder, 0)
                FBNodeMessageAddErrors(fbbuilder, errors_string)
                if metadataNodeFB != None:
                    FBNodeMessageAddMetadataNode(fbbuilder, metadataNodeFB)
                if hierarchyNodeFB != None:
                    FBNodeMessageAddHierarchyNode(fbbuilder, hierarchyNodeFB)
                if geometryNodeFB != None:
                    FBNodeMessageAddGeometryNode(fbbuilder, geometryNodeFB)
                data = FBNodeMessageEnd(fbbuilder)
                fbbuilder.Finish(data)
                data_buffer = fbbuilder.Output()
                self.redis_client.Publish(data_buffer, done=False, errors=error_messages, verbose=False)
            except Exception as e:
                Logger().Error(f"=====> Redis Publish Error {e}")