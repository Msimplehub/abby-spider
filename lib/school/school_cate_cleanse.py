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


class SchoolCateSpider(BaseSpider):
    def collect_city_loupan_data(self):
        self.get_school()


    def get_school(self):

        db = self.getDb()
        sql = 'select * from category order by id asc;'
        cursor = db.cursor()
        cursor.execute(sql)
        datas = cursor.fetchall()
        c_1 = -1
        c1 = ""
        c_2 = -1
        c2 = ""
        c_3 = 0
        c3 = ""
        for data in datas:
           if data[1] != c1:
               c1=data[1]
               c2 = data[2]
               c_1 = c_1 + 1
               c_2 = 0
               c_3 = 0
           else:
                if data[2] != c2:
                    c_2 = c_2 + 1
                    c2 = data[2]
                    c_3 = 0
                else:
                    c_3 = c_3 + 1
           print(c_1,c_2,c_3)
           update_sql = "update category set c_1=%s,c_2=%s,c_3=%s where id = %s;"
           cursor.execute(update_sql,(c_1,c_2,c_3,data[0]))
           db.commit()
        cursor.close()
        db.close()


    def start(self):
        self.collect_city_loupan_data()

    def getDb(self):
        connection = pymysql.connect(host='10.40.10.115',
                                     user='root',
                                     password='Aijia@1234.com',
                                     db='tanko'
                                     )
        return connection



if __name__ == '__main__':
    spider = SchoolCateSpider(SPIDER_NAME)
    spider.start()
    pass
