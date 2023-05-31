#/utils/data_utils.py
from utils.finviz_utils import get_news
from typing import List, Dict
import json
import datetime
from dateutil import parser

def get_headlines(ticker: str) -> List[Dict[str, str]]:
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
    headlines_data = get_news(ticker)
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
