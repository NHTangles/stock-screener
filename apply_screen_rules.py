import pandas as pd
import os
import yaml
from rs_data import read_json

DIR = os.path.dirname(os.path.realpath(__file__))

pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_columns', None)


SCREEN_DATA_FILE = os.path.join(DIR, "data", "screen_data.json")
TICKER_INFO_FILE = os.path.join(DIR, "data_persist", "ticker_info.json")
TICKER_INFO_DICT = read_json(TICKER_INFO_FILE)
SCREEN_DATA_DICT = read_json(SCREEN_DATA_FILE)

TITLE_TICKER = "Ticker"
TITLE_OVERMA50 = "Trading over MA50"
TITLE_LATEST_REC = "Latest Recommendation"
TITLE_BEST_REC = "Best Recommendation"
TITLE_WORST_REC = "Worst Recommendation"
TITLE_LOW_TARGET = "Lowest target growth"
TITLE_MED_TARGET = "Median target growth"
TITLE_OPT_PERIOD = "Option Period"
TITLE_LAST_SALE = "Last Sale price"

GOODSTOCKS = []

if not os.path.exists('output'):
    os.makedirs('output')

def apply_screen(ticker):
    print(ticker) #debug
    industry = TICKER_INFO_DICT[ticker]['info']['industry']
    sector = TICKER_INFO_DICT[ticker]['info']['sector']
    # No biotech or drug manufacturers
    if sector == "Healthcare":
        if "Biotech" in industry or "Drug" in industry:
            print (f"REJECT: {ticker} - industry {industry}")
            return
    sd = SCREEN_DATA_DICT[ticker]
    latest_rec = -1
    best_rec = None
    worst_rec = None
    for i in range(0 if 'period' not in sd['recs'] else len(sd['recs']['period'])):
        for k in sd['recs'].keys():
            if k == 'period': continue
            if int(sd['recs'][k][i]) > 0:
               latest_rec = i
               worst_rec = k
               if not best_rec: best_rec = k
               if "ell" in k: # sell or strongSell
                   print(f"REJECT: {ticker} - Most recent recommendations have at least one sell or strongSell")
                   return
        if latest_rec >= 0:
            break # ignore older recommendations
     
    if sd['targets']['low']:
        if sd['targets']['low'] < sd['Price']: #this one may be a little too brutal
            print(f"REJECT: {ticker} - lowest analyst target is below current price")
            return
        low_target_growth = (sd['targets']['low'] - sd['Price'])/sd['Price']
    else:
        low_target_growth = 0
    if sd['targets']['median']:
        med_target_growth = (sd['targets']['median'] - sd['Price'])/sd['Price']
        min_med_target_growth = 20
        if med_target_growth*100 < min_med_target_growth:
            print(f"REJECT: {ticker} - median analyst target is less than {min_med_target_growth}% over current price")
            return
    else:
        med_target_growth = 0
    if sd['Price'] < sd['MA200']:
        print(f"REJECT: {ticker} - Tradng below 200-day moving average")
        return
    if sd['MA50'] < sd['MA200']:
        print(f"REJECT: {ticker} - MA50 is below MA200")
        return

    ###
    over_ma50 = 'Y' if sd['Price'] > sd['MA50'] else 'N'
    GOODSTOCKS.append((ticker, over_ma50,
                       "-" if latest_rec == -1 else sd['recs']['period'][latest_rec],
                       "-" if latest_rec == -1 else f"{best_rec}({sd['recs'][best_rec][latest_rec]})",
                       "-" if latest_rec == -1 else f"{worst_rec}({sd['recs'][worst_rec][latest_rec]})",
                       low_target_growth, med_target_growth, sd['Period'], sd['Price']))
    

def main(skipEnter = False):
    for ticker in SCREEN_DATA_DICT.keys():
        apply_screen(ticker)
    df = pd.DataFrame(GOODSTOCKS, columns=[TITLE_TICKER, TITLE_OVERMA50, TITLE_LATEST_REC, TITLE_BEST_REC, TITLE_WORST_REC,
                                           TITLE_LOW_TARGET, TITLE_MED_TARGET, TITLE_OPT_PERIOD, TITLE_LAST_SALE])
    df.to_csv(os.path.join(DIR, "output", f'screened_stocks.csv'), index = False)
    print("***\nYour 'screened_stocks.csv' is in the output folder.\n***")

if __name__ == "__main__":
    main()
