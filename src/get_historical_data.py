import pandas as pd
import requests
import time
import os

def get_historical_data(symbol, frequency, length):
    """
    Obtains historical price data for a given cryptocurrency and saves it to a CSV file.
    
    Args:
        symbol (str): The symbol of the cryptocurrency to get data for (e.g., BTC-USD).
        frequency (str): The frequency of the data (e.g., 'day', 'hour', 'minute').
        length (int): The length of the data to retrieve (in units of the specified frequency).
        
    Returns:
        None
    """
    # Define the API endpoint URL
    endpoint = f"https://api.pro.coinbase.com/products/{symbol}/candles"

    if frequency == "day":
        s_granularity = "86400"
    elif frequency == "hour":
        s_granularity = "3600"
    elif frequency == "minute":
        s_granularity = "60"
    else:
        print("Error: Invalid frequency")
        return None

    # Set the parameters for the API request
    params = {
        "granularity": s_granularity,
        "start": "",
        "end": "",
    }
    #params['start'] = str(int(params['start']) + int(s_granularity)*300)

    # Create an empty list to hold the data
    data = []

    # Loop through the API results until we have retrieved the desired length of data
    while len(data) < length:
        # Make the API request
        response = requests.get(endpoint, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response and append the data to our list
            data += response.json()

            # Set the start time for the next request to be the end time of the previous request
            params["end"] = data[-1][0]
            params['start'] = str(int(params['end']) - int(s_granularity)*300)

            # Sleep for a short time to avoid hitting the rate limit
            time.sleep(0.1)
        else:
            # If the request failed, print an error message and return None
            raise Exception(f"Error: API request failed with status code {response.status_code}")

    # Convert the data to a Pandas DataFrame and save it to a CSV file
    df = pd.DataFrame(data, columns=["time", "low", "high", "open", "close", "volume"])
    df["time"] = pd.to_datetime(df["time"], unit="s")
    filename = f"{symbol}_{frequency}.csv"
    return df

if __name__ == "__main__":
    #define inputs
    symbols = ["BTC-USD","ETH-USD","LTC-USD","BCH-USD","XRP-USD","DOGE-USD","SOL-USD","AVAX-USD","MATIC-USD",
    "ADA-USD","DOT-USD","LINK-USD","UNI-USD","LUNA-USD","ATOM-USD","FIL-USD","TRX-USD","XLM-USD","VET-USD","EOS-USD",
    "THETA-USD","XMR-USD","NEO-USD","ETC-USD","AAVE-USD","MKR-USD","ALGO-USD","XTZ-USD","COMP-USD","HBAR-USD","DASH-USD",
    ]
    frequency = "minute"
    length = 45000
    for symbol in symbols:
        # Get the historical data for coin
        try:
            print(f"Getting {frequency} data for {symbol}")
            df = get_historical_data(symbol, frequency, length)
            filename = f"{symbol}.csv"
            df.to_csv(os.path.join(os.getcwd(),'data',filename), index=False)
        except:
            print(f"Error: Could not get data for {symbol}")
            continue
