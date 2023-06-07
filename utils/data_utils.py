#/utils/data_utils.py
from utils.finviz_utils import get_news
from typing import List, Dict
import json
import os
import datetime

def load_ticker_data(trade_period):
    """
    Loads the ticker data from a JSON file in a timestamped directory.

    Parameters
    ----------
    trade_period : dict
        Dictionary containing the current trade period's details.

    Returns
    -------
    dict
        Dictionary containing the data for the specific tickers.
    """
    # Format the timestamp to use it in the directory name
    datetime_string = trade_period['trade_buy_time'].strftime('%Y%m%d_%H%M')

    # Construct the file path
    file_path = f'data/{datetime_string}/ticker_data.json'
    
    if not os.path.exists(file_path):
        return {}

    with open(file_path, 'r') as infile:
        ticker_data = json.load(infile)

    return ticker_data

def save_ticker_data(ticker_data, trade_period):
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
    
    with open(f'{directory}/ticker_data.json', 'w') as outfile:
        json.dump({ticker: data for ticker, data in ticker_data.items()}, outfile, indent=4, default=str)

def get_headlines(ticker: str, trade_period) -> List[Dict[str, str]]:
    """
    Collects all news headlines for a given ticker.

    Parameters
    ----------
    ticker : str
        The ticker symbol for the stock.

    Returns
    -------
    List[Dict]
        A list of dictionaries containing 'date', 'time', 'headline' and 'url'.
    """
    headlines_data = get_news(ticker, trade_period)
    headlines = []
    for headline_data in headlines_data:
        headline = {
            'publish_time': datetime.datetime.strptime(headline_data['date'] + ' ' + headline_data['time'], '%Y-%m-%d %H:%M'),
            'headline': headline_data['headline'],
            'url': headline_data['url'],
        }
        headlines.append(headline)
    return headlines



def preprocess_headlines(headlines: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Preprocesses headlines (removes duplicates, filters irrelevant ones, etc.).

    Parameters
    ----------
    headlines : List[Dict]
        A list of dictionaries containing 'date', 'headline' and 'url'.

    Returns
    -------
    List[Dict]
        A list of preprocessed dictionaries containing 'date', 'headline' and 'url'.
    """
    # TODO: Implement your preprocessing logic here
    return headlines


def save_headlines_to_file(headlines: List[Dict[str, str]], filename: str) -> None:
    """
    Saves preprocessed headlines to a file.

    Parameters
    ----------
    headlines : List[Dict]
        A list of preprocessed dictionaries containing 'date', 'headline' and 'url'.
    filename : str
        The name of the file where the headlines will be stored.
    """
    with open(filename, 'w') as file:
        json.dump(headlines, file, indent=4, default=str)
