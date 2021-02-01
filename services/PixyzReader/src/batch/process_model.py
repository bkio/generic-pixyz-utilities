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
from .protobuf_messages_pb2 import *

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class ProcessModel:
    def __init__(self, model_id, redis_client:RedisClient, number_of_thread = 20, decimate_target_strategy = "ratio", lod_levels = [100, 90, 80, 60, 20, 10], small_object_threshold = 50, scale_factor = 1000):
        # Parameters
        self.model_id = model_id
        self.redis_client = redis_client
        if number_of_thread <= 0:
            number_of_thread = 1
        self.number_of_thread = number_of_thread
        self.decimate_target_strategy = decimate_target_strategy
        self.lod_levels = lod_levels
        self.small_object_threshold = small_object_threshold
        self.scale_factor = scale_factor
        self.custom_informations = []

        self.workerItems = []
        self.root = scene.getRoot()

        self.part_occurrences = []
        self.prototype_parts = []
        self.decimate_values = []

    def Start(self):
        Logger().Warning("=====> Model processing has been started, please wait processing...")
        self.ApplyCustomInformations(self.root)
        
        self.part_occurrences = scene.getPartOccurrences(self.root)
        self.prototype_parts = self.GetPrototypeParts()

        if len(self.lod_levels) <= 0:
            self.lod_levels = [100]

        # for current_lod in range(len(self.lod_levels)):
        #     decimate_value = current_lod
            
        #     if current_lod > 0:
        #         if self.decimate_target_strategy == "ratio":
        #             decimate_value = math.ceil((self.lod_levels[current_lod]/self.lod_levels[current_lod-1]) * 100)
            
        #     self.decimate_values.append(decimate_value)
            # PixyzAlgorithms(verbose=True).DecimateTarget([], [self.decimate_target_strategy, decimate_value])
        
        # for current_lod in range(len(self.lod_levels)):
        #     if current_lod == 0:
        #         self.CreateWorkerItems(self.root, '18446744069414584320')
        #     else:
        #         self.CreateWorkerItemsOnlyGeometry()

        #     self.StartProcess(current_lod)

        self.CreateWorkerItems(self.root, '18446744069414584320')
        self.StartProcess()
        
        self.redis_client.Done()

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

    def StartProcess(self):
        # Logger().Warning(f"=====> LOD{lod_number} processing is started.")

        # 1) Init a Thread pool with the desired number of threads
        pool = ThreadPool(self.number_of_thread)

        for worker in self.workerItems:
            # 2) Add the task to the queue
            pool.AddTask(self.GetItemDetails, worker)

        # 3) Wait for completion
        pool.WaitCompletion()

        # Logger().Warning(f"=====> LOD{lod_number} processing is completed. Current Message Count : {self.redis_client.GetMessageCount()}")        
        
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
    
    def GetItemDetails(self, item):
        occurrence = item['occurrence']
        parent_id = item['parent_id']

        hierarchy_id = core.getProperty(occurrence, "hierarchy_id")

        NodeMessage = PNodeMessage()
        NodeMessage.ModelID = int(self.model_id)
        NodeMessage.Done = False

        metadata_id = str(random.getrandbits(64))
        try:
            metadataNode = MetadataNode(NodeMessage.MetadataNode, occurrence, metadata_id).Get()
            if metadataNode == None:
                metadata_id = None
        except Exception as e:
            Logger().Error(f"=====> MetadataNode Error {e}")

        try:
            hierarchyNode = HierarchyNode(NodeMessage.HierarchyNode, self.part_occurrences, occurrence, parent_id, hierarchy_id, metadata_id, self.scale_factor).Get()
        except Exception as e:
            Logger().Error(f"=====> HierarchyNode Error {e}")

        geometryNode, error_messages = [None, None]

        if Utils().BisectSearch(self.prototype_parts, occurrence):
            thread_lock = self.redis_client.GetLock()
            try:
                geometryNode, error_messages = GeometryNode(NodeMessage.GeometryNode, thread_lock, occurrence, self.decimate_target_strategy, self.lod_levels, self.small_object_threshold, self.scale_factor).Get()
            except Exception as e:
                Logger().Error(f"=====> GeometryNode Error {e}")

        NodeMessage.Errors.extend(error_messages)

        try:
            self.redis_client.Publish(NodeMessage, verbose=False)
        except Exception as e:
            Logger().Error(f"=====> Redis Publish Error {e}")