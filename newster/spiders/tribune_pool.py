import scrapy
from ..items import NewsterItem
from datetime import datetime
from dateutil.parser import parse as dateParse
from ..utilfunc import extract_summary, get_url_attributes

scrape_next_page = True

class TribunePoolSpider(scrapy.Spider):
	name = 'tribune'
	start_urls = ['https://tribune.com.pk/business/archives/', 'https://tribune.com.pk/pakistan/archives/']

	def parse(self, response):
		global scrape_next_page
		# follow links to author pages
		for href in response.css('div.long-story a::attr(href)'):
			yield response.follow(href, self.parse_author)
		if scrape_next_page:
			url_attributes = get_url_attributes(response.request.url, '/?page=', '/')
			next_page_url = url_attributes['core_url'] + '?page=' + url_attributes['page_number']
			yield scrapy.Request(url = next_page_url, callback = self.parse)


	def parse_author(self, response):

		global scrape_next_page
		meta = response.css('head meta')
		header = response.css('div.story .template__header')

		try:
			published_time = dateParse(meta.css('[property="article:published_time"]::attr(content)').extract_first()).replace(tzinfo=None)
		except:
			return None

		todays_date = datetime.now()
		if published_time.date() < todays_date.date():
			scrape_next_page = False
			return None
		try:
			modified_time = dateParse(meta.css('[property="article:modified_time"]::attr(content)').extract_first()).replace(tzinfo=None)
		except:
			modified_time = published_time
		
		first_paragraph = extract_summary(response, "div.clearfix.story-content.read-full")

		category = response.css('meta[property="article:tag"]::attr(content)').extract()
		article_section = response.css('meta[property="article:section"]::attr(content)').extract_first()
		if article_section.lower() == 'pakistan':
			article_section = 'national'
		category.append(article_section)

		newsterItem = NewsterItem(
			_id = 'tribune' + '-' + response.css('.story::attr(id)').extract_first().split('-')[1],
			url = response.request.url,
			published_time = published_time,
			modified_time = modified_time,
			title = response.css('div.story.clearfix h1.title a::text').extract_first(),
			category = list(set(category)),
			content = '\n\n'.join(response.css('div.clearfix.story-content.read-full p *::text').extract()),
			image_link = response.css('div.story-image-container img::attr(src)').extract_first(),
			summary = first_paragraph
			)
		return newsterItem