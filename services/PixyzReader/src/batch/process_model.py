import random
from .logger import Logger
from .thread_pool import ThreadPool
from .metadata_node import MetadataNode
from .hierarchy_node import HierarchyNode
from .geometry_node import GeometryNode

import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class ProcessModel:
    def __init__(self, model_id, redis_client, number_of_thread = 20, decimate_target_strategy = "ratio", lod_levels = [100, 90, 80, 60, 20, 10], small_object_threshold = 50, scale_factor = 1000):
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

    def Start(self):
        Logger().Warning("=====> Model processing has been started, please wait processing...")
        self.ApplyCustomInformations(self.root)
        self.CreateThreadPool()

    def AddCustomInformation(self, key, value):
        customInfo = {}
        customInfo["key"] = key
        customInfo["value"] = value
        self.custom_informations.append(customInfo)

    def ClearCustomInformation(self):
        self.custom_informations = []

    def ApplyCustomInformations(self, occurrence):
        for custom_info in self.custom_informations:
            core.addCustomProperty(occurrence, custom_info["key"], custom_info["value"])

        for child in scene.getChildren(occurrence):
            self.ApplyCustomInformations(child)

    def CreateThreadPool(self):
        self.CreateWorkerItems(self.root, '18446744069414584320')

        # 1) Init a Thread pool with the desired number of threads
        pool = ThreadPool(self.number_of_thread)

        for worker in self.workerItems:
            # 2) Add the task to the queue
            pool.AddTask(self.GetItemDetails, worker)

        # 3) Wait for completion
        pool.WaitCompletion()

        self.redis_client.Done()

    def CreateWorkerItems(self, occurrence, parent_id):
        worker = {}
        worker['occurrence'] = occurrence
        worker['model_id'] = self.model_id
        worker['parent_id'] = parent_id
        self.workerItems.append(worker)
        
        hierarchy_id = core.getProperty(occurrence, "hierarchy_id")

        # get child information
        for child in scene.getChildren(occurrence):
            self.CreateWorkerItems(child, hierarchy_id)

    def GetItemDetails(self, item):
        occurrence = item['occurrence']
        model_id = item['model_id']
        parent_id = item['parent_id']

        metadata_id = str(random.getrandbits(64))
        hierarchy_id = core.getProperty(occurrence, "hierarchy_id")
        metadataNode = MetadataNode(occurrence, metadata_id).Get()
        if metadataNode == None:
            metadata_id = None

        hierarchyNode = HierarchyNode(occurrence, parent_id, hierarchy_id, metadata_id, self.scale_factor).Get()

        thread_lock = self.redis_client.GetLock()
        geometryNodeArray, error_messages = GeometryNode(thread_lock, occurrence, self.decimate_target_strategy, self.lod_levels, self.small_object_threshold, self.scale_factor).Get()

        for geometryNode in geometryNodeArray:
            lodNumber = geometryNode["lodNumber"]
            geometryNodeModified = {}
            geometryNodeModified["id"] = geometryNode["id"]
            geometryNodeModified["lodNumber"] = lodNumber
            geometryNodeModified["lods"] = [ geometryNode["lod"] ]

            if int(lodNumber) == 0:
                data = {'model_id': model_id, 'hierarchyNode': hierarchyNode, 'metadataNode': metadataNode, 'geometryNode': geometryNodeModified, 'errors': error_messages, 'done': False }
                self.redis_client.Publish(data)
            else:
                data = {'model_id': model_id, 'hierarchyNode': None, 'metadataNode': None, 'geometryNode': geometryNodeModified, 'errors': error_messages, 'done': False }
                self.redis_client.Publish(data)