import yfinance as yf
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def get_historical_data(stock_symbol, start_date, end_date):
    # Create a Ticker object for the stock symbol
    stock = yf.Ticker(stock_symbol)

    # Fetch historical data within the specified date range
    historical_data = stock.history(start=start_date, end=end_date)

    return historical_data


# Define the stock symbol and date range
stock_symbol = "AMZN"
start_date = "2020-01-01"
end_date = "2023-12-31"

# Get the historical stock data
historical_data = get_historical_data(stock_symbol, start_date, end_date)


# Print the first few rows of historical data
def get_historical_news(stock_symbol, start_date, end_date):
    # Set up the Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    # Navigate to Yahoo Finance
    driver.get(f"https://finance.yahoo.com/quote/{stock_symbol}/news?p={stock_symbol}")

    # Scroll and load news articles
    news_articles = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        articles = driver.find_elements(
            By.XPATH, '//li[contains(@class, "js-stream-content")]'
        )
        for article in articles:
            title = article.find_element(By.XPATH, ".//h3").text
            date = article.find_element(
                By.XPATH, './/span[contains(@class, "C(#959595)")]'
            ).text
            link = article.find_element(By.XPATH, ".//a").get_attribute("href")
            news_articles.append({"title": title, "date": date, "link": link})

        # Scroll down to load more articles
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for the page to load

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    driver.quit()
    return news_articles


# Get the historical news data
historical_news = get_historical_news(stock_symbol, start_date, end_date)

# Print the first few news articles
for news in historical_news[:5]:
    print(news)
print(historical_data.head())
print(historical_data.shape)
