from flask import Flask
from flask_cors import CORS
from api.upbit_connect import connect_bp
from api.upbit_trading import trading_bp
from api.openai_api import openai_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(connect_bp, url_prefix='/api/upbit')
app.register_blueprint(trading_bp, url_prefix='/api/trading')
app.register_blueprint(openai_bp, url_prefix='/api/openai')

if __name__ == '__main__':  
    print("🚀 Flask 서버가 시작됩니다...")
    app.run(host="0.0.0.0", debug=True, port=7777, use_reloader=False)
