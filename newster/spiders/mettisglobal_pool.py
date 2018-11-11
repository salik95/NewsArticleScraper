import scrapy
from ..items import NewsterItem
import datetime 
from dateutil.parser import parse as dateParse
from tzlocal import get_localzone
from ..utilfunc import extract_summary

class MettisglobalPoolSpider(scrapy.Spider):
	name = 'mettisglobal'
	start_urls = ["https://mettisglobal.news/?s=pakistan"]

	def parse(self, response):
		for href in response.css('div.td-main-content h3.td-module-title a::attr(href)'):
			yield response.follow(href, self.parse_author)

	def parse_author(self, response):

		published_time = dateParse(response.css('meta[property="article:published_time"]::attr(content)').extract_first()).astimezone(get_localzone()).replace(tzinfo=None)

		todays_date = datetime.datetime.now(datetime.timezone.utc).astimezone(get_localzone())
		if published_time.date() < todays_date.date():
			return None
		try:
			modified_time = dateParse(response.css('meta[property="article:modified_time"]::attr(content)').extract_first()).astimezone(get_localzone()).replace(tzinfo=None)
		except:
			modified_time = published_time

		id_extractor = response.css('article::attr(id)').extract_first().split('-')
		
		first_paragraph = extract_summary(response, "article.post-" + str(id_extractor[len(id_extractor)-1]) + " div.td-post-content")

		category = response.css('article div.td-post-source-tags li a::text').extract()
		category.append('Tigrosa-Internation')

		newsterItem = NewsterItem(
			_id = 'mettisglobal' + '-' + str(id_extractor[len(id_extractor)-1]),
			url = response.request.url,
			published_time = published_time,
			modified_time = modified_time,
			title = response.css('meta[property="og:title"]::attr(content)').extract_first(),
			category = list(set(category)),
			content = '\n\n'.join(response.css('article.post-' + str(id_extractor[len(id_extractor)-1]) + ' div.td-post-content p *::text').extract()),
			image_link = response.css('meta[property="og:image"]::attr(content)').extract_first(),
			summary = first_paragraph
			)
		return newsterItem