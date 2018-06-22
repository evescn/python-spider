#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-6-22 下午2:49
# @Author  : Evescn
# @Site    : 
# @File    : bs4-lx.py
# @Software: PyCharm Community Edition

from urllib.request import urlopen
from bs4 import BeautifulSoup as bs

html = urlopen("http://pythonscraping.com/pages/page1.html")
bsObj = bs(html.read(), "lxml")
print(bsObj.text)
print(bsObj.h1)