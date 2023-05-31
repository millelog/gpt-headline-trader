from datetime import datetime
from user_agent import generate_user_agent
import requests
from lxml import html
import pandas as pd
import pandas_market_calendars as mcal
import asyncio
import pytz

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

        content.raise_for_status()  # Raise HTTPError for bad requests (4xx or 5xx)
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

def get_most_recent_trading_period_start():
    nyse = mcal.get_calendar('NYSE')
    now = pd.Timestamp.now(tz='US/Eastern')

    # Get today's schedule
    today_schedule = nyse.schedule(start_date=now, end_date=now)

    if not today_schedule.empty and now <= today_schedule.market_close[0]:
        # If we are within today's trading period, return the opening time of today
        return today_schedule.market_open[0]
    
    if not today_schedule.empty and now > today_schedule.market_close[0]:
        return today_schedule.market_close[0]

    # If we are after today's trading period or today is a non-trading day,
    # check the previous days (up to 10) to find the most recent trading period
    for days_back in range(1, 11):
        previous_day = now - pd.DateOffset(days=days_back)
        previous_day_schedule = nyse.schedule(start_date=previous_day, end_date=previous_day)
        if not previous_day_schedule.empty:
            # Return the closing time of the most recent trading day
            return previous_day_schedule.market_close[0]

    # If no trading day is found within the last 10 days, return None
    return None



def get_news(ticker):
    """
    Returns a list of sets containing news headline and url

    :param ticker: stock symbol
    :return: list
    """

    get_page(ticker)
    page_parsed = STOCK_PAGE[ticker]
    news_table = page_parsed.cssselect('table[id="news-table"]')

    if len(news_table) == 0:
        return []

    rows = news_table[0].xpath("./tr[not(@id)]")

    start_of_most_recent_trading_period = get_most_recent_trading_period_start()
    if start_of_most_recent_trading_period is None:
        # If we couldn't determine the start of the most recent trading period, return an empty list
        return []

    results = []
    date = None
    for row in rows:
        raw_timestamp = row.xpath("./td")[0].xpath("text()")[0]

        if len(raw_timestamp) > 8:
            parsed_timestamp = datetime.strptime(raw_timestamp, "%b-%d-%y %I:%M%p")  # Update the date format
            date = parsed_timestamp.date()
        else:
            parsed_timestamp = datetime.strptime(raw_timestamp, "%I:%M%p").replace(
                year=date.year, month=date.month, day=date.day)
        parsed_timestamp = parsed_timestamp.replace(tzinfo=pytz.timezone('US/Pacific'))
        if parsed_timestamp < start_of_most_recent_trading_period:
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


