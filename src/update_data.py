from datetime import datetime, timezone
import os
import pandas as pd
from get_historical_data import get_historical_data

def update_data(symbol):
    #get current utc time
    utc_time = datetime.now(timezone.utc)
    #get latest time from csv
    df = pd.read_csv(os.path.join('data',f"{symbol}.csv"))
    latest_time = df.iloc[0]['time']
    latest_time = datetime.strptime(latest_time, '%Y-%m-%d %H:%M:%S')
    diff = (utc_time.replace(tzinfo=None) - latest_time.replace(tzinfo=None)).total_seconds()/60
    diff = int(round(diff,0) + 1)
    updated_df = get_historical_data(symbol, "minute", diff)
    #append old data to new data
    updated_df = updated_df._append(df, ignore_index=True)
    #remove duplicates
    updated_df = updated_df.drop_duplicates(subset=['time'])
    #save to csv
    updated_df.to_csv(os.path.join('data',f"{symbol}.csv"), index=False)
    return 

if __name__ == "__main__":
    update_data("BTC-USD")