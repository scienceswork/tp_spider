# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TpLinkItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # pass
    # 定义采集的字段
    model = scrapy.Field()  # 商品名称
    platform = scrapy.Field()  # 平台名称
    original_price = scrapy.Field()  # 原始价格
    price = scrapy.Field()  # 折扣价格
    reseller = scrapy.Field()  # 销售网站
    in_stock = scrapy.Field()  # 库存
    fast_delivery = scrapy.Field()  # 未知字段
    free_shipping = scrapy.Field()  # 未知字段
    created_at = scrapy.Field()  # 采集时间
    url = scrapy.Field()  # 采集的URL
    md5 = scrapy.Field()  # md5加密


class DmozItem(scrapy.Item):
    model = scrapy.Field()
    reseller = scrapy.Field()
    original_price = scrapy.Field()
    price = scrapy.Field()
