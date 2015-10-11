# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ReviewPipeline(object):
    def process_item(self, item, spider):
        #if spider.name == 'scrapy_spider_reviews':#not working
           item.save()
           return item
'''
class RecursivePipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'scrapy_spider_recursive':
           item.save()
           return item
'''