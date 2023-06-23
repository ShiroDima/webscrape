import scrapy
from ..items import KohlScraperItem
import re
from scrapy.shell import inspect_response



BASE_URL = "https://www.kohls.com"

class KohlSpider(scrapy.Spider):
    name = "kohls"
    allowed_domains = ["kohls.com"]
    # start_urls = [BASE_URL+"/content/navigation.html"]
    

    def start_requests(self):
        
    #     
        yield scrapy.Request(url=BASE_URL+"/content/navigation.html", callback=self.parse)

    def parse(self, response):
        links = self._parse_links(response)

        # yield {
        #     "text": links
        # }

        for link in links:
            yield scrapy.Request(
                url = BASE_URL+link,
                callback=self._iter_products
            )
            # for product in products:
            #     # yield  self.parse_product(product)
            #     yield product
            # yield {
            #     'link': link
            # }

        # for category in categories:
        # yield {
            
        #     # 'text': response.xpath('//h3/a/@href').getall()
        #     'text': response.selector.xpath('//a[not(contains(@class, "navigation-item-link"))]/@href').getall()
        # }
        # with open('image.png', 'wb') as image_file:
        #     image_file.write(response.meta["screenshot"])
    
    def _parse_links(self, data):
        # categories = self._get_categories(data.selector.css('a.navigation-item-link::text').getall())
        main_categories_links = data.selector.xpath('//a[contains(@class, "navigation-item-link")]/@href').getall()
        # sub_categories_links = data.selector.xpath('//a[not(contains(@class, "navigation-item-link"))]/@href').getall()

        links =  main_categories_links #+ sub_categories_links

        return links[0:2]
        # for link in links:
        #     data.follow(BASE_URL+link, callback=None)

    def _iter_products(self, response):
        # num = len(response.selector.xpath('//li[contains(@class, "products_grid")]').getall())
        # yield {
        #         'num_of_prods': num,
        #         "url": response.url
        #     }
        #   inspect_response(data, self)
        for products in response.selector.xpath('//li[contains(@class, "products_grid")]'):
            item = KohlScraperItem()
            # yield {
            #     "product": products.xpath("./@id").get()
            # }
            item['id'] = products.xpath("./@id").get()
            product_link = products.xpath('.//div[contains(@class, "prod_img_block")]/a/@href')

            yield scrapy.Request(
                url=BASE_URL+product_link.get(),
                callback=self.parse_product,
                cb_kwargs={'item': item}
            )

            # for product in product_links:
                # yield {
                #     'id': products.xpath("./@id").get()
                # }
                # item = KohlScraperItem()
                # item['id'] = products.xpath("./@id").get()
                # yield scrapy.Request(
                #     url=BASE_URL+product.get(),
                #     callback=self.parse_product,
                #     cb_kwargs={'item': item}
                # )

    def parse_product(self, response, item):
        item['name'] = response.xpath('//h1[contains(@class, "product-title")]/text()').get().strip()
        # item['currencyUnit'] = re.findall('\$', response.xpath('[//p[contains(@class, "pdpprice-row2")] or //span[contains(@class, "pdpprice-row2")]]/text()').get().split())[0]
        # item['currencyUnit'] = self._get_currency_unit(re.findall("\$", response.xpath('//ul[contains(@class, "pricingList")][//span or //p]/text()').get().strip())[0])

        
        # KohlSpider.product_url = BASE_URL + data.xpath('//div/a/@href')

        item['seller'] = response.selector.xpath('//div[contains(@class, "sub-product-title")]//a/text()').get().strip()
        item['shortDescription'] = response.selector.xpath('//div[contains(@class, "inner")][//p | //ul]').get()
        # data.follow(product_url, callback=self._parse_product_page)
        # for product_link in data.selector.xpath('//li[contains(@class, "products_grid")]/@id'):
        
        # print("##############################################################")
        # print("##############################################################")
        # print("##############################################################")
        # print(data)

        yield item
        # for link in self._iter_products(data):
            
            

    def _get_currency_unit(self, data):
        if data is '$':
            return 'USD'
        else:
            return 'EUR'

        # return (seller, product_details)