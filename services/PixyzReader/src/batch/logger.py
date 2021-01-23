import logging
import pxz
try:# Prevent IDE errors
    from pxz import scene
    from pxz import core
except: pass

class Logger:
    """ 
    The wrapper class for logging module and Pixyz verbose settings
    """
    def __init__(self, message = ""):
        # remove all verbose message from pixyz
        self.message = message
        self.RemoveAllVerbose()

    def Warning(self, warning_message):
        logging.warning(warning_message)

    def Error(self, error_message):
        logging.error(error_message)

    def Info(self, info_message):
        logging.info(info_message)
    
    def RemoveAllVerbose(self):
        core.removeConsoleVerbose(2)
        core.removeLogFileVerbose(2)
        core.removeSessionLogFileVerbose(2)

    def AddAllVerbose(self):
        core.addLogFileVerbose(2)
        core.addSessionLogFileVerbose(2)
        core.addConsoleVerbose(2)
    
    def MessageInfo(self, data, message_size):
        total_vertexNormalTangentList = 0
        total_indexes = 0
        
        try:
            geometryNode = data['geometryNode']
            lod = geometryNode['lods'][0]
            lod_level = geometryNode['lodNumber']

            total_vertexNormalTangentList += len(lod['vertexNormalTangentList'])
            total_indexes += len(lod['indexes'])
            
            logging.warning(f"=====> Sent message length = {message_size}. LOD{lod_level} indices:{total_indexes}, vertices:{total_vertexNormalTangentList}.")
        except Exception as e:
            logging.warning(f"=====> Sent message length = {message_size} without any geometry node.")

    def OccurrenceInfo(self, occurrences):
        n_triangles = scene.getPolygonCount(occurrences, True, False, False)
        n_vertices = scene.getVertexCount(occurrences, False, False, False)
        logging.warning(f"=====> Model info step {self.message} = triangles:{n_triangles}, vertices:{n_vertices}")

    def ModelInfo(self, root):
        n_triangles = scene.getPolygonCount([root], True, False, False)
        n_vertices = scene.getVertexCount([root], False, False, False)
        n_parts = len(scene.getPartOccurrences(root))
        logging.warning(f"=====> Model info step {self.message} = triangles:{n_triangles}, vertices:{n_vertices}, parts:{n_parts}.")