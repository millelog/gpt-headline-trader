# GPT-3 Headline Trader

This is a simple trading bot project that uses the GPT-3 model provided by OpenAI to analyze financial news headlines and decide on trading actions. The bot retrieves recent headlines for a given list of tickers, analyzes them using GPT-3, and then decides to trade based on the analysis results.

## Setup

To get the bot running, follow these steps:

1. Clone the repository to your local machine:

```
git clone https://github.com/your-repo/gpt-headline-trader.git
cd gpt-headline-trader
```

2. Install the required Python packages:

```
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your OpenAI API Key. You can get this key from your OpenAI account dashboard.

```
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

4. Set the list of tickers you're interested in. You can modify the list in the `config.py` file:

```python
TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
```

5. Run the bot:

```
python main.py
```

## How it works

The bot works by following these steps:

1. Retrieves recent headlines for each ticker.
2. Preprocesses the headlines to ensure they're suitable for the GPT-3 model.
3. Generates a prompt for each headline and asks GPT-3 for a response.
4. Based on the GPT-3 response, decides whether to buy or sell the ticker.
