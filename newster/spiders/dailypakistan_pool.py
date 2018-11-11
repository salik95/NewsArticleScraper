import scrapy
from ..items import NewsterItem
from datetime import datetime 
from dateutil.parser import parse as dateParse
from ..utilfunc import extract_summary, get_url_attributes

class DailyPakistanPoolSpider(scrapy.Spider):
	name = 'dailypakistan'
	start_urls = ['https://en.dailypakistan.com.pk/category/pakistan/', 'https://en.dailypakistan.com.pk/category/business/']

	def parse(self, response):
		global scrape_next_page
		# follow links to author pages
		for href in response.css('div.container main article a::attr(href)').extract():
			yield response.follow(href, self.parse_author, meta={'category' : response.css('main.category-list h1.page-title::text').extract_first()})
	def parse_author(self, response):

		published_time = dateParse(response.css('article header.entry-header span.posted-on time[itemprop="datePublished"]::attr(content)').extract_first()).replace(tzinfo=None)

		todays_date = datetime.now()
		if published_time.date() < todays_date.date():
			return None

		try:
			modified_time = dateParse(response.css('article header.entry-header span.posted-on time[itemprop="dateModified"]::attr(content)').extract_first()).replace(tzinfo=None)
		except:
			modified_time = published_time

		article_title = response.css('div.container h2.entry-title::text').extract_first()

		id_extractor = response.css('article::attr(id)').extract_first().split('-')

		first_paragraph = extract_summary(response, "article div.entry-content div.content-body")

		category = []
		if response.request.meta['category'].lower() == 'pakistan':
			category.append('National')
		else:
			category.append(response.request.meta['category'])

		newsterItem = NewsterItem(
			_id = 'dailypakistan' + '-' + id_extractor[len(id_extractor)-1],
			url = response.request.url,
			published_time = published_time,
			modified_time = modified_time,
			title = article_title,
			category = list(set(category)),
			content = '\n\n'.join(response.css('article div.entry-content div.content-body p *::text').extract()),
			image_link = response.css('article header.entry-header div[itemprop="image"] img::attr(src)').extract_first(),
			summary = first_paragraph
			)
		return newsterItem