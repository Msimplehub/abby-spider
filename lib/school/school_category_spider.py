#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 爬取楼盘数据的爬虫派生类
import json
import re
import math
import traceback

import requests
from bs4 import BeautifulSoup
from lib.item.loupan import *
from lib.spider.base_spider import *
from lib.request.headers import *
from lib.utility.date import *
from lib.utility.path import *
from lib.zone.city import get_city
from lib.utility.log import *
import lib.utility.version
import pymysql
from concurrent.futures import ThreadPoolExecutor
import threading


class SchoolCategorySpider(BaseSpider):
    def collect(self):
        years = ["2022", "2023", "2024"]
        db = self.getDb()
        cursor = db.cursor()
        sql = "select * from school where schoolId > 0 order by schoolId desc"
        cursor.execute(sql)
        schools_data = cursor.fetchall()
        pool = ThreadPoolExecutor(max_workers=3)
        for year in years:
            pool.submit(self.get_school_data, schools_data, year)
        cursor.close()
        db.close()

    def get_school_data(self, schools_data, year):
        db = self.getDb()
        cursor = db.cursor()
        for school in schools_data:
            # print("school Id:", school[1])
            # pool.submit(self.get_data, year, school[1], cursor, 0, db)
            self.get_data(year, school[1], cursor, 0, db)
            time.sleep(1)
        cursor.close()
        db.close()

    def get_data(self, year, schoolId, cursor, retry, db):

        try:
            check_sql = "select * from school_category where schoolId = %s and `year` = %s"
            check_num = cursor.execute(check_sql, (schoolId, year))
            if (check_num > 0):
                return
            body = {"school_id": schoolId, "page": 1, "limit": 1000, "recruit_type": "", "year": year, "keyword": "",
                    "is_apply": 2}
            result = requests.post("https://api.kaoyan.cn/pc/school/planList", body, timeout=5).json()
            #print(result)
            data = result["data"]
            school_datas = data["data"]
            if len(school_datas) == 0:
                return
            return_json = []
            for school_data in school_datas:
                return_json.append((schoolId, school_data["research_area"], school_data.get("degree_type", ""),
                                    school_data["spe_id"], school_data["year"], school_data["depart_id"],
                                    school_data.get("degree_type_name", ""), school_data.get("recruit_number", ""),
                                    school_data.get("special_code", ""), school_data["special_name"],
                                    school_data["recruit_type_name"], school_data["depart_name"],
                                    school_data["plan_id"]))

            sql = 'INSERT INTO tanko.school_category (schoolId, research_area, degree_type, spe_id, `year`, depart_id, degree_type_name, recruit_number, special_code, special_name, recruit_type_name, depart_name, plan_id, batch) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 2);'

            cursor.executemany(sql, return_json)
            db.commit()
        except Exception as e:
            # print("exce catch exception:", year, schoolId, e)
            if retry < 5:
                self.get_data(year, schoolId, cursor, retry + 1, db)
            else:
                print(year, ",", schoolId)
                # traceback.print_exc()

    def start(self):
        self.collect()

    def getDb(self):
        connection = pymysql.connect(host='mysql-01.db.sit.ihomefnt.org',
                                     user='root',
                                     password='aijia1234567',
                                     db='tanko'
                                     )
        return connection


if __name__ == '__main__':
    spider = SchoolCategorySpider(SPIDER_NAME)
    spider.start()
    pass
