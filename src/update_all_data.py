from update_data import update_data
import os

def update_all_data():
    #get list of symbols
    symbols = []
    for filename in os.listdir(os.path.join('data')):
        if filename.endswith(".csv") and filename != "tickers.csv":
            symbols.append(filename[:-4])
    #update data for each symbol
    for symbol in symbols:
        print(f"Updating data for {symbol}")
        update_data(symbol)
    return

if __name__ == "__main__":
    update_all_data()