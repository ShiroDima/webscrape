# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class ScrapersItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class WalmartScraperItem(Item):
    # define the fields for your item here like:
    product_url = Field()
    image_url = Field()
    id = Field()
    name = Field()
    # brand = Field()
    average_rating = Field()
    # manufacturerName = Field()
    description = Field()
    # thumbnailUrl = Field()
    price = Field()
    time = Field()
    # currencyUnit = Field()


class KohlScraperItem(Item):
    # define the fields for your item here like:
    product_url = Field()
    image_url = Field()
    id = Field()
    name = Field()
    # brand = Field()
    average_rating = Field()
    # manufacturerName = Field()
    description = Field()
    # thumbnailUrl = Field()
    price = Field()
    time = Field()
    # currencyUnit = Field()
    
    
    
    # currencyUnit = Field()
    
    # position = Field()
    
    # id = Field()
    # type = Field()
    # brand = Field()
    # averageRating = Field()
    # manufacturerName = Field()
    # thumbnailUrl = Field()
    # price = Field()
    # currencyUnit = Field()


class TargetScraperItem(Item):
    # define the fields for your item here like:
    keyword = Field()
    page = Field()
    url = Field()
    id = Field()
    name = Field()
    brand = Field()
    averageRating = Field()
    ratingCount = Field()
    thumbnailUrl = Field()
    price = Field()
