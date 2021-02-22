# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
from haodaifu.items import Hos_info_Item, Doc_info_Item, Vote_info_Item

class HaodaifuPipeline(object):
    def process_item(self, item, spider):
        return item


class MongoPipeline(object):
    def __init__(self):
        # 获取数据库参数
        host = "localhost"
        port = 27017
        dbname = 'haodaifu'
        # 表名
        colname1 = 'hospital_info'

        colname2 = 'doctor_person_info'

        colname3 = 'doctor_vote_info'

        colname4 = 'doctor_article_info'

        colname5 = 'doctor_inquiry_info'

        # 连接数据库
        self.client = MongoClient(host, port)

        # 选择数据库
        self.db = self.client[dbname]

        # 选择集合
        self.col1 = self.db[colname1]
        self.col2 = self.db[colname2]
        self.col3 = self.db[colname3]
        self.col4 = self.db[colname4]
        self.col5 = self.db[colname5]

    def process_item(self, item, spider):
        if 'city' in item:
            data1 = dict(item)

            self.col1.insert(data1)

        if 'score' in item:
            data2 = dict(item)

            self.col2.insert(data2)

        if 'purpose' in item:
            data3 = dict(item)

            self.col3.insert(data3)

        if 'pageview' in item:
            data4 = dict(item)

            self.col4.insert(data4)

        if 'title' in item:
            data5 = dict(item)

            self.col4.insert(data5)

        return item

    def __del__(self):
        # 关闭数据库链接
        self.client.close()

