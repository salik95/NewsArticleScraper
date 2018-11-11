import scrapy
from ..items import NewsterItem
from datetime import datetime 
from dateutil.parser import parse as dateParse

page_number = 1
scrape_next_page = True

class PakistanTodayPoolSpider(scrapy.Spider):
	name = 'pakistantoday'
	start_urls = ['https://profit.pakistantoday.com.pk/category/headlines/']

	def parse(self, response):
		global page_number
		global scrape_next_page
		# follow links to author pages
		for href in response.css('div.td-module-thumb a::attr(href)'):
			yield response.follow(href, self.parse_author)
		if scrape_next_page:
			page_number = page_number + 1
			next_page_url = response.urljoin('/page/' + str(page_number))
			yield scrapy.Request(url = next_page_url, callback = self.parse)


	def parse_author(self, response):

		global scrape_next_page

		article_section = response.css('meta[property="article:section"]::attr(content)').extract_first()
		if article_section != 'HEADLINES':
			return None

		article_title = response.css('div.td-post-header h1.entry-title::text').extract_first()

		published_time = dateParse(response.css('meta[itemprop="datePublished"]::attr(content)').extract_first()).replace(tzinfo=None)
		try:
			modified_time = dateParse(response.css('meta[itemprop="dateModified"]::attr(content)').extract_first()).replace(tzinfo=None)
		except:
			modified_time = published_time

		todays_date = datetime.now()
		if published_time.date() < todays_date.date():
			scrape_next_page = False
			return None

		child_int = 1
		while True:
			first_para_text = "div.td-post-content > p:nth-of-type("+ str(child_int) + ") *::text"
			first_paragraph = ''.join(response.css(first_para_text).extract())
			if len(first_paragraph) > 7:
				break
			child_int = child_int + 1

		newsterItem = NewsterItem(
			_id = 'pakistantoday' + '-' + response.css('article::attr(id)').extract_first().split('-')[1],
			url = response.request.url,
			published_time = published_time,
 			modified_time = modified_time,
			title = article_title,
			content = '\n\n'.join(response.css('div.td-post-content p *::text').extract()),
			image_link = response.css('div.td-post-featured-image img::attr(src)').extract_first(),
			summary = first_paragraph
			)
		return newsterItem