import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.configs import IS_LOCAL_DEV

def get_proxies():
    if IS_LOCAL_DEV:
        proxies = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890"
        }    
    else:
        proxies = None
    return proxies