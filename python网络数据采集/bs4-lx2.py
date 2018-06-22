#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-6-22 下午3:07
# @Author  : Evescn
# @Site    : 
# @File    : bs4-lx2.py
# @Software: PyCharm Community Edition

from urllib.request import urlopen
from bs4 import BeautifulSoup as bs

html = urlopen("http://pythonscraping.com/pages/warandpeace.html")
bsObj = bs(html.read(), "lxml")

nameList = bsObj.findAll("span", {"class": "green"})
# print(nameList)
# print(type(nameList))
for name in nameList:
    # print(name)
    # print(type(name))
    print(name.get_text())

# nameList = bsObj.findAll("span", {"class": "red"})
# for name in nameList:
#     print(name.get_text())

allText = bsObj.findAll(id="text")
print(allText[0].get_text())
