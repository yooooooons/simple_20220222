#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
import pyupbit
import datetime
import pandas as pd
#import numpy as np
import warnings

#from scipy.signal import savgol_filter
#from scipy.signal import savitzky_golay

#import matplotlib.pyplot as plt


# In[2]:


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# In[3]:


warnings.filterwarnings(action='ignore')   # 경고 메시지 비활성화, 활성화시엔 action=default 으로 설정


# In[4]:


access_key = "eziU49y9cSYp6BFEu8Vu8yEwk0AAZIxn1o0ya7Bp"
secret_key = "mjkWq13cmg1XE38l9xK7x80XhcIsyChHrmyx3IVe"

upbit = pyupbit.Upbit(access_key, secret_key)


# In[5]:


check_currency = 'KRW'

candle_count = 10
candle_type = '5min'

avg_duration_1 = 1
#avg_duration_2 = 15

coin_target = ['KRW-NEO']

#series_1_cnt_No = 1
#series_1_cnt_buy_cri = 2
#series_1_cnt_sell_cri = 2

criteria_buy = 1.0005
criteria_sell = 0.9995

invest_ratio = 0.015   # 보유 금액의 최대 몇 % 를 투자할것인가 (예> 0.1 <-- 보유금액 10% 투자) 

#buy_time_value = 2
#sell_time_value = 1
#idle_time_value = 0

sell_force = 0.03   # 강제 매도 하락율
transaction_fee_ratio = 0.0005   # 거래 수수료 비율

time_factor = 9   # 클라우드 서버와 한국과의 시차


if candle_type == '1min' :
    candle_adapt = 'minute1'
    time_unit = 1
elif candle_type == '3min' :
    candle_adapt = 'minute3'
    time_unit = 3
elif candle_type == '5min' :
    candle_adapt = 'minute5'
    time_unit = 5
elif candle_type == '10min' :
    candle_adapt = 'minute10'
    time_unit = 10
elif candle_type == '15min' :
    candle_adapt = 'minute15'
    time_unit = 15
elif candle_type == '30min' :
    candle_adapt = 'minute30'
    time_unit = 30
elif candle_type == '60min' :
    candle_adapt = 'minute60'
    time_unit = 60
elif candle_type == '240min' :
    candle_adapt = 'minute240'
    time_unit = 240


# In[6]:


# 잔고 조회, 현재가 조회 함수 정의

def get_balance(target_currency):   # 현급 잔고 조회
    """잔고 조회"""
    balances = upbit.get_balances()   # 통화단위, 잔고 등이 Dictionary 형태로 balance에 저장
    for b in balances:
        if b['currency'] == target_currency:   # 화폐단위('KRW', 'KRW-BTC' 등)에 해당하는 잔고 출력
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_balance_locked(target_currency):   # 거래가 예약되어 있는 잔고 조회
    """잔고 조회"""
    balances = upbit.get_balances()   # 통화단위, 잔고 등이 Dictionary 형태로 balance에 저장
    for b in balances:
        if b['currency'] == target_currency:   # 화폐단위('KRW', 'KRW-BTC' 등)에 해당하는 잔고 출력
            if b['locked'] is not None:
                return float(b['locked'])
            else:
                return 0
    return 0

def get_avg_buy_price(target_currency):   # 거래가 예약되어 있는 잔고 조회
    """평균 매수가 조회"""
    balances = upbit.get_balances()   # 통화단위, 잔고 등이 Dictionary 형태로 balance에 저장
    for b in balances:
        if b['currency'] == target_currency:   # 화폐단위('KRW', 'KRW-BTC' 등)에 해당하는 잔고 출력
            if b['avg_buy_price'] is not None:
                return float(b['avg_buy_price'])
            else:
                return 0
    return 0


def get_current_price(invest_coin):
    """현재가 조회"""
    #return pyupbit.get_orderbook(tickers=invest_coin)[0]["orderbook_units"][0]["ask_price"]
    return pyupbit.get_current_price(invest_coin)

#price = pyupbit.get_current_price("KRW-BTC")


# In[7]:


get_balance('KRW')


# In[8]:


#get_avg_buy_price('NEO')


# In[9]:


bought_state = 0


# In[10]:


