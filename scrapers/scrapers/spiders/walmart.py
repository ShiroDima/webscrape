import scrapy
import json
import math
from urllib.parse import urlencode

import selenium.common.exceptions

from ..items import WalmartScraperItem
# from scrapy_playwright.page import PageMethod
import re
from datetime import datetime
import os
from dotenv.main import load_dotenv
# from scrapy_playwright.page import PageMethod
import undetected_chromedriver as uc
import selenium.webdriver as webdriver
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# # from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


# API_KEY = "a137708d-feb6-45b7-8020-159f63938342"


def get_proxy():
    load_dotenv()
    USERNAME = os.environ["PROXY_USERNAME"]
    PASSWORD = os.environ["PROXY_PASSWORD"]
    GEONODE_DNS = os.environ["GEONODE_DNS"]

    # proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    proxy = "http://{}:{}@{}".format(USERNAME, PASSWORD, GEONODE_DNS)

    return proxy


# headers = {
#     "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
BASE_URL = 'https://www.walmart.com'


class WalmartSpider(scrapy.Spider):
    name = "walmart"
    custom_settings = {
        'COLLECTION_NAME': 'walmart',
        'FEEDS': {
            './data/walmart.csv': {
                'format': 'csv'
            }
        }

    }

    # options = Options()
    # # options.page_load_strategy = "eager"
    # # options.add_experimental_option("detach", True)
    # # options.add_argument('--headless=new')
    # options.add_argument(f'--proxy-server={get_proxy()}')  # = True

    # browser = webdriver.Chrome(
    #     # service=Service(
    #     #     # ChromeDriverManager().install()
    #     #     ),
    #     options=options
    # )

    def start_requests(self):
        # keyword_list = ['tires']  # , 'phones', 'grills', 'household items']
        # for keyword in keyword_list:
        # keyword = self._get_keyword()
        keyword_list = self._get_keyword_list()
        scraped = open("target_keywords/scraped.txt", 'a+')
        for keyword in keyword_list:
            try:
                keyword = re.split(r"\d+.", keyword)[1].strip()
            except IndexError:
                keyword = re.split(r"\d+.", keyword)[0].strip()
            key_enc = urlencode({"keyword": keyword.lower()})
            if key_enc.split("=")[1] in scraped.readlines():
                continue
            payload = {'q': keyword,
                       #    'sort': 'best_seller',
                       'page': 1, 'affinityOverride': 'default'
                       }
            walmart_search_url = 'https://www.walmart.com/search?' + urlencode(payload)
            # max_pages = self._get_max_pages(walmart_search_url)
            print("#######################################################")
            print("#######################################################")
            print(f"SCRAPING KEYWORD {keyword.upper()}")
            print("##################################")
            scraped.write(keyword)
            yield scrapy.Request(url=walmart_search_url,
                                 callback=self.parse_search_results,
                                 meta={
                                     'keyword': keyword,
                                     'page': 1,
                                     # 'max_pages': int(max_pages),
                                     'proxy': get_proxy()
                                 },
            )
            scraped.write(keyword)


    def parse_search_results(self, response):

        page = response.meta['page']
        keyword = response.meta['keyword']
        # max_pages = response.meta["max_pages"]
        is_next_page = response.selector.xpath("//a[@aria-label='Next Page']")

        script_tag = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()

        if script_tag is not None:
            json_blob = json.loads(script_tag)
            print("#######################################################")
            print("#######################################################")
            print(f"Scraping Page {page}")
            print("##################################")
            # Request Product Page
            product_list = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"][0]["items"]

            for _, product in enumerate(product_list):
                item = WalmartScraperItem()
                try:
                    item["id"] = product.get('id')
                except:
                    item["id"] = ""

                try:
                    item["name"] = product.get('name')
                except:
                    item["name"] = ""

                try:
                    item["product_url"] = product.get('canonicalUrl')
                except:
                    item["product_url"] = ""

                try:
                    item["image_url"] = product.get('imageInfo').get("thumbnailUrl")
                except:
                    item["image_url"] = ""
                # item["image_url"] = response.selector.xpath("//img[@height=612]/@src").get()
                try:
                    item["description"] = product.get("description")
                except:
                    item["description"] = ""

                try:
                    item["price"] = product.get("price")
                except:
                    item["price"] = ""

                try:
                    item["average_rating"] = product.get('averageRating')
                except:
                    item["average_rating"] = ""

                item["time"] = datetime.now()
                yield item

            if page < 25 and is_next_page:
                payload = {'q': keyword, 'sort': 'best_seller',
                           'page': page + 1, 'affinityOverride': 'default'}
                walmart_search_url = 'https://www.walmart.com/search?' + urlencode(payload)
                yield response.follow(
                    walmart_search_url,
                    callback=self.parse_search_results,
                    meta={
                        'keyword': keyword,
                        'page': page + 1,
                        # 'max_pages': max_pages,
                        # 'proxy': get_proxy()
                    }
                )


    # def _get_max_pages(self, url):
    #     options = Options()
    #     # options.page_load_strategy = "eager"
    #     options.add_experimental_option("detach", True)
    #     # options.add_argument('--headless=new')
    #     # options.add_argument(f'--proxy-server={get_proxy()}')  # = True
    #     # options.add_argument("--disable-extensions")
    #     # options.add_argument("--silent")
    #     # options.add_argument("test-type")
    #     # options.add_experimental_option('excludeSwitches', ['enable-logging'])
    #     browser = webdriver.Chrome(
    #         # service=Service(ChromeDriverManager().install()),
    #         options=options
    #     )
    #     # browser = uc.Chrome(
    #     #     # options=options
    #     # )
    #     print("#################################################################################################")
    #     print("#################################################################################################")
    #     print("Getting Max Pages")
    #     print("########################################")
    #     browser.get(url)
    #     try:
    #         max_pages = browser.find_element(By.XPATH, '//div/nav//li[last()-1]/div').text
    #     except selenium.common.exceptions.NoSuchElementException as e:
    #         browser.get(url)
    #         max_pages = browser.find_element(By.XPATH, '//div/nav//li[last()-1]/div').text
    #     # browser.quit()
    #     return max_pages


    def _get_average_rating(self, data):
        return re.sub("\(", "", re.sub("\)", "", data))

    # def _get_keyword(self):
    #     # scraped = open("walmart_keywords/scraped.txt", 'r').read()
    #     with open("walmart_keywords/keywords.txt", "r") as keywords:
    #         with open("walmart_keywords/scraped.txt", "a+") as scraped:
    #             for keyword in keywords.readlines():
    #                 if keyword in scraped.readlines():
    #                     continue
    #                 else:
    #                     scraped.write(keyword+"\n")
    #                     return keyword

    def _get_keyword_list(self):
        with open("walmart_keywords/keywords.txt", "r") as keywords:
            return keywords.readlines()
