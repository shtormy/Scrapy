import scrapy
from scrapy.http import HtmlResponse
from parse_castorama.items import ParseCastoramaItem
from scrapy.loader import ItemLoader


class CastoramaSpider(scrapy.Spider):
    name = 'castorama'
    allowed_domains = ['castorama.ru']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://www.castorama.ru/decoration/{kwargs.get("search")}/?limit=96']

    def parse(self, response: HtmlResponse, **kwargs):

        next_page = response.xpath('//a[@class="next i-next"]/@href').get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath(
            "//ul[@class='products-grid products-grid--max-4-col']/li/a[@class='product-card__img-link']")
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):

        loader = ItemLoader(item=ParseCastoramaItem(), response=response)

        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price',
                         "//div[@class='price-wrapper ']//span/span/span/span[1]/text() | //div[@class='price-wrapper ']//span/span/span/span[2]/text()")
        loader.add_xpath('photos', "//div[@class='js-zoom-container']/img/@data-src")
        loader.add_value('url', response.url)
        yield loader.load_item()
