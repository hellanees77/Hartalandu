import scrapy


class NepsefloorsheetSpider(scrapy.Spider):
    name = "nepsefloorsheet"
    allowed_domains = ["s"]
    start_urls = ["http://s/"]

    def parse(self, response):
        pass
