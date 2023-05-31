import datetime
import numpy as np
from typing import List, Tuple
import pandas_market_calendars as mcal
import pandas as pd
import json

# We will need to import any relevant financial libraries that can provide market data
# Assuming we have a library named 'finance_lib' providing 'get_market_open', 'get_market_close', 'get_next_day' functions



def map_headlines_to_market_period(headlines: List[Tuple[str, datetime.datetime]]) -> List[Tuple[str, datetime.datetime]]:
    """
    Maps headlines to the next market period based on the time the headline was published.

    Parameters
    ----------
    headlines : List[Tuple[str, datetime.datetime]]
        List of tuples containing the headline and its publish time.

    Returns
    -------
    List[Tuple[str, datetime.datetime]]
        List of tuples containing the headline and the next market period it corresponds to.
    """
    nyse = mcal.get_calendar('NYSE')
    mapped_headlines = []

    for headline in headlines:
        publish_time = pd.Timestamp(headline['publish_time'], tz='US/Pacific')
        headline = headline['headline']
        # Get the market schedule for the day
        market_schedule = nyse.schedule(start_date=publish_time, end_date=publish_time)

        if not market_schedule.empty:
            # Convert the publish_time to the timezone of the exchange
            publish_time = publish_time.tz_convert(nyse.tz)

            # If before market open on the opening day, it can be traded by market opening of the same day
            if publish_time <= market_schedule.market_open[0]:
                trade_time = market_schedule.market_open[0]
            # If after market open but before market close, it can be traded at the same day's close
            elif market_schedule.market_open[0] < publish_time <= market_schedule.market_close[0]:
                trade_time = market_schedule.market_close[0]
            # If after market close, it can be traded at the opening price of the next day
            else:
                next_day = publish_time + pd.DateOffset(days=1)
                next_day_schedule = nyse.schedule(start_date=next_day, end_date=next_day)
                trade_time = next_day_schedule.market_open[0] if not next_day_schedule.empty else None
        else:
            trade_time = None

        if trade_time:
            mapped_headlines.append((headline, trade_time))

    return mapped_headlines



def calculate_cumulative_score(scores: List[int]) -> float:
    """
    Calculates the total score for a given list of scores.

    Parameters
    ----------
    scores : List[int]
        List of scores.

    Returns
    -------
    float
        The total score.
    """
    return np.sum(scores)

def calculate_average_score(scores: List[int]) -> float:
    """
    Calculates the average score for a given list of scores.

    Parameters
    ----------
    scores : List[int]
        List of scores.

    Returns
    -------
    float
        The average score.
    """
    return np.mean(scores)

def execute_trade(ticker: str, data: dict):
    """
    Executes a trade based on the score and saves data to a JSON file.

    Parameters
    ----------
    ticker : str
        The ticker symbol of the stock to trade.
    data : dict
        The data containing headlines, responses, scores, average score, and trade time.
    """
    # For now, just log the whole data object into a JSON file
    total_score = str(round(data['total_score']))
    average_score = str(round(data['average_score'],2))
    with open(f'data/{ticker}_{average_score}_{total_score}_data.json', 'w') as f:
        json.dump(data, f, indent=4, default=str)  # `default=str` is used to handle datetime objects

    # TODO: Implement your trading strategy here. For instance:
    # if data['average_score'] > 0, buy; if data['average_score'] < 0, sell; if data['average_score'] == 0, hold.
