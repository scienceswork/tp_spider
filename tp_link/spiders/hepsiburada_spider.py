# -*- coding: utf-8 -*-
import scrapy
import hashlib
from tp_link.items import DmozItem
from tp_link.items import TpLinkItem
from scrapy.http import Request


class HepsiburadaSpider(scrapy.Spider):
    name = "hepsiburada"
    allowed_domains = ["hepsiburada.com"]
    start_urls = []
    # 获取翻页的所有数据
    for pn in range(1, 2):
        url = 'http://www.hepsiburada.com/tplink?sayfa=%s' % pn
        start_urls.append(url)

    # 获取每个商品列表的单个URL
    def parse(self, response):
        # 获取分页的所有商品链接
        urls = response.xpath('//li[contains(@class,"search-item")]/div/a/@href').extract()
        for url in urls:
            url_new = 'http://www.hepsiburada.com' + url
            print '>>new url: %s' % url_new
            yield Request(url_new, callback=self.parse_item)

    def parse_item(self, response):
        # 获得item
        item = TpLinkItem()
        # 模型名称
        item['model'] = response.xpath('//*[@id="product-name"]/text()').extract()[0].strip()
        # 模型缩略名
        item['platform'] = 'Hepsiburada'
        # 原始价格
        item['original_price'] = response.xpath('//*[@id="originalPrice"]/text()')\
            .extract_first()\
            .strip('TL')\
            .strip()\
            .replace(',', '.')
        item['original_price'] = float(item['original_price'])
        # 折扣价格，需要进行处理
        item['price'] = response.xpath('//*[@id="offering-price"]/span[1]/text()').extract_first() + '.' + response.xpath(
            '//*[@id="offering-price"]/span[2]/text()').extract_first()
        if len(item['price']) > 1:
            item['price'] = float(item['price'])
        else:
            item['price'] = 0
        # 发货信息
        item['fast_delivery'] = ''
        # 配送信息
        item['free_shipping'] = ''
        # 供应商，需要进行字段处理
        # item['reseller'] = [
        #     {
        #         'seller': 'Hepsiburada',
        #         'url': 'http://hepsiburada.com',
        #         'fast_delivery': item['fast_delivery']
        #     }
        # ]
        # item['reseller'] = str(item['reseller'])
        item['reseller'] = ''
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
