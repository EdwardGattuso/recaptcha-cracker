import time
import logging as logger
from io import BytesIO

from PIL import Image
from scrapy.http import HtmlResponse
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from examtopicscrawler.captchasolver.solver import CaptchaSolver
from examtopicscrawler.middlewares.waitpageload import WaitPageLoad


def convert_selenium_cookies(selenium_cookies):
    """
    Convert selenium cookies to scrapy format
    :param selenium_cookies:
    :return:
    """
    return {s['name']: s['value'] for s in selenium_cookies}


class SeleniumMiddleware:
    """SeleniumMiddleware"""
    def __init__(self):
        """
        __init__
        """
        self.captchasolver = CaptchaSolver()

    def process_request(self, request, spider):
        """
        Process request
        :param request:
        :param spider:
        :return:
        """
        used_selenium = request.meta.get('usedSelenium', False)
        page_type = request.meta.get('pageType', '')
        if used_selenium:
            if page_type == 'non-login':
                try:
                    spider.browser.get("https://www.examtopics.com/login/")
                    username_el = spider.wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH,
                             "//input[@name='email']"))
                    )
                    time.sleep(2)
                    username_el.clear()
                    username_el.send_keys('<your-examtopics-username>')

                    password_el = spider.browser.find_element_by_xpath(
                        "//input[@name='password']")
                    time.sleep(2)
                    password_el.clear()
                    password_el.send_keys('<your-examtopics-password>')

                    login_btn_el = spider.browser.find_element_by_class_name('login-button')
                    with WaitPageLoad(spider.browser):
                        login_btn_el.click()
                    selenium_cookies = spider.browser.get_cookies()
                except Exception as e:
                    logger.error(f"Login in error, Exception = {e}")
                    return HtmlResponse(url=request.url, status=500, request=request)
                else:
                    time.sleep(3)
                    request.cookies = convert_selenium_cookies(selenium_cookies)
                    logger.info(f"selenium_cookies {request.cookies}")
                    request.meta['usedSelenium'] = False
            elif page_type == 'coordinates':
                try:
                    spider.browser.maximize_window()
                    spider.browser.get(request.url)
                    robot_btn_el = spider.wait.until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME,
                             'g-recaptcha'))
                    )
                    robot_btn_el.click()
                except Exception as e:
                    logger.error(f"Validation Captcha in error, Exception = {e}")
                    return HtmlResponse(url=request.url, status=500, request=request)
                else:
                    captcha_iframe = spider.wait.until(
                        EC.visibility_of_element_located(
                            (By.XPATH,
                             '//iframe[contains(@name, "c-")]'))
                    )
                    if captcha_iframe is not None:
                        self.coordinates_captcha_handler(captcha_iframe, spider)
                        spider.browser.switch_to.default_content()
                        selenium_cookies = spider.browser.get_cookies()
                        request.cookies = convert_selenium_cookies(selenium_cookies)
                        request.meta['usedSelenium'] = False
                        return HtmlResponse(url=request.url, body=spider.browser.page_source, status=200,
                                            request=request, encoding='utf-8')
            elif page_type == 'normal_captcha':
                try:
                    spider.browser.get(request.url)
                    normal_captcha = spider.wait.until(
                        EC.visibility_of_element_located(
                            (By.XPATH,
                             '//img[@class="captcha"]'))
                    )
                    time.sleep(2)
                    normal_captcha_screenshot = normal_captcha.screenshot_as_png
                    normal_captcha_screenshot = Image.open(BytesIO(normal_captcha_screenshot))
                    byte_array = BytesIO()
                    normal_captcha_screenshot = normal_captcha_screenshot.convert('RGB')
                    normal_captcha_screenshot.save(byte_array, format='JPEG', quality=75)
                    normal_captcha_screenshot = byte_array.getvalue()
                    with open('normal_captcha.jpeg', 'wb') as f:
                        f.write(normal_captcha_screenshot)
                    input_cap = spider.browser.find_element_by_xpath('//form//input[@name="captcha_1"]')
                    submit_btn = spider.browser.find_element_by_xpath('//form//button[@class="btn btn-primary"]')
                    time.sleep(2)
                    result = self.captchasolver.solve_normal_captcha('./normal_captcha.jpeg')
                    if result is not None:
                        input_cap.clear()
                        input_cap.send_keys(result.get('code'))
                        time.sleep(2)
                        with WaitPageLoad(spider.browser):
                            submit_btn.click()
                except Exception as e:
                    logger.error(f"Validation Captcha in error, Exception = {e}")
                    return HtmlResponse(url=request.url, status=500, request=request)
                else:
                    selenium_cookies = spider.browser.get_cookies()
                    request.cookies = convert_selenium_cookies(selenium_cookies)
                    request.meta['usedSelenium'] = False
                    return HtmlResponse(url=request.url, body=spider.browser.page_source, status=200, request=request,
                                        encoding='utf-8')

    def coordinates_captcha_handler(self, captcha_iframe, spider):
        """
        Coordinates captcha handler
        :param captcha_iframe:
        :param spider:
        :return:
        """
        screenshot = captcha_iframe.screenshot_as_png
        screenshot = Image.open(BytesIO(screenshot))
        byte_array = BytesIO()
        screenshot = screenshot.convert('RGB')
        screenshot.save(byte_array, format='JPEG', quality=75)
        screenshot = byte_array.getvalue()
        with open('captcha.jpeg', 'wb') as f:
            f.write(screenshot)
        result = self.captchasolver.solve_coordinates_captcha("./captcha.jpeg")
        if result is not None:
            groups = result.get('code').replace('coordinates:', '').replace('x=', '').replace('y=',
                                                                                              '').split(
                ';')
            result_locations = [[int(number) for number in group.split(',')] for group in groups]
            for result_location in result_locations:
                ActionChains(spider.browser).move_to_element_with_offset(captcha_iframe,
                                                                         result_location[0],
                                                                         result_location[
                                                                             1]).click().perform()
            spider.browser.switch_to.frame(captcha_iframe)
            verify_btn_el = spider.browser.find_element_by_xpath(
                '//div[@class="verify-button-holder"]//button[@id="recaptcha-verify-button"]')
            verify_btn_el.click()
            time.sleep(3)
            try:
                spider.browser.switch_to.default_content()
                re_captcha_iframe = spider.browser.find_element_by_xpath('//iframe[contains(@name, "c-")]')
                if re_captcha_iframe is not None:
                    self.coordinates_captcha_handler(re_captcha_iframe, spider)
            except Exception as e:
                logger.error(f"Exception: {e}")
