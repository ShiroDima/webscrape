import scrapy
import json
import math
from urllib.parse import urlencode
from ..items import WalmartScraperItem
# from scrapy_playwright.page import PageMethod
import re
from datetime import datetime
import os
from dotenv.main import load_dotenv
# from scrapy_playwright.page import PageMethod

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

    # payload = {
    #     'api_key': API_KEY,
    #     'url': url,
    #     # "render_js": 'true'
    # }

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
        keyword = self._get_keyword()

        payload = {'q': keyword,
                   #    'sort': 'best_seller',
                   'page': 1, 'affinityOverride': 'default'}
        walmart_search_url = 'https://www.walmart.com/search?' + urlencode(payload)
        max_pages = self._get_max_pages(walmart_search_url)
        yield scrapy.Request(url=walmart_search_url,
                             callback=self.parse_search_results,
                             meta={
                                 'keyword': keyword,
                                 'page': 1,
                                 'max_pages': int(max_pages),
                                 'proxy': get_proxy()
                             },
                             )

    def parse_search_results(self, response):

        page = response.meta['page']
        keyword = response.meta['keyword']
        max_pages = response.meta["max_pages"]
        is_next_page = response.selector.xpath("//a[@aria-label='Next Page']")
        # max_pages = response.selector.xpath('//div/nav//li[last()-1]/div').get()
        # script_tag = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        # max_pages = response.css('#maincontent > main > div > div:nth-child(2) > div > div > div:nth-child(2) > nav').get()
        # yield {
        #     "max_pages": max_pages,
        #     "is_next_page": is_next_page,
        #     # 'script_tag': script_tag
        #     'text': response.text
        # }
        script_tag = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()

        if script_tag is not None:
            json_blob = json.loads(script_tag)
            print("##################################")
            print(f"Scraping Page {page}")
            # Request Product Page
            product_list = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"][0]["items"]
            # first_prod = product_list[0].get("id")
            # page += 1
            # if type(product_list).__name__ == "list":
            #     product_list = product_list[0]
            # ids = [prod.get("id") for prod in product_list]
            # if page != 1:
            #     if prod_list[0].get("id") not in ids:
            # yield{
            #     'page': page
            # }   
            for _, product in enumerate(product_list):
                item = WalmartScraperItem()
                # '//span[@itemprop="price"]/text()'
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

                yield item
                # walmart_product_url = BASE_URL + product.get('canonicalUrl', '').split('?')[0]
                # yield {
                #     "product": product
                # }
                # yield scrapy.Request(url=walmart_product_url,
                #                     callback=self.parse_product_data,
                #                     meta={
                #                         'keyword': keyword, 
                #                         'page': page, 
                #                         'position': idx + 1,
                #                         'proxy': get_proxy()
                #                         }
                #                     # headers=headers
                #                     )

            # # Request Next Page
            # if page == 1:
            #     # total_product_count = json_blob["props"]["pageProps"][
            #     #     "initialData"]["searchResult"]["itemStacks"][0]["count"]
            #     # max_pages = math.ceil(total_product_count / 40)
            #     # if max_pages > 5:
            #     #     max_pages = 5

            #     for p in range(2, max_pages):
            #         payload = {'q': keyword, 'sort': 'best_seller',
            #                 'page': page+1, 'affinityOverride': 'default'}
            #         walmart_search_url = 'https://www.walmart.com/search?' + urlencode(payload)
            #         # yield response.follow(
            #         #     walmart_search_url,
            #         #     callback=self.parse_search_results
            #         # )

            # payload = {'q': keyword, 'sort': 'best_seller',
            #             'page': page+1, 'affinityOverride': 'default'}
            # walmart_search_url = 'https://www.walmart.com/search?' + urlencode(payload)
            if page < max_pages:
                payload = {'q': keyword, 'sort': 'best_seller',
                           'page': page + 1, 'affinityOverride': 'default'}
                walmart_search_url = 'https://www.walmart.com/search?' + urlencode(payload)
                yield response.follow(
                    walmart_search_url,
                    callback=self.parse_search_results,
                    meta={
                        'keyword': keyword,
                        'page': page + 1,
                        'max_pages': max_pages,
                        # 'proxy': get_proxy()
                    }
                )

                # yield scrapy.Request(
                #     url=walmart_search_url,
                #     callback=self.parse_search_results,
                #     meta={
                #         'keyword': keyword,
                #         'page': page+1}
                #         )
                #  headers=headers
                # )
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
        item["average_rating"] = self._get_average_rating(
            response.selector.xpath('//span[contains(@class, "rating-number")]/text()').get())
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
            item["average_rating"] = self._get_average_rating(
                response.selector.xpath('//span[contains(@class, "rating-number")]/text()').get())
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

    def _get_max_pages(self, url):
        options = Options()
        options.page_load_strategy = "eager"
        options.add_experimental_option("detach", True)
        options.add_argument('--headless=new')
        # options.add_argument(f'--proxy-server={get_proxy()}')  # = True
        # options.add_argument("--disable-extensions")
        # options.add_argument("--silent")
        # options.add_argument("test-type")
        # options.add_experimental_option('excludeSwitches', ['enable-logging'])
        browser = webdriver.Chrome(
            # service=Service(ChromeDriverManager().install()),
            options=options
        )
        print("#################################################################################################")
        print("Getting Max Pages")
        browser.get(url)
        max_pages = browser.find_element(By.XPATH, '//div/nav//li[last()-1]/div').text
        # browser.quit()
        return max_pages

    # def _load_product_page(self, browser, product_url):
    #     wait = WebDriverWait(browser, 20)
    #     browser.get(product_url)
    #     img_frame = browser.find_element(By.CSS_SELECTOR, 'img.pdp-image-main-img')
    #     span_frame = browser.find_element(By.XPATH, '//span[@class="pdpprice-row2"]/span/text()')
    #     img_frame = wait.until(
    #         EC.visibility_of(img_frame)
    #     )
    #     wait.until(
    #         EC.visibility_of_element_located((By.CLASS_NAME, "pdp-main-bazarvoice-ratings"))
    #     )
    #     # wait.until(
    #     #     EC.visibility_of(span_frame)
    #     # )

    #     return img_frame

    def _get_average_rating(self, data):
        return re.sub("\(", "", re.sub("\)", "", data))

    def _get_keyword(self):
        # scraped = open("walmart_keywords/scraped.txt", 'r').read()
        with open("walmart_keywords/keywords.txt", "r") as keywords:
            with open("walmart_keywords/scraped.txt", "a+") as scraped:
                for keyword in keywords.readlines():
                    if keyword in scraped.readlines():
                        continue
                    else:
                        scraped.write(keyword)
                        return keyword
