import os
import sys
import time
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pyupbit
from dotenv import load_dotenv

# Add the root directory to the system path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

import handle_candle as hc
from performance import logging_on_excel_rsi


def get_candles_from_days_ago(days=150):
    current_time = datetime.now(timezone.utc) + timedelta(hours=9)
    a_week_ago = current_time - timedelta(days=days)
    a_week_ago = str(
        a_week_ago.replace(hour=4, minute=0, second=0, microsecond=0).replace(
            tzinfo=None
        )
    )
    df = hc.get_candles(
        interval="minutes", interval2="60", market="KRW-BTC", start=a_week_ago
    )
    # Convert the 'time_kst' column to datetime
    df["time_kst"] = pd.to_datetime(df["time_kst"])

    # Step 1: Set the index to 'time_kst'
    df.set_index("time_kst", inplace=True)

    # Step 2: Resample the data starting at 4:00 AM each day
    # This will give daily intervals starting from 4:00 AM
    daily_df = (
        df.resample("24h", offset="4h", origin="epoch")
        .agg(
            {
                "open": "first",  # Open price at 4:00 AM
                "high": "max",  # Highest price in the interval
                "low": "min",  # Lowest price in the interval
                "close": "last",  # Close price at 4:00 AM next day
                "volume_krw": "sum",  # Total volume in the interval
                "volume_market": "sum",  # Total market volume in the interval
            }
        )
        .reset_index()
    )

    # Step 3: Rename the time column
    daily_df.rename(columns={"time_kst": "day_starting_at_4am"}, inplace=True)
    # daily_df[f"ma_days"] = daily_df["open"].rolling(window=days).mean()
    # Display the result
    return daily_df


def concat_candles(long_df, short_df):
    concatenated_df = pd.concat([long_df, short_df])

    # Drop duplicates based on 'day_starting_at_4am', keeping the last occurrence (from df2)
    final_df = concatenated_df.drop_duplicates(
        subset="day_starting_at_4am", keep="last"
    )

    # Sort the DataFrame by 'day_starting_at_4am' to maintain chronological order
    final_df = final_df.sort_values(by="day_starting_at_4am").copy()

    # Reset the index if needed
    final_df.reset_index(drop=True, inplace=True)
    lenght = len(final_df)
    final_df = final_df[lenght - 200 : lenght]
    final_df.to_csv(root_dir + "/data/df_long_rsi.csv")

    final_df["price_change"] = final_df["open"].diff()
    # Calculate the gains and losses
    final_df["gain"] = np.where(
        final_df["price_change"] > 0, final_df["price_change"], 0
    )
    final_df["loss"] = np.where(
        final_df["price_change"] < 0, -final_df["price_change"], 0
    )

    # Calculate the average gain and average loss
    window_length = 14
    final_df["avg_gain"] = (
        final_df["gain"].rolling(window=window_length, min_periods=1).mean()
    )
    final_df["avg_loss"] = (
        final_df["loss"].rolling(window=window_length, min_periods=1).mean()
    )

    # Calculate the RS (Relative Strength) and RSI
    final_df["rs"] = final_df["avg_gain"] / final_df["avg_loss"]
    final_df["rsi"] = 100 - (100 / (1 + final_df["rs"]))

    return final_df


