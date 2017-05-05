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


class HizlialSpider(scrapy.Spider):
    name = "hizlial"
    allowed_domains = ["hizlial.com"]
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
    # 获取翻页的所有数据
        for pn in range(1, 5):
            url = 'http://www.hizlial.com/Arama.aspx?text=%s&sayfano=%s' % (value, pn)
            start_urls.append(url)
    db.close()

    # 获取每个商品列表的单个URL
    def parse(self, response):
        # 获取分页的所有商品链接
        urls = response.xpath('//*[contains(@class,"productList")]').extract()
        for url in urls:
            url_new = 'http://www.teknosa.com' + url
            print '>>new url: %s' % url_new
            yield Request(url_new, callback=self.parse_item)

    def parse_item(self, response):
        # 获得item
        item = TpLinkItem()
        # 模型名称
        item['model'] = response.xpath('//h1/text()').extract()[0].strip()
        # 模型缩略名
        item['platform'] = 'Hizlial'
        # 原始价格
        item['original_price'] = 0
        # 折扣价格，使用正则来匹配
        item['price'] = float(re.findall('price:(.*?)\r\s}', response.body)[0].strip())
        # 发货信息
        item['fast_delivery'] = ''
        # 配送信息
        item['free_shipping'] = response.xpath('//div[contains(@class,"note")]/span/text()')
        if len(item['free_shipping']) == 1:
            item['free_shipping'] = item['free_shipping'].extract_first().strip()
        else:
            item['free_shipping'] = ''
        # 供应商，自营则使用本身数据来代替即可，并且将其格式化为json字符串格式
        item['reseller'] = [
            {
                'seller': 'Teknosa',
                'url': 'http://www.teknosa.com',
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
