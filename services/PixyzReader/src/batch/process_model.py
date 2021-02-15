import random
from .logger import Logger
from .redis_client import RedisClient
from .check_status_code import CheckStatusCode
from .utils import Utils
from .thread_pool import ThreadPool
from .metadata_node import MetadataNode
from .hierarchy_node import HierarchyNode
from .geometry_node import GeometryNode
from .pixyz_algorithms import PixyzAlgorithms
from .export_scene import ExportScene

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
        
        for current_lod_level in range(len(self.lod_decimations)):
            if current_lod_level == 0:
                self.UpdatePartInformation()
                self.CreateWorkerItems(self.root, '18446744069414584320')
            else:
                self.ApplyDecimateAlgorithms(current_lod_level)
                self.UpdatePartInformation()
                self.CreateWorkerItemsOnlyGeometry()

            if current_lod_level > 0:
                syncing = False
                while (syncing != True):
                    syncing = CheckStatusCode(check_url="http://127.0.0.1:8081/healthcheck").Run()

            self.StartProcess(current_lod_level)

            self.redis_client.Done()

            ending_process = False
            while (ending_process != True):
                ending_process = CheckStatusCode(check_url="http://127.0.0.1:8081/endprocess").Run()
    
    def StartExport(self):
        Logger().Warning("=====> Model processing has been started, please wait processing...")
        self.ApplyCustomInformations(self.root)

        if len(self.lod_decimations) <= 0:
            self.lod_decimations = [-1]
        
        for current_lod_level in range(len(self.lod_decimations)):
            file_name = "C:/tmp/AV_EXP_lod"+ str(current_lod_level)
            if current_lod_level == 0:
                ExportScene((file_name + ".fbx")).Run()
                ExportScene((file_name + ".gltf")).Run()
            else:
                self.ApplyDecimateAlgorithms(current_lod_level)
                ExportScene((file_name + ".fbx")).Run()
                ExportScene((file_name + ".gltf")).Run()

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
                Logger().Error(f"Wrong LOD information for LOD{current_lod_level}, please to be sure it is a list and contains 3 or 4 elements for decimateToQuality or HiddenRemoval algorithms.")
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

        error_message_str = None
        if len(error_messages) > 0:
            error_message_str = str(error_messages)

        if metadataNode == None and hierarchyNode == None and geometryNode == None and error_message_str == None:
            pass
        else:
            try:
                data = {'model_id': self.model_id, 'hierarchyNode': hierarchyNode, 'metadataNode': metadataNode, 'geometryNode': geometryNode, 'errors': error_message_str, 'done': False, 'messageCount' : 0 }
                self.redis_client.Publish(data, verbose=False)
            except Exception as e:
                Logger().Error(f"=====> Redis Publish Error {e}")