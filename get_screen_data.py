#!/usr/bin/env python
import json
import os
import yfinance as yf
import pandas as pd
import datetime

DIR = os.path.dirname(os.path.realpath(__file__))

if not os.path.exists(os.path.join(DIR, 'data')):
    os.makedirs(os.path.join(DIR, 'data'))
if not os.path.exists(os.path.join(DIR, 'tmp')):
    os.makedirs(os.path.join(DIR, 'tmp'))
suffix = ''
rs_rank_csv = os.path.join(DIR, 'output', f'rs_stocks{suffix}.csv')

def write_to_file(dict, file):
    with open(file, "w", encoding='utf8') as fp:
        json.dump(dict, fp, ensure_ascii=False)

def escape_ticker(ticker):
    return ticker.replace(".","-")

def get_info_from_dict(dict, key):
    value = dict[key] if key in dict else "n/a"
    # fix unicode
    # value = value.replace("\u2014", " ")
    return value

def load_ticker_info(ticker, info_dict):
    escaped_ticker = escape_ticker(ticker)
    yft = yf.Ticker(escaped_ticker)
    if not yft.options: return # no point including it if there's no option chain
    ticker_info = {}
    ticker_info['Period'] = 'Single' # only one option chain
    if len(yft.options) > 1:
        d0 = datetime.datetime.strptime(yft.options[0],"%Y-%m-%d").date()
        d1 = datetime.datetime.strptime(yft.options[1],"%Y-%m-%d").date()
        p = (d1 - d0).days
        if p < 10: # should always be 7 for weeklies but this seems safer
           ticker_info['Period'] = 'Week'
        elif p > 40: # 21, 28, or 35 for monthlies
           ticker_info['Period'] = 'Quarter'
        else:
           ticker_info['Period'] = 'Month'

    yft_info = yft.get_fast_info()
    ticker_info['MA50'] = yft_info['fiftyDayAverage']
    ticker_info['MA200'] = yft_info['twoHundredDayAverage']
    ticker_info['Price'] = yft_info['lastPrice']
    recs = yft.get_recommendations()
    rec_info = {}
    for r in recs.keys():
        rec_info[r] = list(recs[r])
    ticker_info['recs'] = rec_info
    ticker_info['targets'] = yft.get_analyst_price_targets()
    info_dict[ticker] = ticker_info

def main():
    try:
        df = pd.read_csv(rs_rank_csv)
    except:
        print ("Run the relative strength scripts first")
        return
    tickers = df['Ticker'].values
    info_dict = {}
    for t in tickers:
        load_ticker_info(t, info_dict)
    write_to_file(info_dict, os.path.join(DIR,"data","screen_data.json"))

if __name__ == "__main__":
    main()