while True:
    
    now = datetime.datetime.now() + datetime.timedelta(seconds = (time_factor * 3600))   # 클라우드 서버와 한국과의 시간차이 보정 (9시간)
    print ('bought_state : {0}   / now : {1}'.format(bought_state, now))
    
    if (now.minute % time_unit == 0) & (52 < (now.second % 60) <= 57) :   # N시:00:02초 ~ N시:00:07초 사이 시각이면
        balances1 = upbit.get_balances()
        print ('current_aseet_status\n', balances1)
        
        # 매수 영역        
        if bought_state == 0 :   # 매수가 없는 상태라면
            DF_inform = pyupbit.get_ohlcv(coin_target[0], count = candle_count, interval = candle_adapt)
            DF_inform['prior_close'] = DF_inform['close'].shift(1)
            DF_inform['ratio_close'] = DF_inform['close'] / DF_inform['prior_close']
            print ('\nDF_inform\n', DF_inform['prior_close'])
            print ('criteria_BUY_ratio_close : {0}  / current_ratio_close[-2] : {1}'.format(criteria_buy, DF_inform['ratio_close'][-2]))
            
            if DF_inform['ratio_close'][-2] >= criteria_buy :
                print ('$$$$$ [{0}] buying_transaction is coducting $$$$$'.format(coin_target[0]))
                investable_budget = get_balance('KRW') * invest_ratio
                transaction_buy = upbit.buy_market_order(coin_target[0], investable_budget)   # 시장가로 매수
                bought_volume = investable_budget / get_current_price (coin_target[0])
                print ('buy_transaction_result :', transaction_buy)
                print ('time : {0}  /  bought_target_volume : {1}  /  bought_volume_until_now : {2}'.format((datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))), bought_volume, get_balance(coin_target[0][4:])))
                bought_state = 1
                time.sleep(5)
    
    
    # 자동 매도 영역               

    if (now.minute % time_unit == 0) & (52 < (now.second % 60) <= 57) & (bought_state == 1) :   # N시:00:02초 ~ N시:00:07초 사이 시각이면
        balances1 = upbit.get_balances()
        print ('current_aseet_status\n', balances1)

        print ('\nnow :', (datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))))
        print ('\n bought_state : {0}  [[[[[[[[[[[[ coin___{1} selling condition checking]]]]]]]]]] :'.format(bought_state, coin_target[0]))
            
        DF_inform_sell = pyupbit.get_ohlcv(coin_target[0], count = candle_count, interval = candle_adapt)
        DF_inform_sell['prior_close'] = DF_inform_sell['close'].shift(1)
        DF_inform_sell['ratio_close'] = DF_inform_sell['close'] / DF_inform_sell['prior_close']

        print ('criteria_sell_ratio_close : {0}  / current_ratio_close[-2] : {1}'.format(criteria_sell, DF_inform_sell['ratio_close'][-2]))
                                
        if DF_inform_sell['ratio_close'][-2] <= criteria_sell :
            print ('$$$$$ [{0}] AUTO Selling_transaction is coducting $$$$$'.format(coin_target[0]))                         
            transaction_sell = upbit.sell_market_order(coin_target[0], get_balance(coin_target[0][4:]))   # 시장가에 매도
            time.sleep(5)
            print ('\nnow :', (datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))))
            print ('sell_transaction_result :', transaction_sell)
                
            bought_state = 0
                
            time.sleep(5)
        
        
    # 하락시 강제 매도 영역
    if bought_state == 1 :   # 매수가 되어 있는 상태라면
        if get_current_price(coin_target[0]) <= (get_avg_buy_price(coin_target[0]) * (1-sell_force)) :   # 강제 매도 가격 이하로 현재가격이 하락하게 되면
            
            print ('$$$$$ [{0}] Forced Selling_transaction is coducting $$$$$'.format(coin_target[0]))            
            transaction_sell = upbit.sell_market_order(coin_target[0], get_balance(coin_target[0][4:]))   # 시장가에 매도
            time.sleep(5)
            print ('\nnow :', (datetime.datetime.now() + datetime.timedelta(seconds = (time_factor*3600))))
            print ('sell_transaction_result :', transaction_sell)
            bought_state = 0
            time.sleep(5)
        
    time.sleep(1)
    

