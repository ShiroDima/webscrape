import scrapy
import json
import math
from urllib.parse import urlencode
from ..items import WalmartScraperItem
# from scrapy_playwright.page import PageMethod
import re
from datetime import datetime
# from scrapy_playwright.page import PageMethod

# from scrapy_selenium import SeleniumRequest
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC

API_KEY = "a137708d-feb6-45b7-8020-159f63938342"

def get_proxy_url(url):
    payload = {
        'api_key': API_KEY,
        'url': url,
        "render_js": 'true'
    }

    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)

    return proxy_url

# headers = {
#     "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
BASE_URL = 'https://www.walmart.com'


class WalmartSpider(scrapy.Spider):
    name = "walmart"
    custom_settings = {
        'COLLECTION_NAME': 'walmart',

    }

    def start_requests(self):
        keyword_list = ['laptop']  # , 'phones', 'grills', 'household items']
        for keyword in keyword_list:
            payload = {'q': keyword,
                       #    'sort': 'best_seller',
                       'page': 1, 'affinityOverride': 'default'}
            walmart_search_url = 'https://www.walmart.com/search?' + \
                urlencode(payload)
            yield scrapy.Request(url=walmart_search_url,
                                 callback=self.parse_search_results,
                                 meta={
                                     #  "playwright": True,
                                     #  "playwright_page_methods": [
                                     #  PageMethod("wait_for_selector", '//*[@id="maincontent"]/main/div/div[2]/div/div/div[1]/div[2]/div/section')
                                     #  ],
                                     'keyword': keyword,
                                     'page': 1
                                 },
                                #  headers=headers
                                 )

    def parse_search_results(self, response):
        page = response.meta['page']
        keyword = response.meta['keyword']
        script_tag = response.xpath(
            '//script[@id="__NEXT_DATA__"]/text()').get()

        if script_tag is not None:
            json_blob = json.loads(script_tag)

            # Request Product Page
            product_list = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"][0]["items"]
            # yield{
            #     "info": product_list
            # }
            for idx, product in enumerate(product_list):
                if "ip" not in product.get('canonicalUrl', '').split('?')[0]:
                    continue
                walmart_product_url = BASE_URL + \
                    product.get('canonicalUrl', '').split('?')[0]
                # yield {
                #     "product_url": walmart_product_url
                # }
                yield scrapy.Request(url=get_proxy_url(walmart_product_url),
                                    callback=self.parse_product_data,
                                    meta={'keyword': keyword, 'page': page, 'position': idx + 1},
                                    # headers=headers
                                    )
                

        #     # Request Next Page
        #     if page == 1:
        #         # total_product_count = json_blob["props"]["pageProps"][
        #         #     "initialData"]["searchResult"]["itemStacks"][0]["count"]
        #         # max_pages = math.ceil(total_product_count / 40)
        #         # if max_pages > 5:
        #         #     max_pages = 5
        #         max_pages = 5
        #         for p in range(2, max_pages):
        #             payload = {'q': keyword, 'sort': 'best_seller',
        #                        'page': p, 'affinityOverride': 'default'}
        #             walmart_search_url = 'https://www.walmart.com/search?' + urlencode(payload)
        #             yield scrapy.Request(url=walmart_search_url,
        #                                  callback=self.parse_search_results,
        #                                  meta={'keyword': keyword, 'page': p},
        #                                  headers=headers)
        # yield {
        #     "len": len(response.xpath('//section//div[@role="group"]/a/@href').getall()),
        #     "res": response.text
        # }
        # for product in response.xpath('//section//div[@role="group"]/a/@href'):
        #     yield {
        #         # "product": product.get()
        #         len:
        #     }

    def parse_product_data(self, response):
        item = WalmartScraperItem()
        # '//span[@itemprop="price"]/text()'
        item["name"] = response.selector.css("h1.f6::text").get()
        item["product_url"] = response.url,
        # item["image_url"] = response.selector.css("img.noselect::attr(src)")
        item["image_url"] = response.selector.xpath("//img[@height=612]/@src").get()
        item["description"] = self._get_product_description(response)
        item["price"] = re.sub('\$', "", response.selector.xpath('//span[@itemprop="price"]/text()').get().strip())
        item["average_rating"] = self._get_average_rating(response.selector.xpath('//span[contains(@class, "rating-number")]/text()').get())
        # try:
        #     # item["price"] = re.findall('\$', response.selector.xpath('//span[contains(@class, "f1")]//span[@itemprop="price"]/text()').get().strip())[1]
        #     item["description"] = self._get_product_description(response)
        #     # item["average_rating"] = self._get_average_rating(response.selector.xpath('//span[@class="rating-number"]/text()').get())
        # except (AttributeError, IndexError, TypeError):
        #     yield {
        #         # "see_elem": response.selector.xpath('//span[contains(@class, "f1")]//span[@itemprop="price"]/text()'),
        #         'text': response.text
        #     }
        
        # try:
        #     item["price"] = re.findall('\$', response.selector.xpath('//span[@itemprop="price"]/text()').get().strip())[1]
        #     # item["description"] = self._get_product_description(response)
        #     # item["average_rating"] = self._get_average_rating(response.selector.xpath('//span[@class="rating-number"]/text()').get())
        # except (AttributeError, IndexError, TypeError):
        #    print(response.selector.xpath('//span[@itemprop="price"]/text()').get())
        try:
            item["average_rating"] = self._get_average_rating(response.selector.xpath('//span[contains(@class, "rating-number")]/text()').get())
        except (AttributeError, IndexError, TypeError):
            print(response.selector.xpath('//span[contains(@class, "rating-number")]/text()').get())
            item["average_rating"] = ""
        
        item["time"] = datetime.now()

        yield item
        # script_tag = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        # script_tag = response.selector.css('script#__NEXT_DATA__::text').get()

        # if script_tag is not None:
        #     json_blob = json.loads(script_tag)

        #     raw_product_data = json_blob["props"]["pageProps"]["initialData"]["data"]["product"]

        #     yield {
        #         "item": raw_product_data
        #     }
        # else:
        # yield {
        #     "price": re.findall("itemprop", response.text),
        #     "rating": re.findall("rating-number", response.text),
        #     "desc": re.findall("dangerous-html", response.text)
        # }

    def _get_product_description(self, response):
        # text_1 = response.selector.css("span.f6>div.dangerous-html::text").get()
        text_1 = response.selector.xpath('//span[contains(@class, "f6")]//div[contains(@class, "dangerous-html")]/text()').get()
        # text_2 = response.selector.css("span.f6>div.dangerous-html>ul>li::text").get()
        text_2 = response.selector.xpath('//span[contains(@class, "f6")]//div[contains(@class, "dangerous-html")]//li/text()').get()

        desc = text_1 + "\n"
        for text in text_2:
            desc = desc + text + "\n"

        return desc

    def _get_average_rating(self, data):
        return re.sub("\(", "", re.sub("\)", "", data))

    # def
