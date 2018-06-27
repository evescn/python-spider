#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18-6-27 上午9:16
# @Author  : Evescn
# @Site    : 
# @File    : mongo.py
# @Software: PyCharm Community Edition
import csv
import pymongo
from config import *


class MongodbConn(object):

    def __init__(self):
        self.CONN = pymongo.MongoClient(MONGO_URL)

    def run(self):
        database = MONGO_DB
        db = self.CONN[database]
        # db.authenticate("username", "password")
        col = db[MONGB_TABLE]

        # query all document
        documents = col.find()
        for item in documents:
            csvFile3 = open(CSVFile, 'a', newline='')
            writer2 = csv.writer(csvFile3)
            writer2.writerow([item['公布期号'],item['公告日期'], item['公告类型'], item['注册号'], item['申请人'], item['商标名称'], item['图片地址']])
            csvFile3.close()


if __name__ == '__main__':
    mongo_obj = MongodbConn()
    mongo_obj.run()