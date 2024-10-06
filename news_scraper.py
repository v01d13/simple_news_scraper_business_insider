from bs4 import BeautifulSoup as Soup
import requests
import pandas as pd
from typing import List


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

    df = pd.DataFrame(columns=["date_time", "title", "source", "link"])

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

                df = pd.concat(
                    [
                        pd.DataFrame(
                            [[date_time, title, source, link]], columns=df.columns
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


def main():
    financialNewsScraper(["amzn", "aapl", "msft", "nvda"])


if __name__ == "__main__":
    main()
