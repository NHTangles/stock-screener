# Basic stock screener for covered calls/wheel strategy

This is forked from github.com/skyte/relative_strength, and the first step of screening is to calculate the relative strengths of all considered stocks.  It then takes the top 25% (75th percentile) of these stocks, and further screens them as follows:
- Remove stocks that don't have an option chain
- Remove biotech and pharmaceutical companies (these can sometimes be subject to sudden and unpredictable moves depending on FDA approval)
- Remove any stocks with analyst recommendations of "Sell" or "StrongSell"
- Remove any stocks with minimum analyst price target below the current price
- Remove any stocks with the median analyst price target less than 20% above the current price.
- Remove any stocks where the current price, or the 50 day moving average, is below the 200-day moving average.
**The above screening rules were made up by me, based on nothing in particular, and I make no claims whatsoever as to their usefulness.  I further do not guarantee these scripts work as described, and state that the output they produce is for informational purposes only, and am not responsible for any loss (financial or otherwise) resulting from the use of these scripts for any purpose.**
For clarity: **This does not constitute financial advice**
## relative-strength
This part is largely unchanged from the original aside from some tidying up and removing TD-Ameritrade as a datasource. Everything comes from Yahoo Finance now
From the original author: 
>IBD Style Relative Strength Percentile Ranking of Stocks (i.e. 0-100 Score).  
>I also made a TradingView indicator, but it cannot give you the percentile ranking, it just shows you the Relative Strength: https://www.tradingview.com/script/SHE1xOMC-Relative-Strength-IBD-Style/

## Considered Stocks
Tickers from ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqtraded.txt disregarding ETFs and all stocks where the industry and sector information couldn't be retrieved from yahoo finance.
## How To Run

Just run the main script.

python3 screener.py

It'll take a while to chunk through everything, but less time than it'd take you to screen by hand.

#### Separate Steps

Instead of running `screener.py` you can also:

1. Run `rs_data.py` to aggregate the price data
2. Run `rs_ranking.py` to calculate the relative strength rankings
3. Run `get_screen_data.py` to collect analyst recommendations, target prices, moving averages, etc.
4. Run `apply_screen_rules.py` to screen out the stocks.


### \*\*\* Output \*\*\*

- in the `output` folder you will find:
  - the list of ranked stocks: `rs_stocks.csv`
  - the list of ranked industries: `rs_industries.csv`
  - the list of stocks that passed the screen: `screened_stocks.csv`


## Config

The relative_strength component of this still has some configurable options.
The screening rules may become configurable at some point in the future.

#### Private File

You can create a `config_private.yaml` next to `config.yaml` and overwrite some parameters like `API_KEY`. That way you don't get conflicts when pulling a new version.

