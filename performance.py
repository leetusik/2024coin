import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows


def get_rounded(number):
    return round(number * 100, 2)


def get_total_return(inital_value, final_value):
    number = (final_value - inital_value) / inital_value
    return float(number)


def get_cagr(total_return, days):
    years = days / 365
    cagr = (1 + total_return) ** (1 / years) - 1
    return float(cagr)


def get_mdd(values):
    peak = values[0]
    max_drawdown = 0

    # Check if peak is NaN
    temp = 1
    while np.isnan(peak):
        peak = values[temp]
        temp += 1

    for value in values:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    return max_drawdown


def print_things(strategy="None", round=True, **kwargs):
    print("Investment Summary".center(30, "="))
    print(f"{'Strategy':<15} : {strategy}")
    if round:
        for key, value in kwargs.items():
            if type(value) != float and type(value) != np.float64:
                # print(f"{key} is not a float. It's {type(value)}")
                print(f"{key:<15} : {value}")
            else:
                print(f"{key:<15} : {get_rounded(value)}")
    else:
        for key, value in kwargs.items():
            print(f"{key:<15} : {value}")
    print("=" * 30)


def get_performance(df, title, add_to_excel=False, file_path=None):
    # get total return
    initial_value = df["cumulative_returns"].iloc[1]
    final_value = df["cumulative_returns"].iloc[-1]
    tr = get_total_return(
        inital_value=initial_value,
        final_value=final_value,
    )

    # # get cagr
    # days = len(df)

    # Calculate the number of days from the first signal to the last day in the DataFrame
    # Find the first day where a position is taken (signal == 1)
    first_signal_day = df[df["signal"] == 1].index[0]

    # Calculate the number of days from the first signal to the last day in the DataFrame
    days = len(df) - first_signal_day
    cagr = get_cagr(
        total_return=tr,
        days=days,
    )
    # print(len(df), first_signal_day, days)

    # get mdd
    balance = df["cumulative_returns"]
    mdd = get_mdd(balance)

    try:
        initial_value2 = df["cumulative_returns2"].iloc[1]
        final_value2 = df["cumulative_returns2"].iloc[-1]
        tr2 = get_total_return(
            inital_value=initial_value2,
            final_value=final_value2,
        )

        cagr2 = get_cagr(
            total_return=tr2,
            days=days,
        )

        balance2 = df["cumulative_returns2"]
        mdd2 = get_mdd(balance2)

        print_things(
            strategy=title,
            total_return=tr,
            cagr=cagr,
            mdd=mdd,
            total_return_w_fee=tr2,
            cagr_w_fee=cagr2,
            mdd_w_fee=mdd2,
            investing_days=days,
        )

        if add_to_excel:
            new_data = {
                "strategy_name": title,
                "cagr": get_rounded(cagr2),
                "mdd": get_rounded(mdd2),
                "investing_days": days,
            }
            add_row_to_excel(file_path=file_path, new_data=new_data)

    except:
        print_things(
            strategy=title,
            total_return=tr,
            cagr=cagr,
            mdd=mdd,
            investing_days=days,
        )


def draw_graph(df):
    # Plot the cumulative returns
    plt.figure(figsize=(14, 7))
    try:
        plt.plot(df["cumulative_returns2"], label="Strategy Cumulative Returns")
    except:
        plt.plot(df["cumulative_returns"], label="Strategy Cumulative Returns")
    plt.plot(
        df["benchmark_returns"],
        label="Benchmark (Buy and Hold) Cumulative Returns",
        linestyle="--",
    )
    plt.title("Cumulative Returns of the Trading Strategy")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Returns")
    plt.legend()
    plt.grid(True)
    plt.show()


def add_row_to_excel(file_path, new_data):
    """
    Adds a new row to an existing Excel file with the specified columns.

    :param file_path: Path to the existing Excel file.
    :param new_data: A dictionary containing the new row data.
                        The keys should be 'name', 'cagr', 'mdd', and 'investing_days'.
    """
    # Load the existing Excel file
    try:
        df = pd.read_excel(file_path, engine="openpyxl")
    except FileNotFoundError:
        # If the file doesn't exist, create an empty DataFrame with the correct columns
        df = pd.DataFrame(columns=["strategy_name", "cagr", "mdd", "investing_days"])

    # Convert new_data to a DataFrame and concatenate it with the existing DataFrame
    new_row_df = pd.DataFrame([new_data])
    df = pd.concat([df, new_row_df], ignore_index=True)

    # Save back to the Excel file
    df.to_excel(file_path, index=False, engine="openpyxl")


