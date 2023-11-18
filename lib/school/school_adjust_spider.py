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


class SchoolAdjustSpider(BaseSpider):
    def collect(self):

        pool = ThreadPoolExecutor(max_workers=3)
        pool.submit(self.get_school_data, 0, 500)
        pool.submit(self.get_school_data, 500, 1000)
        pool.submit(self.get_school_data, 1000, 2000)

    def get_school_data(self, startIndex, endIndex):
        db = self.getDb()
        cursor = db.cursor()
        sql = "select * from school where schoolId >= {0} and schoolId < {1} order by schoolId desc".format(startIndex, endIndex)
        cursor.execute(sql)
        schools_data = cursor.fetchall()
        for school in schools_data:
            # print("school Id:", school[1])
            # pool.submit(self.get_data, year, school[1], cursor, 0, db)
            self.get_data(school[1], cursor, 0, db)
            time.sleep(1)
        cursor.close()
        db.close()

    def get_data(self, school_id, cursor, retry, db):

        try:
            check_sql = "select count(1) from school_adjust where schoolId={0}".format(school_id)
            count = cursor.execute(check_sql)
            if count > 0:
                return

            print("开始获取：", school_id)
            body = {"school_id":school_id,"keyword":"","page":1,"limit":1000}

            result = requests.post("https://api.kaoyan.cn/pc/adjust/schoolAdjustList", body, timeout=5).json()
            #print(result)
            data = result["data"]
            school_datas = data["data"]
            if len(school_datas) == 0:
                return
            return_json = []
            for school_data in school_datas:
                return_json.append((school_id, json.dumps(school_data)))

            sql = 'INSERT INTO tanko.school_adjust (schoolId, adjust) VALUES(%s, %s);'

            cursor.executemany(sql, return_json)
            db.commit()
        except Exception as e:
            # print("exce catch exception:", year, schoolId, e)
            if retry < 5:
                self.get_data(school_id, cursor, retry + 1, db)
            else:
                print("执行错误", ",", school_id)
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
    spider = SchoolAdjustSpider(SPIDER_NAME)
    spider.start()
    pass
