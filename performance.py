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
            print(f"{key:<15} : {get_rounded(value)}")
    else:
        for key, value in kwargs.items():
            print(f"{key:<15} : {value}")
    print("=" * 30)
