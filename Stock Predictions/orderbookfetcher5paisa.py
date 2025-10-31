import requests
import pandas as pd
import time
import os

class BinanceOrderBook:
    def __init__(self, asset: str, trading_pair_suffix: str = "USDT", depth_limit: int = 20):
        """
        Initialize the BinanceOrderBook fetcher.
        
        :param asset: Base asset symbol, e.g. 'BTC', 'ETH'
        :param trading_pair_suffix: Quote asset symbol, default is 'USDT'
        :param depth_limit: Number of top order book levels to fetch, default is 20
        """
        self.asset = asset.upper()
        self.trading_pair = self.asset + trading_pair_suffix.upper()
        self.depth_limit = depth_limit
        self.base_url = "https://api.binance.com/api/v3/depth"

    def get_order_book(self):
        """
        Fetch the order book for the trading pair.

        :return: Tuple of two pandas DataFrames: (bids_df, asks_df)
        """
        params = {
            "symbol": self.trading_pair,
            "limit": self.depth_limit
        }
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()

        bids_df = pd.DataFrame(data['bids'], columns=["Price", "Quantity"])
        asks_df = pd.DataFrame(data['asks'], columns=["Price", "Quantity"])

        bids_df["Price"] = bids_df["Price"].astype(float)
        bids_df["Quantity"] = bids_df["Quantity"].astype(float)

        asks_df["Price"] = asks_df["Price"].astype(float)
        asks_df["Quantity"] = asks_df["Quantity"].astype(float)

        return bids_df, asks_df


orderbook = BinanceOrderBook("BTC")



try:
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen
        bids, asks = orderbook.get_order_book()
        print("Top Bids:\n", bids.head(), "\n")
        print("Top Asks:\n", asks.head())
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped by user.")