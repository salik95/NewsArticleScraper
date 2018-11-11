import scrapy
from ..items import NewsterItem
from datetime import datetime
from dateutil.parser import parse as dateParse
from ..utilfunc import extract_summary, get_url_attributes

scrape_next_page = True

class BrecorderPoolSpider(scrapy.Spider):
	name = 'brecorder'
	start_urls = ['https://www.brecorder.com/pakistan/business-economy/','https://www.brecorder.com/pakistan/markets-pakistan/']

	def parse(self, response):
		global scrape_next_page
		# follow links to author pages
		for href in response.css('div.cat-post div.singletitle a::attr(href)'):
			yield response.follow(href, self.parse_author)
		if scrape_next_page:
			url_attributes = get_url_attributes(response.request.url, '/page/', '/')
			next_page_url = url_attributes['core_url'] + 'page/' + url_attributes['page_number']
			yield scrapy.Request(url = next_page_url, callback = self.parse)

	def parse_author(self, response):

		global scrape_next_page

		published_time = dateParse(response.css('meta[property="article:published_time"]::attr(content)').extract_first())
		todays_date = datetime.now()
		if published_time.date() < todays_date.date():
			scrape_next_page = False
			return None
		try:
			modified_time = dateParse(response.css('meta[property="article:modified_time"]::attr(content)').extract_first())
		except:
			modified_time = published_time
		
		id_extractor = response.css('article::attr(id)').extract_first().split('-')

		first_paragraph = extract_summary(response, "div.post-" + str(id_extractor[len(id_extractor)-1]))


		category = response.css('meta[property="article:tag"]::attr(content)').extract()
		category.append('Business')

		newsterItem = NewsterItem(
			_id = 'brecorder' + '-' + str(id_extractor[len(id_extractor)-1]),
			url = response.request.url,
			published_time = published_time,
			modified_time = modified_time,
			title = response.css('title::text').extract_first().split('|')[0],
			category = list(set(category)),
			content = '\n\n'.join(response.css('div.post-' + str(id_extractor[len(id_extractor)-1]) + ' p *::text').extract()),
			image_link = response.css('meta[property="og:image"]::attr(content)').extract_first(),
			summary = first_paragraph
			)
		return newsterItem