import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BbendigobankItem
from itemloaders.processors import TakeFirst
import json

pattern = r'(\xa0)?'
base = 'https://www.bendigobank.com.au/api/blogListing/get-by-filter?page={}&bid=33415&totalPages=false&filters=%7B%22topic%22:%22-all-%22%7D&term='

class BlogSpider(scrapy.Spider):
    name = 'blog'
    page = 1
    start_urls = [base.format(page)]

    def parse(self, response):
        data = json.loads(response.text)
        for index in range(len(data['articles'])):
            link = data['articles'][index]['href']
            title = data['articles'][index]['title']
            date = data['articles'][index]['date']
            yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date, title=title))

        if self.page < data['totalPages']:
            self.page += 1
            yield response.follow(base.format(self.page), self.parse)

    def parse_post(self, response, date, title):
        content = response.xpath('//div[@class="wysiwyg"]//text()').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item = ItemLoader(item=BbendigobankItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()