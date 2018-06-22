#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-6-22 下午3:28
# @Author  : Evescn
# @Site    : 
# @File    : spider.py
# @Software: PyCharm Community Edition
import re
import requests
from requests.exceptions import RequestException
import pymongo

client = pymongo.MongoClient('localhost')
db = client['KG']


def get_index_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        print("请求页面出错")
        return None


def get_index_page_detail(html):
    pattern = re.compile('<li>.*?title="(.*?)".*?href="(.*?)".*?</li>', re.S)
    url = re.findall(pattern, html)
    return url

def get_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        print("请求页面出错")
        return None


def get_page_detail(html):
    pattern = re.compile('<li.*?title="(.*?)".*?index="(.*?)"')
    results = re.findall(pattern, html)

    for item in results:
        author, name = item[0].split('-', 1)
        name = name[1:]
        paiming = int(item[1])+1

        yield {
            "作者": author,
            "歌名": name,
            "排名": paiming
        }

def save_to_mongo(table_name, result):
    try:
        if db[table_name].insert(result):
            print("保存到MongoDB数据库成功：", result)
        else:
            print("保存到MongoDB数据库失败", result)
    except Exception:
        print("出错了")

def main():
    url = 'http://www.kugou.com/yy/html/rank.html'
    html = get_index_page(url)
    # print(html)
    if html:
        data = get_index_page_detail(html)
        for item in data:
            table_name = item[0]
            url = item[1]
            html = get_page(url)
            if html:
                data = get_page_detail(html)
                if data:
                    for item in data:
                        # print(item)
                        save_to_mongo(table_name, item)

if __name__ == '__main__':
    main()
