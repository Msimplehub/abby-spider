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


class SchoolLuQuMingDanSpider(BaseSpider):
    def collect_city_loupan_data(self):
        self.get_school()

    def get_school(self):
        for i in range(1, 200):
            response = requests.get("https://www.okaoyan.com/luqumingdan/2022/list_20457_{0}.html".format(i))
            if response.status_code != 200:
                break
            html = response.content
            soup = BeautifulSoup(html, "lxml")
            list = soup.find("ul", class_="contentlist rank-ullist").find_all("a")
            for a_href in list:
                print(a_href.get("href"))
                detail = requests.get("https://www.okaoyan.com/{0}".format(a_href.get("href")))
                detail_html = detail.content
                detail_soup = BeautifulSoup(detail_html, "lxml")
                link = detail_soup.find("div", class_="content").find("a")
                print(link.get("href"))
                self.urldownload(link.get("href"))

    def urldownload(self, url):
        """
        下载文件到指定目录
        :param url: 文件下载的url
        :param filename: 要存放的目录及文件名，例如：./test.xls
        :return:
        """
        path = 'F:/school/2022/'
        filename = path + os.path.basename(url)
        down_res = requests.get(url)
        with open(filename, 'wb') as file:
            file.write(down_res.content)

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
    spider = SchoolLuQuMingDanSpider(SPIDER_NAME)
    spider.start()
    pass
