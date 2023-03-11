import asyncio
import json
import websockets
import time
from DB.database import DataBase
from Settings.main_config import *
from algorythm import correlation, get_self_price


class RunTime:
    hashlist_ethusdt = []
    hashlist_btcusdt = []
    url = wss_url
    max_price = 0
    min_price = 0

    def __init__(self):
        self.max_price = start_price
        self.min_price = start_price
        self.list_len = length_list
        self.db = DataBase()
        self.e = eth
        self.b = btc
        self.hashlist_ethusdt = start_hash
        self.hashlist_btcusdt = start_hash
        self.prices_lists = [self.hashlist_ethusdt, self.hashlist_btcusdt]
        self.previous_price_ethusdt = frst_prvs_price
        self.previous_price_btcusdt = frst_prvs_price
        self.previous_hour = start_hour
        self.current_hour = start_hour


    def check_prices_list(self):
        if len(self.hashlist_ethusdt) > (self.list_len * 2) and len(self.hashlist_btcusdt) > (self.list_len * 2):
            self.hashlist_ethusdt = self.hashlist_ethusdt[self.list_len:]
            self.hashlist_btcusdt = self.hashlist_btcusdt[self.list_len:]


    def prepearing_config(self):
        self.db.create_table(self.e)
        self.db.create_table(self.b)
        self.hashlist_ethusdt = self.db.get_data(self.e)
        self.hashlist_btcusdt = self.db.get_data(self.b)
        print(self.hashlist_ethusdt)

        if len(self.hashlist_ethusdt) > 0 and len(self.hashlist_btcusdt) > 0:
            self.previous_price_ethusdt = self.hashlist_ethusdt[-1]
            self.previous_price_btcusdt = self.hashlist_btcusdt[-1]

    def get_price_diff(self):
        if (self.current_hour - self.previous_hour) >= 3600:
            self.previous_hour = self.current_hour
            price_difference = self.max_price-self.min_price
            price_diff_percent = (price_difference / self.max_price) * 100
            if price_diff_percent > (self.max_price / 100):
                print(f"Price has changed by {price_diff_percent}% in last hour")


    async def main(self):
        queue = asyncio.Queue()
        try:
            self.prepearing_config()
            async with websockets.connect(self.url) as ws:
                while True:
                    self.check_prices_list()
                    new_prices_eth = []
                    new_prices_btc = []
                    ethusdt_data = {}
                    btcusdt_data = {}
                    corr = correlation(self.prices_lists)
                    self.previous_price_ethusdt = self.hashlist_ethusdt[-1]
                    j = 0
                    while j < 10:
                        data_ws = json.loads(await ws.recv())['data']
                        await queue.put(data_ws)
                        data = await queue.get()
                        if data['s'] == self.e.upper():
                            current_price = float(data['c'])
                            datetime = int(data['E'])
                            self_price = get_self_price(corr, current_price, self.previous_price_ethusdt)
                            new_prices_eth.append(current_price)
                            print(time.ctime(int(datetime/1000)), '>>>', self.e, '>>>', self_price)
                            if self_price:
                                ethusdt_data[datetime] = (current_price, self_price)
                            else:
                                ethusdt_data[datetime] = current_price
                            self.previous_price_ethusdt = current_price
                            if self.max_price == 0 or self.min_price == 0:
                                self.max_price = current_price
                                self.min_price = current_price
                            if current_price < self.min_price:
                                self.min_price = current_price
                            if current_price > self.max_price:
                                self.max_price = current_price
                        elif data['s'] == self.b.upper():
                            current_price = float(data['c'])
                            datetime = int(data['E'])
                            new_prices_btc.append(current_price)
                            btcusdt_data[datetime] = (current_price, 0)
                            self.current_hour = datetime / 1000
                        j += 1
                    self.hashlist_ethusdt = self.hashlist_ethusdt + new_prices_eth
                    self.hashlist_btcusdt = self.hashlist_btcusdt + new_prices_btc
                    self.prices_lists = [self.hashlist_ethusdt, self.hashlist_btcusdt]
                    await self.db.insert_data(self.e, ethusdt_data)
                    await self.db.insert_data(self.b, btcusdt_data)
                    self.get_price_diff()

        except Exception as ex:
            self.db.connection_close()
            print(f"[ERROR] While running main: {ex}")



if __name__ == '__main__':
    while True:
        run = RunTime()
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.run(run.main())
        except Exception as main_ex:
            print(f"[ERROR] While running loop: {main_ex}")
            print("Restarting programm")
            continue