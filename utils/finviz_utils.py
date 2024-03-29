from datetime import datetime
from user_agent import generate_user_agent
import requests
from lxml import html
import pandas as pd
import pandas_market_calendars as mcal
import asyncio
import pytz
import urllib3


from lxml import etree

STOCK_URL = "https://finviz.com/quote.ashx"
NEWS_URL = "https://finviz.com/news.ashx"
CRYPTO_URL = "https://finviz.com/crypto_performance.ashx"
STOCK_PAGE = {}

connection_settings = dict(
    CONCURRENT_CONNECTIONS=30,
    CONNECTION_TIMEOUT=30000,
)

class ConnectionTimeout(Exception):
    """ The request has timed out while trying to connect to the remote server. """

    def __init__(self, webpage_link):
        super(ConnectionTimeout, self).__init__(
            f'Connection timed out after {connection_settings["CONNECTION_TIMEOUT"]} while trying to reach {webpage_link}'
        )

def http_request_get(
    url, session=None, payload=None, parse=True, user_agent=generate_user_agent()
):
    """ Sends a GET HTTP request to a website and returns its HTML content and full url address. """

    if payload is None:
        payload = {}

    try:
        if session:
            content = session.get(
                url,
                params=payload,
                verify=False,
                headers={"User-Agent": user_agent},
            )
        else:
            content = requests.get(
                url,
                params=payload,
                verify=False,
                headers={"User-Agent": user_agent},
            )
        content.raise_for_status()
              # Raise HTTPError for bad requests (4xx or 5xx)
        if parse:
            return html.fromstring(content.text), content.url
        else:
            return content.text, content.url
    except (asyncio.TimeoutError, requests.exceptions.Timeout):
        raise ConnectionTimeout(url)

def get_page(ticker):
    global STOCK_PAGE

    if ticker not in STOCK_PAGE:
        STOCK_PAGE[ticker], _ = http_request_get(
            url=STOCK_URL, payload={"t": ticker}, parse=True
        )


def get_news(ticker, trade_period):
    """
    Returns a list of sets containing news headline and url

    :param ticker: stock symbol
    :return: list
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    get_page(ticker)
    page_parsed = STOCK_PAGE[ticker]
    news_table = page_parsed.cssselect('table[id="news-table"]')

    if len(news_table) == 0:
        return []

    rows = news_table[0].xpath("./tr[not(@id)]")


    results = []
    date = None
    for row in rows:
        raw_timestamp = row.xpath("./td")[0].xpath("text()")[0].strip()

        if len(raw_timestamp) > 8:
            parsed_timestamp = datetime.strptime(raw_timestamp, "%b-%d-%y %I:%M%p")  # Update the date format
            date = parsed_timestamp.date()
        else:
            parsed_timestamp = datetime.strptime(raw_timestamp, "%I:%M%p").replace(
                year=date.year, month=date.month, day=date.day)
        parsed_timestamp = parsed_timestamp.replace(tzinfo=pytz.timezone('US/Pacific'))
        if parsed_timestamp > trade_period['headline_end_time']:
            # If the news item was released after the end of the designated new period, skip it
            continue
        if parsed_timestamp < trade_period['headline_start_time']:
            # If the news item was released before the start of the most recent trading period, break the loop
            break
        if row.xpath("./td")[1].cssselect('div[class="news-link-left"] a') :
            results.append({
                'date': parsed_timestamp.strftime("%Y-%m-%d"),
                'time': parsed_timestamp.strftime("%H:%M"),
                'headline': row.xpath("./td")[1].cssselect('div[class="news-link-left"] a')[0].xpath("text()")[0] ,
                'url': row.xpath("./td")[1].cssselect('div[class="news-link-left"] a')[0].get("href"),
                'source': row.xpath("./td")[1].cssselect('div[class="news-link-right"] span')[0].xpath("text()")[0][1:-1]
            })

    return results


