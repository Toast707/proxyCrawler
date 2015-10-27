# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from bs4 import BeautifulSoup
import re

from proxyCrawler.items import ProxycrawlerItem


REG_IP = re.compile(r'((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))[^\d]*((\d){1,5})', re.M)


class ProxySpider(CrawlSpider):
    name = 'Proxy'
    start_urls = [
        r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy",
        r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy&pn=10",
        r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy&pn=20",
        r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy&pn=30",
        r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy&pn=40",
        r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy&pn=50",
        r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy&pn=60",
        r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy&pn=70",
        r"http://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=ip%20proxy&pn=80",
        r"http://cn.bing.com/search?q=ip%20proxy&qs=n&pq=ip%20hproxy"
        r"http://cn.bing.com/search?q=ip%20proxy&qs=n&pq=ip%20hproxy&first=10"
        r"http://cn.bing.com/search?q=ip%20proxy&qs=n&pq=ip%20hproxy&first=20"
        r"http://cn.bing.com/search?q=ip%20proxy&qs=n&pq=ip%20hproxy&first=30"
        r"http://cn.bing.com/search?q=ip%20proxy&qs=n&pq=ip%20hproxy&first=40"
        r"http://cn.bing.com/search?q=ip%20proxy&qs=n&pq=ip%20hproxy&first=50"
        r"http://cn.bing.com/search?q=ip%20proxy&qs=n&pq=ip%20hproxy&first=60"
        r"http://cn.bing.com/search?q=ip%20proxy&qs=n&pq=ip%20hproxy&first=70"
    ]
    rules = (
        Rule(LinkExtractor(allow=r''), callback='parse_item'),
    )

    def parse_item(self, response):
        soup = BeautifulSoup(response.body)
        str_list = [tag.string or '' for tag in soup.find_all(True)]
        body_str = ' '.join(str_list)
        items = [ProxycrawlerItem(ip=group[0], port=group[7], protocol='HTTP') for group in re.findall(REG_IP, body_str)]
        #  from scrapy.shell import inspect_response
        #  inspect_response(response, self)
        return items
