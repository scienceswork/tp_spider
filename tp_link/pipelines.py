# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
from  twisted.enterprise import adbapi
from scrapy import log
import MySQLdb
import MySQLdb.cursors


class TpLinkPipeline(object):
    def process_item(self, item, spider):
        return item


class MySQLStoreTpLinkPipeline(object):
    # 构造函数
    def __init__(self, db_pool):
        self.db_pool = db_pool
        self.db = MySQLdb.connect(
            "localhost",
            "root",
            "tplink123",
            "tp_app"
        )
        self.cursor = self.db.cursor()
        self.cursor.execute('set names utf8')
        self.db.commit()

    @classmethod
    def from_settings(cls, settings):
        # 数据库参数
        db_args = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DB'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset=settings['MYSQL_CHARSET'],
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        # 建立数据库连接池
        db_pool = adbapi.ConnectionPool('MySQLdb', **db_args)
        # 返回连接池
        return cls(db_pool)

    def spider_closed(self, spider):
        self.db.close()
        self.db_pool.close()

    # 默认调用的pipeline
    def process_item(self, item, spider):
        # 调用插入的方法
        query = self.db_pool.runInteraction(self._conditional_insert, item)
        # 调用异常处理方法
        query.addErrback(self._handle_error)
        # 返回item
        return item

    # 写入数据库中
    def _conditional_insert(self, tx, item):
        # 先查询数据映射表中是否有该数据，没有则插入
        select_sql = "SELECT * FROM product WHERE url='%s'" % item['url']
        # 执行sql语句
        tx.execute(select_sql)
        # 查询得到结果，结果为tuple类型
        model = tx.fetchall()
        print len(model)
        # 判断表中是否有数据
        if len(model) == 1:
            # product，得到该id
            id = model[0]['id']
            # 首先先更新数据
            update_sql = "UPDATE product SET name='%s', num=num+1 WHERE id=%s" % (item['model'], id)
            # 执行更新语句，更新内容，名字，采集次数，更新时间
            tx.execute(update_sql)
            # 查找平台的id
            platform_select_sql = "SELECT * FROM platform WHERE name='%s'" % item['platform']
            tx.execute(platform_select_sql)
            platform = tx.fetchall()
            # 插入product_info数据
            insert_sql = "INSERT INTO product_info (product_id, platform_id, price, " \
                         "in_stock, num, fast_delivery, free_shipping, reseller)" \
                         "values (%s, %s, %s, %s, %s, '%s', '%s', '%s')" % (
                             id, platform[0]['id'], item['price'], 0,
                             model[0]['num'] + 1, item['fast_delivery'],
                             item['free_shipping'], item['reseller']
                         )
            # 插入到model_info表
            tx.execute(insert_sql)
            pass
        else:
            # model表里没有该记录，重新插入该数据
            model_insert_sql = "INSERT INTO product (name, md5, url) " \
                               "VALUES('%s', '%s', '%s')" % (
                                   item['model'],
                                   item['md5'],
                                   item['url']
                               )
            self.cursor.execute(model_insert_sql)
            self.db.commit()
            # 查找到该条数据，插入到model_info表
            select_sql = "SELECT * FROM product WHERE url='%s'" % item['url']
            self.cursor.execute(select_sql)
            self.db.commit()
            model = self.cursor.fetchall()
            print model[0][0]
            # 查找平台的id
            platform_select_sql = "SELECT * FROM platform WHERE name='%s'" % item['platform']
            tx.execute(platform_select_sql)
            platform = tx.fetchall()
            insert_sql = "INSERT INTO product_info (product_id, platform_id, price, " \
                         "in_stock, num, fast_delivery, free_shipping, reseller)" \
                         "VALUES (%s, %s, %s, %s, %s, '%s', '%s', '%s')" % (
                             model[0][0], platform[0]['id'], item['price'], 0,
                             1, item['fast_delivery'], item['free_shipping'],
                             item['reseller']
                         )
            tx.execute(insert_sql)
            pass

    # 异常处理
    def _handle_error(self, e):
        log.err(e)
