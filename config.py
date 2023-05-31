# config.py
import os

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Trading account details
TRADING_ACCOUNT_USERNAME = os.getenv("TRADING_ACCOUNT_USERNAME")
TRADING_ACCOUNT_PASSWORD = os.getenv("TRADING_ACCOUNT_PASSWORD")
TRADING_ACCOUNT_API_KEY = os.getenv("TRADING_ACCOUNT_API_KEY")


# List of S&P 500 tickers you're interested in
TICKERS =  ['TSLA', 'NVDA', 'JPM', 'JNJ'] #, 'AAPL', 'MSFT', 'GOOGL', 'META', 'AMZN', 'V', 'HD', 'PG', 'UNH', 'DIS', 'MA', 
           #'PYPL', 'BAC', 'INTC', 'VZ', 'XOM', 'KO', 'NKE', 'MCD', 'ADBE', 'IBM', 'CRM', 'CMCSA', 'CSCO', 'PEP', 
           #'AMGN', 'ABBV', 'ACN', 'MDT', 'TXN', 'ABT', 'WMT', 'AVGO', 'TMO', 'QCOM', 'COST', 'NEE', 'LIN', 'HON', 
           #'DHR', 'PM', 'PG', 'UNP', 'LLY', 'MMM', 'LOW', 'SBUX', 'CVX', 'RTX', 'GS', 'INTU', 'UPS', 'SCHW', 'BA', 
           #'BKNG', 'GILD', 'ISRG', 'CAT', 'SPGI', 'ANTM', 'BLK', 'AMT', 'BMY', 'GE', 'AMD', 'LMT', 'MO', 'WBA', 'CVS', 
           #'CI', 'PNC', 'MS', 'AXP', 'SYK', 'DUK', 'FIS', 'TJX', 'NOW', 'USB', 'C', 'SO', 'MU', 'CSX', 'T', 'PLD', 
           #'ZTS', 'CCI', 'DD', 'VRTX', 'FISV', 'ADP', 'CL', 'VRTX', 'NSC', 'D', 'EL', 'GD']

