# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsterItem(scrapy.Item):
	# define the fields for your item here like:
	_id = scrapy.Field()
	url = scrapy.Field()
	published_time = scrapy.Field()
	modified_time = scrapy.Field()
	category = scrapy.Field()
	title = scrapy.Field()
	content = scrapy.Field()
	image_link = scrapy.Field()
	summary = scrapy.Field()

	def __repr__(self):
		return repr({"timestamp": self["published_time"]})