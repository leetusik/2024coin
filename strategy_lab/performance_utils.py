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


def get_mdd(df):
    values = list(df["cumulative_returns2"])

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


def get_win_rate(df):
    # Initialize variables to track buy and win times
    buy_time = 0
    win_time = 0
    holding_period = False  # Track whether we're in a holding period
    start_returns = 0  # To store the returns at the start of the buy signal

    for index, row in df.iterrows():
        if row["signal"] == 1 and not holding_period:
            # Start of a new buy period
            holding_period = True
            buy_time += 1
            start_returns = row["cumulative_returns2"]

        elif row["position"] == 0 and holding_period:
            # End of a buy period (sell signal)
            holding_period = False
            # Calculate total returns during this holding period
            end_returns = row["cumulative_returns2"]
            if end_returns > start_returns:
                win_time += 1  # Count as a winning trade if returns increased

    # Calculate win rate
    if buy_time > 0:
        win_rate = win_time / buy_time
    else:
        win_rate = 0

    return win_rate


def get_gain_loss_ratio(df):
    holding_period = False  # Track whether we're in a holding period
    start_returns = 0  # To store the returns at the start of the buy signal
    win_list = []
    loss_list = []

    for index, row in df.iterrows():
        if row["signal"] == 1 and not holding_period:
            # Start of a new buy period
            holding_period = True
            start_returns = row["cumulative_returns2"]

        elif row["position"] == 0 and holding_period:
            # End of a buy period (sell signal)
            holding_period = False
            # Calculate total returns during this holding period
            end_returns = row["cumulative_returns2"]
            if end_returns > start_returns:
                gain = (end_returns - start_returns) / start_returns
                win_list.append(gain)
            elif end_returns < start_returns:
                gain = (end_returns - start_returns) / start_returns
                loss_list.append(gain)

    if len(win_list) != 0:
        win_avg = sum(win_list) / len(win_list)
    else:
        win_avg = 0

    if len(loss_list) != 0:
        loss_avg = sum(loss_list) / len(loss_list)
    else:
        loss_avg = 0

    if win_avg != 0 and loss_avg != 0:
        gain_loss_ratio = win_avg / abs(loss_avg)
    else:
        gain_loss_ratio = "not enough data"
    return gain_loss_ratio


def get_holding_time_ratio(df):
    # Step 1: Filter rows where there is no NaN in any column except 'highest_price' and 'exit_price'
    df_no_na_except_cols = df.dropna(
        subset=[col for col in df.columns if col not in ["highest_price", "exit_price"]]
    )

    # Step 2: Calculate the total period from the first non-NaN row in this filtered dataframe
    total_period_except_cols = len(df_no_na_except_cols)

    # Step 3: Calculate the position time (when position is non-zero) in this filtered dataframe
    position_time_except_cols = len(
        df_no_na_except_cols[df_no_na_except_cols["position"] != 0]
    )

    # Calculate the ratio of position time to total period
    if total_period_except_cols > 0:
        position_time_ratio_except_cols = (
            position_time_except_cols / total_period_except_cols
        )
    else:
        position_time_ratio_except_cols = 0

    return position_time_ratio_except_cols


def get_performance(df):
    # get total return
    initial_value = df["cumulative_returns2"].iloc[1]
    final_value = df["cumulative_returns2"].iloc[-1]

    tr = get_total_return(
        inital_value=initial_value,
        final_value=final_value,
    )

    df_no_na_except_cols = df.dropna(
        subset=[col for col in df.columns if col not in ["highest_price", "exit_price"]]
    )

    # Step 2: Calculate the total period from the first non-NaN row in this filtered dataframe
    days = len(df_no_na_except_cols)
    cagr = get_cagr(
        total_return=tr,
        days=days,
    )
    # print(len(df), first_signal_day, days)

    # get mdd
    mdd = get_mdd(df)

    # get win rate
    win_rate = get_win_rate(df)

    # get gain loss ratio
    gain_loss_ratio = get_gain_loss_ratio(df)

    if type(gain_loss_ratio) != str:
        gain_loss_ratio = round(gain_loss_ratio, 2)

    # holding percent
    holding_time_ratio = get_holding_time_ratio(df)

    return {
        "total_return": tr,
        "cagr": cagr,
        "mdd": mdd,
        "win_rate": win_rate,
        "gain_loss_ratio": gain_loss_ratio,
        "holding_time_ratio": holding_time_ratio,
        "investing_period": days,
    }
