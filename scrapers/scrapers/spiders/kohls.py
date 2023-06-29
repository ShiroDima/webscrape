from urllib.parse import urlencode
import selenium
import scrapy
from ..items import KohlScraperItem
import re
from scrapy.shell import inspect_response
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import os
from dotenv.main import load_dotenv
from datetime import datetime
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# from scrapy_playwright.page import PageMethod


BASE_URL = "https://www.kohls.com"

# API_KEY = "a137708d-feb6-45b7-8020-159f63938342"

BASE_SEARCH_URL = 'https://www.kohls.com/search.jsp?submit-search=web-regular&search={}&spa=2&kls_sbp=24887225120402166131371483924801720822'

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

class KohlSpider(scrapy.Spider):
    name = "kohls"
    allowed_domains = ["kohls.com"]
    # start_urls = [BASE_URL+"/content/navigation.html"]


    custom_settings = {
        'COLLECTION_NAME': 'walmart',
        'FEEDS': {
            './data/run2/kohls.csv': {
                'format': 'csv'
            }
        }

    }

    def start_requests(self):
        # keyword_list = ['tv']  # , 'phones', 'grills', 'household items']

        # for keyword in keyword_list:
        keyword_list = self._get_keyword_list()
        scraped = open("target_keywords/scraped.txt", 'a+')

        # for keyword in keyword_list:
        #     try:
        #         keyword = re.split(r"\d+.", keyword)[1].strip()
        #     except IndexError:
        #         keyword = re.split(r"\d+.", keyword)[0].strip()
        #     key_enc = urlencode({"keyword": keyword.lower()})
        #     if key_enc.split("=")[1] in scraped.readlines():
        #          continue
        #     # max_pages = self._get_max_pages(walmart_search_url)
        #     max_pages = self._get_max_pages(BASE_SEARCH_URL.format(keyword))
        #     if max_pages > 20:
        #         max_pages = 20
        #     print("################################################################################")
        #     print("################################################################################")
        #     print(f"STARTING KEYWORD {keyword.upper()}")
        #     print("########################################################")
        #     scraped.write(keyword)
        #     yield scrapy.Request(
        #         # url=BASE_URL+"/content/navigation.html",
        #         url=BASE_SEARCH_URL.format(keyword),
        #         callback=self._iter_products,
        #         meta={
        #             'proxy': get_proxy(),
        #             'page': 1,
        #             'max_pages': max_pages,
        #             'keyword': keyword
        #         }
        #     )
        #     scraped.write(keyword)
        keyword = self._get_keyword()
        max_pages = self._get_max_pages(BASE_SEARCH_URL.format(keyword))
        if max_pages > 20:
            max_pages = 20
        print("################################################################################")
        print("################################################################################")
        print(f"STARTING KEYWORD {keyword.upper()}")
        print("########################################################")
        scraped.write(keyword)
        yield scrapy.Request(
            # url=BASE_URL+"/content/navigation.html",
            url=BASE_SEARCH_URL.format(keyword),
            callback=self._iter_products,
            meta={
                'proxy': get_proxy(),
                'page': 1,
                'max_pages': max_pages,
                'keyword': keyword
            }
        )

    def _iter_products(self, response):
        page = response.meta["page"]
        max_pages = response.meta["max_pages"]
        keyword = response.meta["keyword"]
        crawled_products_for_page = 0
        # next_page = response.xpath('//a[@title="Next Page"]/@href').get()
        num_products_to_crawl_for_page = len(response.selector.xpath('//li[contains(@class, "products_grid")]'))
        print("######################################################################################")
        print("######################################################################################")
        print(f"CRAWLING PAGE {page} OF {keyword.upper()}")
        print("########################################################")

        for product in response.selector.xpath('//li[contains(@class, "products_grid")]'):
            crawled_products_for_page += 1
            
            item = KohlScraperItem()
            try:
                item['id'] = self._get_product_id(product.xpath("./@id").get())
            except:
                item['id'] = ""

            product_link = product.xpath('.//div[contains(@class, "prod_img_block")]/a/@href').get()
            try:

                item["product_url"] = BASE_URL + product_link
            except:
                item["product_url"] = ""

            try:
                item['name'] = product.css('div.prod_nameBlock>p::text').get().strip()
            except:
                item['name'] = ""

            try:
                item["image_url"] = self._get_image_url(product.xpath('//img[@class="pmp-hero-img"]/@srcset').get())
            except:
                item["image_url"] = ""

            try:
                item["price"] = re.sub("\$", "", product.css('div.prod_priceBlock>span.prod_price_amount::text').get())
            except:
                item["price"] = ""
            # item["average_rating"] = self._get_rating(product.css('span.prod_ratingImg>a.stars::attr(title)').get())
            try:
                item["average_rating"] = self._get_rating(product.css('span.prod_ratingImg>a.stars::attr(title)').get())
            except:
                item["average_rating"] = ""

            item["time"] = datetime.now()

            yield scrapy.Request(
                url=BASE_URL + product_link,
                callback=self._parse_description,
                cb_kwargs={
                    'item': item,
                },
                # meta={
                #     "proxy
                # }
            )

        if crawled_products_for_page==num_products_to_crawl_for_page and page < max_pages:
            yield response.follow(
                self._get_next_page_url(response.url),
                callback=self._iter_products,
                meta={
                    'page': page+1,
                    'max_pages': max_pages,
                    'keyword': keyword,
                    'proxy': get_proxy()
                },
                # dont_filter=True
            )

        

    def _parse_description(self, response, item ):
        
        item['description'] = response.selector.xpath('//div[contains(@class, "inner")][//p | //ul]').get()

        yield item


    def _get_max_pages(self, url):
        options = Options()
        options.page_load_strategy = "eager"
        # options.add_experimental_option("detach", True)
        options.add_argument('--headless=new')
        browser = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        print("#################################################################################################")
        print("GETTING MAX PAGES")
        print("#################################################################################################")
        browser.get(url)
        max_pages = re.findall("\d+", browser.find_element(By.CSS_SELECTOR, 'div.totalPages').text)[0]
        browser.quit()
        return int(max_pages)


    def _get_currency_unit(self, data):
        if data == '$':
            return 'USD'
        else:
            return 'EUR'


    def _get_product_id(self, link_id):
        return re.findall("\d+", link_id)[0]


    def _get_rating(self, rate):
        return rate.split(" ")[0]


    def _get_image_url(self, links):
        return links.split()[0]


    def _get_next_page_url(self, prev_page_url):
        options = Options()
        options.page_load_strategy = "eager"
        # options.add_experimental_option("detach", True)
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
        print("GETTING URL FOR THE NEXT PAGE")
        print("#################################################################################################")
        try:
            browser.get(prev_page_url)
            # browser.implicitly_wait(10)
            browser.find_element(By.CSS_SELECTOR, 'a.nextArw').click()
        except (selenium.common.exceptions.NoSuchElementException, Exception):
            browser.refresh()
            browser.find_element(By.CSS_SELECTOR, 'a.nextArw').click()
        browser.implicitly_wait(5)
        # page = browser.find_element(By.CSS_SELECTOR, 'input.pageInput').get_attribute('value')
        # print("#################################################################################################")
        # print(f"Page {page} URL gotten")
        # print("#################################################################################################")
        next_page_url = browser.current_url
        browser.quit()
        return next_page_url # int(page)

    def _get_keyword(self):
        # scraped = open("walmart_keywords/scraped.txt", 'r').read()
        with open("kohls_keywords/keywords.txt", "r") as keywords:
            with open("kohls_keywords/scraped.txt", "a+") as scraped:
                scraped_txts = scraped.readlines()
                for keyword in keywords.readlines():
                    try:
                        keyword = re.split(r"\d+.", keyword)[1].strip()
                    except IndexError:
                        keyword = re.split(r"\d+.", keyword)[0].strip()
                    if "+" in keyword:
                        tmp = keyword.split("+")
                        keyword = " ".join(tmp)
                        keyword = keyword.lower()
                    # key_enc = urlencode({"keyword": keyword.lower()})
                    if keyword in scraped_txts:
                        continue
                    else:
                        scraped.write(keyword.lower() + "\n")
                        return keyword



    def _get_keyword_list(self):
        with open("walmart_keywords/keywords.txt", "r") as keywords:
            return keywords.readlines()

