from .logger import Logger

import pxz
try:# Prevent IDE errors
    from pxz import io
except: pass

class ImportScene:
    """Import Scene to Pixyz via pxz file name"""
    def __init__(self, file_name = ""):
        self.file_name = file_name

    def ImportScene(self):
        Logger().Warning(f"=====> Scene to be imported = {self.file_name}")
        io.importScene(self.file_name)
        return None
  
    def Run(self):
        return self.ImportScene()