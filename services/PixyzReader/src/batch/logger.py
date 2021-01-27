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
    
    def PrintMessageInfo(self, data, message_size, message_count):
        total_vertexNormalTangentList = 0
        total_indexes = 0

        done = data['done']
        errors = data['errors']
        error_count = 0
        if errors is not None:
            error_count = len(errors)

        if done:
            logging.warning(f"=====> Done message has been sent. \tMessageCount: {message_count} \tMessageSize: {message_size} \tErrorCount: {error_count}")
        else:
            try:
                geometryNode = data['geometryNode']
                if geometryNode is not None:
                    lod = geometryNode['lods'][0]
                    lod_level = geometryNode['lodNumber']
                    id = geometryNode['id']

                    total_vertexNormalTangentList += len(lod['vertexNormalTangentList'])
                    total_indexes += len(lod['indexes'])
                    
                    logging.warning(f"=====> Message has been sent. \tMessageCount: {message_count} \tMessageSize: {message_size} \tErrorCount: {error_count}. \tID:{id} \tLOD{lod_level} \tIndices: {total_indexes} \tVertices: {total_vertexNormalTangentList}")
                else:
                    logging.warning(f"=====> Message has been sent. \tMessageCount: {message_count} \tMessageSize: {message_size} \tErrorCount: {error_count}. \t*** No LOD information")    
            except Exception as e:
                logging.warning(f"=====> Message has been sent. \tMessageCount: {message_count} \tMessageSize: {message_size} \tErrorCount: {error_count}. \t*** No LOD information")

    def PrintOccurrenceInfo(self, occurrences):
        n_triangles = scene.getPolygonCount(occurrences, True, False, False)
        n_vertices = scene.getVertexCount(occurrences, False, False, False)
        logging.warning(f"=====> Occurrence Info \t{self.message} \t-> Triangles: {n_triangles} \tVertices: {n_vertices}")

    def PrintModelInfo(self, root):
        n_triangles = scene.getPolygonCount([root], True, False, False)
        n_vertices = scene.getVertexCount([root], False, False, False)
        part_occurrences = scene.getPartOccurrences(root)
        n_parts = len(part_occurrences)
        n_prototypes = self.GetPrototypePartsCount(part_occurrences)
        logging.warning(f"=====> Model Info \t{self.message} \t-> Triangles: {n_triangles} \tVertices: {n_vertices} \tGeometry Parts: {n_parts} \tUnique Geometry Parts: {n_prototypes}")

    def GetPrototypePartsCount(self, part_occurrences):
        prototypeCount = 0
        for occurrence in part_occurrences:
            prototype = scene.getPrototype(occurrence)
            if prototype == 0:
                prototypeCount += 1
        
        return prototypeCount