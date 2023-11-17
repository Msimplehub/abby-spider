#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 爬取楼盘数据的爬虫派生类
import json
import re
import math
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


class SchoolBaseSpider(BaseSpider):
    def collect_city_loupan_data(self):
        self.get_school()


    def get_school(self):
        result = requests.get("https://static.kaoyan.cn/json/school/code.json").json()
        data = result["data"]
        return_json = []
        db = self.getDb()
        for school_key, school_value in data.items():
            return_json.append((school_value["id"],school_value["pid"],school_value["n"]))
        sql = 'INSERT INTO tanko.school (schoolId, schoolPid, schoolName) VALUES(%s, %s, %s);'
        cursor = db.cursor()
        cursor.executemany(sql,return_json)
        db.commit()
        cursor.close()
        db.close()
        return return_json


    def start(self):
        self.collect_city_loupan_data()

    def getDb(self):
        connection = pymysql.connect(host = 'mysql-01.db.sit.ihomefnt.org',
            user = 'root',
            password = 'aijia1234567',
            db = 'tanko'
            )
        return connection



if __name__ == '__main__':
    spider = SchoolBaseSpider(SPIDER_NAME)
    spider.start()
    pass
