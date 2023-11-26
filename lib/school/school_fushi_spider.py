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
        self.clean_data()

    def clean_data(self):
        db = self.getDb()
        cursor = db.cursor()
        sql_school = "select * from school"
        cursor.execute(sql_school)
        schools = cursor.fetchall()
        for school in schools:
            school_id = school[1]
            fushi_2023 = school[5]
            fushi_2022 = school[6]
            insert_sql = "INSERT INTO tanko.school_retest(schoolId, note, `year`, total, english, politics, diff_total, degree_type, special_one, special_two, diff_english, special_code, special_name, diff_politics, degree_type_name, diff_special_one, diff_special_two)VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            insert_data = []
            if fushi_2022 is not None:
                for fushi in json.loads(fushi_2022):
                    insert_data.append((school_id, fushi["note"],fushi["year"],fushi["total"],fushi["english"],fushi["politics"],fushi["diff_total"],fushi["degree_type"],fushi["special_one"],fushi["special_two"],fushi["diff_english"],fushi["special_code"],fushi["special_name"],fushi["diff_politics"],fushi["degree_type_name"],fushi["diff_special_one"],fushi["diff_special_two"]))
            if fushi_2023 is not None:
                for fushi in json.loads(fushi_2023):
                    insert_data.append((school_id, fushi["note"], fushi["year"], fushi["total"], fushi["english"],
                                        fushi["politics"], fushi["diff_total"], fushi["degree_type"], fushi["special_one"],
                                        fushi["special_two"], fushi["diff_english"], fushi["special_code"],
                                        fushi["special_name"], fushi["diff_politics"], fushi["degree_type_name"],
                                        fushi["diff_special_one"], fushi["diff_special_two"]))
            cursor.executemany(insert_sql, insert_data)
            db.commit()
        cursor.close()
        db.close()

    def getDb(self):
        connection = pymysql.connect(host='10.40.10.115',
                                     user='root',
                                     password='Aijia@1234.com',
                                     db='tanko'
                                     )
        return connection

    def getDb_yan(self):
        connection = pymysql.connect(host='10.40.10.115',
                                     user='root',
                                     password='Aijia@1234.com',
                                     db='x-yan'
                                     )
        return connection



if __name__ == '__main__':
    spider = SchoolFuShiSpider(SPIDER_NAME)
    spider.start()
    pass
