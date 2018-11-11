import scrapy
from ..items import NewsterItem
from ..utilfunc import extract_summary
from datetime import datetime 
from dateutil.parser import parse as dateParse

class DunyaNewsPoolSpider(scrapy.Spider):
	name = 'dunyanews'
	start_urls = ['http://dunyanews.tv/en/Pakistan', 'http://dunyanews.tv/en/Business']

	def parse(self, response):
		# follow links to author pages
		article_links = response.css('article a::attr(href)').extract()
		for index, article in enumerate(article_links):
			if 'http' not in article:
				article_links[index] = response.request.url + "/" + article_links[index].split('/')[len(article_links[index].split('/'))-1]
		for href in article_links:
			yield response.follow(href, self.parse_author, meta={'category' : response.css('body div.main_content h1.page-title::text').extract_first().split('-')[0].strip()})

	def parse_author(self, response):

		article_title = response.css('h2.page-title::text').extract_first()

		published_time = dateParse(str(response.css('div.post_date b::text').extract_first()) + str(response.css('div.post_date::text').extract()[1])).replace(tzinfo=None)
		modified_time = published_time

		todays_date = datetime.now()
		if published_time.date() < todays_date.date():
			return None

		first_paragraph = extract_summary(response, "div.post_content")

		category = response.css('meta[property="article:section"]::attr(content)').extract()
		category.append(response.request.meta['category'])

		article_url_peices = str(response.request.url).split('/')

		newsterItem = NewsterItem(
			_id = 'dunyanews' + '-' + article_url_peices[len(article_url_peices)-1].split('-')[0],
			url = response.request.url,
			published_time = published_time,
 			modified_time = modified_time,
			title = article_title,
			category = list(set(category)),
			content = '\n\n'.join(response.css('div.post_content p *::text').extract()),
			image_link = response.css('meta[property="og:image"]::attr(content)').extract_first(),
			summary = first_paragraph
			)
		return newsterItem