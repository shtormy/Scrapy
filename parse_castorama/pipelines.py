# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
# useful for handling different item types with a single interface

from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from pymongo import errors
import os
from urllib.parse import urlparse


class ParseCastoramaPipeline:
    def __init__(self):
        client = MongoClient('localhost:27017')
        self.mongodb = client.castorama

    def process_item(self, item, spider):
        collection = self.mongodb[spider.name]
        try:
            collection.insert_one(item)
        except errors.DuplicateKeyError:
            pass
        return item


class AdsPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item.get('photos'):
            item['photos'] = ['https://www.castorama.ru' + itm for itm in item['photos']]
            for img in item.get('photos'):
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    # def file_path(self, request, response=None, info=None, *, item=None):
    #     return str(item['_id']) + '/' + os.path.basename(urlparse(request.url).path)

    # def file_path(self, request, response=None, info=None, *, item=None):
    #     return {'item["photos"]': os.path.basename(urlparse(request.url).path)}

    # def file_path(self, request, response=None, info=None, *, item=None):
    #     fold = f"{item.get('_id')}/"
    #     return fold + super().file_path(request, response=response, info=info, item=item)