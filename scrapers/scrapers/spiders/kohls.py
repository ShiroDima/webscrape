import scrapy
import requests
from ..items import KohlScraperItem
from scrapy.selector import Selector


BASE_URL = "https://www.kohls.com"
headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}


class KohlSpider(scrapy.Spider):
    name = "kohls"
    custom_settings = {
        'COLLECTION_NAME' : 'kohls'
    }

    def start_requests(self):
        keyword_list = ['shoes', 'babies', 'women', 'men', 'home']
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
                price = product.css(".prod_price_amount::text").get()
            except:
                price = product.css(".prod_price_amount red_color::text").get()
            
            # clean price
            price = price.replace("$", "").replace(",", "").split("-")[0].strip()

            item = KohlScraperItem(
                keyword=keyword,
                page=page,
                name=name,
                url=kohl_product_url,
                price=price,
                currencyUnit="dollars",
                shortDescription=self.get_product_description(kohl_product_url),
                position=idx,
            )
            yield item

            # Request Next Page
            if page == 1:
                max_pages = 5
                for p in range(2, max_pages):
                    kohl_search_url = f'{BASE_URL}/search.jsp?submit-search=web-regular&search={keyword}&spa=1&kls_sbp=14364143033523432012112151531737783468'
                    kohl_search_url += f"&sks=true&PPP=48&WS={48*p}&S=1"
                    yield scrapy.Request(url=kohl_search_url, 
                                         callback=self.parse_search_results, 
                                         meta={'keyword': keyword, 'page': p},
                                         headers=headers)
                    
    def get_product_description(self, product_url):
        response = requests.get(url=product_url, headers=headers)
        sel = Selector(response=response)
        description = sel.xpath('//div[@id="productDetailsTabContent"]//p/text()').get().strip()
        return description