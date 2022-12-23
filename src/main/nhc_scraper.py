# Author: Edrick
# Create date: 12/23/2022

# libraries
import os
import pandas as pd
import requests
import regex as re
from tqdm import tqdm
from bs4 import BeautifulSoup

from src.main.event_handler import Prompt_type
from src.main.session_creator import Session_Creator

# Class
class Nhc_Daily_Disclosure_Scraper:
    """

    """
    def __init__(self):
        self.cd_path = os.path.join('src', 'drivers', 'chromedriver.exe') # chromedriver path
        self.news_url_csv_path = os.path.join('.', 'data', 'df_news_links.csv')

        #
        self.news_home_url = r'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml'
        self.news_page_url = r'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd_{page_num}.shtml'
        self.nhc_home_url = r'http://www.nhc.gov.cn'

        # Request session
        self.session_creator = Session_Creator()
        self.rq_session = requests.session()

    # Scraping methods
    def update_session(self):
        self.rq_session = self.session_creator.prepare_session()

    def check_last_page(self):
        """
        Finding how many pages in the news home
        :return:
        """
        # Prepare the session
        self.update_session()

        # If the session is usable, we check for the last page
        res = self.rq_session.get(self.news_home_url)
        soup = BeautifulSoup(res.text, 'lxml')
        script_ele = soup.find('script', src='/xcs/xhtml/js/page.js')

        # The page rows are created by the above js
        # the following element call the function to create the div in the window
        # "createPageHTML(divName,_nPageCount, _nCurrIndex, _sPageName, _sPageExt,_nPageSum)"
        # what we need is the second argument
        function_call_re_pattern = r'createPageHTML\((.{,100})\)'
        function_call_str = re.search(function_call_re_pattern, script_ele.nextSibling.text).group(1)
        total_page_num = function_call_str.split(',')[1]

        # Make it integer and return
        return int(total_page_num)

    def scrape_links_on_pages(self, page=2):
        """

        :param page: Cannot be 1 or 0, range within 2 to max page num
        :return:
        """
        # Prepare session
        self.update_session()

        # Preapre the page url
        if page in range(2):
            page_url = self.news_home_url
        else:
            page_url = self.news_page_url.replace('{page_num}', str(page))

        # Extracting news link url
        res = self.rq_session.get(page_url)
        soup = BeautifulSoup(res.text, 'lxml')
        news_list = soup.find_all('li')
        news_dict = {}
        for news in news_list:
            ele = news.find('a')
            span = news.find('span')
            news_dict[span.text] = ele['href']

        # Format the dataframe
        df_page = pd.DataFrame.from_dict(news_dict, orient='index').reset_index()
        df_page.columns = ['date', 'news_url']

        # Complete news_url
        df_page['news_url'] = self.nhc_home_url + df_page['news_url']

        # return
        return df_page

    def scrape_all_urls_into_table(self):
        """
        One-off function, starting from next time will be updating the dataframe

        :return:
        """
        df_main = pd.DataFrame()

        # Max page number
        max_page_number = self.check_last_page()

        # Loop all the urls
        print(Prompt_type.SYS.value, 'Scraping pages url...')
        for page_num in tqdm(range(1, max_page_number+1)):
            df_temp = self.scrape_links_on_pages(page=page_num)
            df_main = pd.concat([df_main, df_temp])

        # Save the dataframe as csv
        df_main = df_main.sort_values('date', ascending=False)
        df_main.to_csv(self.news_url_csv_path, index=False)

    # Scraping the text content
    def scrape_news_content(self, news_url, date):
        # Update session
        self.update_session()
        news_json = {'date': date, 'title': None, 'para': None}

        # Request
        res = self.rq_session.get(news_url)
        soup = BeautifulSoup(res.text, 'lxml')

        # Extract Title
        news_json['title'] = soup.find_all('div', class_='tit')[0].text

        # Extract Paragraphs
        text_boxes = soup.find_all('div', id='xw_box')
        para_list = text_boxes[0].find_all('p')
        para_list = [para.text for para in para_list if para.text not in ['', '\n']]
        news_json['para'] = '\n'.join(para_list)

        return news_json
#
if __name__ == '__test__':
    ndds = Nhc_Daily_Disclosure_Scraper()
    self = ndds

    self.check_last_page()

    self.scrape_links_on_pages(page=1)

    self.update_nhc_rt_cookie()