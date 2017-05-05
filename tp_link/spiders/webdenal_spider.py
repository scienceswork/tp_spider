# -*- coding: utf-8 -*-
import scrapy
import json
import hashlib
from tp_link.items import DmozItem
from tp_link.items import TpLinkItem
from scrapy.http import Request
import MySQLdb
import MySQLdb.cursors


class WebdenalSpider(scrapy.Spider):
    handle_httpstatus_list = [301, 302, 204, 206, 404, 500]
    name = "webdenal"
    allowed_domains = ["webdenal.com"]
    start_urls = []
    # 链接数据库
    db = MySQLdb.connect(
        "localhost",
        "homestead",
        "secret",
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
            url = 'https://www.webdenal.com/arama.jsp?p=%s&myquerycat1=%s' % (pn, value)
            start_urls.append(url)
    db.close()

    # 获取每个商品列表的单个URL
    def parse(self, response):
        # 获取分页的所有商品链接
        urls = response.xpath('//div[contains(@class,"product")]/a[1]/@href').extract()
        for url in urls:
            url_new = 'http://www.webdenal.com' + url
            print '>>new url: %s' % url_new
            yield Request(url_new, callback=self.parse_item)

    def parse_item(self, response):
        # 获得item
        item = TpLinkItem()
        # 模型名称
        item['model'] = response.xpath('//h1/text()').extract()[0].strip()
        # 模型缩略名
        item['platform'] = 'Webdenal'
        # 折扣价格，需要进行处理
        print response.xpath('//meta/@content')
        item['price'] = response.xpath('//meta[contains(@property, "amount")]/@content').extract()[0].strip()
        # 供应商，需要进行字段处理
        item['reseller'] = 'Webdenal'
        # 发货信息，需要判断发货信息存不存在，不存在则设置为空
        item['fast_delivery'] = response.xpath('//span[contains(@class, "hizlikargo")]/strong/text()')
        if len(item['fast_delivery']) == 1:
            item['fast_delivery'] = item['fast_delivery'].extract_first().strip()
        else:
            item['fast_delivery'] = ''
        # 配送信息，需要判断配送信息存不存在，不存在则设置为空
        item['free_shipping'] = response.xpath('//span[contains(@class, "shipping")]/text()')
        if len(item['free_shipping']) == 1:
            item['free_shipping'] = item['free_shipping'].extract_first().strip()
        else:
            item['free_shipping'] = ''
        # 供应商，自营则使用本身数据来代替即可，并且将其格式化为json字符串格式
        item['reseller'] = [
            {
                'seller': 'Istanbulbilisim',
                'url': 'http://www.istanbulbilisim.com.tr',
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
