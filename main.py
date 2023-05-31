import json
import logging
from typing import List, Tuple
from utils.data_utils import get_headlines, preprocess_headlines, save_headlines_to_file
from utils.gpt_utils import generate_prompt, get_gpt3_response, process_gpt3_response
from utils.trading_utils import map_headlines_to_market_period, calculate_cumulative_score, execute_trade, calculate_average_score
from config import TICKERS
import heapq

def main():
    logging.basicConfig(filename='logs/trading_bot.log', level=logging.INFO)
    logging.info("Starting trading bot")

    ticker_data = {}  # The dictionary to store information for each ticker

    for ticker in TICKERS:
        logging.info(f"Processing ticker {ticker}")

        # Get headlines for the ticker
        try:
            headlines = get_headlines(ticker)
            logging.info(f"Found {len(headlines)} headlines for {ticker}")
        except:
            logging.info(f"Error getting headlines for {ticker}, continuing.")
            continue

        #skip this loop if no headlines returned
        if not headlines:
            continue

        # Preprocess the headlines
        headlines = preprocess_headlines(headlines)
        logging.info(f"After preprocessing, {len(headlines)} headlines left for {ticker}")

        # Map headlines to the next market period
        headlines = map_headlines_to_market_period(headlines)
        logging.info(f"Mapped headlines to market period for {ticker}")

        records = []

        # Generate prompt and get GPT-3's response for each headline
        for headline, publish_time in headlines:
            prompt = generate_prompt(headline, ticker, publish_time)
            response = get_gpt3_response(prompt)
            score = process_gpt3_response(response)

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
        ticker_data[ticker] = {
            "records": records,
            "average_score": average_score,
            "total_score": total_score,
            "trade_time": records[0]["headline"][1] if records else None  # Assumes all headlines for the same ticker have the same trade time
        }

        if average_score < 0:
            with open('data/negative_averages.json', 'w') as outfile:
                json.dump({ticker: data for ticker, data in ticker_data.items() if data['average_score'] < 0}, outfile, indent=4, default=str)


    logging.info("Finished processing all tickers")

    # Now execute trades based on the three tickers with the lowest average scores
    worst_tickers = heapq.nsmallest(3, ticker_data.items(), key=lambda x: x[1]["average_score"])
    for ticker, data in worst_tickers:
        logging.info(f"Executing trade for {ticker} with average score {data['average_score']} and trade time {data['trade_time']}")
        execute_trade(ticker, data)

if __name__ == "__main__":
    main()
