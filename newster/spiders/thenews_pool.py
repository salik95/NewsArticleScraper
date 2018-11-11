import scrapy
from ..items import NewsterItem
from ..utilfunc import extract_summary
from datetime import datetime 
from dateutil.parser import parse as dateParse

class TheNewsPoolSpider(scrapy.Spider):
	name = 'thenews'
	start_urls = ['https://www.thenews.com.pk/print/category/top-story', 'https://www.thenews.com.pk/print/category/national', 'https://www.thenews.com.pk/latest/category/business']
	def parse(self, response):
		# follow links to author pages
		for href in response.css('div.siteContent a.open-section::attr(href)'):
			yield response.follow(href, self.parse_author)

	def parse_author(self, response):

		published_time = dateParse(response.css('div.container div.category-date::text').extract_first()).replace(tzinfo=None)
		modified_time = published_time

		todays_date = datetime.now()
		if published_time.date() < todays_date.date():
			return None

		first_paragraph = extract_summary(response, "div.story-detail")
		
		article_url_peices = str(response.request.url).split('/')

		newsterItem = NewsterItem(
			_id = 'thenews' + '-' + article_url_peices[len(article_url_peices)-1].split('-')[0],
			url = response.request.url,
			published_time = published_time,
 			modified_time = modified_time,
			title = response.css('meta[property="og:title"]::attr(content)').extract_first(),
			category = response.css('body div.detail-content div.category-name h2::text').extract(),
			content = '\n\n'.join(response.css('div.story-detail p *::text').extract()),
			image_link = response.css('meta[property="og:image"]::attr(content)').extract_first(),
			summary = first_paragraph
			)
		return newsterItem