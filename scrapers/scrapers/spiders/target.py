import scrapy
import requests
import json
from urllib.parse import urlencode

from ..items import TargetScraperItem


class TargetSpider(scrapy.Spider):
    name = "target"

    def start_requests(self):
        keyword_list = ['laptop', 'iphone']

        for keyword in keyword_list:
            payload = {
                'key': '9f36aeafbe60771e321a7cc95a78140772ab3e96',
                'channel': 'WEB',
                'count': '24',
                'default_purchasability_filter': 'true',
                'include_sponsored': 'true',
                'keyword': keyword,
                'offset': '0',
                'page': '/s/' + keyword,
                'platform': 'desktop',
                'pricing_store_id': '1771',
                'store_ids': '1771,1768,1113,3374,1792',
                'useragent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
                'visitor_id': '0188234D388B0201908FB68437D20911',
                'zip': '52404',
            }
            api_url = 'https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2?' + urlencode(payload)

            yield scrapy.Request(api_url , callback=self.parse_products_lists, meta={'keyword': keyword, 'page': 0})



    def parse_products_lists(self, response):
        page = response.meta['page']
        keyword = response.meta['keyword']

        data = response.json()
        total_pages = data['data']['search']['search_response']['metadata']['total_pages']

        products_list = data['data']['search']['products']

        for product in products_list:

            rating = {}

            try:
                rating['averageRating'] = product['ratings_and_reviews']['statistics']['rating']['average']
            except:
                rating['averageRating'] = None

            try:
                rating['count'] = product['ratings_and_reviews']['statistics']['rating']['count']
            except:
                rating['count'] = None

            item = TargetScraperItem(
                keyword = keyword,
                page = page,
                url = product['item']['enrichment']['buy_url'],
                id = product['tcin'],
                name = product['item']['product_description']['title'],
                brand = product['item']['primary_brand']['name'],
                averageRating = rating['averageRating'],
                ratingCount = rating['count'],
                thumbnailUrl = [product['item']['enrichment']['images']['primary_image_url']] + product['item']['enrichment']['images']['alternate_image_urls'],
                price = product['price']['formatted_current_price']
            )

            yield item

        if total_pages > page:
            payload = {
                'key': '9f36aeafbe60771e321a7cc95a78140772ab3e96',
                'channel': 'WEB',
                'count': '24',
                'default_purchasability_filter': 'true',
                'include_sponsored': 'true',
                'keyword': keyword,
                'offset': 24 * (page + 1),
                'page': '/s/' + keyword,
                'platform': 'desktop',
                'pricing_store_id': '1771',
                'store_ids': '1771,1768,1113,3374,1792',
                'useragent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
                'visitor_id': '0188234D388B0201908FB68437D20911',
                'zip': '52404',
            }
            api_url = 'https://redsky.target.com/redsky_aggregations/v1/web/plp_search_v2?' + urlencode(payload)

            yield scrapy.Request(api_url , callback=self.parse_products_lists, meta={'keyword': keyword, 'page': page})
