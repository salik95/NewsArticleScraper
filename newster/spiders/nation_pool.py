# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from ..items import NewsterItem
from ..utilfunc import extract_summary
from dateutil.parser import parse as dateParse
import hashlib

class NationPoolSpider(scrapy.Spider):
	name = 'nation'
	start_urls = ['https://nation.com.pk/Todays-paper']

	def parse(self, response):
		# follow links to author pages
		for href in response.css('.ntitle a::attr(href)').extract():
			yield response.follow(href, self.parse_author)

	def parse_author(self, response):
		meta = response.css('head meta')

		category = meta.css('[property="article:section"]::attr(content)').extract()
		valid_article = False

		for item in category:
			if item == "Business" or item == "National":
				valid_article = True
				break
		if not valid_article:
			return None

		published_time = dateParse(meta.css('[property="article:published_time"]::attr(content)').extract_first()).replace(tzinfo=None)

		try:
			modified_time = dateParse(meta.css('[property="article:modified_time"]::attr(content)').extract_first()).replace(tzinfo=None)
		except:
			modified_time = published_time

		article_title = response.css('head title::text').extract_first()

		first_paragraph = extract_summary(response, "article .post-content")

		newsterItem = NewsterItem(
			_id = 'nation' + '-' + hashlib.md5(article_title.encode('utf-8')).hexdigest(),
			url = response.request.url,
			published_time = published_time,
			modified_time = modified_time,
			title = article_title,
			category = list(set(category)),
			content = '\n\n'.join(response.css('article .post-content p *::text').extract()),
			image_link = meta.css('[property="og:image"]::attr(content)').extract_first(),
			summary = first_paragraph
			)

		return newsterItem