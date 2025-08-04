# -*- coding: utf-8 -*-

import random
import urllib3
import requests
from tenacity import retry, stop_after_attempt, wait_fixed, wait_random, retry_if_result
from curl_cffi import requests as ja3requests
from lib.logger import logger

chrome_list = ["edge99", "edge101", "chrome99", "chrome100", "chrome101", "chrome104", "chrome107", "chrome110", "chrome99_android", "safari15_3", "safari15_5"]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def custom_retry_by_result(response: requests.Response) -> bool:
    if response is None or response.status_code != 200:
        return True
    else:
        return False

@retry(wait=wait_fixed(3) + wait_random(0, 2), stop=stop_after_attempt(3), retry=retry_if_result(custom_retry_by_result))
def base_requests(url, *args, **kwargs):
    kwargs.setdefault("verify", False)
    kwargs.setdefault("timeout", 10)
    kwargs.setdefault("headers", {})
    kwargs.setdefault("proxies", {})
    kwargs.setdefault("cookies", {})
    kwargs.setdefault("allow_redirects", True)
    kwargs.setdefault("stream", False)
    kwargs.setdefault("ja3", False)
    kwargs.setdefault("method", "GET")
    
    method = kwargs.pop("method")
    use_ja3 = kwargs.pop("ja3")
    
    try:
        if use_ja3:
            response = ja3requests.request(method, url, impersonate=random.choice(chrome_list), **kwargs)
        else:
            response = requests.request(method, url, **kwargs)
    except requests.exceptions.RequestException as e:
        logger.error(f"{url} 请求失败，原因：{e}，报错行数：{e.__traceback__.tb_lineno}")
        return None
    logger.info(f"{url} 请求成功，状态码：{response.status_code}")
    return response