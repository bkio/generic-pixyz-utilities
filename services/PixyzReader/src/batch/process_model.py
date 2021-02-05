import random
import math
from .logger import Logger
from .redis_client import RedisClient
from .utils import Utils
from .thread_pool import ThreadPool
from .metadata_node import MetadataNode
from .hierarchy_node import HierarchyNode
from .geometry_node import GeometryNode
from .pixyz_algorithms import PixyzAlgorithms
from .PB.protob_messages_pb2 import PNodeMessage

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class ProcessModel:
    def __init__(self, model_id, redis_client:RedisClient, number_of_thread = 20, decimate_target_strategy = "ratio", lod_decimations = [100, 90, 80, 60, 20, 10], small_object_threshold = 50, scale_factor = 1000):
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
                self.CreateWorkerItems(self.root, '18446744069414584320')
            else:
                self.ApplyDecimateAlgorithms(current_lod)
                self.CreateWorkerItemsOnlyGeometry()

            self.StartProcess(current_lod)
        
        self.redis_client.Done()

    def ApplyDecimateAlgorithms(self, current_lod_level):
        lod_decimation_value = self.lod_decimations[current_lod_level]
        if(type(lod_decimation_value) is list):
            if(len(lod_decimation_value) == 3):
                Logger().Warning(f"=====> Applying DecimateToQuality algorithm to LOD{current_lod_level}...")
                PixyzAlgorithms(verbose=True).Decimate([], lod_decimation_value[0], lod_decimation_value[1], lod_decimation_value[2])
            else:
                Logger().Error(f"Wrong LOD information for LOD{current_lod_level}, please to be sure it is a list and contains 3 elements for surfaic, lineic and normal parameter ")
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
        Logger().Warning(f"=====> LOD{current_lod_level} processing is started.")

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

        NodeMessage = PNodeMessage()

        if current_lod_level == 0:
            metadata_id = str(random.getrandbits(64))
            try:
                MetadataNode(NodeMessage.MetadataNode, occurrence, metadata_id)
            except Exception as e:
                Logger().Error(f"=====> MetadataNode Error {e}")

            try:
                HierarchyNode(NodeMessage.HierarchyNode, self.part_occurrences, occurrence, parent_id, hierarchy_id, metadata_id, self.scale_factor)
            except Exception as e:
                Logger().Error(f"=====> HierarchyNode Error {e}")

        error_messages = []
        has_geometry_node = False

        if Utils().ForLoopSearch(self.prototype_parts, occurrence):
            thread_lock = self.redis_client.GetLock()
            current_small_object_threshold = self.small_object_threshold[current_lod_level]
            try:
                has_geometry_node, error_messages = GeometryNode(NodeMessage.GeometryNode, thread_lock, occurrence, current_lod_level, current_small_object_threshold, self.scale_factor).Get()
            except Exception as e:
                Logger().Error(f"=====> GeometryNode Error {e}")
        
        if current_lod_level > 0 and has_geometry_node == False and len(error_messages) == 0:
            pass
        else:
            try:
                NodeMessage.ModelID = int(self.model_id)
                NodeMessage.Done = False
                NodeMessage.Errors = str(error_messages)
                self.redis_client.Publish(NodeMessage, verbose=False)
            except Exception as e:
                Logger().Error(f"=====> Redis Publish Error {e}")