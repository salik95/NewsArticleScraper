# pipelines.py

import logging
import pymongo
import pytz


class NewsterPipeline(object):

	collection_name = 'nice_collection'
	def __init__(self, mongo_uri, mongo_db ,mongo_port, mongo_user, mongo_password):
		self.mongo_uri = mongo_uri
		self.mongo_db = mongo_db
		self.mongo_port = mongo_port
		self.mongo_user = mongo_user
		self.mongo_password = mongo_password


	@classmethod
	def from_crawler(cls, crawler):
		## pull in information from settings.py
		return cls(
			mongo_uri=crawler.settings.get('MONGO_URI'),
			mongo_db= crawler.settings.get('MONGO_DATABASE'),
			mongo_port = crawler.settings.get('MONGO_PORT'),
			mongo_user = crawler.settings.get('MONGO_USER'),
			mongo_password = crawler.settings.get('MONGO_PASSWORD'),
		)

	def open_spider(self, spider):
		## initializing spider
		## opening db connection
		self.client = pymongo.MongoClient(self.mongo_uri , self.mongo_port)
		self.db = self.client[self.mongo_db]
		self.db.authenticate(self.mongo_user , self.mongo_password)
		

	def close_spider(self, spider):
		## clean up when spider is closed
		self.client.close()

	def process_item(self, item, spider):
		## how to handle each post
		try:
			self.db[self.collection_name].insert(dict(item))
			logging.debug("Article added to MongoDB")
		except:
			utc=pytz.UTC
			existing_article_time = (self.db[self.collection_name].find_one(dict(item)['_id'])['modified_time']).replace(tzinfo=utc)
			current_article_time = (dict(item)['modified_time']).replace(tzinfo=utc)
			if existing_article_time < current_article_time:
				self.db[self.collection_name].replace_one({"_id" : self.db[self.collection_name].find_one(dict(item)['_id'])}, dict(item))
				logging.debug("Article updated on MongoDB")
			else:
				logging.debug("Article remains unchanged")
		return item
