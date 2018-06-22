#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-6-22 下午4:58
# @Author  : Evescn
# @Site    : 
# @File    : spider.py
# @Software: PyCharm Community Edition
import time
from selenium import webdriver
import requests
from requests.exceptions import RequestException
import re

# browser = webdriver.Chrome()
# browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)
# wait = WebDriverWait(browser, 10)

# browser.set_window_size(1400, 900)

def get_index(url):
    try:
        # browser.get('http://music.163.com/#/discover/toplist?id=19723756')
        # time.sleep(8)
        response =requests.get(url)
        if response.status_code == 200:
        # pageSource = browser.page_source
        # print(pageSource)
        # browser.close()
        # return browser.page_source
            return response.text
        else:
            return None
    except RequestException:
        print("请求出错了")
        return None

def get_index_datail(html):
    pattern = re.compile('<tr.*?num">(.*?)</span.*?title="(.*?)">.*?dur ">(.*?)</span.*?title="(.*?)">.*?</tr>', re.S)
    items = re.findall(pattern, html)
    print(items)
    for item in items:
        print(type(item))
        print(item)

def main():
    url = 'https://music.163.com/#/discover/toplist?id=19723756'
    html = get_index(url)
    if html:
        print(html)
        # data = get_index_datail(html)

if __name__ == '__main__':
    main()

