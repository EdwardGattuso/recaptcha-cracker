import logging as logger
from twocaptcha import TwoCaptcha


class CaptchaSolver:

    def __init__(self):
        self.solver = TwoCaptcha('your-twocaptcha-api-key')

    def solve_normal_captcha(self, file):
        """
        Solve normal captcha
        :param file:
        :return:
        """
        try:
            result = self.solver.normal(file)
        except Exception as e:
            logger.error(f"Solver normal captcha in error, Exception = {e}")
            return None
        else:
            return result

    def solve_coordinates_captcha(self, file):
        """
        Solve coordinates captcha
        :param file:
        :return:
        """
        try:
            result = self.solver.coordinates(file)
        except Exception as e:
            logger.error(f"Solver coordinates captcha in error, Exception = {e}")
        else:
            return result
