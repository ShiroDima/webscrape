import scrapy
import requests
import json
from urllib.parse import urlencode
import os
from dotenv.main import load_dotenv
from ..items import TargetScraperItem


class TargetSpider(scrapy.Spider):
    load_dotenv()
    name = "target"
    custom_settings = {
        'COLLECTION_NAME': 'walmart',
        'FEEDS': {
            './data/target.csv': {
                'format': 'csv'
            }
        }

    }

    def start_requests(self):
        # keyword_list = ['laptop', 'iphone']
        keyword = self._get_keyword()
        yield scrapy.Request("https://httpstat.us/200", callback=self.parse_products_lists, meta={'keyword': keyword})

    def parse_products_lists(self, response):
        item = TargetScraperItem()
        keyword = response.meta["keyword"]
        payload = {
            'api_key': os.environ["TARGET_API_KEY"],
            'search_term': keyword,
            'type': 'search',
            'max_page': '5',
            # 'include_html': 'true',
            'output': 'json'
        }
        api_url = 'https://api.redcircleapi.com/request'  # + urlencode(payload)

        res = requests.get(api_url, params=payload)
        results = res.json()
        for product in results["search_results"]:

            try:
                item["id"] = product["product"]["dpci"]
            except:
                item["id"] = ""
            # product = product["product"]
            try:
                item["name"] = product["product"]["title"]
            except:
                item["name"] = ""

            try:
                item["product_url"] = product["product"]["link"]
            except:
                item["product_url"] = ""

            try:
                item["image_url"] = product["product"]["main_image"]
            except:
                item["image_url"] = ""

            try:
                item["price"] = product["offers"]["primary"]["price"]
            except:
                item["price"] = product["offers"]["primary"]["price"]

            try:
                item["discount"] = self._get_discount(product["offers"]["primary"])
            except:
                item["discount"] = ""

            try:
                item["description"] = self._get_description(product["product"]["feature_bullets"])
            except:
                item["description"] = ""

            try:
                item["average_rating"] = product["product"]["rating"]
            except:
                item["average_rating"] = ""

            # print("####################################")
            # print(type(results).__name__)
            # print("####################################")
            yield item


    def _get_discount(self, data):
        reg_price = data["regular_price"]
        price = data["price"]

        return str(((reg_price - price) / reg_price) * 100) + ' %'


    def _get_description(self, data):
        desc = ""
        for bullet in data:
            desc += bullet + "\n"

        return desc

    def _get_keyword(self):
        # scraped = open("walmart_keywords/scraped.txt", 'r').read()
        with open("kohls_keywords/keywords.txt", "r") as keywords:
            with open("kohls_keywords/scraped.txt", "a+") as scraped:
                for keyword in keywords.readlines():
                    if keyword in scraped.readlines():
                        continue
                    else:
                        scraped.write(keyword + "\n")
                        return keyword