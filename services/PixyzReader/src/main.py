import os
import time
import random
from batch.unzip_files import UnzipFiles
from batch.download_files import DownloadFiles
from batch.import_files import ImportFiles
from batch.import_file_list import ImportFileList
from batch.import_scene import ImportScene
from batch.check_status_code import CheckStatusCode
from batch.logger import Logger
from batch.redis_client import RedisClient
from batch.pixyz_algorithms import PixyzAlgorithms
from batch.process_model import ProcessModel

def StartModelProcess(_logger):
    # Sync with worker process
    _logger.Warning("=====> Syncing...")
    syncing = False
    while (syncing != True):
        syncing = CheckStatusCode(check_url="http://127.0.0.1:8081/healthcheck").Run()
        # syncing = CheckStatusCode(check_url="http://192.168.137.139:8081/healthcheck").Run()

    # Get environment variables
    SIGNED_FILE_URL = os.environ.get('SIGNED_FILE_URL')
    ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY = os.environ.get('ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY')
    _logger.Warning(f"=====> SIGNED_FILE_URL = {SIGNED_FILE_URL}")
    _logger.Warning(f"=====> ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY = {ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY}")

    system_error_message = None

    model_id = str(random.getrandbits(64))
    _RedisClient = RedisClient(model_id, channel="models", host="127.0.0.1", port=6379)

    # Download Files
    #system_error_message = DownloadFiles(file_url=SIGNED_FILE_URL, file_download_path="/app/file.zip").Run()

    # Unzip Downloaded Files
    #system_error_message = UnzipFiles(zip_file="/app/file.zip", extract_location="/app/models").Run()
    
    if system_error_message == None:
        # Import Unzipped Files
        #system_error_message = ImportFiles(models_folder_path="/app/models", zip_main_assembly_file_name_if_any=ZIP_MAIN_ASSEMBLY_FILE_NAME_IF_ANY).Run()

        files_with_path = []
        # files_with_path.append("C:/tmp/models/fbx/UI-18-8101.fbx")
        files_with_path.append("C:/tmp/models/fbx/OLOverall.fbx")
        # files_with_path.append("C:/tmp/models/fbx/AREAQB.fbx")

        system_error_message = ImportFileList(files_with_path).Run()
        # system_error_message = ImportScene("C:/tmp/models/pxz/AV_EXP.pxz").Run()

        Logger("before operation").PrintModelInfo()
        PixyzAlgorithms(verbose=True).RepairCAD()
        PixyzAlgorithms(verbose=True).Tesellate()
        PixyzAlgorithms(verbose=True).DeletePatches()
        PixyzAlgorithms(verbose=True).ExplodePartByMaterials()
        PixyzAlgorithms(verbose=True).TransferCADMaterialsOnPartOccurrences()
        PixyzAlgorithms(verbose=True).MakeInstanceUnique()
        # PixyzAlgorithms(verbose=True).CreateInstancesBySimilarity()
        PixyzAlgorithms(verbose=True).Triangularize()
        PixyzAlgorithms(verbose=True).CreateNormals()
        PixyzAlgorithms(verbose=True).RepairMesh()

        try:
            _ModelProcess = ProcessModel(model_id, _RedisClient, number_of_thread = 20, decimate_target_strategy="ratio", lod_decimations=[-1, [0.5, 0.1, 1.0], [1.0, -1, 8.0], [5.0, -1, 15.0], [-1.0, 4096, 32, 100.0], [30.0, 10.0, 40.0]], small_object_threshold=[0, 0, 0, 0, 0, 0], scale_factor=1000)
            _ModelProcess.AddCustomInformation("hierarchy_id", None, True)
            _ModelProcess.Start()
        except Exception as e:
            Logger().Error(f"=====> ProcessModel Error {e}")
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