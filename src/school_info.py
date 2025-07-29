import os
import sys
import json
from pymongo import UpdateMany
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.configs import HOST
from lib.logger import logger
from lib.header import UserAgent
from lib.mongo_pool import MongoPool
from lib.base_requests import base_requests

class SchoolInfo:
    def __init__(self):
        self.mongo_pool = MongoPool("schoolInfo")
        self.headers = {"User-Agent": UserAgent(), "Referer": HOST}

    def get_school_info(self):
        page = 1
        update_list = []
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
                response = base_requests(url, method="POST", headers=self.headers, params=params, data=data)
                data_json = json.loads(response.text)
                if data_json.get("total") == 0 or isinstance(data_json.get("data"), str):
                    logger.info("数据获取为空，结束循环！！")
                    break
                if data_json.get("code") == "0000":
                    item = data_json.get("data").get("item")
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
                page += 1
                params["page"] = str(page)
                data["page"] = page

if __name__ == "__main__":
    school_info = SchoolInfo()
    school_info.get_school_info()