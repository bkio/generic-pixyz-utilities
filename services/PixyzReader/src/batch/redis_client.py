import redis
import base64
import zlib
import time
import capnpy
# import json
import sys
from threading import Lock
from .logger import Logger

class RedisClient:
    """ 
    Redis Client for connecting redis server and publish data to specified channel

    - Parameters:\n
        - model_id : model_id for the message that you want to send\n
        - channel : channel name for publishing the messages\n
        - host : Redis host name for connecting the server\n

    - Returns:\n
        - void\n
    """
    def __init__(self, model_id = "", channel = "models", host = "redis", port = 6379, password = None):
        #Parameters
        self.model_id = model_id
        self.channel = channel
        self.host = host
        self.password = password
        self.port = port
        self.logger = Logger()
        self.thread_lock = Lock()
        self.redis_instance = self.__GetRedisInstance()

        #Message Count
        self.message_count = 0

        self.capnproto = capnpy.load_schema(None, None, '../../Protobufs/capnproto_messages.capnp')

    def GetCapnProto(self):
        return self.capnproto
        
    def GetLock(self):
        return self.thread_lock    

    def GetMessageCount(self):
        return self.message_count

    def DeflateEncodeBase64(self, message):
        # compressed_message = zlib.compress(bytes(message, 'utf-8'))[2:-4]
        compressed_message = zlib.compress(message)[2:-4]
        return base64.b64encode(compressed_message)

    def Publish(self, data, verbose = True):
        """ 
        Publish json data to specified channel

        - Parameters:\n
            - data : Data to be sent as a message\n
            - verbose : If True, it will write a message information\n

        - Returns:\n
            - void\n
        """
        self.message_count = self.message_count + 1

        # capnp_data = self.capnproto.CPNodeMessage(model_id=data['modelID'], errors=data['errors'], hierarchyNode=data['hierarchyNode'], metadataNode=data['metadataNode'], geometryNode=data['geometryNode'], done=data['done'], messageCount=data['messageCount'])
        capnp_data = self.capnproto.CPNodeMessage(**data)
        message = capnp_data.dumps()
        
        base64_message = self.DeflateEncodeBase64(message)

        message_size = sys.getsizeof(base64_message)
        if verbose:
            self.logger.PrintMessageInfo(data, message_size, self.message_count)

        retryCount = 0
        while retryCount < 10 :
            try:
                self.redis_instance.publish(self.channel, base64_message)
                retryCount = 10
            except Exception as e:
                self.logger.Error(f"=////=> Redis publish retry count: {retryCount} - error: {e} -  message to be published: {message}")
                retryCount = retryCount + 1
                time.sleep(1)

    def SetChannel(self, channel):
        """ 
        You can set channel name value that uses in the methods\n

        - Parameters:\n
            - channel : Channel name to publish messages\n

        - Returns:\n
            - void\n
        """
        self.channel = channel

    def Done(self):
        """ 
        Publish specific done message for listeners\n

        - Returns:\n
            - void\n
        """
        # data = {'model_id': self.model_id, 'hierarchyNode': None, 'metadataNode': None, 'geometryNode': None, 'errors': None, 'done': True, 'messageCount' : self.message_count }
        # self.Publish(data)
        node_message = {}
        node_message['model_id'] = int(self.model_id)
        node_message['errors'] = []
        node_message['hierarchy_node'] = None
        node_message['metadata_node'] = None
        node_message['geometry_node'] = None
        node_message['done'] = True
        node_message['message_count'] = self.message_count
        self.Publish(node_message)

    def Error(self, error_messages = []):
        """ 
        Publish specific error messages for listeners\n

        - Parameters:\n
            - error_messages : Array that contains error messages\n

        - Returns:\n
            - void\n
        """
        # data = {'model_id': self.model_id, 'hierarchyNode': None, 'metadataNode': None, 'geometryNode': None, 'errors': error_messages, 'done': True, 'messageCount' : self.message_count }
        # self.Publish(data)
        node_message = {}
        node_message['model_id'] = int(self.model_id)
        node_message['errors'] = error_messages
        node_message['hierarchy_node'] = None
        node_message['metadata_node'] = None
        node_message['geometry_node'] = None
        node_message['done'] = True
        node_message['message_count'] = self.message_count
        self.Publish(node_message)

    def __GetRedisInstance(self):
        """ 
        Get redis instance using host\n

        - Returns:\n
            - redis.Redis\n
        """
        try:
            r = redis.Redis(host=self.host, port=self.port, db=0)
            return r
        except Exception as e:
            Logger().Error(f"=////=> Error while creating Redis instance: {e}")
            return None
        