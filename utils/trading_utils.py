import numpy as np
from typing import List, Tuple, Optional
import pandas_market_calendars as mcal
import pandas as pd
import json
import os
import csv
import random
import datetime

def get_trade_period(date_time: Optional[pd.Timestamp] = None) -> dict:
    """
    Gets the current market period along with the next market open/close time and previous market open/close time based on provided time.

    Parameters
    ----------
    date_time : Optional[datetime.datetime]
        The datetime object to base the start_date and end_date on. If None, uses the current time.

    Returns
    -------
    Dict[str, datetime.datetime]
        Dictionary containing the headline start time, headline end time, trade buy time and trade sell time.
    """
    nyse = mcal.get_calendar('NYSE')
    if date_time is None:
        date_time = pd.Timestamp.now(tz='US/Pacific').tz_convert('UTC')
    else:
        date_time = date_time.tz_convert('UTC')

    trading_days = nyse.valid_days(start_date=date_time - pd.DateOffset(days=10), end_date=date_time + pd.DateOffset(days=10))

    trading_periods = []

    for day in trading_days:
        market_schedule = nyse.schedule(start_date=day, end_date=day)
        trading_periods.extend([market_schedule.market_open[0], market_schedule.market_close[0]])

    trading_periods = [period.tz_convert('US/Pacific') for period in trading_periods]
    trading_periods = sorted(trading_periods)

    current_period_index = next((i for i, period in enumerate(trading_periods) if period > date_time.tz_convert('US/Pacific')), None)

    headline_start_time = trading_periods[current_period_index - 1] if current_period_index is not None else None
    headline_end_time = trading_periods[current_period_index] if current_period_index is not None else None
    trade_buy_time = trading_periods[current_period_index] if current_period_index is not None else None
    trade_sell_time = trading_periods[current_period_index + 1] if current_period_index is not None and len(trading_periods) > current_period_index + 1 else None

    return {
        'headline_start_time': headline_start_time,
        'headline_end_time': headline_end_time,
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


def remove_duplicates(existing_data):
    """
    Remove duplicates from existing data.

    This function finds all entries with the same ticker. If there are multiple
    entries, it sorts them by the length of their 'records' list, and removes the
    one with the fewest records. If there are multiple entries with the same number
    of records, it randomly chooses one to remove.
    """
    tickers = [entry['ticker'] for entry in existing_data]
    for ticker in set(tickers):
        duplicates = [entry for entry in existing_data if entry['ticker'] == ticker]
        if len(duplicates) > 1:
            # Sort duplicates by the length of their records and remove the one with fewest records
            duplicates.sort(key=lambda x: len(x['records']))
            if len(duplicates[0]['records']) == len(duplicates[1]['records']):
                # If equal, randomly select one to remove
                duplicate_to_remove = random.choice(duplicates)
            else:
                duplicate_to_remove = duplicates[0]

            # Remove the duplicate from the existing_data list
            existing_data.remove(duplicate_to_remove)
    return existing_data


def save_to_json(directory: str, action: str, ticker: str, data: dict):
    json_path = f'{directory}/{action}_data.json'

    if os.path.isfile(json_path):
        # If the file exists, read it
        with open(json_path, 'r') as f:
            existing_data = json.load(f)
    else:
        # Otherwise, create an empty list
        existing_data = []

    # Append the new data to the existing data
    new_data = {
        'ticker': ticker,
        'records': data['records'],
        'total_articles': len(data['records']),
        'average_score': data['average_score'],
        'total_score': data['total_score'],
        'buy_time': data['buy_time'],
        'sell_time': data['sell_time'],
    }
    existing_data.append(new_data)

    # Remove duplicates from the existing data
    existing_data = remove_duplicates(existing_data)

    # Write the updated data back to the file
    with open(json_path, 'w') as f:
        json.dump(existing_data, f, indent=4, default=str)  # `default=str` is used to handle datetime objects


def append_to_csv(directory: str, action: str, ticker: str, data: dict):
    with open(f'{directory}/{action}_orders.csv', 'a', newline='') as csvfile:
        fieldnames = ['ticker', 'total_articles', 'average_score', 'total_score', 'buy_time', 'sell_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writerow({
            'ticker': ticker,
            'total_articles': len(data['records']),
            'average_score': data['average_score'],
            'total_score': data['total_score'],
            'buy_time': data['buy_time'],
            'sell_time': data['sell_time'],
        })

def execute_trade(action: str, ticker: str, data: dict, trade_period: dict):
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
    datetime_string = trade_period['trade_buy_time'].strftime('%Y%m%d_%H%M')

    # Create a new directory if it doesn't exist
    directory = f'data/{datetime_string}'
    os.makedirs(directory, exist_ok=True)

    save_to_json(directory, action, ticker, data)
    append_to_csv(directory, action, ticker, data)

    # TODO: Implement your trading strategy here. For instance:
    # if data['average_score'] > 0, buy; if data['average_score'] < 0, sell; if data['average_score'] == 0, hold.


def get_tickers_with_records_above_one(sorted_tickers: List[Tuple[str, dict]], num_tickers: int) -> List[Tuple[str, dict]]:
    """
    Helper function that filters the tickers based on the length of their records.

    Parameters
    ----------
    sorted_tickers : List[Tuple[str, dict]]
        List of tuples containing sorted tickers and their data.
    num_tickers : int
        The target number of tickers to return.

    Returns
    -------
    List[Tuple[str, dict]]
        List of tuples containing filtered tickers and their data.
    """
    tickers = []
    for ticker, data in sorted_tickers:
        if len(data['records']) > 1:
            tickers.append((ticker, data))
            if len(tickers) == num_tickers:
                break
        else:
            tickers.append((ticker, data))
            num_tickers += 1
    return tickers


def get_worst_tickers(ticker_data: dict, num_tickers: int = 5) -> List[Tuple[str, dict]]:
    """
    Gets the tickers with the worst (lowest) average scores, excluding tickers with only one record.

    Parameters
    ----------
    ticker_data : dict
        Dictionary containing the ticker data.
    num_tickers : int
        The target number of tickers to return.

    Returns
    -------
    List[Tuple[str, dict]]
        List of tuples containing the worst tickers and their data.
    """

    sorted_tickers = sorted(ticker_data.items(), key=lambda x: x[1]["average_score"])
    worst_tickers = get_tickers_with_records_above_one(sorted_tickers, num_tickers)
    return worst_tickers


def get_best_tickers(ticker_data: dict, num_tickers: int = 5) -> List[Tuple[str, dict]]:
    """
    Gets the tickers with the best (highest) average scores, excluding tickers with only one record.

    Parameters
    ----------
    ticker_data : dict
        Dictionary containing the ticker data.
    num_tickers : int
        The target number of tickers to return.

    Returns
    -------
    List[Tuple[str, dict]]
        List of tuples containing the best tickers and their data.
    """
    sorted_tickers = sorted(ticker_data.items(), key=lambda x: x[1]["average_score"], reverse=True)
    best_tickers = get_tickers_with_records_above_one(sorted_tickers, num_tickers)
    return best_tickers



