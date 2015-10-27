#!/usr/bin/env python
# encoding: utf-8

USAGE = """This is s special daemon used for checking whether the IP proxy works.
It can be managed by supervisor or some other tools, just make sure it works
all the time."""

import urllib
import urllib2
import httplib
import threading
import time
import sys
import os
import MySQLdb
from scrapy.conf import settings
from optparse import OptionParser
import Queue
from DBUtils.PooledDB import PooledDB

conn_pool = PooledDB(MySQLdb, 20, host=settings['MYSQL_HOST'], user=settings['MYSQL_USER'], passwd=settings['MYSQL_PASSWD'], db='ip_proxy', port=int(settings['MYSQL_PORT']))
src_db_queue = Queue.Queue()
dst_db_queue = Queue.Queue()


class IPPool(object):

    def __init__(self, src_path, dst_path, queue):
        self.queue = queue
        self.src_database = src_path
        self.dst_db = dst_path




    def check_one(self, handler, url):
        if self.queue.empty() :
            load_to_queue(self.src_database)
            if self.queue.empty():
                time.sleep(360)
                return

        res = self.queue.get()

        print "%s %s:%s, try to check" % (res[2], res[0],
                res[1])


        ret, delay = handler(str(res[0]), str(res[1]), str(res[2]), url)

        if ret:
            print "IP %s:%s delay:%s" % (res[0], res[1],delay)
            conn = conn_pool.connection()
            cursor = conn.cursor()
            sql_cmd = "insert into checked values (\"%s\",\"%s\",\"%s\",%s) on duplicate key update port=values(port), delay=values(delay)" % (res[0],res[1],res[2],delay)
            cursor.execute(sql_cmd)
            conn.commit()
            cursor.close()
            conn.close()
        else:
            sql_cmd = 'delete from %s where ip="%s"' % (self.dst_db, res[0])
            print sql_cmd
            conn = conn_pool.connection()
            cursor = conn.cursor()
            cursor.execute(sql_cmd)
            sql_cmd = 'delete from %s where ip="%s"' %(self.src_database, res[0])
            cursor.execute(sql_cmd)
            conn.commit()
            cursor.close()
            conn.close()



def proxy_test(ip, port='80', protocol='http', url='http://www.douban.com'):
    proxy_url = protocol + '://' + ip + ':' + port
    proxy_support = urllib2.ProxyHandler({'http':proxy_url})
    opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
    request = urllib2.Request(url)
    request.add_header("Accept-Language", "zh-cn")
    request.add_header("Content-Type", "text/html; charset=gb2312")
    request.add_header("User-Agent", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.1.4322)")

    trycount = 1
    while trycount <= 2:
        try:
            t1 = time.time()
            f = opener.open(request, timeout=5.0)
            data = f.read()
            t2 = time.time()
            if '豆瓣' in data:
                #  break
                return True, t2 - t1
            else:
                return False,None
        except:
            time.sleep(3)
            trycount = trycount + 1

    if trycount > 2:
        return False, None



class CheckTask(threading.Thread):
    def __init__(self, pool, handler, url):
        threading.Thread.__init__(self)
        self.pool = pool

        self.handler = handler
        self.url = url


    def run(self):
        while 1:
            self.pool.check_one(self.handler, url)


class ClickTask(threading.Thread):
    def __init__(self, pool, handler, url):
        threading.Thread.__init__(self)
        self.pool = pool
        self.handler = handler
        self.url = url


    def run(self):
        while 1:
            for res in self.pool.get_all_iter():
                self.handler(res["ip"], res["port"], res["protocol"], self.url)
                print "Click %s by %s" % (self.url, res["ip"])


def load_to_queue(path):

    connection = conn_pool.connection()
    cursor = connection.cursor()
    if path == "unchecked":
        sql_cmd = "select * from unchecked"
        queue = src_db_queue
    elif path  == "checked":
        sql_cmd = "select * from checked "
        queue = dst_db_queue
    cursor.execute(sql_cmd)
    proxy_list = cursor.fetchall()
    for proxy_ip in proxy_list:
        queue.put(proxy_ip)

    cursor.close()
    connection.close()




if __name__ == "__main__":
    load_to_queue('unchecked')
    load_to_queue('checked')
    pool1 = IPPool("unchecked", "checked", src_db_queue)
    pool2 = IPPool("checked", "checked", dst_db_queue)

    parser = OptionParser(usage=USAGE,
            version='0.0.1')

    parser.add_option("-n", "--number", dest="number",
            default='20', metavar='NUMBER',
            help="The number of threads used to scan.")

    parser.add_option("-u", "--url", dest="url",
            default='http://www.douban.com', metavar='URL',
            help="The url to used to scan.")

    parser.add_option("-c", "--click", dest="click",
            default=False, action="store_true",
            help="Click url by proxy IP")


    (options, args) = parser.parse_args()

    thread_number = int(options.number)
    print "Thread number is %d + %d" % (thread_number, 1)
    url = options.url

    if options.click:
        tasktype =ClickTask
    else:
        tasktype =CheckTask

    tasks = []

    for i in range(thread_number):
        tasks.append(tasktype(pool1, proxy_test, url))

    tasks.append(tasktype(pool2, proxy_test, url))

    for task in tasks:
        task.start()

    for task in tasks:
        task.join()


