#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-6-27 上午10:07
# @Author  : Evescn
# @Site    : 
# @File    : spider.py
# @Software: PyCharm Community Edition
import json
import pymongo
import requests
from urllib.parse import urlencode
from config import *
import csv
import os

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
db.authenticate(ACCOUNT, PASSWORD, MONGO_DB)

headers1 = {
    'Host': 'sc.gsxt.gov.cn',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'http://sc.gsxt.gov.cn/corp-query-entprise-info-xxgg-510000.html',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': '__jsluid=8560e8ac2a67615979b4ac053c5f3d5d; UM_distinctid=1643f3a48f661f-0bad67ff17215c8-32634646-1fa400-1643f3a48f756f; CNZZDATA1261033118=1536604988-1530068933-http%253A%252F%252Fsc.gsxt.gov.cn%252F%7C1530085133; __jsl_clearance=1530089443.272|0|hvg%2Bt4GxNtAR6p3T%2FwAHLDPMMyM%3D; SECTOKEN=7101454758092474687; JSESSIONID=C0A38961FF061AB2B5F6720AFAF62891-n2:2; tlb_cookie=S172.16.12.69',
    'Connection': 'keep-alive'
}

headers2 = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Cookie': '__jsluid=bed83703dc4fb2be0fed22377b0fa9d5; SECTOKEN=7098392206164886255; tlb_cookie=S172.16.12.42; UM_distinctid=1643ef49916727-0e3f0dc1b388dc-3a760e5d-1fa400-1643ef49917aa0; CNZZDATA1261033118=1965307862-1530063533-http%253A%252F%252Fsc.gsxt.gov.cn%252F%7C1530079733; __jsl_clearance=1530084311.786|0|edZwMKgIeEQ80hySzqxhZPne%2FDY%3D; JSESSIONID=0737C887F73DAF929119A266B14A5459-n1:34'

}

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
        db.authenticate(ACCOUNT, PASSWORD, MONGO_DB)
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
    data = {
        'draw': draw_num,
        'start': (draw_num-1)*10,
        'length': '10'
    }
    print(data)
    response = requests.post(url, data=data, headers=headers2, proxies=proxies)
    while response.status_code == 521:
        response = requests.post(url, data=data, headers=headers1)
        print(response.status_code)

    if response.status_code == 200:
        print(response.status_code)
        return response.text
    else:
        return None

def get_index_detail(html):
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