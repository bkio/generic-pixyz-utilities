import pathlib
from .logger import Logger

import pxz
try:# Prevent IDE errors
    from pxz import io
except: pass

class ImportFileList:
    """Import Files to Pixyz via file list as full path instead of given folder"""
    def __init__(self, file_list = []):
        self.file_list = file_list

    def Run(self):
        return self.ImportFiles()

    def ImportFiles(self):
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

        for file in self.file_list:
            file_ext = pathlib.Path(file).suffixes[0]
            if supported_import_format_list.find(file_ext.lower()) >= 0:
                supported_files.append(file)
                files_with_path.append(file)
            else:
                unsupported_files.append(file)
        
        if(len(unsupported_files) > 0):
            _logger.Warning(f"=====> Founded models = {supported_files}, Some files unsupported by pixyz = {unsupported_files}")
        else:
            _logger.Warning(f"=====> Founded models = {supported_files}")

        _logger.Warning(f"=====> Files to be imported = {files_with_path}")
        io.importFiles(files_with_path)
        return None