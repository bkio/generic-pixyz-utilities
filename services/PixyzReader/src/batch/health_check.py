import requests
import time
from .logger import Logger

class HealthCheck:
    """It returns True if the check_url is returned 200 status code, otherwise returns False"""
    def __init__(self, check_url):
        self.health_check_url = check_url

    def Run(self):
        return self.CheckStatus()

    def CheckStatus(self):
        try:
            _logger = Logger()
            r = requests.get(self.health_check_url)
            _logger.Warning(f"=====> Status Code: {r.status_code}")
            if r.status_code == 200:
                _logger.Warning("=====> Synced successfully")
                return True
            else:
                time.sleep(1)
        except Exception as e:
            time.sleep(1)
        
        return False
