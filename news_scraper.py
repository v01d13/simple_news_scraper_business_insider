import requests
from bs4 import BeautifulSoup as Soup
from typing import Dict, List, Optional
import re
from multiprocessing import Pool, cpu_count


class NewsScraper:

    def __init__(self):
        self.cpu = cpu_count()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
        }

    def fetch_html(self, link: str) -> tuple[Optional[Soup()], str]: # type: ignore
        try:
            response = requests.get(link, headers=self.headers)
            if response.status_code != 200:
                domain = re.search(r"https?://(?:www\.)?([^.]+)", link)

                print(f"{domain.group(1)} Status code: {response.status_code}")
                return None, link
            details_html = response.text
            details = Soup(details_html, "lxml")
            return details, link
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None, link

    def fetch_helper(self, links: List[str], sources: List[str]) -> Dict:
        data = {}
        assert len(links) == len(sources)
        with Pool(processes=self.cpu) as pool:
            results = pool.map(self.fetch_html, links)
            for details, link in results:
                if details is not None:
                    data[link] = details
        return data

    def financialNewsScraper(self, companies: List[str], pages: int = 10):
        for company in companies:
            for page in range(1, pages + 1):
                details = []
                urls = []
                sources = []

                url = (
                    f"https://markets.businessinsider.com/news/{company}-stock?p={page}"
                )
                response = requests.get(url, headers=self.headers)

                if response.status_code != 200:
                    print(f"Failed to retrieve the {company} page {page}")
                    continue

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
                    if link.startswith("/"):
                        link = f"https://markets.businessinsider.com{link}"
                    urls.append(link)
                    sources.append(source)

                # Fetch details for each URL
                data = self.fetch_helper(urls, sources)
                print(
                    f"Page {page} of company {company} done. Collected {len(data)} articles."
                )


scrape = NewsScraper()
scrape.financialNewsScraper(["aapl", "amzn", "msft", "nvda"])
