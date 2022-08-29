from selenium.webdriver.support.ui import WebDriverWait


class WaitPageLoad:
    """WaitPageLoad Class"""

    def __init__(self, browser, timeout=5):
        """
        __init__
        :param browser:
        :param timeout:
        """
        self.browser = browser,
        self.timeout = timeout

    def __enter__(self):
        """
        __enter__
        :return:
        """
        self.old_page = self.browser[0].find_element_by_tag_name("html")

    def __exit__(self, *_):
        """
        __exit__
        :param _:
        :return:
        """
        WebDriverWait(self.browser[0], self.timeout).until(EC.staleness_of(self.old_page))
