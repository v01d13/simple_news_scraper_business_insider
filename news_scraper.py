from bs4 import BeautifulSoup as Soup
import requests
import pandas as pd
from typing import List
from pathlib import Path
import pandas as pd
import os
import json


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

        print(f"{counter} number of articles scraped")

        df.to_csv(f"./data/{company}_fin_news.csv")
    print("Scraping completed.")


def export_details(item):
    try:
        link = item['link']
        output_file_name = link.split('/')[-1]  # get last part of the url
        output_file_name = output_file_name.split('?')[0]  # removes url search params

        output_dir = Path(f"data/{item['company']}")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = f"{str(output_dir)}/{output_file_name}.json"

        if os.path.exists(output_path):
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
                'company': item['company'],
                'date_time': item['date_time'],
                'title': item['title'],
                'link': link,
                'details': details.get_text()
            }, f)
            print(output_path)
    except Exception as ex:
        print(item['link'], ex)


def details_scraper():
    for entry in os.scandir('data'):
        if entry.name.endswith('.csv'):
            df = pd.read_csv(entry.path)
            for _, item in df.iterrows():
                export_details(item)
    

def main():
    # financialNewsScraper(["amzn", "aapl", "msft", "nvda"], 1)
    details_scraper()


if __name__ == "__main__":
    main()
