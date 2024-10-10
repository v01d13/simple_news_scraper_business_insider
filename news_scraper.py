from bs4 import BeautifulSoup as Soup
import requests
import pandas as pd
from typing import List
from pathlib import Path
import pandas as pd
import os
import json
import re
from collections import Counter
from multiprocessing import Pool


companies = ["amzn", "aapl", "msft", "nvda", 'ibm', 'nke','mmm','ba','crm','tsla']

def financialNewsScraper(companies: List[str], pages: int = 10):
    """
    Scrapes financial news articles for a list of companies from Business Insider.
    Args:
        companies (List[str]): A list of company names to scrape news for.
        pages (int, optional): The number of pages to scrape for each company. Defaults to 10.
    Returns:
        None: The function saves the scraped data to CSV files named after each company.
    Note:
        - The function uses the `requests` library to send HTTP requests.
        - The function uses the `BeautifulSoup` library to parse HTML content.
        - The function uses the `pandas` library to handle data and save it to CSV files.
    """

    df = pd.DataFrame(columns=["company", "date_time", "title", "source", "link"])

    counter = 0
    for company in companies:
        for page in range(1, pages + 1):
            output_dir = Path(f'./data/{company}_fin_news')
            output_dir.mkdir(exist_ok=True)

            output_filename =f"./data/{company}_fin_news/{page}.csv"
            if os.path.exists(output_filename):
                continue
            
            url = f"https://markets.businessinsider.com/news/{company}-stock?p={page}"

            response = requests.get(url)
            html = response.text
            soup = Soup(html, "lxml")
            articles = soup.find_all("div", class_="latest-news__story")

            for article in articles:
                date_time = article.find("time", class_="latest-news__date").get(
                    "datetime"
                )
                title = article.find("a", class_="news-link").text
                source = article.find("span", class_="latest-news__source").text
                link = article.find("a", class_="news-link").get("href")

                if link.startswith('/'):
                    link = f'https://markets.businessinsider.com{link}'

                df = pd.concat(
                    [
                        pd.DataFrame(
                            [[company, date_time, title, source, link]], columns=df.columns
                        ),
                        df,
                    ],
                    ignore_index=True,
                )
                counter += 1
            print(f"Page number of {company}: {page}")
            
            df.to_csv(output_filename)

        print(f"{company} {counter} number of articles scraped")

    print("Scraping completed.")


def export_details(item):
    try:
        link = item['link']
        output_path = item['output_path']

        if os.path.exists(output_path):
            return
        
        # dead links
        if link.__contains__('feeds.reuters.com'):
            return
        
        details = requests.get(link)
        soup = Soup(details.text, 'lxml')
        
        if link.startswith('https://markets.businessinsider.com/'):
            details = soup.find('div', class_='news-content')
        elif link.startswith('https://seekingalpha.com/'):
            return
        else:
            return
        
        if details is None:
            return
    
        with open(output_path, 'w') as f:
            json.dump({
                'date_time': item['date_time'],
                'title': item['title'],
                'link': link,
                'details': details.get_text()
            }, f)
            print(output_path)
    except Exception as ex:
        print(item['link'], ex)


def details_scraper():
    data_list = []
    total = 0
    url_list = []

    for scrip_entry in os.scandir('data'):
        if not scrip_entry.is_dir():
            continue

        for entry in os.scandir(scrip_entry.path):
            if len(data_list) > 5000:
                break
            if entry.name.endswith('.csv'):
                df = pd.read_csv(entry.path)
                for _, item in df.iterrows():

                    link = item['link']
                    if link in url_list:
                        continue

                    url_list.append(link)

                    output_file_name = link.split('/')[-1]  # get last part of the url
                    output_file_name = output_file_name.split('?')[0]  # removes url search params

                    output_path = f"./data/details/{output_file_name}.json"

                    total += 1
                    if not os.path.exists(output_path):
                        item['output_path'] = output_path
                        data_list.append(item)
                        print(len(data_list), end='\r')
    print()
    

    source_list = []
    print(total-len(data_list), total, f'Completed: {(total-len(data_list))/total:.0%}')
    for item in data_list:
        source = re.findall(r'(https?:.*\.com)', item['link'])
        source_list.extend(source)
    print(Counter(source_list))

    pool = Pool(20)
    pool.map(export_details, data_list)


def export_csv():

    def add_details(link):
        output_file_name = link.split('/')[-1]  # get last part of the url
        output_file_name = output_file_name.split('?')[0]  # removes url search params
        output_file_name = f'./data/details/{output_file_name}.json'
        
        if not os.path.exists(output_file_name):
            return ''
        
        with open(output_file_name, 'r') as f:
            details = json.load(f)
            return details['details'].replace('\n', '').replace('\r', '').strip()

    for company in companies:
        df = pd.DataFrame(columns=['company', 'date_time', 'title', 'source', 'link', 'details'])
        for entry in os.scandir(f'data/{company}_fin_news'):
            entry_df = pd.read_csv(entry.path)
            entry_df['details'] = entry_df['link'].apply(add_details)
            df = pd.concat([df, entry_df])
        df.to_csv(f'./data/{company}.csv')
    

def main():
    # financialNewsScraper(companies, 50)
    # details_scraper()

    export_csv()


if __name__ == "__main__":
    main()
