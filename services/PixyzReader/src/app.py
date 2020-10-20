import redis
import os
import random
import time
import json
import sys
import subprocess
import math
import logging
import requests
import sys
import pathlib

import pxz
try:# Prevent IDE errors
    from pxz import io
    from pxz import algo
    from pxz import scene
    from pxz import core
    from pxz import generateproxy
    from pzy import material
    from pzy import polygonal
    from pzy import scenario
except: pass

def get_redis():
    r = redis.Redis(host="localhost", db=0)
    return r

def removeAllVerbose():
    core.removeConsoleVerbose(2)
    core.removeLogFileVerbose(2)
    core.removeSessionLogFileVerbose(2)

def addAllVerbose():
    core.addLogFileVerbose(2)
    core.addSessionLogFileVerbose(2)
    core.addConsoleVerbose(2)

def is_part(occurrence):
    partOccurrenceList = scene.getPartOccurrences(scene.getRoot())
    for item in partOccurrenceList:
        if item == occurrence:
            return True
    return False

def is_prototype_part(occurrence):
    partOccurrenceList = scene.getPartOccurrences(scene.getRoot())
    prototype = scene.getPrototype(occurrence)
    for item in partOccurrenceList:
        if item == occurrence and prototype == 0:
            return True
    return False

def get_point3_info(array):
    point3_array = []
    for item in array:
        point3 = {}
        point3['x'] = item.x
        point3['y'] = item.y
        point3['z'] = item.z
        point3_array.append(point3)
    return point3_array

def get_curvates_info(array):
    curvates_array = []
    for item in array:
        curvates = {}
        curvates['k1'] = item.k1
        curvates['k2'] = item.k2
        curvates['v1'] = item.v1
        curvates['v2'] = item.v2
        curvates_array.append(curvates)
    return curvates_array

def get_coloralpha_info(array):
	color_array = []
	for item in array:
		color = {}
		color['r'] = item.r
		color['g'] = item.g
		color['b'] = item.b
		color['a'] = item.a
		color_array.append(color)
	return color_array

def get_color_json(color):
    color_json = {}
    color_json['r'] = int(round(color.r*255))
    color_json['g'] = int(round(color.g*255))
    color_json['b'] = int(round(color.b*255))
    return color_json

def print_occurrence_info(data, message_size):
    total_vertexNormalTangentList = 0
    total_indexes = 0
    
    try:
        geometryNode = data['geometryNode']
        i = 0
        for lod in geometryNode['lods']:
            total_vertexNormalTangentList += len(lod['vertexNormalTangentList'])
            total_indexes += len(lod['indexes'])
            logging.warning(f"-----> Sent message length = Part has {str(message_size)}. LOD{i} informations = {str(total_vertexNormalTangentList)} vertices, normals, and tangents, {str(total_indexes)} indexes.")
            i += 1
    except Exception as e:
        logging.warning(f"-----> Sent message length = {str(message_size)} without any geometry node.")

def print_model_info(root, step):
    n_triangles = scene.getPolygonCount([root], True, False, False)
    n_vertices = scene.getVertexCount([root], False, False, False)
    n_parts = len(scene.getPartOccurrences(root))
    logging.warning(f"======Reader===========> Model information step {step} = triangles count is {n_triangles}, vertices count is {n_vertices}, and it has {n_parts} parts.")

# Matrix Utils
def clean_angle(angle):
  return min(1,max(angle,-1))

# calculates rotation matrix to euler angles
# The result is the same as MATLAB except the order of the euler angles ( x and z are swapped ).
def matrix4x4_to_euler_xyz(mat):
    sy = math.sqrt(mat[0][0] * mat[0][0] +  mat[1][0] * mat[1][0])

    singular = sy < 1e-6

    if not singular:
        x = math.atan2(mat[2][1] , mat[2][2])
        y = math.atan2(mat[2][0], sy)
        z = math.atan2(mat[1][0], mat[0][0])
    else:
        x = math.atan2(-mat[1][2], mat[1][1])
        y = math.atan2(-mat[2][0], sy)
        z = 0

    return convert_vector3(math.degrees(x),math.degrees(y),math.degrees(z))

