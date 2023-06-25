import scrapy
from ..items import KohlScraperItem
import re
from scrapy.shell import inspect_response
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime
# from scrapy_playwright.page import PageMethod


BASE_URL = "https://www.kohls.com"


class KohlSpider(scrapy.Spider):
    name = "kohls"
    allowed_domains = ["kohls.com"]
    # start_urls = [BASE_URL+"/content/navigation.html"]
    options = Options()
    # options.page_load_strategy = "eager"
    options.add_experimental_option("detach", True)
    options.add_argument('--headless=new')  # = True

    browser = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    def start_requests(self):

        #
        yield scrapy.Request(
            url=BASE_URL+"/content/navigation.html",
            callback=self.parse,
        )

    def parse(self, response):
        links = self._parse_links(response)
        # yield{
        #     'links': links
        # }
        # yield {
        #     "text": links
        # }

        for link in links:
            # yield {
            #     'link': link
            # }
            yield scrapy.Request(
                url=BASE_URL+link,
                callback=self._iter_products,
            )

            # break

    def _parse_links(self, data):
        # categories = self._get_categories(data.selector.css('a.navigation-item-link::text').getall())
        main_categories_links = data.selector.xpath('//a[contains(@class, "navigation-item-link")]/@href').getall()
        sub_categories_links = data.selector.xpath('//a[not(contains(@class, "navigation-item-link"))]/@href').getall()

        links = main_categories_links   + sub_categories_links

        # return links[0:2]
        return links
        # for link in links:
        #     data.follow(BASE_URL+link, callback=None)

    def _iter_products(self, response):
        for products in response.selector.xpath('//li[contains(@class, "products_grid")]'):
            item = KohlScraperItem()
            item['id'] = products.xpath("./@id").get()
            product_link = products.xpath('.//div[contains(@class, "prod_img_block")]/a/@href')

            yield scrapy.Request(
                url=BASE_URL+product_link.get(),
                callback=self.parse_product,
                cb_kwargs={'item': item}
            )
            # break
            # continue

        next_page = response.xpath('//a[@title="Next Page"]/@href').get()
        if next_page is not None:
            yield scrapy.Request(
                url=self._get_next_page_url(self.browser, response.url),
                callback=self._iter_products,
            )


    def parse_product(self, response, item):
        item['name'] = response.xpath('//h1[@class="product-title"]/text()').get().strip()
        item["product_url"] = response.url
        item["image_url"] = response.selector.xpath('//img[@class="pdp-image-main-img"]/@src').get()
        item["price"] = re.sub("\$", "", response.selector.xpath('//span[@class="pdpprice-row2"]/span/text()').get())
        item['description'] = response.selector.xpath('//div[contains(@class, "inner")][//p | //ul]').get()
        item["average_rating"] = response.selector.xpath('//div[contains(@class, "notranslate")]/text()').get()

        item["time"] = datetime.now()
        # item['currencyUnit'] = re.findall('\$', response.xpath('[//p[contains(@class, "pdpprice-row2")] or //span[contains(@class, "pdpprice-row2")]]/text()').get().split())[0]
        # item['currencyUnit'] = self._get_currency_unit(re.findall("\$", response.xpath('//ul[contains(@class, "pricingList")][//span or //p]/text()').get().strip())[0])

        # item['seller'] = response.selector.xpath('//div[contains(@class, "sub-product-title")]//a/text()').get().strip()

        yield item


    def _get_currency_unit(self, data):
        if data == '$':
            return 'USD'
        else:
            return 'EUR'


    def _get_next_page_url(self, browser, prev_page_url):
        browser.get(prev_page_url)
        browser.find_element(By.CSS_SELECTOR, 'a.nextArw').click()
        browser.implicitly_wait(5)
        next_page_url = browser.current_url
        browser.quit()
        return next_page_url

