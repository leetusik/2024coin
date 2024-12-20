## 1. 딥러닝을 이용한 비트코인 투자전략의 성과 분석 | 김선웅, 2021, 국민대학교

### 키워드

- LSTM
- 이동평균선 교차전략
  1. 5일, 20일 이동평균선 사용
  2. ma(5) > ma(20) then buy
  3. ma(5) < ma(20) then sell

### 문장들

- 내재가치를판단할수없는상 황에서는 기본적 분석(fundamental analysis)보다는 본 연구에서 제안하는 모형과 같은 기술적 분석(technical analysis) 접근법이 유효하다.
- 비트코인을 포함한 암 호화폐 가격에는 long memory 특성이 있음이 밝혀지 고 있다[37,38].
- 본 연구에서는 Python 3.9 환경에서 Tensorflow 2.4와 Keras를 사용하여 실험을 진행하였다.
- 017년 5월 23일부 터 2019년 12월 17일까지는 학습용 데이터, 2019년 12 월 18일부터 2021년 1월 23일까지는 검증용 데이터로 구분하였으며, 학습용 데이터는 전체 데이터의 70%에 해당한다.
- 937일의 학습 데이터 구간에서 최적화된 LSTM 모형 을 403일의 검증 데이터 구간에 적용하여 비트코인의 다 음 날 가격을 예측한다.
- LSTM의 비교 모형으로는 단순 RNN 모형을 분석한다. 딥러닝 최적화 알고리즘은 오차 감소 속도가 빠른 Adam optimizer를 이용하였고 활성 화 함수는 hyperbolic tangent를 이용하였고, 지도학습 은 100번의 반복 학습을 시행하였다. 지도학습을 추가적 으로 확대하여도 예측 성과에 큰 차이는 없음을 확인하 였다. 실험 결과의 성과평가 지표는 비트코인 가격의 예 측값과 실제 값과의 평균 제곱근 오차를 계산하는 RMSE(Root Mean Square Error)이다.
- 연구의 1단계에서 LSTM의 입력변수로는 비트코인의 일별 시가, 고가, 저가, 종가와 일별 수익률 자료를 이용 한다. 5개의 입력변수를 이용하여 다음 날의 비트코인 종가를 예측하는 것을 목표로 한다.

### 궁금증

왜 short ma랑 long ma 구할 때 predict_c 만 쓰는겨. t빼고 나머지 t-들은 다 actual price 있잖아.

# MA5/MA20 Crossover Strategy Backtest Results

## Strategy Overview

### 1. Backtest Environment

- **Data Source**: Bitcoin OHLCV (Daily, UTC 00:00)
- **Moving Averages**:
  - **MA5**: Calculated on the closing price with a 5-day window
  - **MA20**: Calculated on the closing price with a 20-day window
- **sleepage**: 0.2% buy and sell

### 2. Trading Conditions

- **Buy Condition**: When MA5 > MA20
- **Sell Condition**: When MA5 < MA20

## Performance Metrics

```json
{
  "total_return": 29.75,
  "cagr": 0.6212,
  "mdd": 0.6179,
  "win_rate": 0.3824,
  "gain_loss_ratio": 4.59,
  "holding_time_ratio": 0.5348,
  "investing_period": 2588 days
}

```

# MA5/MA20 Crossover Strategy with LSTM Prediction Backtest Results

## Strategy Overview

### 1. Backtest Environment

- **Data Source**: Bitcoin OHLCV (Daily, UTC 00:00)
- **Moving Averages**:

  - **MA5**: Calculated on the closing price with a 5-day window
    the last value of closing price is prediction. so at t4 is completed, the ma5(t5) is already created.
  - **MA20**: Calculated on the closing price with a 20-day window
  - **sleepage**: 0.2% buy and sell

- **LSTM Setting**
  - **features**: df_full[['open', 'high', 'low', 'close', 'volume_krw', 'volume_market', 'Daily Return']].values
  - **hyperparameters**: the paper as is.
  - ![Alt text for the image](/strategy_lab/1/parameters.png)

### 2. Trading Conditions

- **Buy Condition**: When MA5 > MA20 and close > MA5
- **Sell Condition**: When MA5 < MA20

## Performance Metrics

```json
{
  "total_return": 36.575791857820974,
  "cagr": 0.6700152854207029,
  "mdd": 0.5567359070199527,
  "win_rate": 0.4107142857142857,
  "gain_loss_ratio": 5.07,
  "holding_time_ratio": 0.487020534676482,
  "investing_period": 2581
}
```

## concerns

완성된 lstm 모델로 모델을 트레이닝할 때 사용한 트레이닝 기간에 대한 가격 예측도 포함하여 백테스트를 진행했기 때문에 overfitting 문제가 있을 수 있다.
=-> 그래도 early stop옵션이 있기 때문에 엄청나게 오버트레이닝 되지는 않았을 듯.

마지막 value만 predict를 할 게 아니라 ma를 구해놓고 지난 ma + 다른 features로 predicted ma를 구하면 되는 것이 아닌가. 뭐 큰 차이는 없겠다만
