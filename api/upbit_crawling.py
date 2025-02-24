from flask import Blueprint, jsonify
import numpy as np
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests
import ta


def calculate_heikin_ashi(df):
    ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    ha_open = (df['open'].shift(1) + df['close'].shift(1)) / 2
    
    # 첫 번째 봉의 시가는 해당 봉의 (시가 + 종가) / 2
    ha_open.iloc[0] = (df['open'].iloc[0] + df['close'].iloc[0]) / 2

    ha_high = df[['high', 'open', 'close']].max(axis=1)
    ha_low = df[['low', 'open', 'close']].min(axis=1)
    
    return pd.DataFrame({
        'open': ha_open,
        'high': ha_high,
        'low': ha_low,
        'close': ha_close
    })

def calculate_ema_200(df):
    # 전체 데이터에 대해 EMA-200 계산
    close_prices = df['close'].astype(float)
    ema_200_full = []
    
    # 마지막 200개 데이터 포인트에 대해 각각 EMA-200 계산
    for i in range(200):
        # i번째 시점까지의 데이터로 EMA-200 계산
        end_idx = len(close_prices) - 199 + i  # 끝에서 200개씩 슬라이딩
        current_data = close_prices[:end_idx]
        if len(current_data) >= 200:  # 충분한 데이터가 있는 경우에만 계산
            current_ema = ta.trend.ema_indicator(current_data, window=200).iloc[-1]
            ema_200_full.append(float(current_ema))
        else:
            ema_200_full.append(float(current_data.mean()))  # 데이터가 부족한 경우 평균값 사용
    
    return ema_200_full

def calculate_stoch_rsi(df, period=14, smooth_k=3, smooth_d=3):
    # StochRSI 계산
    rsi = ta.momentum.rsi(df['close'], window=period)
    
    # 최소/최대 RSI 계산을 위한 rolling window
    rsi_min = rsi.rolling(window=period).min()
    rsi_max = rsi.rolling(window=period).max()
    
    # StochRSI 계산
    stoch_rsi = (rsi - rsi_min) / (rsi_max - rsi_min)
    
    # K와 D 라인 계산
    k = stoch_rsi.rolling(window=smooth_k).mean()
    d = k.rolling(window=smooth_d).mean()
    
    # NaN 값 처리
    k = k.fillna(method='bfill')
    d = d.fillna(method='bfill')
    
    return k, d

def fetch_market_data(market="KRW-BTC"):
    # 충분한 데이터를 확보하기 위해 더 많은 캔들 데이터 요청
    url = f"https://api.upbit.com/v1/candles/minutes/10"
    params = {
        "market": market,
        "count": 400  # EMA-200 계산을 위해 더 많은 데이터 필요
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            df = df[['opening_price', 'high_price', 'low_price', 'trade_price']]
            df.columns = ['open', 'high', 'low', 'close']
            # 시간순 정렬 (과거 -> 현재)
            df = df.iloc[::-1].reset_index(drop=True)
            return df
        return None
    except Exception as e:
        print(f"데이터 가져오기 실패: {e}")
        return None

def update_market_data():
    df = fetch_market_data()
    if df is not None:
        # 기술적 지표 계산
        ha_df = calculate_heikin_ashi(df)
        ema_200 = calculate_ema_200(df)
        stoch_k, stoch_d = calculate_stoch_rsi(df)
        
        # 최근 200개 데이터만 반환
        last_200_indices = slice(-200, None)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'heikin_ashi': {
                'open': ha_df['open'][last_200_indices].tolist(),
                'high': ha_df['high'][last_200_indices].tolist(),
                'low': ha_df['low'][last_200_indices].tolist(),
                'close': ha_df['close'][last_200_indices].tolist()
            },
            'ema_200': ema_200,
            'stoch_rsi': {
                'k': stoch_k[last_200_indices].tolist(),
                'd': stoch_d[last_200_indices].tolist()
            }
        }
        return data
    return None