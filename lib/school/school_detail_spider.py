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


class SchoolDetailSpider(BaseSpider):
    def collect_city_loupan_data(self):
        db = self.getDb()
        cursor = db.cursor()
        sql = "update school set detail= %s where id = %s"
        schools = self.list_school()
        for school in schools:
            detail = self.get_school_detail(school[1])
            data = json.dumps(detail)
            cursor.execute(sql, (data, school[0]))
            db.commit()
        cursor.close()
        db.close()

    def get_school_detail(self, schoolId):
        page = "https://static.kaoyan.cn/json/school/{0}/info.json".format(schoolId)
        response = requests.get(page).json()
        data = response["data"]
        return data

    def list_school(self):
        db = self.getDb()
        sql = 'select * from tanko.school where detail is null'
        cursor = db.cursor()
        cursor.execute(sql)
        schools = cursor.fetchall()
        cursor.close()
        db.close()
        return schools


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
    spider = SchoolDetailSpider(SPIDER_NAME)
    spider.start()
    pass
