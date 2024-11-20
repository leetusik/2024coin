import numpy as np
import pandas as pd


# Function to calculate moving averages
def moving_average(series, length, method="SMA"):
    if method == "SMA":
        return series.rolling(window=length).mean()
    elif method == "EMA":
        return series.ewm(span=length, adjust=False).mean()
    elif method == "WMA":
        weights = np.arange(1, length + 1)
        return series.rolling(window=length).apply(
            lambda prices: np.dot(prices, weights) / weights.sum(), raw=True
        )
    elif method == "RMA":
        return series.ewm(com=length - 1, adjust=False).mean()
    elif method == "VWMA":
        return (series * volume).rolling(window=length).sum() / volume.rolling(
            window=length
        ).sum()


# Function to calculate ATR
def atr(data, length):
    high_low = data["High"] - data["Low"]
    high_close = np.abs(data["High"] - data["Close"].shift())
    low_close = np.abs(data["Low"] - data["Close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=length).mean()


# SuperTrend Calculation
def supertrend(data, length, factor, ma_method="WMA"):
    vwma = moving_average(
        data["Close"] * data["Volume"], length, method=ma_method
    ) / moving_average(data["Volume"], length, method=ma_method)
    atr_value = atr(data, length)
    upper_band = vwma + factor * atr_value
    lower_band = vwma - factor * atr_value

    super_trend = pd.Series(index=data.index)
    direction = pd.Series(index=data.index, dtype=int)
    for i in range(1, len(data)):
        if super_trend[i - 1] == upper_band[i - 1]:
            direction[i] = -1 if data["Close"][i] > upper_band[i] else 1
        else:
            direction[i] = 1 if data["Close"][i] < lower_band[i] else -1
        super_trend[i] = lower_band[i] if direction[i] == 1 else upper_band[i]

    return super_trend, direction


# KNN Algorithm
def knn(data, labels, k, current_point):
    distances = np.abs(data - current_point)
    sorted_indices = np.argsort(distances)
    nearest_labels = labels[sorted_indices][:k]

    # Weighting the neighbors
    weights = 1 / (distances[sorted_indices][:k] + 1e-6)
    weighted_sum = np.sum(weights * nearest_labels)
    total_weight = np.sum(weights)

    return weighted_sum / total_weight


# Sample DataFrame setup
data = pd.DataFrame(
    {
        "Close": np.random.random(100),
        "High": np.random.random(100),
        "Low": np.random.random(100),
        "Volume": np.random.random(100),
    }
)

# User-configurable parameters
k = 3  # Number of neighbors
length = 10  # SuperTrend length
factor = 3.0  # SuperTrend factor

# Calculating SuperTrend
super_trend, direction = supertrend(data, length, factor)

# KNN usage example
data_points = np.array(data["Close"])
labels = np.array(
    [1 if data["Close"][i] > super_trend[i] else 0 for i in range(len(data))]
)
current_point = super_trend.iloc[-1]
label = knn(data_points, labels, k, current_point)

# Resulting trend and signal
print("SuperTrend:", super_trend)
print("Direction:", direction)
print("KNN Label:", label)
