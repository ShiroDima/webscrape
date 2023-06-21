import scrapy
from ..items import KohlScraperItem
from bs4 import BeautifulSoup


BASE_URL = "https://www.kohls.com"
headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}


class KohlSpider(scrapy.Spider):
    name = "kohl"
    def start_requests(self):
        keyword_list = ['shoes']
        for keyword in keyword_list:
            kohl_search_url = f'{BASE_URL}/search.jsp?submit-search=web-regular&search={keyword}&spa=1&kls_sbp=14364143033523432012112151531737783468'
            yield scrapy.Request(url=kohl_search_url, 
                                 callback=self.parse_search_results, 
                                 meta={'keyword': keyword, 'page': 1},
                                 headers=headers)

    def parse_search_results(self, response):
        page = response.meta['page']
        keyword = response.meta['keyword']

        # Request Product Page
        product_list = response.css("div.product-description")
        for idx, product in enumerate(product_list):
            kohl_product_url = BASE_URL + product.css(".prod_nameBlock p::attr(rel)").get().strip()
            name = product.css(".prod_nameBlock p::text").get().strip()
            try:
                price = product.css(".prod_price_amount::text").get().strip()
            except:
                price = product.css(".prod_price_amount red_color::text").get().strip()

            item = KohlScraperItem(
                name=name,
                url=kohl_product_url,
                price=price,
                currencyUnit="dollars",
            )
            yield item
            # yield scrapy.Request(url=kohl_product_url, 
            #                     callback=self.parse_product_data,
            #                     meta={'keyword': keyword, 'page': page, 'position': idx + 1},
            #                     headers=headers)

            # Request Next Page
            if page == 1:
                # total_product_count = #
                # max_pages = math.ceil(total_product_count / 48)
                # if max_pages > 5:
                #     max_pages = 5
                max_pages = 5
                for p in range(2, max_pages):
                    kohl_search_url = f'{BASE_URL}/search.jsp?submit-search=web-regular&search={keyword}&spa=1&kls_sbp=14364143033523432012112151531737783468'
                    yield scrapy.Request(url=kohl_search_url, 
                                         callback=self.parse_search_results, 
                                         meta={'keyword': keyword, 'page': p},
                                         headers=headers)
                    
    # def parse_product_data(self, response):
    #         soup = BeautifulSoup(response.body)
    #         yield {"body": soup.prettify()}

        # for product in response.css("div.product-description"):
        #     name = product.css(".prod_nameBlock p::text").get().strip()
        #     url = BASE_URL+product.css(".prod_nameBlock p::attr(rel)").get().strip()
        #     try:
        #         price = product.css(".prod_price_amount::text").get().strip()
        #     except:
        #         price = product.css(".prod_price_amount red_color::text").get().strip()

        #     item = KohlScraperItem(
        #         name=name,
        #         url=url,
        #         price=price,
        #         currencyUnit="dollars",
        #     )

            # item = {
            #     "name": name,
            #     "price": price,
            #     "url": url, 
            # }

            # yield item

