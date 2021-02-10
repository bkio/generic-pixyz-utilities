import requests
import time
from .logger import Logger

class CheckStatusCode:
    """It returns True if the check_url is returned given status code, otherwise returns False"""
    def __init__(self, check_url, check_status_code = 200):
        self.check_url = check_url
        self.check_status_code = check_status_code

    def Run(self):
        return self.CheckStatus()

    def CheckStatus(self):
        try:
            _logger = Logger()
            r = requests.get(self.check_url)
            if r.status_code == self.check_status_code:
                return True
            else:
                time.sleep(1)
        except Exception as e:
            time.sleep(1)
        
        return False
