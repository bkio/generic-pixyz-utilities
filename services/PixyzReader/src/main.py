import os
import time
import random
from batch.unzip_files import UnzipFiles
from batch.download_files import DownloadFiles
from batch.import_files import ImportFiles
from batch.import_file_list import ImportFileList
from batch.health_check import HealthCheck
from batch.logger import Logger
from batch.redis_client import RedisClient
from batch.pixyz_algorithms import PixyzAlgorithms
from batch.process_model import ProcessModel

def StartModelProcess(_logger):
    # Sync with worker process
    syncing = False
    _logger.Warning("=====> Syncing...")
    while (syncing != True):
        syncing = HealthCheck(check_url="http://127.0.0.1:8081/healthcheck").Run()
        # syncing = HealthCheck(check_url="http://192.168.137.139:8081/healthcheck").Run()

    # Get environment variables
    SIGNED_FILE_URL = os.environ.get('SIGNED_FILE_URL')
    ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY = os.environ.get('ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY')
    _logger.Warning(f"=====> SIGNED_FILE_URL = {SIGNED_FILE_URL}")
    _logger.Warning(f"=====> ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY = {ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY}")

    system_error_message = None

    model_id = str(random.getrandbits(64))
    _RedisClient = RedisClient(model_id, channel="models", host="127.0.0.1", port=6379, password="Kongsberg.,2021")

    # Download Files
    #system_error_message = DownloadFiles(file_url=SIGNED_FILE_URL, file_download_path="/app/file.zip").Run()

    # Unzip Downloaded Files
    #system_error_message = UnzipFiles(zip_file="/app/file.zip", extract_location="/app/models").Run()
    
    if system_error_message == None:

        # Import Unzipped Files
        #system_error_message = ImportFiles(models_folder_path="/app/models", zip_main_assembly_file_name_if_any=ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY).Run()

        files_with_path = []
        #files_with_path.append("C:/models/rvm/M22-EY.rvm")
        #files_with_path.append("C:/models/rvm/M22-EP.rvm")
        #files_with_path.append("C:/models/gltf/model2.gltf")
        #files_with_path.append("C:/models/fbx/model2.fbx")
        #files_with_path.append("C:/tmp/models/rvm/O10-EP.rvm")
        files_with_path.append("C:/tmp/models/fbx/UI-18-8101.fbx")
        #files_with_path.append("C:/tmp/models/fbx/UI-18-8201.fbx")
        #files_with_path.append("C:/tmp/models/fbx/UI-18-8101.fbx")
        #files_with_path.append("C:/tmp/models/fbx/UI-18-8101.fbx")
        #files_with_path.append("C:/tmp/models/fbx/model2.fbx")
        #files_with_path.append("C:/models/monkey.dae")

        system_error_message = ImportFileList(files_with_path).Run()

        _Algo = PixyzAlgorithms()
        _Algo.RepairCAD()
        _Algo.Tesellate()
        _Algo.RepairMesh()
        _Algo.ExplodePartByMaterials()
        _Algo.DeletePatches()
        _Algo.DeleteLines()
        _Algo.DeleteFreeVertices()
        _Algo.Triangularize()
        _Algo.CreateNormals()
        _Algo.MakeInstanceUnique()
        # _Algo.CreateInstancesBySimilarity()
        # _Algo.Decimate()

        _ModelProcess = ProcessModel(model_id, _RedisClient, number_of_thread = 10, decimate_target_strategy="ratio", lod_levels=[100, 90, 80, 60, 20, 10], small_object_threshold=0, scale_factor=1000)
        _ModelProcess.AddCustomInformation("hierarchy_id", str(random.getrandbits(64)))
        _ModelProcess.Start()
    else:
        _RedisClient.Error([system_error_message])

def main():
    try:
        _logger = Logger()
        start_time = time.time()
        _logger.Warning(f"=====> Pixyz script is started at {time.ctime(start_time)}")

        StartModelProcess(_logger)

        finish_time = time.time()
        process_time_seconds = finish_time - start_time
        times_taken = time.strftime("%H:%M:%S", time.gmtime(process_time_seconds))
        _logger.Warning(f"=====> Pixyz script is finished its job at {time.ctime(finish_time)}, and total process time is {times_taken}")
        #os._exit(0)
    except Exception as e:
        Logger().Error(f"=////=> Error in main function: {e}")

main()