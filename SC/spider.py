#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-6-27 上午10:07
# @Author  : Evescn
# @Site    : 
# @File    : spider.py
# @Software: PyCharm Community Edition
import json
import re

import execjs
import pymongo
import requests
from urllib.parse import urlencode

import time
from config import *
import csv
import os

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
# db.authenticate(ACCOUNT, PASSWORD, MONGO_DB)

Cookie_set = '__jsluid=bed83703dc4fb2be0fed22377b0fa9d5; UM_distinctid=1643ef49916727-0e3f0dc1b388dc-3a760e5d-1fa400-1643ef49917aa0'

caculat = '''
var endAllJSStr = "";
while (z++) try {
    endAllJSStr = y.replace(/\\b\w+\\b/g, function (y) {
        return x[f(y, z) - 1] || ("_" + y)
    });
    break
} catch (_) {
    return "00"
}
return endAllJSStr
'''

proxies = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}


class MongodbConn(object):

    def __init__(self):
        self.CONN = pymongo.MongoClient(MONGO_URL)

    def run(self):
        database = MONGO_DB
        db = self.CONN[database]
        # db.authenticate(ACCOUNT, PASSWORD, MONGO_DB)
        col = db[MONGB_TABLE]

        # query all document
        documents = col.find()

        csv_file = 'data/' + CSVFile
        if os.path.exists(csv_file):
            os.remove(csv_file)
        for item in documents:
            csvFile3 = open(csv_file, 'a', newline='')
            writer2 = csv.writer(csvFile3)
            writer2.writerow([item['noticeId'],item['noticeTitle'],item['judAuth_CN'], item['noticeContent']])
            csvFile3.close()


def get_index(url, draw_num):
    global Cookie_set
    i = 10
    data = {
        'draw': draw_num,
        'start': (draw_num-1)*10,
        'length': '10'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Cookie': Cookie_set
    }

    print("获取html页面...")
    response = requests.post(url, data=data, headers=headers)
    while response.status_code == 521:
        print("获取cookie...")
        # 获取521页面，解析cookie值
        html = response.text
        p = re.compile('<script>(.*?)</script>', re.S)
        data = re.findall(p, html)
        jsStr = data[0]

        #判断多次521
        if i == 0:
            time.sleep(10)

        p = re.compile('(.*)while.*?')
        data = re.findall(p, str(jsStr))

        #添加新的尾部
        caculat_str = data[0] + str(caculat)

        #调用解析js文件函数
        data = creatjsfunction(caculat_str)
        print("data:", data)

        #循环判断是否获取到数据
        while data == '':
            time.sleep(1)
            data = creatjsfunction(caculat_str)
            print("while-data:", data)

        Cookie_set = Cookie_set + '; ' + data
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'Cookie': Cookie_set
        }

        response = requests.post(url, data=data, headers=headers)
        i -= 1

    if response.status_code == 200:
        return response.text
    else:
        return None


def creatjsfunction(js):
    print("解析js文件...")

    # 解析js文件
    jsfunc = "function testFunc(){%s}" % (str(js))
    ctx = execjs.compile(jsfunc)
    searchKey = ctx.call("testFunc")

    # 提取__jsl_clearance字符串 以及新的js代码
    p1 = re.compile("document.cookie='(.*?)'+", re.S)
    data_1 = re.findall(p1, searchKey)

    try:
        p2 = re.compile('.*__jsl_clearance=(.*?)+\(function\(\)(.*?)\)\(\)', re.S)
        searchKey = re.findall(p2, searchKey)
        print("获取cookie...")
        data_2 = searchKey[0][1]
        # print(data_2)

        # 提取cookie __jsl_clearance 中|后面字符串
        jsfunc1 = "function testFunc2()%s" % (str(data_2))
        ctx = execjs.compile(jsfunc1)
        data_3 = ctx.call("testFunc2")
    except Exception as e:
        print('获取cookie错误')
        return None
    cookie = data_1[0] + data_3
    print(cookie)
    return cookie


def get_index_detail(html):
    print("抓取异常信息...")

    result = json.loads(html)
    for item in result['data']:
        noticeTitle = item['noticeTitle']
        judAuth_CN = item['judAuth_CN']
        noticeContent = item['noticeContent']
        noticeId = item['noticeId']

        yield {
            'noticeId': noticeId,
            'noticeTitle': noticeTitle,
            'judAuth_CN': judAuth_CN,
            'noticeContent': noticeContent
        }


def save_to_mongo(result):
    try:
        if db[MONGB_TABLE].update({'noticeId': result['noticeId']}, {'$set': result}, True):
            print("更新数据库成功：", result['noticeId'])
        elif db[MONGB_TABLE].insert(result):
            print("保存到MongoDB数据库成功：", result)
        else:
            print("保存到MongoDB数据库失败", result)
    except Exception:
        print("出错了")


def main():
    url = 'http://sc.gsxt.gov.cn/affiche-query-area-info-paperall.html?noticeType=11&areaid=510000&noticeTitle=&regOrg=510100'
    for draw_num in range(DRAW_START, DRAW_END+1):
        html = get_index(url, draw_num)
        print(html)
        if html:
            data = get_index_detail(html)
            for item in data:
                # print(item)
                save_to_mongo(item)


if __name__ == '__main__':
    main()
    mongo_obj = MongodbConn()
    mongo_obj.run()