def matrix4x4_to_scale(mat):
    xs = -1 if mat[0][0] * mat[0][1] * mat[0][2] < 0 else 1
    ys = -1 if mat[1][0] * mat[1][1] * mat[1][2] < 0 else 1
    zs = -1 if mat[2][0] * mat[2][1] * mat[2][2] < 0 else 1
    
    x = xs * math.sqrt(mat[0][0] * mat[0][0] + mat[0][1] * mat[0][1] + mat[0][2] * mat[0][2])
    y = ys * math.sqrt(mat[1][0] * mat[1][0] + mat[1][1] * mat[1][1] + mat[1][2] * mat[1][2])
    z = zs * math.sqrt(mat[2][0] * mat[2][0] + mat[2][1] * mat[2][1] + mat[2][2] * mat[2][2])
    
    return [x, y, z]

def combine_part_and_world_scale(wmat, pmat):
    x1, y1, z1 = matrix4x4_to_scale(wmat)
    if pmat != None:
        x2, y2, z2 = matrix4x4_to_scale(pmat)
    else:
        x2, y2, z2 = [1, 1, 1]
    
    x = x1 * x2
    y = y1 * y2
    z = z1 * z2

    return convert_vector3(x,y,z)

def matrix4x4_to_translation(mat):
    # convert from mm to cm
    x = mat[0][3] * 0.1
    y = mat[1][3] * 0.1
    z = mat[2][3] * 0.1
    return convert_vector3(x,y,z)
    
def convert_vector3(x,y,z):
    return {'x': format(x, 'f'), 'y': format(y, 'f'), 'z': format(z, 'f')}

def get_material_info(component):
    material_color = None
    for partMaterial in scene.listPartSubMaterials(component):
        materialDefinition = material.getMaterialDefinition(partMaterial)
        material_color = get_color_json(materialDefinition.albedo[1])
        # material_color['normal'] = get_color_json(materialDefinition.normal[1])
        # material_color['metallic'] = materialDefinition.metallic[1]
        # material_color['roughness'] = materialDefinition.roughness[1]
        # material_color['ao'] = materialDefinition.ao[1]
        # material_color['opacity'] = materialDefinition.opacity[1]
    return material_color

def get_geometry_info(mesh):
    error_message = None

    meshDefinition = polygonal.getMeshDefinition(mesh)
    meshVertices = meshDefinition.vertices
    meshNormals = meshDefinition.normals
    meshTangents = meshDefinition.tangents
    meshTriangles = meshDefinition.triangles

    vertices_len = len(meshVertices)
    normals_len = len(meshNormals)
    tangents_len = len(meshTangents)
    triangles_len = len(meshTriangles)
    
    if vertices_len != normals_len or normals_len != tangents_len:
        error_message = f"Vertices, normals, and tangents must be same. Please check your model. Vertices Count={vertices_len}, Normals Count={normals_len}, Tangents Count={tangents_len}"

    if vertices_len > 0 and triangles_len == 0:
        error_message = f"If your triangles count is equal to 0 (zero), vertices count must be 0 (zero). Please check your model. Vertices Count={vertices_len}, Triangles Count={triangles_len}"

    if triangles_len > 0 and triangles_len % 3 != 0:
        error_message = f"Triangles count must be divided by 3. Please check your model. Triangles Count={triangles_len}"

    vertices = get_point3_info(meshVertices)
    normals = get_point3_info(meshNormals)
    tangents = get_point3_info(meshTangents)
    indexes = meshTriangles

    vertexNormalTangentList = []
    i = 0
    while i < vertices_len:
        vertexNormalTangent = {}
        vertexNormalTangent['vertex'] = vertices[i]
        vertexNormalTangent['normal'] = normals[i]
        vertexNormalTangent['tangent'] = tangents[i]
        vertexNormalTangentList.append(vertexNormalTangent)
        i += 1
    geometry_info = {}
    geometry_info['vertexNormalTangentList'] = vertexNormalTangentList
    geometry_info['indexes'] = indexes
    return [geometry_info, error_message]

