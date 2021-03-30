import scrapy

from scrapy.loader import ItemLoader

from ..items import SouthsideItem
from itemloaders.processors import TakeFirst


class SouthsideSpider(scrapy.Spider):
	name = 'southside'
	start_urls = ['https://www.southside.com/blog/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="medium-8 large-9 columns"]')
		for post in post_links:
			url = post.xpath('.//a[text()="read more"]/@href').get()
			title = post.xpath('./h3/a/font/text()').get()
			date = post.xpath('./b/text()').get()

			yield response.follow(url, self.parse_post, cb_kwargs={'date': date, 'title': title})

		next_page = response.xpath('//li[@class="arrow"]/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, title, date):
		description = response.xpath('//div[@class="post"]//div[@class="medium-8 large-9 columns"]/p//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=SouthsideItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
