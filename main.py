import json
import logging
from typing import List, Tuple
from utils.data_utils import get_headlines, preprocess_headlines, save_headlines_to_file
from utils.gpt_utils import generate_prompt, get_gpt3_response, process_gpt3_response
from utils.trading_utils import calculate_cumulative_score, execute_trade, calculate_average_score, get_current_market_period, save_negative_averages
from config import TICKERS
import heapq


def process_ticker(ticker, trade_period):
    logging.info(f"Processing ticker {ticker}")

    # Get headlines for the ticker
    try:
        headlines = get_headlines(ticker, trade_period['headline_start_time'])
        logging.info(f"Found {len(headlines)} headlines for {ticker}")
    except:
        logging.info(f"Error getting headlines for {ticker}, continuing.")
        return None

    #skip this loop if no headlines returned
    if not headlines:
        return None

    # Preprocess the headlines
    headlines = preprocess_headlines(headlines)
    logging.info(f"After preprocessing, {len(headlines)} headlines left for {ticker}")

    records = []

    # Generate prompt and get GPT-3's response for each headline
    for headline in headlines:
        prompt = generate_prompt(headline, ticker)
        response = get_gpt3_response(prompt)
        score = process_gpt3_response(response)

        if prompt is None or response is None or score is None:
            continue

        # Store the headline, response, and score as a record
        records.append({
            "headline": headline,
            "response": response,
            "score": score
        })

    # Calculate average score for the day
    total_score = calculate_cumulative_score([record["score"] for record in records])
    average_score = calculate_average_score([record["score"] for record in records])
    logging.info(f"Average score for {ticker}: {average_score}, {total_score}")

    # Store all the relevant information for the ticker in the dictionary
    ticker_info = {
        "records": records,
        "average_score": average_score,
        "total_score": total_score,
        "buy_time": trade_period['trade_buy_time'],
        "sell_time": trade_period['trade_sell_time']
    }

    return ticker_info


def execute_trades(ticker_data, trade_period):
    # Now execute trades based on the three tickers with the lowest average scores
    worst_tickers = heapq.nsmallest(3, ticker_data.items(), key=lambda x: x[1]["average_score"])
    for ticker, data in worst_tickers:
        logging.info(f"Executing trade for {ticker} with average score {data['average_score']} and trade time {data['trade_time']}")
        execute_trade(ticker, data, trade_period)


def main():
    logging.basicConfig(filename='logs/trading_bot.log', level=logging.INFO)
    logging.info("Starting trading bot")

    ticker_data = {}  # The dictionary to store information for each ticker
    trade_period = get_current_market_period()

    for ticker in TICKERS:
        ticker_info = process_ticker(ticker, trade_period)
        if ticker_info:
            ticker_data[ticker] = ticker_info
            save_negative_averages(ticker_data, trade_period)

    logging.info("Finished processing all tickers")
    execute_trades(ticker_data, trade_period)


if __name__ == "__main__":
    main()
