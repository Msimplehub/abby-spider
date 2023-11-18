#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 爬取楼盘数据的爬虫派生类
import json
import re
import math
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

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


class SchoolCategoryDetailSpider(BaseSpider):

    def collect_city_loupan_data(self, startIndex, endIndex):
        db = self.getDb()
        cursor = db.cursor()
        sql = "update school_category set detail= %s where id = %s"
        school_categorys = self.list_school(startIndex, endIndex)
        for school_category in school_categorys:
            if school_category[15] is not None:
                continue
            detail = self.get_school_detail(school_category, 0)
            if detail is not None:
                data = json.dumps(detail)
                cursor.execute(sql, (data, school_category[0]))
                db.commit()
            time.sleep(2)
        cursor.close()
        db.close()

    def get_school_detail(self, school_category, retry):
        response = ""
        try:
            page = "https://api.kaoyan.cn/pc/school/planDetail"
            body = {
                "plan_id": school_category[13],
                "is_apply": 2
            }
            response = requests.post(page, data=body, timeout=5)
            json = response.json()
            data = json["data"]
            return data
        except Exception as e:
            if retry < 5:
                return self.get_school_detail(school_category, retry + 1)
            else:
                # traceback.print_exc()
                print("获取专业明细失败", school_category)
                return None

    def list_school(self, startIndex, endIndex):
        db = self.getDb()
        sql = "select * from tanko.school_category where detail is null and id>={0} and id<{1}".format(startIndex,
                                                                                                       endIndex)
        cursor = db.cursor()
        cursor.execute(sql)
        schools = cursor.fetchall()
        cursor.close()
        db.close()
        return schools

    def start(self):
        pool = ThreadPoolExecutor(max_workers=6)
        #self.collect_city_loupan_data(0, 10000)
        pool.submit(self.collect_city_loupan_data, 0, 10000)
        pool.submit(self.collect_city_loupan_data, 10000, 20000)
        pool.submit(self.collect_city_loupan_data, 20000, 30000)
        pool.submit(self.collect_city_loupan_data, 30000, 40000)
        pool.submit(self.collect_city_loupan_data, 40000, 50000)
        pool.submit(self.collect_city_loupan_data, 50000, 60000)

    def getDb(self):
        connection = pymysql.connect(host='mysql-01.db.sit.ihomefnt.org',
                                     user='root',
                                     password='aijia1234567',
                                     db='tanko'
                                     )
        return connection


if __name__ == '__main__':
    spider = SchoolCategoryDetailSpider(SPIDER_NAME)
    spider.start()
    pass
