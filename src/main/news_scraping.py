# Author: Edrick
# Create date: 12/23/2022

# Libraries
import pandas as pd
import datetime
from tqdm import tqdm
from src.main.nhc_scraper import NHC_Daily_Disclosure_Scraper

# main
if __name__ == '__main__':
    ndds = NHC_Daily_Disclosure_Scraper()

if __name__ == '__extract_all_news_link_url__':
    # Update the news url dataframe
    ndds.scrape_all_urls_into_table()


if __name__ == '__extract_all_news_content__':
    # Get all news text
    news_url_csv_path = ndds.news_url_csv_path
    df_news_url = pd.read_csv(news_url_csv_path)

    # Extract the news content as text
    df_news_text = pd.DataFrame()
    records = df_news_url[['date', 'news_url']].to_dict(orient='index')
    existing_dates = df_news_text['date'].to_list()
    for record in tqdm(records.values()):
        if record['date'] not in existing_dates:
            js_news_temp = ndds.scrape_news_content(record['news_url'], record['date'])
            df_temp = pd.DataFrame.from_dict(js_news_temp, orient='index').T
            df_news_text = pd.concat([df_news_text, df_temp])

    # Date adjustment
    adj_dates = pd.to_datetime(df_news_text['date']) + datetime.timedelta(days=-1)
    df_news_text.insert(0, 'adjusted_date', adj_dates)
    # Save csv
    news_content_csv_path = ndds.news_content_csv_path
    df_news_text.to_csv(news_content_csv_path, index=False)
    # TODO: Check if the record has existed, if existed, we can skip it, we can save every record after
