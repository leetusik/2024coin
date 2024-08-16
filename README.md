# 2024coin

## project layout

1. research & make strategies
2. validate strategies (backtest)
3. make it work
4. make a outfit (program or just local page)

## 기존 연구 분석

### 1. 딥러닝과 단기매매전략을 결합한 암호화폐 투자 방법론 실증 연구 - 이유민, 이민혁

#### 1.1 참고 문헌

이은우, 이원부, 2022
변동성돌파전략 적용 시 매수가 일어난 날들을 학습 -> LSTM

#### 1.2 연구 설계 부분

하락 추세였던 2022년 1월 ~ 5월 자료를 사용했음.
과거 7일의 데이터로 다음 날 종가를 예측.

#### 1.3 데이터

- 날짜
- 시가
- 고가
- 저가
- 종가
- 거래량

#### 1.4 LSTM 파라미터

##### Model3

1. learning rate = 0.002
2. 1st layer unit = 64
3. 2nd layer unit = 4
4. epoch = 200
5. batch size = 64
6. loss function = MSE

7. window size = 7
8. 활성화 함수(activation function) = 하이퍼볼릭 탄젠트(hyperbolic tangent)
9. 옵티마이저(optimizer) = Adam (오차 감소 속도가 빠름(?))

#### 1.5 best model 매매 규칙

당일 고점과 당일 예측 종가가 당일 타겟가보다 높을 때, 당일 타겟가에 구매해서 당일 종가에 판매.

```python
if high(t) > target(t) & pred(t) > close(t):
 buy(price=target(t))
```

#### 1.6 연구 결과 성과 분석을 위한 성과 지표

![p_i](image/performance_indiators.png)

#### 1.? 궁금증

- 종가 기준은 몇시?
  1. 아마 pyupbit에서 일별 데이터 그대로 가져다 쓴 것 같은데 이런 경우에는 오전 9시로 설정됨
- 슬리피지 고려 했나?
- combo1-C 가 시장참여비율이 낮아서 수익률이 높을 수도. 하락장에 시자아 참여 비율이 낮다는 것은 긍정적이지만, 상승장에서 따라갈 수 있는지도 확인해야.

### 2. 딥러닝을 이용한 비트코인 투자전략의 성과 분석

<!-- ![hi](images/hi.png) -->

## ideas

- 하루의 기준 -> 평균 거래량이 가장 적은 시간대가 적당하지 않을까?
