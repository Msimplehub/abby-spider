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
from lib.school.plan_view_js import PlanViewJs
from lib.school.school_spider_header import SchoolSpiderHeader
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


class SchoolAdjustDetailSpider(BaseSpider):
    schoolSpiderHeader = SchoolSpiderHeader()
    planViewJs = PlanViewJs()
    def collect(self):

        pool = ThreadPoolExecutor(max_workers=20)
        start = 0
        step = 3000
        for i in range(1, 2):
            pool.submit(self.get_school_data, start, start + step)
            start = start + step

    def get_school_data(self, startIndex, endIndex):
        db = self.getDb()
        cursor = db.cursor()
        sql = "select * from school_adjust where schoolId >= {0} and schoolId < {1} and detail is null".format(startIndex, endIndex)
        cursor.execute(sql)
        schools_data = cursor.fetchall()
        for school_adjust in schools_data:
            # print("school Id:", school[1])
            # pool.submit(self.get_data, year, school[1], cursor, 0, db)
            self.get_data(school_adjust, cursor, 0, db)
            time.sleep(2)
        cursor.close()
        db.close()

    def get_data(self, adjust, cursor, retry, db):

        school_adjust_str = adjust[2]
        try:
            school_adjust = json.loads(school_adjust_str)
            print("开始获取：", school_adjust)
            body = {"view_sign": self.planViewJs.process_data(school_adjust["tj_id"], school_adjust["is_view"], school_adjust["buy_view"])}
            response = requests.post("https://api.kaoyan.cn/pc/adjust/adjustDetail",
                                     body,
                                     headers=self.schoolSpiderHeader.headers,
                                     timeout=5)
            result = response.json()
            #print(result)
            data = result["data"]
            if len(data) == 0:
                print("获取数据为空", body)
                return

            sql = 'update tanko.school_adjust set detail=%s where id=%s;'
            cursor.execute(sql, (json.dumps(data), adjust[0]))
            db.commit()
        except Exception as e:
            # print("exce catch exception:", year, schoolId, e)
            if retry < 2:
                self.get_data(adjust, cursor, retry + 1, db)
            else:
                print("执行错误", ",", adjust)
                traceback.print_exc()

    def start(self):
        self.collect()

    def getDb(self):
        connection = pymysql.connect(host='10.40.10.115',
                                     user='root',
                                     password='Aijia@1234.com',
                                     db='tanko'
                                     )
        return connection


if __name__ == '__main__':
    spider = SchoolAdjustDetailSpider(SPIDER_NAME)
    spider.start()
    pass
