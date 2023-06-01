import numpy as np
from typing import List
import pandas_market_calendars as mcal
import pandas as pd
import json
import os

def save_negative_averages(ticker_data, trade_period):
    """
    Saves the ticker data to a JSON file in a timestamped directory if average score is less than 0.

    Parameters
    ----------
    ticker_data : dict
        Dictionary containing the data for a specific ticker.

    trade_period : dict
        Dictionary containing the current trade period's details.

    ticker : str
        The ticker symbol.
    """
    # Format the timestamp to use it in the directory name
    datetime_string = trade_period['trade_buy_time'].strftime('%Y%m%d_%H%M')

    # Create a new directory if it doesn't exist
    directory = f'data/{datetime_string}'
    os.makedirs(directory, exist_ok=True)
    
    with open(f'{directory}/negative_averages.json', 'w') as outfile:
        json.dump({ticker: data for ticker, data in ticker_data.items() if data['average_score'] < 0}, outfile, indent=4, default=str)


def get_current_market_period() -> dict:
    """
    Gets the current market period along with the next market open/close time and previous market open/close time based on current time.

    Returns
    -------
    Dict[str, datetime.datetime]
        Dictionary containing the headline start time, trade buy time and trade sell time.
    """
    nyse = mcal.get_calendar('NYSE')
    now = pd.Timestamp.now(tz='US/Pacific').tz_convert('UTC')

    trading_days = nyse.valid_days(start_date=now - pd.DateOffset(days=10), end_date=now + pd.DateOffset(days=10))

    trading_periods = []

    for day in trading_days:
        market_schedule = nyse.schedule(start_date=day, end_date=day)
        trading_periods.extend([market_schedule.market_open[0], market_schedule.market_close[0]])

    trading_periods = [period.tz_convert('US/Pacific') for period in trading_periods]
    trading_periods = sorted(trading_periods)

    current_period_index = next((i for i, period in enumerate(trading_periods) if period > now.tz_convert('US/Pacific')), None)

    headline_start_time = trading_periods[current_period_index - 1] if current_period_index is not None else None
    trade_buy_time = trading_periods[current_period_index] if current_period_index is not None else None
    trade_sell_time = trading_periods[current_period_index + 1] if current_period_index is not None and len(trading_periods) > current_period_index + 1 else None

    return {
        'headline_start_time': headline_start_time,
        'trade_buy_time': trade_buy_time,
        'trade_sell_time': trade_sell_time,
    }




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

def execute_trade(ticker: str, data: dict, trade_period: dict):
    """
    Executes a trade based on the score and saves data to a JSON file.

    Parameters
    ----------
    ticker : str
        The ticker symbol of the stock to trade.
    data : dict
        The data containing headlines, responses, scores, average score, and trade time.
    trade_period : dict
        The trading period data with trading period's details.
    """
    # For now, just log the whole data object into a JSON file
    total_score = str(round(data['total_score']))
    average_score = str(round(data['average_score'],2))

    # Format the timestamp to use it in the directory name
    datetime_string = trade_period['trade_buy_time'].strftime('%Y%m%d_%H%M%S')

    # Create a new directory if it doesn't exist
    directory = f'data/{datetime_string}'
    os.makedirs(directory, exist_ok=True)

    with open(f'{directory}/{ticker}_{average_score}_{total_score}_data.json', 'w') as f:
        json.dump(data, f, indent=4, default=str)  # `default=str` is used to handle datetime objects

    # TODO: Implement your trading strategy here. For instance:
    # if data['average_score'] > 0, buy; if data['average_score'] < 0, sell; if data['average_score'] == 0, hold.

