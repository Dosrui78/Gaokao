import os
import sys
import json
import math
import time
import random
from pymongo import UpdateMany
from datetime import datetime
from prefect import flow, task
from prefect.logging import get_run_logger
from prefect.cache_policies import NO_CACHE
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.configs import HOST
# from lib.logger import logger
from lib.header import UserAgent
from lib.mongo_pool import MongoPool
from lib.proxies_pool import get_proxies
from lib.base_requests import base_requests

class SchoolInfo:
    def __init__(self):
        self.mongo_pool = MongoPool("schoolInfo")
        self.headers = {"User-Agent": UserAgent(), "Referer": HOST}

    @task(name="get_school_info", cache_policy=NO_CACHE)
    def get_school_info(self):
        page = 1
        total_page = 1
        update_list = []
        logger = get_run_logger()
        url = "https://api.zjzw.cn/web/api/"
        params = {
            "keyword": "",
            "page": str(page),
            "province_id": "",
            "ranktype": "",
            "request_type": "1",
            "size": "50",
            "top_school_id": "\\[57,287,3238,1569,442,3269\\]",
            "type": "",
            "uri": "apidata/api/gkv3/school/lists",
            "signsafe": "7b6977536f3c943460bb46f89d8f69b2"
        }
        data = {
            "keyword": "",
            "page": page,
            "province_id": "",
            "ranktype": "",
            "request_type": 1,
            "signsafe": "7b6977536f3c943460bb46f89d8f69b2",
            "size": 50,
            "top_school_id": "[57,287,3238,1569,442,3269]",
            "type": "",
            "uri": "apidata/api/gkv3/school/lists"
        }

        while True:
            try:
                response = base_requests(url, method="POST", headers=self.headers, params=params, data=data, proxies=get_proxies())
                data_json = json.loads(response.text)
                if data_json.get("total") == 0 or isinstance(data_json.get("data"), str) or data_json.get("data", {}).get("item") == []:
                    logger.info("数据获取为空，结束循环！！")
                    break
                if data_json.get("code") == "0000":
                    item = data_json.get("data").get("item")
                    all_num = data_json.get("data").get("numFound")
                    total_page = math.ceil(all_num / 30)
                    for i in item:
                        i["update_time"] = datetime.now()
                        update_operation = UpdateMany({"school_id": i["school_id"]}, {"$set": i}, upsert=True)
                        update_list.append(update_operation)
                    if update_list:
                        self.mongo_pool.collection.bulk_write(update_list)
                        logger.info(f"第{page}页数据插入成功，插入{len(item)}条数据")
                else:
                    logger.error(f"第{page}页数据获取失败，原因：{data_json['msg']}")
            except Exception as e:
                logger.error(f"第{page}页数据获取失败，原因：{e}")
            finally:
                if page == total_page:
                    logger.info(f"达到最大页数——{total_page}，翻页结束！！")
                    break
                page += 1
                params["page"] = str(page)
                data["page"] = page
                time.sleep(random.uniform(1.2, 3.2))

if __name__ == "__main__":
    school_info = SchoolInfo()
    school_info.get_school_info()
