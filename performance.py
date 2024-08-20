import matplotlib.pyplot as plt
import numpy as np


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
            if type(value) != float:
                print(f"{key:<15} : {value}")
            else:
                print(f"{key:<15} : {get_rounded(value)}")
    else:
        for key, value in kwargs.items():
            print(f"{key:<15} : {value}")
    print("=" * 30)


def get_performance(df, title):
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
    cagr = get_cagr(total_return=tr, days=days)
    # print(len(df), first_signal_day, days)

    # get mdd
    balance = df["cumulative_returns"]
    mdd = get_mdd(balance)

    # print things
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
