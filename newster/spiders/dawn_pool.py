# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from ..items import NewsterItem
from ..utilfunc import extract_summary
from dateutil.parser import parse as dateParse

class DawnPoolSpider(scrapy.Spider):
	name = 'dawn'
	start_urls = ['https://www.dawn.com/newspaper/national', 'https://www.dawn.com/newspaper/business']

	def parse(self, response):
		for href in response.css('article.story--small[data-layout="story"] a.story__link::attr(href)').extract():
			yield response.follow(href, self.parse_author, meta={'category' : response.css('title::text').extract_first().split('-')[0].strip()})
		for href in response.css('article.story--large[data-layout="story"] a.story__link::attr(href)').extract():
			yield response.follow(href, self.parse_author, meta={'category' : response.css('title::text').extract_first().split('-')[0].strip()})

	def parse_author(self, response):

		meta = response.css('head meta')
		published_time = dateParse(meta.css('[property="article:published_time"]::attr(content)').extract_first())
		modified_time = dateParse(meta.css('[property="article:modified_time"]::attr(content)').extract_first())
		
		first_paragraph = extract_summary(response,"article.story .story__content")

		category = response.css('meta[property="article:section"]::attr(content)').extract()
		category.append(response.request.meta['category'])
		
		newsterItem = NewsterItem(
			_id = 'dawn' + '-' + response.css('.story__title::attr(data-id)').extract_first(),
			url = response.request.url,
			published_time = published_time,
			modified_time = modified_time,
			title = response.css('.story__title a::text').extract_first(),
			category = list(set(category)),
			content = '\n\n'.join(response.css('article.story .story__content p *::text').extract()),
			image_link = meta.css('[property="og:image"]::attr(content)').extract_first(),
			summary = first_paragraph
			)

		return newsterItem

