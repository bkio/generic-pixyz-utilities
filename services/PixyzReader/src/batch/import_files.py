import os
import pathlib
from .logger import Logger

import pxz
try:# Prevent IDE errors
    from pxz import io
except: pass

class ImportFiles:
    """Import Files to Pixyz via given folder name"""
    def __init__(self, models_folder_path, zip_main_assembly_file_name_if_any = None):
        self.models_folder_path = models_folder_path
        self.zip_main_assembly_file_name_if_any = zip_main_assembly_file_name_if_any

    def Run(self):
        return self.ImportFiles()

    def ImportFiles(self):
        files_in_folder = os.listdir(self.models_folder_path)
        files_with_path = []
        supported_files = []
        unsupported_files = []

        _logger = Logger()

        # get supported import file formats from pixyz
        supported_import_format_list = ""
        supported_import_formats = io.getImportFormats()
        for file_format in supported_import_formats:
            for extension in file_format.extensions:
                supported_import_format_list = supported_import_format_list + extension;

        if self.zip_main_assembly_file_name_if_any is None:
            for file in files_in_folder:
                file_full_path = (self.models_folder_path + "/" + file)
                file_ext = pathlib.Path(file_full_path).suffixes[0]
                if supported_import_format_list.find(file_ext.lower()) >= 0:
                    supported_files.append(file)
                    files_with_path.append(file_full_path)
                else:
                    unsupported_files.append(file)
            
            if(len(unsupported_files) > 0):
                _logger.Warning(f"=====> Founded models = {supported_files}, Some files unsupported by Pixyz = {unsupported_files}")
            else:
                _logger.Warning(f"=====> Founded models = {supported_files}")

            _logger.Warning(f"=====> Files to be imported = {files_with_path}")
            io.importFiles(files_with_path)
            return None
        else:
            main_assembly_path = self.models_folder_path + "/" + self.zip_main_assembly_file_name_if_any
            file_ext = pathlib.Path(main_assembly_path).suffixes[0]
            if supported_import_format_list.find(file_ext.lower()) >= 0:
                _logger.Warning(f"=====> Scene will be imported with {self.zip_main_assembly_file_name_if_any} main assembly.")
                io.importScene(main_assembly_path)
                return None
            else:
                _logger.Warning(f"=====> File {self.zip_main_assembly_file_name_if_any} is not supported.")
                return f"File {self.zip_main_assembly_file_name_if_any} is not supported."