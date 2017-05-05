# -*- coding: utf-8 -*-
import MySQLdb
import csv

'''
基础数据填充，如：平台，搜索词
'''

# 链接数据库
db = MySQLdb.connect(
    "localhost",
    "homestead",
    "secret",
    "spider"
)
# 获得游标
cursor = db.cursor()
# 填充平台数据
args = ["Hepsiburada", "N11", "Gittigidiyor", "Mediamarkt", "Teknosa",
        "Bimeks", "Incehesap", "Webdenal", "Istanbulbilisim", "Hizlial"]
for arg in args:
    # 批量填充
    platform_insert_sql = "INSERT INTO platform (name) VALUES ('%s');" % arg
    print platform_insert_sql
    cursor.execute(platform_insert_sql)
# 填充搜索关键字
csvfile = file('keyword.csv', 'rb')
reader = csv.reader(csvfile)
for line in reader:
    # 批量填充
    keyword_insert_sql = "INSERT INTO keyword (value) values('%s')" % line[0]
    print keyword_insert_sql
    cursor.execute(keyword_insert_sql)

csvfile.close()
cursor.close()
db.commit()
db.close()
csvfile.close()
