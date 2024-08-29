import os
import sys
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import pyupbit
from dotenv import load_dotenv

# Add the root directory to the system path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

import handle_candle as hc


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
    final_df.to_csv(root_dir + "/data/df_long.csv")

    final_df["ma_5"] = final_df["open"].rolling(window=5).mean()

    return final_df


def perform_daily_task():
    """
    Function to perform the daily task.
    Replace this with your actual task.
    """
    long_df = pd.read_csv(root_dir + "/data/df_long.csv", index_col=0)
    long_df["day_starting_at_4am"] = pd.to_datetime(long_df["day_starting_at_4am"])
    short_df = get_candles_from_days_ago(days=2)
    today_df = concat_candles(long_df=long_df, short_df=short_df)

    ### check if -1 condition is satisfied when position 1.
    position = sugang.get_balance("KRW-BTC")
    krw_balance = sugang.get_balance("KRW")

    if position != 0:
        if today_df.loc[-1, "open"] < today_df.loc[-1, "ma_5"]:
            sugang.sell_market_order("KRW-BTC", position)
    else:
        if today_df.loc[-1, "open"] >= today_df.loc[-1, "ma_5"]:
            sugang.buy_market_order("KRW-BTC", krw_balance * 0.9949)

    print(f"Task executed at {datetime.now()}")


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

run_daily_loop()
