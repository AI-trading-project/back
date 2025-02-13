from flask import Flask
from flask_cors import CORS
from api.upbit_connect import connect_bp
from api.upbit_trading import trading_bp
from api.openai_api import openai_bp
from api.upbit_crawling import crawling_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(connect_bp, url_prefix='/api/upbit')
app.register_blueprint(trading_bp, url_prefix='/api/trading')
app.register_blueprint(openai_bp, url_prefix='/api/openai')
app.register_blueprint(crawling_bp, url_prefix='/api/crawling')

if __name__ == '__main__':  
    print("🚀 Flask 서버가 시작됩니다...")
    app.run(debug=True, port=5000, use_reloader=False)