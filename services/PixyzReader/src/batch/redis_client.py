import redis
import base64
import zlib
import time
import json
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

    def GetLock(self):
        return self.thread_lock

    def DeflateEncodeBase64(self, message):
        compressed_message = zlib.compress(bytes(message, 'utf-8'))[2:-4]
        return base64.b64encode(compressed_message)

    def Publish(self, message):
        """ 
        Publish string message to specified channel

        - Parameters:\n
            - message : Message to be sent\n

        - Returns:\n
            - void\n
        """
        self.message_count = self.message_count + 1

        retryCount = 0
        while retryCount < 10 :
            try:
                base64_message = self.DeflateEncodeBase64(message)
                self.redis_instance.publish(self.channel, base64_message)
                retryCount = 10
            except Exception as e:
                self.logger.Error(f"=////=> Redis publish error: {e} -  message to be published: {message}")
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

    def PublishData(self, data, verbose = True):
        """ 
        Publish json object to specified channel\n

        - Parameters:\n
            - data : Data to serialize to string and publish\n

        - Returns:\n
            - void\n
        """
        message = json.dumps(data)
        message_size = sys.getsizeof(message)
        if verbose:
            self.logger.PrintMessageInfo(data, message_size, self.message_count)
        self.Publish(message)

    def Done(self):
        """ 
        Publish specific done message for listeners\n

        - Returns:\n
            - void\n
        """
        data = {'model_id': self.model_id, 'hierarchyNode': None, 'metadataNode': None, 'geometryNode': None, 'errors': None, 'done': True, 'messageCount' : self.message_count }
        self.PublishData(data)

    def Error(self, error_messages = []):
        """ 
        Publish specific error messages for listeners\n

        - Parameters:\n
            - error_messages : Array that contains error messages\n

        - Returns:\n
            - void\n
        """
        data = {'model_id': self.model_id, 'hierarchyNode': None, 'metadataNode': None, 'geometryNode': None, 'errors': error_messages, 'done': True, 'messageCount' : self.message_count }
        self.PublishData(data)

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
        