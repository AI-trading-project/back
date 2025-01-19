from flask import Flask, jsonify
from flask_cors import CORS
from upbit import UpbitTrader  # 작성한 UpbitTrader 클래스 사용

app = Flask(__name__)
CORS(app)
access_key = "YqL93Op43PETzIhLYiygXZmgYbrYDhgPoFBaQCbB"
secret_key = "oxNgzCi3PXZiZUjRvfhljgfHL36rsW1ezxRL9EyZ"
trader = UpbitTrader(access_key, secret_key)

@app.route('/api/chart', methods=['GET'])
def api_get_chart_data():
    """차트 데이터 API"""
    try:
        data = trader.get_chart_data()
        return jsonify(data.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/balance', methods=['GET'])
def api_get_balance():
    """잔고 조회 API"""
    try:
        data = trader.get_balance()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profit-loss', methods=['GET'])
def api_get_profit_loss():
    """수익/손실 API"""
    try:
        data = trader.get_profit_loss()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)