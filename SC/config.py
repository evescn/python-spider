#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-6-27 下午3:41
# @Author  : Evescn
# @Site    : 
# @File    : config.py
# @Software: PyCharm Community Edition

import datetime
#页面信息
DRAW_START=1
DRAW_END=5

Name = '成都-经营异常名录公告-' + str(datetime.date.today())
CSVFile=Name + '.csv'


MongoDB数据信息
MONGO_URL = 'localhost'
MONGO_DB = 'SC-经营异常'
MONGB_TABLE = CSVFile
ACCOUNT = ''
PASSWORD = ''

