# Author: Edrick
# Create date: 12/23/2022

# Libraries
import os
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

from src.main.event_handler import Prompt_type

# Class
class Session_Creator:
    def __init__(self):
        self.cd_path = os.path.join('src', 'drivers', 'chromedriver.exe') # chromedriver path

        #
        self.news_home_url = r'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml'
        self.news_page_url = r'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd_{page_num}.shtml'
        self.nhc_home_url = r'http://www.nhc.gov.cn'

        # Request session
        self.rq_session = requests.session()

    def update_nhc_rt_cookie(self):
        # Create session
        self.rq_session = requests.session()

        # Open driver
        driver = self._create_driver(headless=True)

        # Navigate
        # self._navigate_to_url(driver, self.nhc_home_url)
        self._navigate_to_url(driver, self.news_home_url)

        # Save the cookies
        self._update_session_cookies(driver)
        # self._check_cookies()

        # Validate the cookies
        if not self._test_cookies():
            print(Prompt_type.ERROR.value, 'Invalid real time cookies for scraping, maybe expired?')
        else:
            print(Prompt_type.SYS.value, 'Session cookie updated...')

        # Close the driver
        driver.quit()

    def _create_driver(self, headless=True):
        # Set up chrome options
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        # the headless option
        if headless:
            chrome_options.add_argument("--headless")

        # Randomize the user-agent - proved to be unnecessary, but I will leave it here
        ua = UserAgent()
        userAgent = ua.random
        chrome_options.add_argument(f'user-agent={userAgent}')

        # Open driver with the preset options
        driver = Chrome(self.cd_path, chrome_options=chrome_options)

        return driver

    @staticmethod
    def _navigate_to_url(driver, url):
        driver.get(url)

    def _update_session_cookies(self, driver):
        for cookie in driver.get_cookies():
            self.rq_session.cookies.update({cookie['name']: cookie['value']})

    def _test_cookies(self):
        res = self.rq_session.get(self.news_home_url)
        if res.status_code != 200:
            return False
        else:
            return True

    def _check_cookies(self):
        for i in self.rq_session.cookies.items():
            print(i)

    def prepare_session(self):
        if not self._test_cookies():
            self.update_nhc_rt_cookie()
        return self.rq_session