from .logger import Logger

import pxz
try:# Prevent IDE errors
    from pxz import io
except: pass

class ExportScene:
    """Export Scene with given file name"""
    def __init__(self, file_name = ""):
        self.file_name = file_name

    def Export(self):
        Logger().Warning(f"=====> Scene to be exported = {self.file_name}")
        io.exportScene(self.file_name)
        return None
  
    def Run(self):
        return self.Export()