def get_geometry_node(occurrence, LOD1, LOD2):
    geometry_node = {}
    lods = []
    error_messages = []
    if is_prototype_part(occurrence) == True:    
        error_message_lod0 = None
        error_message_lod1 = None
        error_message_lod2 = None
        name = core.getProperty(occurrence, "Name")

        # get LOD0 info
        part = scene.getComponent(occurrence, scene.ComponentType.Part, False)
        lod0_mesh = scene.getPartMesh(part)
        lod0_info, error_message_lod0 = get_geometry_info(lod0_mesh)

        # create LOD1 from LOD0 information
        lod1 = scene.createOccurrence(name + "_LOD1")
        scene.setComponentOccurrence(core.cloneEntity(part), lod1)
        sufacic, lineic, normal = LOD1
        algo.decimate([lod1], sufacic, lineic, normal)

        # get LOD1 info
        partLOD1 = scene.getComponent(lod1, scene.ComponentType.Part, False)
        lod1_mesh = scene.getPartMesh(partLOD1)
        lod1_info, error_message_lod1 = get_geometry_info(lod1_mesh)

        # create LOD2 from LOD0 information
        lod2 = scene.createOccurrence(name + "_LOD2")
        scene.setComponentOccurrence(core.cloneEntity(part), lod2)
        sufacic, lineic, normal = LOD2
        algo.decimate([lod2], sufacic, lineic, normal)

        # get LOD2 info
        partLOD2 = scene.getComponent(lod2, scene.ComponentType.Part, False)
        lod2_mesh = scene.getPartMesh(partLOD2)
        lod2_info, error_message_lod2 = get_geometry_info(lod2_mesh)

        # delete created occurrences
        scene.deleteOccurrences([lod1])
        scene.deleteOccurrences([lod2])

        lods.append(lod0_info)
        lods.append(lod1_info)
        lods.append(lod2_info)

        if error_message_lod0:
            error_messages.append(error_message_lod0)
        if error_message_lod1:
            error_messages.append(error_message_lod1)
        if error_message_lod2:
            error_messages.append(error_message_lod2)
    
    if len(lods) > 0:
        geometry_node['id'] = core.getProperty(occurrence, "Id")
        geometry_node['lods'] = lods
    else:
        geometry_node = None
    return [geometry_node, error_messages]

def get_metadata_info(occurrence, metadata_id):
    metadata_obj = {}
    # put name info as metadata before getting actual metadata information
    metadata_obj['__hierarchy_name__'] = core.getProperty(occurrence, "Name")

    try:
        metadataComponent = scene.getComponent(occurrence, scene.ComponentType.Metadata)
        metadataDefinitionList = scene.getMetadatasDefinitions([metadataComponent])
        for metadataDefinition in metadataDefinitionList:
            for item in metadataDefinition:
                metadata_obj[item.name] = item.value
    except:
        print("No metadata component found")

    metadata_info = {
        'id': metadata_id,
        'metadata' : json.dumps(metadata_obj)
    }
    return metadata_info

def get_geometry_parts(occurrence):
    geometry_parts = []
    if is_part(occurrence) == True:
        for component in scene.listComponents(occurrence, True):
            matrix_transform = scene.getGlobalMatrix(occurrence)
            part_matrix_transform = scene.getPartsTransforms([component])[0]
            geometry_part = {}
            prototype = scene.getPrototype(occurrence)
            if prototype == 0:
                geometry_part['geometryId'] = core.getProperty(occurrence, "Id")
            else:
                geometry_part['geometryId'] = prototype
            geometry_part['location'] = matrix4x4_to_translation(matrix_transform)
            geometry_part['rotation'] = matrix4x4_to_euler_xyz(matrix_transform)
            geometry_part['scale'] = combine_part_and_world_scale(matrix_transform, part_matrix_transform)
            geometry_part['color'] = get_material_info(component)
            geometry_parts.append(geometry_part)

    if len(geometry_parts) > 0:
        return geometry_parts
    else:
        return None

def get_hierarchy_data(occurrence, parent_id, hierarchy_id, metadata_id):
    geometryParts = get_geometry_parts(occurrence)

    childNodes = []
    for child in scene.getChildren(occurrence):
        child_hierarchy_id = core.getProperty(child, "hierarchy_id")
        childNodes.append(child_hierarchy_id)
    
    hierarchyNode = {'id': hierarchy_id, 'parentId': parent_id, 'metadataId': metadata_id, 'geometryParts': geometryParts, 'childNodes': childNodes}
    return hierarchyNode

