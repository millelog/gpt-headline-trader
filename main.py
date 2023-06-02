import json
import logging
from utils.data_utils import get_headlines, preprocess_headlines, load_ticker_data, save_ticker_data
from utils.gpt_utils import generate_prompt, get_gpt3_response, process_gpt3_response
from utils.trading_utils import calculate_cumulative_score, execute_trade, calculate_average_score, get_current_market_period, get_worst_tickers, get_best_tickers
from config import TICKERS


def get_and_process_headlines(ticker, trade_period):
    # Get headlines for the ticker
    try:
        headlines = get_headlines(ticker, trade_period['headline_start_time'])
        logging.info(f"Found {len(headlines)} headlines for {ticker}")
    except:
        logging.info(f"Error getting headlines for {ticker}, continuing.")
        return None

    # Skip this loop if no headlines returned
    if not headlines:
        return None

    # Preprocess the headlines
    headlines = preprocess_headlines(headlines)
    logging.info(f"After preprocessing, {len(headlines)} headlines left for {ticker}")
    return headlines


def generate_and_store_records(headlines, ticker, ticker_data):
    records = []

    # Create a set of already processed headlines for this ticker
    processed_headlines = {}
    if ticker in ticker_data:
        processed_headlines = {record["headline"]["url"]: record for record in ticker_data[ticker].get('records', [])}

    # Generate prompt and get GPT-3's response for each headline
    for headline in headlines:
        if headline['url'] in processed_headlines:
            # If the headline is already processed, reuse its data
            record = processed_headlines[headline['url']]
        else:
            prompt = generate_prompt(headline, ticker)
            response = get_gpt3_response(prompt)
            score = process_gpt3_response(response)

            if prompt is None or response is None or score is None:
                continue

            # Create a new record
            record = {
                "headline": headline,
                "response": response,
                "score": score
            }
        
        # Append the record to the list
        records.append(record)
    
    return records




def process_ticker(ticker, trade_period, ticker_data):
    logging.info(f"Processing ticker {ticker}")

    headlines = get_and_process_headlines(ticker, trade_period)
    if not headlines:
        return None

    records = generate_and_store_records(headlines, ticker, ticker_data)

    # Calculate average score for the day
    total_score = calculate_cumulative_score([record["score"] for record in records])
    average_score = calculate_average_score([record["score"] for record in records])
    logging.info(f"Average score for {ticker}: {average_score}, {total_score}")

    # Store all the relevant information for the ticker in the dictionary
    ticker_info = {
        "records": records,
        "average_score": average_score,
        "total_score": total_score,
        "buy_time": trade_period['trade_buy_time'].strftime('%Y-%m-%d %H:%M'),
        "sell_time": trade_period['trade_sell_time'].strftime('%Y-%m-%d %H:%M')
    }

    return ticker_info



def execute_trades(ticker_data, trade_period):
    # Now execute trades based on the three tickers with the lowest average scores
    worst_tickers = get_worst_tickers(ticker_data)
    best_tickers = get_best_tickers(ticker_data)
    for ticker, data in worst_tickers:
        logging.info(f"Executing short sell trade for {ticker} with average score {data['average_score']}, total score {data['total_score']}, buy time {data['buy_time']}, and sell time {data['sell_time']}")
        execute_trade('short_sell', ticker, data, trade_period)
    for ticker, data in best_tickers:
        logging.info(f"Executing buy trade for {ticker} with average score {data['average_score']}, total score {data['total_score']}, buy time {data['buy_time']}, and sell time {data['sell_time']}")
        execute_trade('buy', ticker, data, trade_period)

def main():
    logging.basicConfig(filename='logs/trading_bot.log', level=logging.INFO)
    logging.info("Starting trading bot")

    
    trade_period = get_current_market_period()
    ticker_data = load_ticker_data(trade_period)  # The dictionary to store information for each ticker

    for ticker in TICKERS:
        ticker_info = process_ticker(ticker, trade_period, ticker_data)
        if ticker_info:
            ticker_data[ticker] = ticker_info
            save_ticker_data(ticker_data, trade_period)

    logging.info("Finished processing all tickers")
    execute_trades(ticker_data, trade_period)

if __name__ == "__main__":
    main()
