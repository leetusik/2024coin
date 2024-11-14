import os
import sys
import time
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pyupbit
from dotenv import load_dotenv

load_dotenv()

# Start the daily loop
ak = os.getenv("SUGANG_UPBIT_AK")
sk = os.getenv("SUGANG_UPBIT_SK")
sugang = pyupbit.Upbit(access=ak, secret=sk)

# bal = sugang.get_balance("KRW")
# bal = bal * 0.0995
# buy = sugang.buy_market_order("KRW-MTL", price=bal)
# print(buy)
# bal = sugang.get_balance("KRW-MTL")
# sell = sugang.sell_market_order("KRW-MTL", bal)

# if buy:
#     order = sugang.get_order(buy["uuid"])
#     buy_krw = order["price"]
#     fee = order["reserved_fee"]
#     executed_volume = order["executed_volume"]
#     buy_price = round((buy_krw + fee) / executed_volume)

# order = sugang.get_order("0e012152-c108-450f-bb30-27a3036d8580")
# print(order)
# print(order.get("trades"), order.get("kimchi"))
# if None:
#     print("kimchi")

# buy_krw = order["price"]
# fee = order["reserved_fee"]
# executed_volume = order["executed_volume"]
# buy_price = round((buy_krw + fee) / executed_volume)

# print(buy_price)


# # btc_bal = sugang.get_balance("KRW-BTC")
# sell = sugang.sell_market_order("KRW-BTC", btc_bal)

{
    "uuid": "0e012152-c108-450f-bb30-27a3036d8580",
    "side": "bid",
    "ord_type": "price",
    "price": "9950.20707711",
    "state": "wait",
    "market": "KRW-MTL",
    "created_at": "2024-09-11T14:11:02+09:00",
    "reserved_fee": "4.975103538555",
    "remaining_fee": "4.975103538555",
    "paid_fee": "0",
    "locked": "9955.182180648555",
    "executed_volume": "0",
    "trades_count": 0,
}

{
    "uuid": "0e012152-c108-450f-bb30-27a3036d8580",
    "side": "bid",
    "ord_type": "price",
    "price": "9950.20707711",
    "state": "cancel",
    "market": "KRW-MTL",
    "created_at": "2024-09-11T14:11:02+09:00",
    "reserved_fee": "4.975103538555",
    "remaining_fee": "0.00000000063",
    "paid_fee": "4.975103537925",
    "locked": "0.00000126063",
    "executed_volume": "7.74335181",
    "trades_count": 1,
    "trades": [
        {
            "market": "KRW-MTL",
            "uuid": "2676bd4c-feed-4ace-ae53-52d404134ad9",
            "price": "1285",
            "volume": "7.74335181",
            "funds": "9950.20707585",
            "trend": "up",
            "created_at": "2024-09-11T14:11:02+09:00",
            "side": "bid",
        }
    ],
}


{
    "uuid": "9258f62b-80dc-4382-b246-d22d9f9465e9",
    "side": "ask",
    "ord_type": "market",
    "state": "done",
    "market": "KRW-MTL",
    "created_at": "2024-09-11T14:31:22+09:00",
    "volume": "7.74335181",
    "remaining_volume": "0",
    "reserved_fee": "0",
    "remaining_fee": "0",
    "paid_fee": "4.83959488125",
    "locked": "0",
    "executed_volume": "7.74335181",
    "trades_count": 1,
    "trades": [
        {
            "market": "KRW-MTL",
            "uuid": "1f8427d2-1a2d-4c83-a86b-bcdaad3a9c88",
            "price": "1250",
            "volume": "7.74335181",
            "funds": "9679.1897625",
            "trend": "down",
            "created_at": "2024-09-11T14:31:22+09:00",
            "side": "ask",
        }
    ],
}

buy = True

if buy:
    order = sugang.get_order("0e012152-c108-450f-bb30-27a3036d8580")
    trades = order.get("trades")
    while not trades:
        time.sleep(1)
        order = sugang.get_order("0e012152-c108-450f-bb30-27a3036d8580")
        trades = order.get("trades")

    buy_krw = float(order["price"])
    fee = float(order["reserved_fee"])
    executed_volume = float(order["executed_volume"])
    buy_price = round((buy_krw + fee) / executed_volume)
else:
    buy_price = None

print(buy_price)

sell = True
if sell:
    order = sugang.get_order("9258f62b-80dc-4382-b246-d22d9f9465e9")
    trades = order.get("trades")
    while not trades:
        time.sleep(1)
        order = sugang.get_order("9258f62b-80dc-4382-b246-d22d9f9465e9")
        trades = order.get("trades")

    executed_volume = float(order["executed_volume"])
    fee = float(order["paid_fee"])

    krw_total = 0
    for trade in trades:
        krw_total += float(trade["funds"])

    sell_price = round((krw_total + fee) / executed_volume)
else:
    sell_price = None
print(sell_price)