def get_model_data(occurrence, model_id, parent_id):
    metadata_id = str(random.getrandbits(64))
    hierarchy_id = core.getProperty(occurrence, "hierarchy_id")
    
    metadataNode = get_metadata_info(occurrence, metadata_id)
    if metadataNode == None:
        metadata_id = None

    hierarchyNode = get_hierarchy_data(occurrence, parent_id, hierarchy_id, metadata_id)

    # sufacic, lineic, normal
    LOD1 =       [75.0, -1.0, 75.0]
    LOD2 =       [180.0, -1.0, 180.0]
    geometryNode, error_messages = get_geometry_node(occurrence, LOD1, LOD2)

    data = {'model_id': model_id, 'hierarchyNode': hierarchyNode, 'metadataNode': metadataNode, 'geometryNode': geometryNode, 'errors': error_messages, 'done': False }
    message = json.dumps(data)
    message_size = sys.getsizeof(message)

    print_occurrence_info(data, message_size)

    publish_to_redis(message)

    # get child information
    for child in scene.getChildren(occurrence):
        get_model_data(child, model_id, hierarchy_id)

def set_custom_data(occurrence):
    hierarchy_id = str(random.getrandbits(64))
    core.addCustomProperty(occurrence, "hierarchy_id", hierarchy_id)

    for child in scene.getChildren(occurrence):
        set_custom_data(child)

def remove_all_verbose():
    core.removeConsoleVerbose(2)
    core.removeLogFileVerbose(2)
    core.removeSessionLogFileVerbose(2)

    core.removeConsoleVerbose(5)
    core.removeLogFileVerbose(5)
    core.removeSessionLogFileVerbose(5)

def execute_command(cmd):
    """
        Purpose  : To execute a command and return exit status
        Argument : cmd - command to execute
        Return   : result, exit_code
    """
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (result, error) = process.communicate()
    rc = process.wait()
    if rc != 0:
        logging.error(f"Failed to execute command: {cmd}, error: {error}")
        return False
    return True

def publish_to_redis(message):
    global messageCount
    messageCount = messageCount + 1

    retryCount = 0
    while retryCount < 10 :
        try:
            r = get_redis()
            r.publish('models', message)
            retryCount = 10
        except Exception as e:
            logging.error(f"Redis error: {e}")
            logging.warning(message)
            retryCount = retryCount + 1
            time.sleep(1)

