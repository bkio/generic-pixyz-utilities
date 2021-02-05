import redis
import base64
import zlib
import time
import json
import sys
import flatbuffers
from .FB.FBNodeMessage import *
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

    def GetMessageCount(self):
        return self.message_count

    def DeflateEncodeBase64(self, message):
        # compressed_message = zlib.compress(bytes(message, 'utf-8'))[2:-4]
        compressed_message = zlib.compress(message)[2:-4]
        return base64.b64encode(compressed_message)

    def Publish(self, data_buffer, done = False, errors = [], verbose = True):
        """ 
        Publish json data to specified channel

        - Parameters:\n
            - data : Data to be sent as a message\n
            - verbose : If True, it will write a message information\n

        - Returns:\n
            - void\n
        """
        self.message_count = self.message_count + 1
        
        base64_message = self.DeflateEncodeBase64(data_buffer)

        message_size = sys.getsizeof(base64_message)
        if verbose:
            self.logger.PrintMessageInfo(done, errors, message_size, self.message_count)

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
        fbbuilder = flatbuffers.Builder(2048)
        FBNodeMessageStart(fbbuilder)
        FBNodeMessageAddModelID(fbbuilder, int(self.model_id))
        FBNodeMessageAddDone(fbbuilder, True)
        FBNodeMessageAddMessageCount(fbbuilder, self.message_count)
        data = FBNodeMessageEnd(fbbuilder)
        fbbuilder.Finish(data)
        data_buffer = fbbuilder.Output()
        self.Publish(data_buffer, done=True, errors=[], verbose=True)

    def Error(self, error_messages = []):
        """ 
        Publish specific error messages for listeners\n

        - Parameters:\n
            - error_messages : Array that contains error messages\n

        - Returns:\n
            - void\n
        """
        fbbuilder = flatbuffers.Builder(2048)
        errors_string = fbbuilder.CreateString(str(error_messages))
        FBNodeMessageStart(fbbuilder)
        FBNodeMessageAddModelID(fbbuilder, int(self.model_id))
        FBNodeMessageAddDone(fbbuilder, True)
        FBNodeMessageAddMessageCount(fbbuilder, self.message_count)
        FBNodeMessageAddErrors(fbbuilder, errors_string)
        data = FBNodeMessageEnd(fbbuilder)
        fbbuilder.Finish(data)
        data_buffer = fbbuilder.Output()
        self.Publish(data_buffer, done=True, errors=error_messages, verbose=True)

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
        