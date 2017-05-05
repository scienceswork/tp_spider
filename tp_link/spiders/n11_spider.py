# -*- coding: utf-8 -*-
import scrapy
import hashlib
import json
import re
from tp_link.items import DmozItem
from tp_link.items import TpLinkItem
from scrapy.http import Request
import MySQLdb
import MySQLdb.cursors


class N11Spider(scrapy.Spider):
    name = "n11"
    allowed_domains = ["n11.com"]
    start_urls = []
    # 链接数据库
    db = MySQLdb.connect(
        "localhost",
        "root",
        "tplink123",
        "tp_app"
    )
    # 获得cursor
    cursor = db.cursor()
    # 执行sql语句
    num = cursor.execute('SELECT value FROM keyword')
    # 循环遍历得到结果
    info = cursor.fetchmany(num)
    for i in info:
        value = i[0]
        for pn in range(1, 2):
            url = 'http://www.n11.com/arama?q=%s&pg=%s' % (value, pn)
            start_urls.append(url)
    db.close()

    # 获取每个商品列表的单个URL
    def parse(self, response):
        # 获取分页的所有商品链接
        urls = response.xpath('//*[@class="plink"]/@href').extract()
        for url in urls:
            url_new = url
            print '>>new url: %s' % url_new
            yield Request(url_new, callback=self.parse_item)

    def parse_item(self, response):
        # 获得item
        item = TpLinkItem()
        # 模型名称
        item['model'] = response.xpath('//h1/text()').extract()[0].strip()
        # 模型缩略名
        item['platform'] = 'N11'
        # 原始价格
        item['original_price'] = 0
        # 折扣价格，使用正则来匹配
        item['price'] = float(response.xpath('//*[@id="productDisplayPrice"]/@value').extract_first().replace(',', '.'))
        # 发货信息
        item['fast_delivery'] = response.xpath('//*[@class="cargoTime"]/text()')
        if len(item['fast_delivery']) == 1:
            item['fast_delivery'] = item['fast_delivery'].extract_first().strip()
        else:
            item['fast_delivery'] = ''
        # 配送信息
        item['free_shipping'] = response.xpath('//span[contains(@class,"cargoType freeShipment")]/text()')
        if len(item['free_shipping']) == 1:
            item['free_shipping'] = item['free_shipping'].extract_first().strip(' :').strip()
        else:
            item['free_shipping'] = ''
        # 供应商
        seller = response.xpath('//div[@class="sallerTop"]/h3/a/text()').extract_first().strip()
        url = response.xpath('//div[@class="sallerTop"]/h3/a/@href').extract_first().strip()
        item['reseller'] = [
            {
                'seller': seller,
                'url': url,
                'fast_delivery': item['fast_delivery']
            }
        ]
        item['reseller'] = json.dumps(item['reseller'])
        print item['reseller']
        # 采集的URL
        item['url'] = str(response.url)
        # md5码
        md5 = hashlib.md5()
        md5.update(item['url'])
        item['md5'] = md5.hexdigest()
        # for sel in response.xpath('//a'):
        #     item = DmozItem()
        #     item['model'] = 'model'
        #     item['reseller'] = 'reseller'
        #     item['original_price'] = 'original_price'
        #     item['price'] = 'price'
        yield item
