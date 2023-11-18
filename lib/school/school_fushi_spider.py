#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# 爬取楼盘数据的爬虫派生类
import json
import re
import math
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


class SchoolFuShiSpider(BaseSpider):
    def collect_city_loupan_data(self):

        schools = self.list_school()
        years = [2022, 2023]
        pool = ThreadPoolExecutor(max_workers=3)
        for year in years:
            #self.collect_year(schools,year)
            pool.submit(self.collect_year, schools, year)

    def collect_year(self, schools, year):

        db = self.getDb()
        cursor = db.cursor()
        sql = "update school set fushi_%s = %s where id = %s"
        for school in schools:
            if year == 2023:
                if school[5] is not None:
                    continue
            else:
                if school[6] is not None:
                    continue
            print("执行：", year, school)
            detail = self.get_school_fushi(school[1], year)
            if len(detail) == 0:
                continue
            data = json.dumps(detail)
            cursor.execute(sql, (year, data, school[0]))
            db.commit()
        cursor.close()
        db.close()

    def get_school_fushi(self, schoolId, year):

        try:
            fushi_data = []
            for page_num in range(1, 100):
                page = "https://static.kaoyan.cn/json/score/{0}/{1}/0/{2}.json".format(year, schoolId, page_num)
                response = requests.get(page)
                status_code = response.status_code
                if status_code == 404:
                    return fushi_data
                json = response.json()
                data = json["data"]
                if len(data) == 0:
                    return fushi_data
                else:
                    fushi_data.extend(data["item"])
        except Exception as e:
            print("获取复试信息错误", e)
            pass
        return fushi_data

    def list_school(self):
        db = self.getDb()
        sql = 'select * from tanko.school'
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
    spider = SchoolFuShiSpider(SPIDER_NAME)
    spider.start()
    pass
