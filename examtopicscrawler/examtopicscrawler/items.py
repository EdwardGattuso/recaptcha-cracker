# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class QuestionItem(scrapy.Item):
    question_id = scrapy.Field()
    question = scrapy.Field()
    category = scrapy.Field()
    option_nums = scrapy.Field()
    option_items = scrapy.Field()
    choices = scrapy.Field()
    answer = scrapy.Field()
    discussion_id = scrapy.Field()
    discussion_html = scrapy.Field()
    images = scrapy.Field()
