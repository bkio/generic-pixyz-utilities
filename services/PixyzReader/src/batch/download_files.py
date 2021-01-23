from .execute_command import ExecuteCommand
from .logger import Logger

class DownloadFiles:
    """Download files from the web service by file_url and locate to file_download_path"""
    def __init__(self, file_url, file_download_path):
        self.file_url = file_url
        self.file_download_path = file_download_path

    def Run(self):
        return self.Download()

    def Download(self):
        self.system_error_message = None

        # Download file from url
        _logger = Logger()
        _logger.Warning(f"=====> File is started downloading from {self.file_url}")
        cmd_wget = "wget -O "+ self.file_download_path +" \"" + self.file_url + "\""
        result_wget = ExecuteCommand(command_to_execute=cmd_wget).Run()
        if result_wget == True:
            _logger.Warning(f"=====> File is downloaded successfully.")
        else:
            _logger.Error(f"=====> Failed to download file.")
            self.system_error_message = f"Failed to execute command: {cmd_wget}"
        
        return self.system_error_message