import scrapy
from ..items import NewsterItem
import datetime 
from dateutil.parser import parse as dateParse
from tzlocal import get_localzone
from ..utilfunc import extract_summary

# *=====================*
# page_number = 1
# scrape_next_page = True
# *=====================*

class BloombergPoolSpider(scrapy.Spider):
	name = 'bloomberg'
	query_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
	query_string = "https://www.bloomberg.com/search?query=pakistan&sort=time:desc&endTime=" + query_time
	start_urls = [query_string]

	def parse(self, response):
		#*=======================*
		# global page_number
		# global scrape_next_page
		#*=======================*
		# follow links to author pages
		for href in response.css('article.search-result-story.type-article a::attr(href)'):
			yield response.follow(href, self.parse_author)

		# Logic to scrape multiple pages
		# *===============================================================*
		# if scrape_next_page:
		# 	page_number = page_number + 1
		# 	next_page_url = response.urljoin('&page=' + str(page_number))
		# 	yield scrapy.Request(url = next_page_url, callback = self.parse)
		# *===============================================================*

	def parse_author(self, response):

		# *=====================*
		# global scrape_next_page
		# *=====================*
		article_type = response.css('meta[property="og:type"]::attr(content)').extract_first()
		if(article_type != 'article'):
			return None
		published_time = dateParse(response.css('meta[name="iso-8601-publish-date"]::attr(content)').extract_first()).astimezone(get_localzone()).replace(tzinfo=None)
		todays_date = datetime.datetime.now(datetime.timezone.utc).astimezone(get_localzone())
		if published_time.date() < todays_date.date():
		# *=====================*
		# 	scrape_next_page = False
		# *=====================*
			return None
		modified_time = published_time
		
		first_paragraph = extract_summary(response, "div.transporter-item.current article")
		category = []
		category.append(response.css('article::attr(data-theme)').extract_first())
		category.append('Tigrosa-Internation')

		newsterItem = NewsterItem(
			_id = 'bloomberg' + '-' + response.css('div.transporter-item.current article::attr(data-story-id)').extract_first(),
			url = response.request.url,
			published_time = published_time,
			modified_time = modified_time,
			title = response.css('meta[property="og:title"]::attr(content)').extract_first(),
			category = category,
			content = '\n\n'.join(response.css('div.transporter-item.current article p *::text').extract()),
			image_link = response.css('meta[property="og:image"]::attr(content)').extract_first(),
			summary = first_paragraph
			)
		return newsterItem