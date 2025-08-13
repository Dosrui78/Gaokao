import os
import sys
import json
import math
import time
import random
from hashlib import md5
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


class ScoreInfo:
    def __init__(self):
        self.task_mongo_pool = MongoPool("schoolInfo")
        self.headers = {"User-Agent": UserAgent(), "Referer": HOST}
        self.logger = get_run_logger()

    def get_unique_id(self, item: dict) -> str:
        temp = item["school_id"] + "_" + str(item["year"]) + "_" + item["province"] + "_" + item["special_id"] + "_" + item["type"] + "_" + item["spname"]

        return md5(temp.encode()).hexdigest()

    def get_tasks(self) -> list:
        cursor = self.task_mongo_pool.collection.find({"status": 0, "level_name" : "本科"}).limit(10)
        return list(cursor)

    def get_year_and_province(self, school_id) -> dict:
        url = "https://static-data.gaokao.cn/www/2.0/school/{}/dic/provincescore.json?a=www.gaokao.cn".format(school_id)
        response = base_requests(url, method="GET", headers=self.headers, proxies=get_proxies())
        data_json = json.loads(response.text)
        if data_json.get("code") == "0000":
            news_data = data_json.get("data", {}).get("newsdata", {}).get("year", {})
            if news_data:
                return news_data
        else:
            self.logger.error(f"获取年份和省份失败，原因：{data_json['message']}")

    def get_score_info(self, school_id: str, province_id: str, year: str, name: str):
        update_list = []
        temp_list = []
        url = "https://static-data.gaokao.cn/www/2.0/schoolspecialscore/{}/{}/{}.json?a=www.gaokao.cn".format(school_id, year, province_id)

        try:
            response = base_requests(
                url,
                method="GET",
                headers=self.headers,
                proxies=get_proxies(),
            )
            data_json = json.loads(response.text)
            if data_json.get("code") == "0000":
                temp_list.extend(data_json.get("data", {}).values())
                for t in temp_list:
                    items = t.get("item", [])
                    publish_at = data_json.get("time", "")
                    for item in items:
                        item["name"] = name
                        item["publish_at"] = publish_at
                        item["update_time"] = datetime.now()

                        if not item.get("year"):
                            item["year"] = year

                        unique_id = self.get_unique_id(item)
                        update_operation = UpdateMany(
                            {"unique_id": unique_id},
                            {
                                "$set": item,
                                "$setOnInsert": {"create_time": datetime.now()},
                            },
                            upsert=True,
                        )
                        update_list.append(update_operation)
                    if update_list:
                        upd_result = MongoPool("scoreInfo_{}".format(year)).collection.bulk_write(update_list)
                        return upd_result

            else:
                self.logger.error(
                    f"{year}-{name}-{province_id}数据获取失败，报错信息：{data_json['message']}"
                )
        except Exception as e:
            self.logger.error(f"{year}-{name}-{province_id}数据获取失败，原因：{e}")
        finally:
            time.sleep(random.uniform(1.1, 2.1))

    @task(name="get_score_info", cache_policy=NO_CACHE)
    def get_score_info_by_school_id(self, school_id: str, name: str):
        year_and_province = self.get_year_and_province(school_id)
        if year_and_province:
            for province_id, year_list in year_and_province.items():
                for year in year_list:
                    result = self.get_score_info(school_id, province_id, year, name)
                    if result:
                        self.logger.info(f"【{year}-{name}-{province_id}】插入{result.modified_count}条数据")

            self.task_mongo_pool.collection.update_one({"school_id": school_id}, {"$set": {"status": 1}})

    def main(self):
        tasks = self.get_tasks()
        if not tasks:
            self.logger.info("全部采集完成！！！")
            return
        for task in tasks:
            school_id = task["school_id"]
            name = task["name"]
            self.get_score_info_by_school_id.with_options(name=f"get_school_info_{school_id}")(school_id, name)


if __name__ == "__main__":
    school_info = ScoreInfo()
    school_info.main()
