from flask import Blueprint, jsonify, request
from upbit_connect import UpbitTrader

# Blueprint 생성
connect_bp = Blueprint('connect', __name__)

# UpbitTrader 인스턴스 생성
trader = UpbitTrader(
    access_key="your-access-key",
    secret_key="your-secret-key"
)

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
            'data': data.to_dict('records')
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
