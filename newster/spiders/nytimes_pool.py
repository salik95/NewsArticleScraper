import scrapy
from ..items import NewsterItem
import datetime 
from dateutil.parser import parse as dateParse
from tzlocal import get_localzone

class NytimesPoolSpider(scrapy.Spider):
	name = 'nytimes'
	start_urls = ['https://www.nytimes.com/topic/destination/pakistan']

	def parse(self, response):
		print('Parsing list now')
		for href in response.css('#latest-panel article.story .story-link::attr(href)'):
			yield response.follow(href, self.parse_article)

	def parse_article(self, response):
		meta = response.css('meta')
		article_id = meta.css('[name=articleid]::attr(content)').extract_first()
		paragraphs = response.css('.StoryBodyCompanionColumn p')

		published_time = dateParse(meta.css('[property="article:published"]::attr(content)').extract_first()).astimezone(get_localzone()).replace(tzinfo=None)
		try:
			modified_time = dateParse(meta.css('[property="article:modified"]::attr(content)').extract_first()).astimezone(get_localzone()).replace(tzinfo=None)
		except:
			modified_time = published_time

		if published_time is None:
			published_time = dateParse(meta.css('[itemprop="datePublished"]::attr(content)').extract_first()).astimezone(get_localzone()).replace(tzinfo=None)
			try:
				modified_time = dateParse(meta.css('[property="dateModified"]::attr(content)').extract_first()).astimezone(get_localzone()).replace(tzinfo=None)
			except:
				modified_time = published_time

		todays_date = datetime.datetime.now(datetime.timezone.utc).astimezone(get_localzone())
		if published_time.date() < todays_date.date():
			return None

		category = response.css('meta[property="article:tag"]::attr(content)').extract()
		category.append('Tigrosa-Internation')

		article = NewsterItem(
			_id = 'nytimes' + '-' + article_id,
			url = response.request.url,
			published_time = published_time,
			modified_time = modified_time,
			title = meta.css('.balancedHeadline::text').extract_first(),
			category = category,
			content = '\n\n'.join(list(map(lambda p: ' '.join(p.css('::text').extract()), paragraphs))),
			image_link = meta.css('[name=image]::attr(content)').extract_first(),
			summary = meta.css('[name=description]::attr(content)').extract_first()
			)

		return article