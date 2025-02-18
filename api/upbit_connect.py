from flask import Blueprint, jsonify, request
import jwt
import requests
import uuid
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

# Blueprint 생성
connect_bp = Blueprint('connect', __name__)

class UpbitTrader:
    def __init__(self):
        self.access_key = os.getenv('UPBIT_ACCESS_KEY')
        self.secret_key = os.getenv('UPBIT_SECRET_KEY')
        
    def get_chart_data(self, ticker, interval, count):
        try:
            # 기본 URL
            base_url = "https://api.upbit.com/v1/candles"
            
            # interval에 따른 URL 생성
            if 'minute' in interval:
                minutes = interval.replace('minute', '')
                url = f"{base_url}/minutes/{minutes}"
            elif interval in ['day', 'days']:
                url = f"{base_url}/days"
            elif interval in ['week', 'weeks']:
                url = f"{base_url}/weeks"
            elif interval in ['month', 'months']:
                url = f"{base_url}/months"
            else:
                # 잘못된 interval이 전달된 경우 기본값으로 1시간 설정
                url = f"{base_url}/minutes/60"

            params = {
                "market": ticker,
                "count": count
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code}, {response.text}")
                return None
            
        except Exception as e:
            print(f"Error getting chart data: {e}")
            return None

    def get_balance(self):
        try:
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
            }
            jwt_token = jwt.encode(payload, self.secret_key)
            headers = {'Authorization': f'Bearer {jwt_token}'}
            url = "https://api.upbit.com/v1/accounts"
            response = requests.get(url, headers=headers)
            return response.json()
        except Exception as e:
            print(f"Error getting balance: {e}")
            return None

    def get_profit_loss(self):
        try:
            balance = self.get_balance()
            if not balance:
                return None
            
            total_assets = 0
            total_bought = 0
            assets_detail = []
            
            for asset in balance:
                if asset['currency'] == 'KRW':  # 원화는 별도 처리
                    assets_detail.append({
                        'currency': 'KRW',
                        'balance': float(asset['balance']),
                        'current_price': 1,
                        'avg_buy_price': 1,
                        'profit_loss': 0,
                        'profit_loss_rate': 0
                    })
                    total_assets += float(asset['balance'])
                    continue
                
                # 현재가 조회
                ticker = f"KRW-{asset['currency']}"
                current_price_response = requests.get(f"https://api.upbit.com/v1/ticker?markets={ticker}")
                if current_price_response.status_code != 200:
                    continue
                
                current_price = float(current_price_response.json()[0]['trade_price'])
                balance_amount = float(asset['balance'])
                avg_buy_price = float(asset['avg_buy_price'])
                
                # 현재 평가금액
                current_value = balance_amount * current_price
                # 매수 금액
                bought_value = balance_amount * avg_buy_price
                
                # 수익률 계산
                profit_loss = current_value - bought_value
                profit_loss_rate = (profit_loss / bought_value * 100) if bought_value > 0 else 0
                
                assets_detail.append({
                    'currency': asset['currency'],
                    'balance': balance_amount,
                    'current_price': current_price,
                    'avg_buy_price': avg_buy_price,
                    'profit_loss': profit_loss,
                    'profit_loss_rate': profit_loss_rate
                })
                
                total_assets += current_value
                total_bought += bought_value
            
            # 전체 수익률 계산
            total_profit_loss = total_assets - total_bought
            total_profit_loss_rate = (total_profit_loss / total_bought * 100) if total_bought > 0 else 0
            
            return {
                'total_assets': total_assets,
                'total_bought': total_bought,
                'total_profit_loss': total_profit_loss,
                'total_profit_loss_rate': total_profit_loss_rate,
                'assets_detail': assets_detail
            }
            
        except Exception as e:
            print(f"Error calculating profit/loss: {e}")
            return None

# UpbitTrader 인스턴스 생성
trader = UpbitTrader()

# interval 받기위해서 parameter로 수정
@connect_bp.route('/chart', methods=['GET'])
def get_chart():
    """차트 데이터 API"""
    ticker = request.args.get('ticker', 'KRW-BTC')
    interval = request.args.get('interval', 'minute60')
    count = int(request.args.get('count', '24'))
    
    data = trader.get_chart_data(ticker, interval, count)
    if data is not None:
        return jsonify({
            'success': True,
            'data': data
        })
    return jsonify({'success': False, 'error': '차트 데이터 조회 실패'})

@connect_bp.route('/balance', methods=['GET'])
def get_balance():
    """잔고 조회 API"""
    data = trader.get_balance()
    if data is not None:
        return jsonify({
            'success': True,
            'data': data
        })
    return jsonify({'success': False, 'error': '잔고 조회 실패'})

@connect_bp.route('/profit-loss', methods=['GET'])
def get_profit_loss():
    """수익/손실 현황 API"""
    data = trader.get_profit_loss()
    if data is not None:
        return jsonify({
            'success': True,
            'data': data
        })
    return jsonify({'success': False, 'error': '수익/손실 조회 실패'})
