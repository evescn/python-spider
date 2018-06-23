#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-6-22 下午4:58
# @Author  : Evescn
# @Site    : 
# @File    : spider.py
# @Software: PyCharm Community Edition
import time

import requests
import pymongo
from requests.exceptions import RequestException
from bs4 import BeautifulSoup as bs
from pyquery import PyQuery as pq
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import *


# browser = webdriver.Chrome()
browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)
wait = WebDriverWait(browser, 10)
browser.set_window_size(1400, 900)

client = pymongo.MongoClient('localhost')
db = client['QQ']

def get_index(url):
    try:
        browser.get(url)
        time.sleep(3)
        pageSource = browser.page_source
        data = get_index_datail(pageSource)
        for item in data:
            print(item)
            url = item['url']
            table_name = item['table_name']
            get_page(url, table_name)
        browser.close()

    except RequestException:
        print("请求出错了")
        return None

def get_index_datail(html):
    pqObj = pq(html)
    response = pqObj('.main .toplist_nav .toplist_nav__list dd').items()
    # print(response.text)
    for item in response:
        url = item('.toplist_nav__item a')
        yield {
            'url': url.attr.href,
            'table_name': url.text()
        }


def get_page(url, table_name):
    try:
        browser.get(url)
        time.sleep(5)
        pageSource = browser.page_source
        data = get_page_datail(pageSource)
        for item in data:
            print(item)
            save_to_mongo(table_name, item)

        # browser.close()
        return None
    except RequestException:
        print("请求出错了")
        return None


def get_page_datail(html):
    pqObj = pq(html)
    listItems = pqObj('.mod_songlist .songlist__list li').items()
    for item in listItems:
        rankeNum = item('.songlist__number').text()
        artist = item('.songlist__artist').text()
        Time = item('.songlist__time').text()
        item1 = item('.songlist__songname .songlist__songname_txt .js_song')
        Commit = item1('.songlist__song_txt')
        Name = item1('.songlist__song_txt').remove()

        yield {
            'paimeng': rankeNum,
            'name': Name._parent.text(),
            'commit': Commit.text(),
            'author': artist,
            'time': Time
        }


def save_to_mongo(table_name, result):
    try:
        if db[table_name].update({'name': result['name']}, {'$set': result}, True):
            print("更新数据库成功：", result['name'])
        elif db[table_name].insert(result):
            print("保存到MongoDB数据库成功：", result)
        else:
            print("保存到MongoDB数据库失败", result)
    except Exception:
        print("出错了")

    # if db[KUAI_ZHUANWANG].update({'compnyID':paramter['compnyID']},{'$set':paramter},True):
    #     print('Saved to Mongo', paramter['compnyID'])
    # else:
    #     print('Saved to Mongo Failed',paramter['compnyID'])
    # pass


def main():
    url = 'https://y.qq.com/n/yqq/toplist/4.html'
    html = get_index(url)
    if html:
        print(html)
        # data = get_index_datail(html)

if __name__ == '__main__':
    main()

