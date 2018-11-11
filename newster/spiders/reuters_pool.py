import scrapy
from ..items import NewsterItem
import datetime 
from dateutil.parser import parse as dateParse
from tzlocal import get_localzone
from ..utilfunc import extract_summary

class ReutersPoolSpider(scrapy.Spider):
	name = 'reuters'
	start_urls = ["https://www.reuters.com/search/news?blob=pakistan&sortBy=date&dateRange=all"]

	def parse(self, response):
		for href in response.css('div.search-result-indiv h3.search-result-title a::attr(href)').extract():
			yield response.follow(href, self.parse_author)

	def parse_author(self, response):

		published_time = dateParse(response.css('meta[property="og:article:published_time"]::attr(content)').extract_first()).astimezone(get_localzone()).replace(tzinfo=None)

		todays_date = datetime.datetime.now(datetime.timezone.utc).astimezone(get_localzone())
		if published_time.date() < todays_date.date():
			return None
		try:
			modified_time = dateParse(response.css('meta[property="og:article:modified_time"]::attr(content)').extract_first()).astimezone(get_localzone()).replace(tzinfo=None)
		except:
			modified_time = published_time

		id_extractor = str(response.request.url).split('-')
		
		first_paragraph = extract_summary(response, "div.container_17wb1 div.body_1gnLA")
		if len(first_paragraph ) < 7:
			first_paragraph = extract_summary(response, "div.StandardArticleBody_container div.StandardArticleBody_body")

		category = response.css('meta[property="og:article:section"]::attr(content)').extract()
		category.append('Tigrosa-Internation')

		content = response.css('div.container_17wb1 div.body_1gnLA p *::text').extract()
		if len(content) < 10:
			content = response.css('div.StandardArticleBody_container div.StandardArticleBody_body p *::text').extract()

		newsterItem = NewsterItem(
			_id = 'reuters' + '-' + id_extractor[len(id_extractor)-1],
			url = response.request.url,
			published_time = published_time,
			modified_time = modified_time,
			title = response.css('head title::text').extract_first().lstrip().split('|')[0],
			category = category,
			content = '\n\n'.join(content),
			image_link = response.css('meta[property="og:image"]::attr(content)').extract_first(),
			summary = first_paragraph
			)
		return newsterItem