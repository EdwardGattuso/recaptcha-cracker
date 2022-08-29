import random
import time
import logging as logger

import scrapy
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from examtopicscrawler.items import QuestionItem
from scrapy.utils.project import get_project_settings
from scrapy import signals
from pydispatch import dispatcher


def error_handler(failure):
    """
    error_handler
    :param failure:
    :return:
    """
    logger.error(f"request error: {failure}")


class ExamtopicsSpider(scrapy.Spider):
    """ExamtopicsSpider"""

    name = 'examtopics'
    allowed_domains = ['examtopics.com']

    host = 'https://www.examtopics.com/'
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'COOKIES_ENABLED': True,
        'DOWNLOADER_MIDDLEWARES': {
            'examtopicscrawler.middlewares.selenium.SeleniumMiddleware': 543,
            'scrapy.downloadrmiddlewares.useragent.UserAgentMiddleware': None
        }
    }

    def __init__(self, url=None, category=None, *args, **kwargs):
        """
        __init__
        :param url:
        :param category:
        :param args:
        :param kwargs:
        """
        super(ExamtopicsSpider, self).__init__(*args, **kwargs)
        self.url = url
        self.category = category
        self.mySetting = get_project_settings()
        self.timeout = self.mySetting['SELENIUM_TIMEOUT']
        self.isLoadImage = self.mySetting['LOAD_IMAGE']
        self.windowHeight = self.mySetting['WINDOW_HEIGHT']
        self.windowWidth = self.mySetting['WINDOW_WIDTH']
        options = webdriver.FirefoxOptions()
        options.headless = True
        options.add_argument("--disable-gpu")
        self.browser = webdriver.Firefox(options=options)
        if self.windowHeight and self.windowWidth:
            self.browser.set_window_size(self.windowWidth, self.windowHeight)
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)
        super(ExamtopicsSpider, self).__init__()
        dispatcher.connect(receiver=self.close_handler, signal=signals.spider_closed)

    def start_requests(self):
        """
        start_requests
        :return:
        """
        if self.url is not None:
            yield scrapy.Request(
                url=self.url,
                meta={'usedSelenium': True, 'pageType': 'login'},
                callback=self.parse,
                errback=error_handler
            )

    def parse(self, response, **kwargs):
        """
        parse
        :param response:
        :param kwargs:
        :return:
        """
        questions = response.css('.exam-question-card')
        cookies = response.request.cookies
        if len(questions) == 0:
            robot_btn = response.css('.captcha-container .g-recaptcha').extract_first()
            captcha = response.xpath('//img[@class="captcha"]').extract_first()
            if robot_btn is not None:
                yield scrapy.Request(
                    url=response.url,
                    cookies=cookies,
                    meta={'usedSelenium': True, 'pageType': 'coordinates'},
                    callback=self.parse,
                    errback=error_handler,
                    dont_filter=True
                )
            elif captcha is not None:
                yield scrapy.Request(
                    url=response.url,
                    cookies=cookies,
                    meta={'usedSelenium': True, 'pageType': 'normal_captcha'},
                    callback=self.parse,
                    errback=error_handler,
                    dont_filter=True
                )
            return
        for question in questions:
            item = QuestionItem()
            item['category'] = self.category
            item['images'] = question.xpath(
                'div[@class="card-body question-body"]/p[@class="card-text"]/img[@class="in-exam-image"]/@src'
            ).extract()
            item['question'] = ''.join(
                question.xpath('div[@class="card-body question-body"]/p[@class="card-text"]/text()').extract()).strip()
            item['option_nums'] = question.xpath(
                'div[@class="card-body question-body"]/div[@class="question-choices-container"]//li[contains(@class, "multi-choice-item")]/span/text()'
            ).extract()
            item['option_items'] = question.xpath(
                'div[@class="card-body question-body"]/div[@class="question-choices-container"]//li[contains(@class, "multi-choice-item")]/text()'
            ).extract()
            item['answer'] = question.xpath(
                'div[@class="card-body question-body"]/p[contains(@class, "question-answer")]//span[@class="correct-answer"]/text()'
            ).extract_first()
            data_id = question.xpath('div[@class="card-body question-body"]/@data-id').extract_first()
            if data_id is not None:
                item['discussion_id'] = data_id
                time.sleep(3)
                yield scrapy.Request(
                    url='https://www.examtopics.com/ajax/discussion/exam-question/' + data_id,
                    meta={'usedSelenium': False, 'item': item},
                    callback=self.parse_discussion_res,
                    errback=error_handler,
                )
            else:
                yield item

        next_questions = response.xpath('//a[@class="btn btn-success pull-right"]').css(
            'a::attr("href")').extract_first()

        next_url = response.urljoin(next_questions)
        if next_url is not None:
            self.url = next_url
        time.sleep(random.randint(1, 6))

        yield scrapy.Request(
            url=next_url,
            cookies=cookies,
            meta={'usedSelenium': False},
            callback=self.parse,
            errback=error_handler,
        )

    def parse_discussion_res(self, response):
        """
        parse_discussion_res
        :param response:
        :return:
        """
        item = response.meta['item']
        item['discussion_html'] = response.body
        yield item

    def close_handler(self, spider):
        """
        close_handler
        :param spider:
        :return:
        """
        self.browser.quit()
