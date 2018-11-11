import scrapy
from ..items import NewsterItem
from datetime import datetime 
from dateutil.parser import parse as dateParse
from ..utilfunc import extract_summary, get_url_attributes

scrape_next_page = True

class DailyTimesPoolSpider(scrapy.Spider):
	name = 'dailytimes'
	start_urls = ['https://dailytimes.com.pk/pakistan/', 'https://dailytimes.com.pk/business/']

	def parse(self, response):
		global scrape_next_page
		# follow links to author pages
		for href in response.css('body main article h2.entry-title a::attr(href)'):
			yield response.follow(href, self.parse_author, meta={'category' : response.css('main h1.archive-title::text').extract_first()})
		if scrape_next_page:
			url_attributes = get_url_attributes(response.request.url, '/page/', '/')
			next_page_url = url_attributes['core_url'] + 'page/' + url_attributes['page_number']
			yield scrapy.Request(url = next_page_url, callback = self.parse, meta={'category' : response.css('main h1.archive-title::text').extract_first()})

	def parse_author(self, response):

		global scrape_next_page

		published_time = dateParse(response.css('meta[property="article:published_time"]::attr(content)').extract_first()).replace(tzinfo=None)

		todays_date = datetime.now()
		if published_time.date() < todays_date.date():
			scrape_next_page = False
			return None

		try:
			modified_time = dateParse(response.css('meta[property="article:modified_time"]::attr(content)').extract_first()).replace(tzinfo=None)
		except:
			modified_time = published_time

		article_title = response.css('div.post-header h1.entry-title::text').extract_first()

		id_extractor = response.css('body::attr(class)').extract_first().split(' ')
		for item in id_extractor:
			if 'postid' in item:
				article_id = item.split('-')[len(item.split('-'))-1]

		first_paragraph = extract_summary(response, "main.content div.entry-content")

		category = response.css('meta[property="article:section"]::attr(content)').extract()
		category.append(response.request.meta['category'])

		newsterItem = NewsterItem(
			_id = 'dailytimes' + '-' + article_id,
			url = response.request.url,
			published_time = published_time,
			modified_time = modified_time,
			title = article_title,
			category = list(set(category)),
			content = '\n\n'.join(response.css('main.content div.entry-content p *::text').extract()),
			image_link = response.css('meta[property="og:image"]::attr(content)').extract_first(),
			summary = first_paragraph
			)
		return newsterItem