def reader_pixyz_main():
    global messageCount
    messageCount = int(0)
    # remove all verbose message from pixyz
    remove_all_verbose()

    system_error_message = None

    # Get environment variables
    # os.environ.get('SIGNED_FILE_URL')
    # SIGNED_FILE_URL = "https://github.com/berkanuslu/cad_model_samples/raw/master/SAMPLE2.zip"
    SIGNED_FILE_URL = os.environ.get('SIGNED_FILE_URL')
    ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY = os.environ.get('ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY')

    logging.warning(f"======Reader===========> environment variable -> SIGNED_FILE_URL = [{SIGNED_FILE_URL}]")
    logging.warning(f"======Reader===========> environment variable -> ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY = {ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY}")

    # Download file from SIGNED_FILE_URL
    logging.warning(f"======Reader===========> File is started downloading from {SIGNED_FILE_URL}")
    cmd_wget = "wget -O /app/file.zip " + "\"" +SIGNED_FILE_URL + "\""
    result_wget = execute_command(cmd_wget)
    if result_wget == True:
        logging.warning("======Reader===========> File is downloaded successfully.")
    else:
        logging.error("======Reader===========> Failed to download file.")
        system_error_message = f"Failed to execute command: {cmd_wget}"
    
    cmd_la = "ls -la"
    execute_command(cmd_la)

    # Sync with worker process
    syncing = True
    logging.warning("Syncing...")
    while syncing :
        try:
            r = requests.get('http://127.0.0.1:8081/healthcheck')
            logging.warning(r.status_code)
            if r.status_code == 200:
                syncing = False
                logging.warning("Synced")
            else:
                time.sleep(1)
        except Exception as e:
            time.sleep(1)


    # Unzip files to models folder
    logging.warning(f"======Reader===========> File is started unzipping.")
    cmd_unzip = "unzip -o /app/file.zip -d /app/models"
    result_unzip = execute_command(cmd_unzip)
    if result_unzip == True:
        logging.warning("======Reader===========> File is unzipped successfully.")
    else:
        logging.error("======Reader===========> Failed to unzip file.")
        system_error_message = f"Failed to execute command: {cmd_unzip}"

    model_id = str(random.getrandbits(64))

    if system_error_message == None:
        files = os.listdir("/app/models")
        files_with_path = []
        supported_files = []
        unsupported_files = []

        # get supported import file formats from pixyz
        supported_import_format_list = ""
        supported_import_formats = io.getImportFormats()
        for file_format in supported_import_formats:
            for extension in file_format.extensions:
                supported_import_format_list = supported_import_format_list + extension;

        if ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY is None:
            for file in files:
                file_full_path = ("/app/models/" + file)
                file_ext = pathlib.Path(file_full_path).suffixes[0]
                if supported_import_format_list.find(file_ext.lower()) >= 0:
                    supported_files.append(file)
                    files_with_path.append(file_full_path)
                else:
                    unsupported_files.append(file)
            
            if(len(unsupported_files) > 0):
                logging.warning(f"======Reader===========> Founded models = {supported_files}, Some files unsupported by pixyz = {unsupported_files}")
            else:
                logging.warning(f"======Reader===========> Founded models = {supported_files}")

            logging.warning(f"======Reader===========> Files to be imported = {files_with_path}")
            io.importFiles(files_with_path)
        else:
            main_assembly_path = "/app/models/" + ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY
            file_ext = pathlib.Path(main_assembly_path).suffixes[0]
            if supported_import_format_list.find(file_ext.lower()) >= 0:
                logging.warning(f"======Reader===========> Scene will be imported with {ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY} main assembly. Founded models = {files}")
                io.importScene(main_assembly_path)
            else:
                system_error_message = f"File {ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY} is not supported. Founded models = {files}"
                logging.warning(f"======Reader===========> File {ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY} is not supported. Founded models = {files}")
        
        if system_error_message == None:
            root = scene.getRoot()

            print_model_info(root, 'before repairCAD')
            algo.repairCAD([root], 0.1, False)

            print_model_info(root, 'before tessellate')
            algo.tessellate([root], 2.0, -1, -1, True, 0, 1, 0.0, True, False, False, False)

            print_model_info(root, 'before repairMesh')
            algo.repairMesh([root], 0.1, True, False)

            print_model_info(root, 'before explodePartByMaterials')
            algo.explodePartByMaterials([root])

            print_model_info(root, 'before deletePatches')
            algo.deletePatches([root], True)

            print_model_info(root, 'before deleteLines')
            algo.deleteLines([root])

            print_model_info(root, 'before deleteFreeVertices')
            algo.deleteFreeVertices([root])

            print_model_info(root, 'before triangularize')
            algo.triangularize([root])

            print_model_info(root, 'before makeInstanceUnique')
            scene.makeInstanceUnique([root])
        
            print_model_info(root, 'before createInstancesBySimilarity')
            scenario.createInstancesBySimilarity([root], 1.0, 1.0, True, False)

            print_model_info(root, 'before decimate')
            algo.decimate([root], 3.0, -1, 15.0, -1, False)

            set_custom_data(root)

            get_model_data(root, model_id, '18446744069414584320')

            data = {'model_id': model_id, 'hierarchyNode': None, 'metadataNode': None, 'geometryNode': None, 'errors': None, 'done': True, 'messageCount' : messageCount }
            message = json.dumps(data)
            publish_to_redis(message)
        else:
            data = {'model_id': model_id, 'hierarchyNode': None, 'metadataNode': None, 'geometryNode': None, 'errors': [system_error_message], 'done': True, 'messageCount' : messageCount }
            message = json.dumps(data)
            publish_to_redis(message)
    else:
        data = {'model_id': model_id, 'hierarchyNode': None, 'metadataNode': None, 'geometryNode': None, 'errors': [system_error_message], 'done': True, 'messageCount' : messageCount }
        message = json.dumps(data)
        publish_to_redis(message)


# running from there
try:
    start_time = time.time()
    logging.warning(f"======Reader===========> the pixyz script is started at {time.ctime(start_time)}")
    reader_pixyz_main()
    finish_time = time.time()
    process_time_seconds = finish_time - start_time
    times_taken = time.strftime("%H:%M:%S", time.gmtime(process_time_seconds))
    logging.warning(f"======Reader===========> the pixyz script is finished its job at {time.ctime(finish_time)}, and total process time is {times_taken}")
    os._exit(os.EX_OK)
except Exception as e:
    os._exit(os.EX_DATAERR)
