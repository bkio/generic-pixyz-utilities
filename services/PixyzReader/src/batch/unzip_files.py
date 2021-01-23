from .execute_command import ExecuteCommand
from .logger import Logger

class UnzipFiles:
    """Unzip zip_file to extract_location"""
    def __init__(self, zip_file, extract_location):
        self.zip_file = zip_file
        self.extract_location = extract_location

    def Run(self):
        return self.Unzip()

    def Unzip(self):
        _logger = Logger()
        # Unzip files to models folder
        _logger.Warning(f"=====> File is started unzipping.")
        cmd_unzip = "unzip -o " + self.zip_file + " -d " + self.extract_location
        result_unzip = ExecuteCommand(command_to_execute=cmd_unzip).Run()
        if result_unzip == True:
            _logger.Warning(f"=====> File is unzipped successfully.")
            return None
        else:
            _logger.Error(f"=====> Failed to unzip file.")
            return f"Failed to execute command: {cmd_unzip}"
