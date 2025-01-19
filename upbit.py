import pyupbit
import pandas as pd
from datetime import datetime
import time

class UpbitTrader:
    def __init__(self, access_key, secret_key):
        """업비트 API 초기화"""
        self.upbit = pyupbit.Upbit(access_key, secret_key)
        
    def get_chart_data(self, ticker="KRW-BTC", interval="minute60", count=24):
        """차트 데이터 조회
        
        Args:
            ticker (str): 코인 티커 (예: KRW-BTC)
            interval (str): 시간간격 (minute1, minute3, minute5, minute10, minute15, minute30, minute60, minute240, day, week, month)
            count (int): 가져올 데이터 개수
        """
        try:
            df = pyupbit.get_ohlcv(ticker, interval=interval, count=count)
            return df
        except Exception as e:
            print(f"차트 데이터 조회 실패: {e}")
            return None

    def get_balance(self):
        """전체 계좌 잔고 조회"""
        try:
            balances = self.upbit.get_balances()
            result = []
            
            for balance in balances:
                currency = balance['currency']
                balance_amt = float(balance['balance'])
                avg_buy_price = float(balance['avg_buy_price'])
                
                if currency == 'KRW':
                    current_price = 1
                else:
                    ticker = f"KRW-{currency}"
                    current_price = pyupbit.get_current_price(ticker)
                
                current_value = balance_amt * current_price
                
                result.append({
                    'currency': currency,
                    'balance': balance_amt,
                    'avg_buy_price': avg_buy_price,
                    'current_value': current_value
                })
            
            return result
        except Exception as e:
            print(f"잔고 조회 실패: {e}")
            return None

    def get_profit_loss(self):
        """전체 수익/손실 현황 조회"""
        try:
            balances = self.get_balance()
            total_value = 0
            total_invested = 0
            
            for balance in balances:
                if balance['currency'] != 'KRW':
                    current_value = balance['current_value']
                    invested = balance['balance'] * balance['avg_buy_price']
                    
                    total_value += current_value
                    total_invested += invested
                else:
                    total_value += balance['current_value']
                    
            profit_loss = total_value - total_invested
            profit_loss_percentage = (profit_loss / total_invested * 100) if total_invested > 0 else 0
            
            return {
                'total_value': total_value,
                'total_invested': total_invested,
                'profit_loss': profit_loss,
                'profit_loss_percentage': profit_loss_percentage
            }
        except Exception as e:
            print(f"수익/손실 계산 실패: {e}")
            return None

# 사용 예시
if __name__ == "__main__":
    access_key = "YqL93Op43PETzIhLYiygXZmgYbrYDhgPoFBaQCbB"
    secret_key = "oxNgzCi3PXZiZUjRvfhljgfHL36rsW1ezxRL9EyZ"
    
    trader = UpbitTrader(access_key, secret_key)
    
    # 비트코인 시간봉 차트 데이터 조회
    btc_chart = trader.get_chart_data()
    print("비트코인 차트:", btc_chart)
    
    # 계좌 잔고 조회
    balance = trader.get_balance()
    print("계좌 잔고:", balance)
    
    # 수익/손실 현황 조회
    profit_loss = trader.get_profit_loss()
    print("수익/손실 현황:", profit_loss)
