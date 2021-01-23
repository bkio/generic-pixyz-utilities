import subprocess
from .logger import Logger

class ExecuteCommand:
    """Execute system commands with subprocess"""
    def __init__(self, command_to_execute):
        self.command_to_execute = command_to_execute

    def Run(self):
        return self.Execute()
    
    def Execute(self):
        """
            Purpose  : To execute a command and return exit status
            Argument : cmd - command to execute
            Return   : result, exit_code
        """
        process = subprocess.Popen(self.command_to_execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (result, error) = process.communicate()
        rc = process.wait()
        if rc != 0:
            Logger().error(f"=====> Failed to execute command: {self.command_to_execute}, error: {error}")
            return False
        return True