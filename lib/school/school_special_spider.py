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
from lib.school.school_spider import SchoolBaseSpider
from lib.school.school_spider_header import SchoolSpiderHeader
from lib.spider.base_spider import *
from lib.request.headers import *
from lib.utility.date import *
from lib.utility.path import *
from lib.zone.city import get_city
from lib.utility.log import *
import lib.utility.version
import pymysql


class SchoolBaseSpider(BaseSpider):
    schoolSpiderHeader = SchoolSpiderHeader()
    def collect_city_loupan_data(self):
        self.get_school()


    def get_school(self):
        result = requests.get("https://static.kaoyan.cn/json/special/specialIntro.json", headers=self.schoolSpiderHeader.headers).json()
        data = result["data"]
        return_json = []
        db = self.getDb()
        cursor = db.cursor()
        update_sql = "update yan_master_special set info=%s where level2_code  = %s;"
        for school_key, school_value in data.items():
            cursor.execute(update_sql, (school_value,school_key))
            db.commit()
        cursor.close()
        db.close()
        return return_json


    def start(self):
        self.collect_city_loupan_data()

    def getDb(self):
        connection = pymysql.connect(host='10.40.10.115',
                                     user='root',
                                     password='Aijia@1234.com',
                                     db='x-yan'
                                     )
        return connection



if __name__ == '__main__':
    spider = SchoolBaseSpider(SPIDER_NAME)
    spider.start()
    pass