def perform_daily_task():
    """
    Function to perform the daily task.
    Replace this with your actual task.
    """
    print(f"Task started at {datetime.now()}")

    long_df = pd.read_csv(root_dir + "/data/df_long_rsi.csv", index_col=0)
    long_df["day_starting_at_4am"] = pd.to_datetime(long_df["day_starting_at_4am"])
    short_df = get_candles_from_days_ago(days=2)
    # while (
    #     short_df.iloc[-1]["day_starting_at_4am"]
    #     == long_df.iloc[-1]["day_starting_at_4am"]
    # ):
    #     time.sleep(1)
    #     short_df = get_candles_from_days_ago(days=2)
    today_df = concat_candles(long_df=long_df, short_df=short_df)

    btc_balance = sugang.get_balance("KRW-BTC")
    krw_balance = sugang.get_balance("KRW")
    # print(f"btc_balance: {btc_balance}, type: {type(btc_balance)}")
    # print(f"krw_balance: {krw_balance}, type: {type(krw_balance)}")

    buy = False
    sell = False

    if btc_balance == 0:
        # if today_df.loc[-1, "open"] < today_df.loc[-1, "ma_5"]:
        if today_df.iloc[-1]["rsi"] >= 30 and today_df.iloc[-2]["rsi"] < 30:
            buy = sugang.buy_market_order("KRW-BTC", krw_balance * 0.9995)
            signal = 1
            position = 1
            # buy = True
        else:
            signal = 0
            position = 0

    else:
        # if today_df.iloc[-1, "open"] >= today_df.iloc[-1, "ma_5"]:
        if today_df.iloc[-1]["rsi"] <= 70 and today_df.iloc[-2]["rsi"] > 70:
            sell = sugang.sell_market_order("KRW-BTC", btc_balance)
            signal = -1
            position = 0
            # sell = True
        else:
            signal = 0
            position = 1

    print(f"Task 1 executed at {datetime.now()}")

    # Manage positions with stop loss, take profit, and sell signal
    today_df["position"] = 0
    today_df["highest_price"] = np.nan
    today_df["exit_price"] = np.nan
    today_df["stop_loss_triggered"] = np.nan
    holding_position = False
    stop_loss = False
    # Implement RSI strategy for long positions only
    today_df.reset_index(drop=True, inplace=True)
    today_df["signal"] = 0  # Default to no position
    for i in range(1, len(today_df)):
        # 매수 조건
        if (today_df.loc[i, "rsi"] >= 30) and (today_df.loc[i - 1, "rsi"] < 30):
            today_df.loc[i, "signal"] = 1
        # 매도 조건
        elif (today_df.loc[i, "rsi"] <= 70) and (today_df.loc[i - 1, "rsi"] > 70):
            today_df.loc[i, "signal"] = -1

    for i in range(1, len(today_df)):
        stop_loss = False
        if today_df["signal"].iloc[i] == 1 and not holding_position:
            # Enter position
            today_df.loc[i, "position"] = 1
            today_df.loc[i, "highest_price"] = today_df.loc[i, "open"]
            holding_position = True
        elif holding_position:
            # Calculate percentage change since entry
            # today_df['highest_price'].iloc[i] = max(today_df['highest_price'].iloc[i-1], today_df['open'].iloc[i])
            today_df.loc[i, "highest_price"] = max(
                today_df.loc[i - 1, "highest_price"], today_df.loc[i, "open"]
            )
            highest_price = today_df["highest_price"].iloc[i]
            current_price = today_df["open"].iloc[i]
            percent_change = (current_price - highest_price) / highest_price * 100

            if today_df["signal"].iloc[i] == -1:  # Sell signal condition
                # print(f"cond1 on{i}")
                today_df.loc[i, "position"] = 0
                today_df.loc[i, "exit_price"] = current_price
                holding_position = False
            elif percent_change <= -5:  # Stop loss condition
                # print(f"cond2 on{i}")
                today_df.loc[i, "position"] = 0
                today_df.loc[i, "exit_price"] = current_price
                holding_position = False
                stop_loss = True
                today_df.loc[i, "stop_loss_triggered"] = 1
            else:
                # Continue holding the position if no sell conditions are met
                today_df.loc[i, "position"] = today_df.loc[i - 1, "position"]

        else:
            # No signal and no position
            # df['position'].iloc[i] = df['position'].iloc[i-1]
            today_df.loc[i, "position"] = today_df.loc[i - 1, "position"]

    if stop_loss and position == 1:
        sell = sugang.sell_market_order("KRW-BTC", position)
        signal = -1
        position = 0
    # print(stop_loss)

    # Get the current date
    current_date = datetime.now()

    # Format the date as "YYYY-MM-DD"
    formatted_date = current_date.strftime("%Y-%m-%d")

    if buy:
        order = sugang.get_order(buy["uuid"])
        trades = order.get("trades")
        while not trades:
            time.sleep(1)
            order = sugang.get_order(buy["uuid"])
            trades = order.get("trades")

        buy_krw = float(order["price"])
        fee = float(order["reserved_fee"])
        executed_volume = float(order["executed_volume"])
        buy_price = round((buy_krw + fee) / executed_volume)
    else:
        buy_price = None

    if sell:
        order = sugang.get_order(sell["uuid"])
        trades = order.get("trades")
        while not trades:
            time.sleep(1)
            order = sugang.get_order(sell["uuid"])
            trades = order.get("trades")

        executed_volume = float(order["executed_volume"])
        fee = float(order["paid_fee"])

        krw_total = 0
        for trade in trades:
            krw_total += float(trade["funds"])

        sell_price = round((krw_total + fee) / executed_volume)
    else:
        sell_price = None

    new_data = {
        "date": formatted_date,
        "open_price": today_df.iloc[-1]["open"],
        "rsi": today_df.iloc[-1]["rsi"],
        "highest_price": today_df.iloc[-1]["highest_price"],
        "signal": signal,
        "position": position,
        "buy_price": buy_price,
        "sell_price": sell_price,
    }
    dashboard_data = {
        "Total Return": [0, 0, 0],
        "CAGR": [0, 0, 0],
        "MDD": [0, 0, 0],
        "Holding Days": [0, 0, 0],
        "Investing Days": [0, 0, 0],
    }

    logging_on_excel_rsi(
        root_dir + "/machine_logs/test_rsi.xlsx",
        new_data=new_data,
        dashboard_data=dashboard_data,
    )
    print(f"Task 2 executed at {datetime.now()}")
    today_df.to_csv(root_dir + "/data/df_long_history.csv")


def get_next_run_time(target_hour=4, target_minute=0):
    """
    Calculate the next run time for the daily task.

    :param target_hour: The hour at which the task should run (24-hour format)
    :param target_minute: The minute at which the task should run
    :return: The next datetime when the task should run
    """
    now = datetime.now()
    target_time = now.replace(
        hour=target_hour, minute=target_minute, second=0, microsecond=0
    )

    if now >= target_time:
        # If it's already past the target time today, schedule for tomorrow
        target_time += timedelta(days=1)

    return target_time


def run_daily_loop():
    """
    Run a loop that performs a task every day at a specific time.
    """
    while True:
        next_run_time = get_next_run_time()
        wait_time = (next_run_time - datetime.now()).total_seconds()
        t = datetime.now() + timedelta(seconds=wait_time)

        print(
            f"Next run scheduled for {next_run_time}. Waiting for {wait_time} seconds."
        )

        # Sleep until the next scheduled time
        time.sleep(wait_time)

        # Perform the task
        perform_daily_task()


load_dotenv()

# Start the daily loop
ak = os.getenv("SUGANG_UPBIT_AK")
sk = os.getenv("SUGANG_UPBIT_SK")
sugang = pyupbit.Upbit(access=ak, secret=sk)


# perform_daily_task()
# long_df = pd.read_csv(root_dir + "/data/df_long_rsi.csv", index_col=0)
temp_df = get_candles_from_days_ago(days=200)
temp_df.to_csv(root_dir + "/data/df_long_rsi.csv")

run_daily_loop()
