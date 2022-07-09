import multiprocessing
import threading
import time
from datetime import datetime
from pytz import timezone
from brokers.broker import Broker
from core.tejas_run_modes import TejasRunModes
from screeners.screener import Screener
from strategies.strategy import Strategy
import pandas as pd
import matplotlib.pyplot as plt
from termcolor import colored


def create_job(target, *args):
    p = multiprocessing.Process(target=target, args=args)
    p.start()
    return p


class Tejas:
    broker = Broker()
    _strategies: [Strategy] = []
    _screeners: [Screener] = []
    strategy_result = {}
    screener_result = {}
    strategy_process_list = {}
    mtimezone = timezone('Asia/Kolkata')

    def __init__(self, feed, broker=None, mode=TejasRunModes.BACKTEST, plot=False):
        self.feed = feed
        self.broker = broker
        self.mode = mode
        self.plot = plot

    def prepare_initial_data(self, start_time):
        for strategy in self._strategies:
            for symbol_id in strategy.symbol_ids:
                for condition in strategy.entry_conditions:
                    condition.set_symbol_timeframe(symbol_id, strategy_timeframe=strategy.timeframe,
                                                   strategy_compression=strategy.compression)
                    condition.technical1.get_data(minimal_period=220, start_time=start_time,
                                                  is_direction_forward=False, is_initial_setup=True)
                    if condition.technical2 is not None:
                        condition.technical2.get_data(minimal_period=220, start_time=start_time,
                                                      is_direction_forward=False, is_initial_setup=True)
                for condition in strategy.exit_conditions:
                    condition.set_symbol_timeframe(symbol_id, strategy_timeframe=strategy.timeframe,
                                                   strategy_compression=strategy.compression)
                    condition.technical1.get_data(minimal_period=220, start_time=start_time,
                                                  is_direction_forward=False, is_initial_setup=True)
                    if condition.technical2 is not None:
                        condition.technical2.get_data(minimal_period=220, start_time=start_time,
                                                      is_direction_forward=False, is_initial_setup=True)

    def set_broker(self, broker):
        self.broker = broker
        self.broker.set_tejas(self)

    def set_mode(self, mode):
        self.mode = mode

    def add_strategy(self, strategy):
        strategy.set_feed(feed=self.feed)
        self._strategies.append(strategy)

    def add_screener(self, screener):
        screener.set_feed(feed=self.feed)
        self._screeners.append(screener)

    def run(self):
        if self.mode == TejasRunModes.LIVE:
            e = threading.Event()
            self.feed.monitor_live_data(self.get_entire_symbol_list_for_ticker_subscription())
            # t1 = threading.Thread(target=self.feed.monitor_live_data,
            #                       args=(self.get_entire_symbol_list_for_ticker_subscription(), e,))
            t2 = threading.Thread(target=self.run_strategies)
            # t1.start()
            t2.start()
            # t1.join()
            t2.join()
            # q = multiprocessing.Queue()
            # self.feed.data_dict = multiprocessing.Manager().dict()
            # self.feed.monitor_live_data(self.get_entire_symbol_list_for_ticker_subscription(), self.feed.tick_dict)
            # self.prepare_initial_data(datetime.now())
            # p1 = create_job(self.feed.monitor_live_data, self.get_entire_symbol_list_for_ticker_subscription(), q)
            # p2 = create_job(self.run_strategies, self.feed.tick_dict)
            # self.run_strategies(self.feed.tick_dict)
            # print(f"Queue data from child - {q.get()}")
            # p1.join()
            # p2.join()

            print(self.feed.tick_dict)
        else:
            self.backtest()
            if self.plot:
                self.plot_chart()
            return self.strategy_result

    def run_strategies(self):
        # e.wait()
        cnt = 0
        while True:
            if self.feed.tick_flag:
                cnt = cnt + 1
                print(f"Strategy Execution Loop {cnt}")
                for strategy in self._strategies:
                    self.run_strategy(strategy)
                self.feed.tick_flag = False
            else:
                time.sleep(0.8)
        # pool_size = multiprocessing.cpu_count() - 1
        # print(f"Pool size - {pool_size}")
        # with multiprocessing.Pool(pool_size) as pool:
        #     pool.map(self.run_strategy, itertools.zip_longest(self._strategies, itertools.repeat(tdict)))

    # def update_data(self, ticks):
    #     for tick in ticks:
    #         self.process_tick_and_update_feed(tick)
    #
    # def process_tick_and_update_feed(self, tick, symbol, timeframe, compression):
    #     total_minutes = compression
    #     if timeframe == TimeFrame.Minutes:
    #         total_minutes = compression
    #     elif timeframe == TimeFrame.Days:
    #         total_minutes = compression * 24 * 60
    #
    #     if "timestamp" in tick.keys():
    #         current_time = tick['timestamp']
    #         current_time = self.mtimezone.localize(current_time)
    #     else:
    #         current_time = datetime.now(tz=tzoffset(None, 19800))
    #
    #     if (symbol, timeframe, compression) in self.feed.data_dict.keys() and \
    #             self.feed.data_dict[(symbol, timeframe, compression)].loc(1)['date'][
    #                 self.feed.data_dict[(symbol, timeframe, compression)].tail(1).index[-1]
    #             ] + timedelta(minutes=total_minutes) > current_time:
    #         self.feed.data_dict[(symbol, timeframe, compression)].at[
    #             self.feed.data_dict[(symbol, timeframe, compression)].index[-1], 'open'
    #         ] = tick['ohlc']['open']
    #         self.feed.data_dict[(symbol, timeframe, compression)].at[
    #             self.feed.data_dict[(symbol, timeframe, compression)].index[-1], 'high'
    #         ] = tick['ohlc']['high']
    #         self.feed.data_dict[(symbol, timeframe, compression)].at[
    #             self.feed.data_dict[(symbol, timeframe, compression)].index[-1], 'low'
    #         ] = tick['ohlc']['low']
    #         self.feed.data_dict[(symbol, timeframe, compression)].at[
    #             self.feed.data_dict[(symbol, timeframe, compression)].index[-1], 'close'
    #         ] = tick['ohlc']['close']
    #         self.feed.data_dict[(symbol, timeframe, compression)].at[
    #             self.feed.data_dict[(symbol, timeframe, compression)].index[-1], 'volume'
    #         ] = tick['volume']
    #         self.feed.data_dict[(symbol, timeframe, compression)].at[
    #             self.feed.data_dict[(symbol, timeframe, compression)].index[-1], 'oi'
    #         ] = tick['oi']
    #     else:
    #         if timeframe == TimeFrame.Minutes:
    #             mtime = self.mtimezone.localize(tick['timestamp']).replace(
    #                 minute=(floor(tick['timestamp'].minute / compression) * compression)
    #                 , second=0, microsecond=0)
    #         if timeframe == TimeFrame.Days:
    #             mtime = self.mtimezone.localize(tick['timestamp']).replace(
    #                 hour=9, minute=15, second=0, microsecond=0)
    #
    #         if (symbol, timeframe, compression) in self.feed.data_dict.keys():
    #             self.feed.data_dict[(symbol, timeframe, compression)].loc[len(
    #                 self.feed.data_dict[(symbol, timeframe, compression)])] = [
    #                 mtime,
    #                 tick['ohlc']['open'],
    #                 tick['ohlc']['high'],
    #                 tick['ohlc']['low'],
    #                 tick['ohlc']['close'],
    #                 tick['volume'],
    #                 tick['oi']
    #             ]
    #         else:
    #             self.feed.data_dict[(symbol, timeframe, compression)] = pd.DataFrame(columns=[
    #                 "date", "open", "high", "low", "close", "volume", "oi"])
    #             self.feed.data_dict[(symbol, timeframe, compression)].loc[0] = [
    #                 mtime,
    #                 tick['ohlc']['open'],
    #                 tick['ohlc']['high'],
    #                 tick['ohlc']['low'],
    #                 tick['ohlc']['close'],
    #                 tick['volume'],
    #                 tick['oi']
    #             ]

    def plot_chart(self):
        for key in self.strategy_result.keys():
            df = pd.DataFrame(self.strategy_result[key])
            x1 = df['timestamp']
            y1 = df['net_profit']
            plt.xticks(rotation=90)
            plt.plot(x1, y1, label="Net Profit")
            plt.title(f"Net profit for {key[0]}")
            plt.legend()
            plt.show()

    def run_strategy(self, strategy):
        try:
            for symbol_id in strategy.symbol_ids:
                strategy.set_technical_condition_symbol_timeframe(symbol_id)
                self.check_and_execute(-1, strategy, symbol_id)
        except Exception as ex:
            print(ex)

    def get_entire_symbol_list_for_ticker_subscription(self):
        complete_symbol_list = []
        for strategy in self._strategies:
            for symbol_id in strategy.symbol_ids:
                print(symbol_id)
                if symbol_id not in complete_symbol_list:
                    complete_symbol_list.append(symbol_id)
                for condition in strategy.entry_conditions:
                    if symbol_id in condition.symbol_ids_dict.keys() and\
                            condition.symbol_ids_dict[symbol_id] not in complete_symbol_list:
                        complete_symbol_list.append(condition.symbol_ids_dict[symbol_id])
                for condition in strategy.exit_conditions:
                    if symbol_id in condition.symbol_ids_dict.keys() and\
                            condition.symbol_ids_dict[symbol_id] not in complete_symbol_list:
                        complete_symbol_list.append(condition.symbol_ids_dict[symbol_id])

        return complete_symbol_list

    def backtest(self):
        self.feed.set_from_start(True)
        for strategy in self._strategies:
            print(strategy.symbol_ids)
            for symbol_id in strategy.symbol_ids:
                strategy.prepare_feed(symbol_id, strategy.start_time,
                                      strategy.end_time, strategy.timeframe, strategy.compression)
                strategy.set_technical_condition_symbol_timeframe(symbol_id)
                for current_index in range(0, len(
                        self.feed.data_dict[(symbol_id, strategy.timeframe, strategy.compression)]) - 1):
                    mean_price = self.feed.data_dict[(symbol_id, strategy.timeframe,
                                                      strategy.compression)].loc[current_index + 1,
                                                                                 ['open', 'high', 'low', 'close']].mean(
                        axis=0)
                    # temp_row = self.feed.data_dict[(symbol_id, strategy.timeframe,
                    #                                 strategy.compression)][current_index + 1]
                    # mean_price = (temp_row['open'] + temp_row['high'] + temp_row['low'] + temp_row['close']) / 4
                    entry_status, entry_message = self.check_and_place_order(
                        index=current_index,
                        symbol_id=symbol_id,
                        strategy=strategy,
                        token=symbol_id,
                        transaction_type=strategy.position,
                        qty=strategy.qty_dict[symbol_id],
                        exchange=self.broker.exchange,
                        variety="regular",
                        product=strategy.mis_cnc,
                        order_type="MARKET",
                        price=mean_price
                    )
                    print(f"Entry - {entry_message} {symbol_id}")
                    if entry_status == "TEST_FAILED" or entry_status == "ORDER_PLACED":
                        continue

                    # # Trade Exit
                    exit_status, exit_message = self.check_and_exit(
                        index=current_index,
                        symbol_id=symbol_id,
                        strategy=strategy,
                        token=symbol_id,
                        transaction_type=("BUY", "SELL")[strategy.position == "BUY"],
                        qty=strategy.qty_dict[symbol_id],
                        exchange=self.broker.exchange,
                        variety="regular",
                        product=strategy.mis_cnc,
                        order_type="MARKET",
                        price=mean_price
                    )
                    print(f"{exit_status} - {exit_message} for {symbol_id}")

    def check_and_execute(self, index, strategy, symbol_id):
        print("Checking technical condition")
        entry_status, entry_message = self.check_and_place_order(
            index=index,
            symbol_id=symbol_id,
            strategy=strategy,
            token=symbol_id,
            transaction_type=strategy.position,
            qty=strategy.qty_dict[symbol_id],
            exchange=self.broker.exchange,
            variety="regular",
            product=strategy.mis_cnc,
            order_type="MARKET",
        )
        if not entry_status:
            print(f"Entry - {entry_message} {symbol_id}")
            return

        # # Trade Exit
        exit_status, exit_message = self.check_and_exit(
            index=index,
            symbol_id=symbol_id,
            strategy=strategy,
            token=symbol_id,
            transaction_type=("SELL", "BUY")[strategy.position == "BUY"],
            qty=strategy.qty_dict[symbol_id],
            exchange=self.broker.exchange,
            variety="regular",
            product=strategy.mis_cnc,
            order_type="MARKET",
        )
        if not exit_status:
            print(f"Exit - {exit_message} for {symbol_id}")
        # strategy.check_strategy_entry(symbol_id, current_index)

    def check_and_place_order(self, index, strategy, symbol_id, transaction_type, qty, **kwargs):
        if self.broker.check_order_position_holding_exists(symbol_id, qty, ["ORDERS", "POSITIONS"]) != 0:
            return "ORDER_EXIST", "Order already exist"
        elif strategy.check_strategy_entry(symbol_id, index):
            self.broker.place_order(symbol_id, transaction_type, qty, **kwargs)
            return "ORDER_PLACED", "Order placed"
        else:
            return "TEST_FAILED", "Entry conditions not satisfied"

    def check_and_exit(self, index, strategy, symbol_id, transaction_type, qty, **kwargs):
        if self.broker.check_order_position_holding_exists(symbol_id, qty, ["POSITIONS"]) == 0:
            return "POSITION_NOT_FOUND", "Position does not exists"
        elif strategy.check_strategy_exit(symbol_id=symbol_id, current_index=index):
            if self.mode == TejasRunModes.LIVE:
                self.broker.place_order(symbol_id, transaction_type, qty, **kwargs)
            elif self.mode == TejasRunModes.BACKTEST:
                profit = self.broker.place_order(symbol_id, transaction_type, qty, **kwargs)
                if profit is not None:
                    self.update_strategy_result(strategy.name, symbol_id, profit)

            return "TRADE_EXITED", "Trade exited"
        else:
            return "TEST_FAILED", "Exit condition not satisfied"

    def update_strategy_result(self, strategy, symbol, profit):
        if profit > 0:
            win = 1
            loss = 0
        else:
            win = 0
            loss = 1

        if (strategy, symbol) not in self.strategy_result.keys():
            self.strategy_result[(strategy, symbol)] = []
            new_profit = profit
            new_win_count = win
            new_loss_count = loss
        else:
            last_result = self.strategy_result[(strategy, symbol)][len(self.strategy_result[(strategy, symbol)]) - 1]
            new_profit = last_result['profit'] + profit
            new_win_count = last_result['win'] + win
            new_loss_count = last_result['loss'] + loss

        self.strategy_result[(strategy, symbol)].append({
            'timestamp': datetime.now(),
            'strategy': strategy,
            'symbol': symbol,
            'balance': self.broker.get_balance(),
            'curr_profit': profit,
            'profit': new_profit,
            'commission': self.broker.commission,
            'net_profit': new_profit - self.broker.commission,
            'win': new_win_count,
            'loss': new_loss_count
        })

    def __test_screen(self, screener, symbol_id, **kwargs):
        if screener.test_conditions(symbol_id):
            return screener, symbol_id
        else:
            return "SCREENING_FAILED", "Conditions not satisfied"

    def screen(self):
        if self.mode == TejasRunModes.LIVE:
            e = threading.Event()
            self.feed.monitor_live_data(self.get_entire_symbol_list_for_ticker_subscription())
            t2 = threading.Thread(target=self.run_strategies)
            t2.start()
            t2.join()

            print(self.feed.tick_dict)
        else:
            self.__screen_offline()
            return self.screener_result

    def __run_screeners_live(self):
        cnt = 0
        while True:
            if self.feed.tick_flag:
                cnt = cnt + 1
                print(f"Strategy Execution Loop {cnt}")
                for screener in self._screeners:
                    self.__run_screener(screener)
                self.feed.tick_flag = False
            else:
                time.sleep(0.8)

    # To be implemented
    def __run_screener(self, screener):
        try:
            for symbol_id in screener.symbol_ids:
                screener.set_technical_condition_symbol_timeframe(symbol_id)
                self.__test_screen(-1, screener, symbol_id)
        except Exception as ex:
            print(ex)

    def __screen_offline(self):
        self.feed.set_from_start(True)
        print("Screen offline")
        for screener in self._screeners:
            print("Running screen - "+screener.name)
            print(screener.feed.data_dict)
            for symbol_id in screener.symbol_ids:
                try:
                    screener.prepare_feed(symbol_id, screener.start_time,
                                          screener.end_time, screener.timeframe, screener.compression)
                    screener.set_technical_condition_symbol_timeframe(symbol_id)

                    entry_status, entry_message = self.__test_screen(
                        symbol_id=symbol_id,
                        screener=screener
                    )
                    print(colored(f"Screening - {entry_message} {symbol_id}", "red"))
                    if entry_status == "SCREENING_FAILED":
                        continue
                except Exception as ex:
                    print(colored(f"Exception occured while screening {symbol_id}", "red"))
                    print(colored(ex, "red"))