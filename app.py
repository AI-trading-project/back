from flask import Flask
from flask_cors import CORS
from ubit_trading import trading_bp
from upbit_connect import connect_bp

app = Flask(__name__)
CORS(app)  # React와의 CORS 이슈 해결

# 블루프린트 등록
app.register_blueprint(trading_bp, url_prefix='/api/trading')
app.register_blueprint(connect_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
