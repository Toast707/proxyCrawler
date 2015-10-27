# -*- coding: utf-8 -*-
import MySQLdb
import time
from scrapy.conf import settings
# Define your item pipelines here

#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ProxycrawlerPipeline(object):
    def __init__(self):
        """TODO: link to mysql and create databases
        :returns: null

        """
        self.connection = MySQLdb.connect(host=settings['MYSQL_HOST'], user=settings['MYSQL_USER'], passwd=settings['MYSQL_PASSWD'], port=int(settings['MYSQL_PORT']))
        self.cursor = self.connection.cursor()
        self.cursor.execute('create database if not exists ip_proxy Character Set UTF8')
        self.connection.select_db('ip_proxy')
        self.cursor.execute('create table if not exists checked(ip VarChar(15) primary key,port SmallInt,protocol Char(20))')
        self.cursor.execute('create table if not exists unchecked(ip VarChar(15) primary key, port SmallInt, protocol Char(20), delay SmallInt)')

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        self.cursor.execute('select 1 from ip_proxy.unchecked where ip="{}" limit 1'.format(item['ip']))
        flag = self.cursor.fetchall()
        if len(flag) == 0 :
            new_proxy = [item['ip'], item['port'], item['protocol']]
            self.cursor.execute('insert into ip_proxy.unchecked values(%s, %s, %s)', new_proxy)
            self.connection.commit()
        return item
