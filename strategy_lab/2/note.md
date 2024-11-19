## 1. 딥러닝과 단기매매전략을 결합한 암호화폐 투자 방법론 실증 연구 | 이유민, 이민혁 2021, 부산대학교

### 키워드

- LSTM
- 이동평균선 교차전략
  1. 5일, 20일 이동평균선 사용
  2. ma(5) > ma(20) then buy
  3. ma(5) < ma(20) then sell

### 문장들

### 궁금증

# ... Strategy Backtest Results

## Strategy Overview

### 1. Backtest Environment

- **Data Source**: Bitcoin OHLCV (Daily, UTC 00:00)
- **Moving Averages**:
  - **MA5**: Calculated on the closing price with a 5-day window
  - **MA20**: Calculated on the closing price with a 20-day window

### 2. Trading Conditions

- **Buy Condition**: When MA5 > MA20
- **Sell Condition**: When MA5 < MA20

## Performance Metrics

```json


```