def logging_on_excel_ma(file_path, new_data, dashboard_data):
    # Check if the Excel file exists
    if not os.path.exists(file_path):
        # If the file doesn't exist, create it with two sheets
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            # Create a DataFrame for the dashboard with the required rows and columns
            dashboard_df = pd.DataFrame(
                dashboard_data,
                index=[
                    "Total Return",
                    "CAGR",
                    "MDD",
                    "Holding Days",
                    "Investing Days",
                ],
                columns=["Theoretical", "Real", "Benchmark"],
            )
            # Create an empty DataFrame for the logs with the required columns
            logs_df = pd.DataFrame(
                columns=[
                    "date",
                    "open_price",
                    "ma",
                    "signal",
                    "position",
                    "buy_price",
                    "sell_price",
                    # "strategy_buy_price",
                    # "strategy_sell_price",
                    # "strategy_highest_price",
                    # "real_buy_price",
                    # "real_sell_price",
                    # "real_highest_price",
                    # "strategy_returns",
                    # "strategy_cumulative_returns",
                    # "strategy_mdd",
                    # "real_returns",
                    # "real_cumulative_returns",
                    # "real_mdd",
                    # "benchmark_returns",
                    # "benchmark_cumulative_returns",
                    # "benchmark_mdd",
                ]
            )
            # Write the dashboard and logs to separate sheets
            dashboard_df.to_excel(writer, sheet_name="Dashboard")
            logs_df.to_excel(writer, sheet_name="Logs", index=False)

    # Load the existing file
    with pd.ExcelWriter(
        file_path, engine="openpyxl", mode="a", if_sheet_exists="overlay"
    ) as writer:
        # Load the logs sheet to append new data
        try:
            df = pd.read_excel(file_path, sheet_name="Logs", engine="openpyxl")
        except ValueError:
            # If the "Logs" sheet doesn't exist, create it
            df = pd.DataFrame(
                columns=[
                    "date",
                    "open_price",
                    "ma",
                    "signal",
                    "position",
                    "buy_price",
                    "sell_price",
                    # "strategy_buy_price",
                    # "strategy_sell_price",
                    # "strategy_highest_price",
                    # "real_buy_price",
                    # "real_sell_price",
                    # "real_highest_price",
                    # "strategy_returns",
                    # "strategy_cumulative_returns",
                    # "strategy_mdd",
                    # "real_returns",
                    # "real_cumulative_returns",
                    # "real_mdd",
                    # "benchmark_returns",
                    # "benchmark_cumulative_returns",
                    # "benchmark_mdd",
                ]
            )
        # Create a DataFrame for the new data
        new_row_df = pd.DataFrame([new_data])

        # Check if df is empty, if so, use the new_row_df as df
        if df.empty:
            df = new_row_df
        else:
            df = pd.concat([df, new_row_df], ignore_index=True)

        # Save the updated logs back to the Excel file
        df.to_excel(writer, sheet_name="Logs", index=False)

    # Update the Dashboard
    dashboard_df = pd.read_excel(file_path, sheet_name="Dashboard", index_col=0)

    for key, values in dashboard_data.items():
        if key in dashboard_df.index:
            dashboard_df.loc[key, "Theoretical"] = values[0]
            dashboard_df.loc[key, "Real"] = values[1]
            dashboard_df.loc[key, "Benchmark"] = values[2]

    # Write the updated dashboard back to the Excel file
    with pd.ExcelWriter(
        file_path, engine="openpyxl", mode="a", if_sheet_exists="replace"
    ) as writer:
        dashboard_df.to_excel(writer, sheet_name="Dashboard")


