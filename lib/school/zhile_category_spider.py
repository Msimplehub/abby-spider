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


class ZhiLeCategorySpider(BaseSpider):

    __VIEWSTATE = "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BRNkaXF1Y2hlY2tib3hsaXN0JDEyBRNkaXF1Y2hlY2tib3hsaXN0JDEzBRNkaXF1Y2hlY2tib3hsaXN0JDE0BRNkaXF1Y2hlY2tib3hsaXN0JDE1BRNkaXF1Y2hlY2tib3hsaXN0JDE2BRNkaXF1Y2hlY2tib3hsaXN0JDE3BRNkaXF1Y2hlY2tib3hsaXN0JDE4BRNkaXF1Y2hlY2tib3hsaXN0JDE5BRNkaXF1Y2hlY2tib3hsaXN0JDIwBRNkaXF1Y2hlY2tib3hsaXN0JDIxBRNkaXF1Y2hlY2tib3hsaXN0JDIyBRNkaXF1Y2hlY2tib3hsaXN0JDIzBRNkaXF1Y2hlY2tib3hsaXN0JDI0BRNkaXF1Y2hlY2tib3hsaXN0JDI1BRNkaXF1Y2hlY2tib3hsaXN0JDI2BRNkaXF1Y2hlY2tib3hsaXN0JDI3BRNkaXF1Y2hlY2tib3hsaXN0JDI4BRNkaXF1Y2hlY2tib3hsaXN0JDI5BRNkaXF1Y2hlY2tib3hsaXN0JDMwBRNkaXF1Y2hlY2tib3hsaXN0JDMw7t+HdlI53MIrZX4/fnx6s/m7FIUfW9SYE+3m3zLteAY="

    __EVENTVALIDATION = "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"

    LAST__VIEWSTATE = ""
    LAST__EVENTVALIDATION= ""
    second = ""
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "ASP.NET_SessionId=slcrkrbxdmowfzc5hzlomlgr; Hm_lvt_10fdbfb351346526e18e6995afa7ee08=1698887627; yzmcode=6TV6;",
        "Host": "www.zhiliaojy.com",
        "Origin": "http://www.zhiliaojy.com",
        "Referer": "http://www.zhiliaojy.com/admin/newselect_school_center.aspx",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
    }

    def collect(self):
        db = self.getDb()
        sql = "select * from category"
        cursor = db.cursor()
        cursor.execute(sql)
        categorys = cursor.fetchall()
        for category in categorys:
            print("+++++查询类目条件：",category)
            self.get_data(category)

    def get_data(self, category):
        result = []
        for i in range(1, 100):
            list = self.get_main_table(i, category)
            if len(list) == 0:
                break
            result.append(list)

    def get_main_table(self, page, category):

        result = []
        select_page = "Button" + str(page + 3)

        body = {
            "__EVENTTARGET":"",
            "__EVENTARGUMENT":"",
            "__LASTFOCUS":"",
            "__VIEWSTATE":self.__VIEWSTATE,
            "__VIEWSTATEGENERATOR":"270566B4",
            "__EVENTVALIDATION":self.__EVENTVALIDATION,
            "diqucheckboxlist$0":"河北省","diqucheckboxlist$1":"山西省", "diqucheckboxlist$2":"内蒙古","diqucheckboxlist$3":"辽宁省","diqucheckboxlist$4":"吉林省",
            "diqucheckboxlist$5":"黑龙江省","diqucheckboxlist$6":"江苏省","diqucheckboxlist$7":"浙江省", "diqucheckboxlist$8":"安徽省","diqucheckboxlist$09":"福建省",
            "diqucheckboxlist$10":"江西省", "diqucheckboxlist$11":"山东省", "diqucheckboxlist$12":"河南省","diqucheckboxlist$13":"湖北省", "diqucheckboxlist$14":"湖南省",
            "diqucheckboxlist$15":"广东省","diqucheckboxlist$16":"广西", "diqucheckboxlist$17":"海南省","diqucheckboxlist$18":"四川省","diqucheckboxlist$19":"贵州省",
            "diqucheckboxlist$20":"云南省", "diqucheckboxlist$21":"西藏自治区", "diqucheckboxlist$22":"陕西省", "diqucheckboxlist$23":"甘肃省", "diqucheckboxlist$24":"青海省",
            "diqucheckboxlist$25":"宁夏", "diqucheckboxlist$26":"新疆","diqucheckboxlist$27":"北京市","diqucheckboxlist$28":"天津市","diqucheckboxlist$29":"上海市",
            "diqucheckboxlist$30":"重庆市",
            #"diqucheckboxlist$27":"北京市","diqucheckboxlist$6":"江苏省",  "diqucheckboxlist$15":"广东省","diqucheckboxlist$29":"上海市","diqucheckboxlist$7":"浙江省",
            "dropxueke":str(category[1]),
            "dropyiji": str(self.get_cate_num(category[2])),
            "droperji": str(self.get_cate_num(category[3])),
            "dropxxfs":category[4],
            "dropxuexiao":"院校不限",
            "dropeng":"外语科目不限",
            "dropzhuanyeyi":"专业课一不限",
            "dropzhuanyeer":"专业课二不限",
            "dropzuidi":"分数不限",
            "dropzuigao":"分数不限",
            "droppaixun":"分数降序",
            #"dropxuexiao": "苏州大学"
            #"Button1":"开始筛选学校"
            #select_page: 1
        }

        if self.second == "":
            self.second = str(self.get_cate_num(category[2]))

        if page > 4:
            body["Button8"] = ">>"
        elif page == 1:
            body["Button1"] = "开始筛选学校"
        else:
            body[select_page] = 1
            pass

        response = requests.post("http://www.zhiliaojy.com/admin/newselect_school_center.aspx",body,headers=self.headers,timeout=5)
        html = response.content
        soup = BeautifulSoup(html, "lxml")

        if self.second != str(self.get_cate_num(category[2])):
            self.second = str(self.get_cate_num(category[2]))
            print("------页面刷新-----------")

            #self.__VIEWSTATE = self.LAST__VIEWSTATE
            #self.__EVENTVALIDATION = self.LAST__EVENTVALIDATION

        table = soup.find('table', id='sample-table-4')
        if table is None:
            print("===table获取错误，报了运行错误=========")
            if page > 1:
                pass
            return result
        else:
            self.LAST__VIEWSTATE = soup.find("input", id="__VIEWSTATE").get("value")
            self.LAST__EVENTVALIDATION = soup.find("input", id="__EVENTVALIDATION").get("value")
            if self.second != str(self.get_cate_num(category[2])):
                self.__VIEWSTATE = self.LAST__VIEWSTATE
                self.__EVENTVALIDATION = self.LAST__EVENTVALIDATION
                pass
        trs = table.find("tbody").find_all('tr')
        if len(trs) == 0:
            return result

        for tr in trs:
            tds = tr.find_all("td")
            if len(tds) > 10:
                if tds[0].getText() == "24":
                    print()
                print([tds[0].getText(), tds[1].getText(), tds[2].getText(), tds[3].getText(), tds[4].getText(),
                       tds[5].getText(), tds[6].getText(), tds[7].getText(), tds[8].getText(), tds[9].getText(),
                       tds[10].getText()])
                result.append([tds[0].getText(), tds[1].getText(), tds[2].getText(), tds[3].getText(), tds[4].getText(),
                  tds[5].getText(), tds[6].getText(), tds[7].getText(), tds[8].getText(), tds[9].getText(),
                  tds[10].getText()])
                a = tr.find("a")
                if a is None:
                    continue
                onclick = a.get("onclick")
                detail_path = self.get_detail_path(onclick)
                # print(detail_path)
                #self.get_detail(detail_path)

        #self.__VIEWSTATE = __VIEWSTATE
        #self.__EVENTVALIDATION = __EVENTVALIDATION
        return result

    def get_detail_path(self, text):
        pattern = r"zxxiangqing\.aspx\?dataid=[^']+"
        match = re.search(pattern, text)
        if match:
            result = match.group()
            return result

    def start(self):
            self.collect()

    def getDb(self):
        connection = pymysql.connect(host='mysql-01.db.sit.ihomefnt.org',
                                     user='root',
                                     password='aijia1234567',
                                     db='tanko'
                                     )
        return connection

    def get_detail(self, detail_path):

        detail_page = 'http://www.zhiliaojy.com/admin/{0}'.format(detail_path)
        response = requests.get(detail_page, headers=self.headers, timeout=5)
        html = response.content
        soup = BeautifulSoup(html, "lxml")
        try:
            self.__VIEWSTATE = soup.find("input", id="__VIEWSTATE").get("value")
            self.__EVENTVALIDATION = soup.find("input", id="__EVENTVALIDATION").get("value")
        except Exception as e:
            pass
        table_luqu = soup.find("table", id="GridView6")
        result_luqu = []
        self.getGridView6(table_luqu, detail_path, result_luqu, 0)
        print("录取",result_luqu)
        result_fushi = []
        table_fushi = soup.find("table", id="GridView5")
        self.getGridView5(table_fushi, detail_path, result_fushi, 0)
        print("复试",result_fushi)
        table_tiaoji_fushi = soup.find("table", id="GridView3")
        result_tiaoji_fushi = []
        self.get_default_table(table_tiaoji_fushi, result_tiaoji_fushi)
        print("调剂复试",result_tiaoji_fushi)
        table_tiaoji_luqu = soup.find("table", id="GridView4")
        result_tiaoji_luqu  = []
        self.get_default_table(table_tiaoji_luqu, result_tiaoji_luqu)
        print("调剂录取",result_tiaoji_luqu)
        pass


    def getGridView5(self, table, detail_path, result_fushi, page):

        if table is None:
            return
        # 获取到第一页的数据
        self.get_table(table, result_fushi)
        # 判断是否存在下一页 且class不是aspNetDisabled
        next_page_button = table.find("a", id="GridView5_lbnNext")
        page_text = table.find("span", id="GridView5_lblPage")
        if next_page_button is not None:
            next_page_button_class = next_page_button.get("class")
            next_btn_href = next_page_button.get("href")
            page_text = page_text.getText()
            total_page = self.get_detail_total_page(page_text)
            page = page+1
            if page <= int(total_page):
                print(total_page, page)
                if next_btn_href is not None and next_page_button_class != "aspNetDisabled":
                    next_btn_href_path = self.get_detail_next_page_path(next_btn_href)
                    self.get_next_page_getGridView5(detail_path,next_btn_href_path,page, result_fushi)
                # 下一页请求
            else:
                return

    def getGridView6(self, table, detail_path, result_luqu, page):

        # 获取到第一页的数据
        self.get_table(table, result_luqu)
        # 判断是否存在下一页 且class不是aspNetDisabled
        next_page_button = table.find("a", id="GridView6_lbnNext")
        page_text = table.find("span", id="GridView6_lblPage")
        if next_page_button is not None:
            next_page_button_class = next_page_button.get("class")
            next_btn_href = next_page_button.get("href")
            page_text = page_text.getText()
            total_page = self.get_detail_total_page(page_text)
            page = page+1
            if page <= int(total_page):
                print(total_page, page)
                if next_btn_href is not None and next_page_button_class != "aspNetDisabled":
                    next_btn_href_path = self.get_detail_next_page_path(next_btn_href)
                    self.get_next_page_getGridView6(detail_path,next_btn_href_path,page, result_luqu)
                # 下一页请求
            else:
                return

    def get_next_page_getGridView6(self, detail_path, next_btn_href_path,page_num, result_luqu):

        detail_page = 'http://www.zhiliaojy.com/admin/{0}'.format(detail_path)
        body={
            "__EVENTTARGET": next_btn_href_path,
            "__EVENTARGUMENT":"",
            "__VIEWSTATE": self.__VIEWSTATE,
            "__VIEWSTATEGENERATOR": "60DA1A3B",
            "__EVENTVALIDATION": self.__EVENTVALIDATION,
            "GridView6$ctl25$inPageNum": page_num,
            "GridView5$ctl25$inPageNum":"",
        }
        response = requests.post(detail_page, body, headers=self.headers)
        html = response.content
        soup = BeautifulSoup(html, "lxml")
        try:
            self.__VIEWSTATE = soup.find("input", id="__VIEWSTATE").get("value")
            self.__EVENTVALIDATION = soup.find("input", id="__EVENTVALIDATION").get("value")
        except Exception as e:
            pass
        table_luqu = soup.find("table", id="GridView6")
        self.getGridView6(table_luqu, detail_path, result_luqu, page_num)

    def get_next_page_getGridView5(self, detail_path,next_btn_href_path, page_num, result_luqu):

        detail_page = 'http://www.zhiliaojy.com/admin/{0}'.format(detail_path)
        body={
            "__EVENTTARGET": next_btn_href_path,
            "__EVENTARGUMENT":"",
            "__VIEWSTATE": self.__VIEWSTATE,
            "__VIEWSTATEGENERATOR": "60DA1A3B",
            "__EVENTVALIDATION": self.__EVENTVALIDATION,
            "GridView6$ctl25$inPageNum": 1,
            "GridView5$ctl25$inPageNum":page_num,
        }
        response = requests.post(detail_page, body, headers=self.headers)
        html = response.content
        soup = BeautifulSoup(html, "lxml")
        try:
            self.__VIEWSTATE = soup.find("input", id="__VIEWSTATE").get("value")
            self.__EVENTVALIDATION = soup.find("input", id="__EVENTVALIDATION").get("value")
        except Exception as e:
            pass
        table_luqu = soup.find("table", id="GridView5")
        self.getGridView5(table_luqu, detail_path, result_luqu, page_num)

    def get_detail_next_page_path(self, next_btn_href):
        pattern = r"javascript:__doPostBack\('([^']+)'"
        match = re.search(pattern, next_btn_href)
        if match:
            result = match.group(1)
            return result

    def get_detail_total_page(self, total_page_text):
        pattern = r"共(\d+)页"
        match = re.search(pattern, total_page_text)
        if match:
            result = match.group(1)
            return result

    def get_cate_num(self, categoryName):
        pattern = '[a-zA-Z0-9]+'
        result = re.findall(pattern, categoryName)
        if result:
            return result[0]
        else:
            return None

    def get_table(self, table, results):
        if table is None:
            return results
        trs = table.find_all("tr", align="center")
        for tr in trs:
            tds = tr.find_all("td")
            if len(tds) == 1:
                continue
            td_content = []
            for td in tds:
                td_content.append(td.getText())
            try:
                results.append(td_content)
            except Exception as e:
                print("-----",tr)
        return results

    def get_default_table(self, table, results):
        trs = table.find_all("tr")
        for tr in trs:
            tds = tr.find_all("td")
            if len(tds) == 1:
                continue
            td_content = []
            for td in tds:
                td_content.append(td.getText())
            try:
                if len(td_content) == 0:
                    continue
                results.append(td_content)
            except Exception as e:
                print("-----",tr)
        return results

if __name__ == '__main__':
    spider = ZhiLeCategorySpider(SPIDER_NAME)
    spider.start()
    #print(spider.get_cate_num("(0101Z2)国学"))
    pass
