#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-6-25 下午2:34
# @Author  : Evescn
# @Site    : 
# @File    : spider.py
# @Software: PyCharm Community Edition
import csv
import json

import pymongo
import requests
from multiprocessing import Pool
from requests.exceptions import RequestException
from pyquery import PyQuery as pq
from urllib.parse import urlencode
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
# db.authenticate("ACCOUNT", "PASSWORD")

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}


def get_page(url, offset):
    data = {
        'page': offset,
        'rows': '20',
        'annNum': AnnNum,
        'annType': 'TMSDGG',
        'totalYOrN': 'true'
    }


    url = url + urlencode(data)
    print(url)
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print(response.status_code)
            return None
    except RequestException:
        print("请求出错了")
        return None


def get_page_detail(html):
    result = json.loads(html)
    for item in result['rows']:
        ann_num = item['ann_num']
        ann_date = item['ann_date']
        ann_type = item['ann_type']
        reg_num = item['reg_num']
        reg_name = item['reg_name']
        tm_name = item['tm_name']
        image = get_image(item['page_no'])
        # print(image)

        yield {
            '公布期号': ann_num,
            '公告日期': ann_date,
            '公告类型': ann_type,
            '注册号': reg_num,
            '申请人': reg_name,
            '商标名称': tm_name,
            '图片地址': image
        }


def get_image(page_no):
    data = {
        'pageNum': page_no,
        'id': ImageID,
        'flag': 1
    }
    url = 'http://sbgg.saic.gov.cn:9080/tmann/annInfoView/imageView.html?' + urlencode(data)
    response = requests.get(url, headers=headers)

    if page_no < 4:
        num = page_no - 1
    else:
        num = 3

    if response.status_code == 200:
        image_dict = response.text
        image_dict = json.loads(image_dict)
        image_list = image_dict['imaglist']
        image = image_list[num]
        return image


def save_to_mongo(result):
    try:
        # if db[MONGB_TABLE].update({'注册号': result['注册号']}, {'$set': result}, True):
        #     print("更新数据库成功：", result['注册号'])
        if db[MONGB_TABLE].insert(result):
            print("保存到MongoDB数据库成功：", result)
        else:
            print("保存到MongoDB数据库失败", result)
    except Exception:
        print("出错了")


def main():
    url = 'http://sbgg.saic.gov.cn:9080/tmann/annInfoView/annSearchDG.html?'
    for i in range(GROUP_START, GROUP_END+1):
        print(i)
        html = get_page(url, i)
        if html:
            # print(html)
            data = get_page_detail(html)
            for item in data:
                # print(item)
                csvFile3 = open(CSVFile, 'a', newline='')
                writer2 = csv.writer(csvFile3)
                writer2.writerow([item['公布期号'],item['公告日期'], item['公告类型'], item['注册号'], item['申请人'], item['商标名称'], item['图片地址']])
                csvFile3.close()
                save_to_mongo(item)


if __name__ == '__main__':
    # groups = [x  for x in range(GROUP_START, GROUP_END+1)]
    # print(groups)
    # pool = Pool()
    # pool.map(main, groups)

    main()