def logging_on_excel_rsi(file_path, new_data, dashboard_data):
    # Check if the Excel file exists
    if not os.path.exists(file_path):
        # If the file doesn't exist, create it with two sheets
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            # Create a DataFrame for the dashboard with the required rows and columns
            dashboard_df = pd.DataFrame(
                dashboard_data,
                index=[
                    "Total Return",
                    "CAGR",
                    "MDD",
                    "Holding Days",
                    "Investing Days",
                ],
                columns=["Theoretical", "Real", "Benchmark"],
            )
            # Create an empty DataFrame for the logs with the required columns
            logs_df = pd.DataFrame(
                columns=[
                    "date",
                    "open_price",
                    "rsi",
                    "highest_price",
                    "signal",
                    "position",
                    "buy_price",
                    "sell_price",
                    # "strategy_buy_price",
                    # "strategy_sell_price",
                    # "strategy_highest_price",
                    # "real_buy_price",
                    # "real_sell_price",
                    # "real_highest_price",
                    # "strategy_returns",
                    # "strategy_cumulative_returns",
                    # "strategy_mdd",
                    # "real_returns",
                    # "real_cumulative_returns",
                    # "real_mdd",
                    # "benchmark_returns",
                    # "benchmark_cumulative_returns",
                    # "benchmark_mdd",
                ]
            )
            # Write the dashboard and logs to separate sheets
            dashboard_df.to_excel(writer, sheet_name="Dashboard")
            logs_df.to_excel(writer, sheet_name="Logs", index=False)

    # Load the existing file
    with pd.ExcelWriter(
        file_path, engine="openpyxl", mode="a", if_sheet_exists="overlay"
    ) as writer:
        # Load the logs sheet to append new data
        try:
            df = pd.read_excel(file_path, sheet_name="Logs", engine="openpyxl")
        except ValueError:
            # If the "Logs" sheet doesn't exist, create it
            df = pd.DataFrame(
                columns=[
                    "date",
                    "open_price",
                    "rsi",
                    "highest_price",
                    "signal",
                    "position",
                    "buy_price",
                    "sell_price",
                    # "strategy_buy_price",
                    # "strategy_sell_price",
                    # "strategy_highest_price",
                    # "real_buy_price",
                    # "real_sell_price",
                    # "real_highest_price",
                    # "strategy_returns",
                    # "strategy_cumulative_returns",
                    # "strategy_mdd",
                    # "real_returns",
                    # "real_cumulative_returns",
                    # "real_mdd",
                    # "benchmark_returns",
                    # "benchmark_cumulative_returns",
                    # "benchmark_mdd",
                ]
            )
        # Create a DataFrame for the new data
        new_row_df = pd.DataFrame([new_data])

        # Check if df is empty, if so, use the new_row_df as df
        if df.empty:
            df = new_row_df
        else:
            df = pd.concat([df, new_row_df], ignore_index=True)

        # Save the updated logs back to the Excel file
        df.to_excel(writer, sheet_name="Logs", index=False)

    # Update the Dashboard
    dashboard_df = pd.read_excel(file_path, sheet_name="Dashboard", index_col=0)

    for key, values in dashboard_data.items():
        if key in dashboard_df.index:
            dashboard_df.loc[key, "Theoretical"] = values[0]
            dashboard_df.loc[key, "Real"] = values[1]
            dashboard_df.loc[key, "Benchmark"] = values[2]

    # Write the updated dashboard back to the Excel file
    with pd.ExcelWriter(
        file_path, engine="openpyxl", mode="a", if_sheet_exists="replace"
    ) as writer:
        dashboard_df.to_excel(writer, sheet_name="Dashboard")


# # Example usage
# file_path = "machine_logs/test.xlsx"

# new_data = {
#     "date": "2024-08-31",
#     "open_price": 101,
#     "ma": 102,
#     "signal": "Buy",
#     "position": 1,
#     "buy_price": 1,
#     "sell_price": 1,
#     "strategy_returns": 0.02,
#     "strategy_cumulative_returns": 0.02,
#     "strategy_mdd": -0.01,
#     "real_returns": 0.018,
#     "real_cumulative_returns": 0.045,
#     "real_mdd": -0.012,
# }

# dashboard_data = {
#     "Total Return": [0.12, 0.12],
#     "CAGR": [0.27, 0.26],
#     "MDD": [-0.02, -0.05],
#     "Holding Days": [2, 2],
#     "Investing Days": [200, 200],
# }

# logging_on_excel_ma(file_path, new_data, dashboard_data)
