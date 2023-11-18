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
    my_headers = [

        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
        "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"
    ]

    headers = {
        "Accept": "application/json,text/plain,*/*",
        "Accept-Encoding": "gzip,deflate,br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        #"Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://www.kaoyan.cn",
        "Pragma": "no-cache",
        "Referer": "https://www.kaoyan.cn/",
        "User-Agent": random.choice(my_headers)
        #"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

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
            #time.sleep(2)
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
            response = requests.post(page, data=body, headers=self.headers)
            json = response.json()
            data = json["data"]
            return data
        except Exception as e:
            if retry < 1:
                return self.get_school_detail(school_category, retry + 1)
            else:
                #traceback.print_exc()
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
        start = 170000
        step = 10000
        for i in range(1, 5):
            pool.submit(self.collect_city_loupan_data, start, start+step)
            start = start + step


    def getDb(self):
        connection = pymysql.connect(host='10.40.10.115',
                                     user='root',
                                     password='Aijia@1234.com',
                                     db='tanko'
                                     )
        return connection


if __name__ == '__main__':
    spider = SchoolCategoryDetailSpider(SPIDER_NAME)
    spider.start()
    pass
