from flask import Blueprint,request, jsonify, current_app
from flask.wrappers import Response
from openai import OpenAI
from api import upbit_connect
from dotenv import load_dotenv
import os
import json
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import atexit

# 환경 변수 로드
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

openai_bp = Blueprint('openai', __name__)

# 🚀 OpenAI API 호출 대신 테스트용 데이터 반환
@openai_bp.route('/chat-chart', methods=['GET'])
def get_chat_chart():
    try:    
        # 데이터 가져오기
        data = upbit_connect.get_chart()
        print(f"Received data: {data}")

        # Flask Response 객체 처리
        if isinstance(data, Response): 
            try:
                data = data.get_json()
                print(f"Parsed JSON data: {data}")
            except Exception as e:
                data = data.get_data(as_text=True)
                print(f"Raw text data: {data}")

                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    return jsonify({"error": "Invalid JSON format in chart data"}), 400

        if not isinstance(data, dict):
            return jsonify({"error": "Chart data is not in the expected format"}), 400

        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a Bitcoin or stock investing expert."
                    "Based on the chart data provided or the information I've been given, and based on the trades I've told you to make"
                    "Tell me if I should buy, sell, or hold at this time."
                    "The trading method is as follows"
                    "You should analyze the chart based on these trading methods. The trading method utilizes three indicators: Haikin Ashi candles, Exponential Moving Average (EMA), and Stochastic RSI."
                    "Haikin Ashi candles: An uptrend is expected when the body of a black candle is longer than the previous one and has no lower tail, and a downtrend is expected when the body of a black candle is longer and has no upper tail. A candle with tails on both sides indicates a trend reversal."
                    "EMA (200-period moving average): When the price is above the EMA, an uptrend is favorable for a buy (long) entry, and when it is below the EMA, a downtrend is considered for a sell (short) entry."
                    "Stochastic RSI: A buy opportunity when the Kijun is below 20 and a sell signal when it is above 80. If the Kijun line breaks above the D-line, it is a buy, and if it breaks below, it is a sell."
                    "Please judge based on the above"
                    "Please send your response in JSON format."
                    "Please send your response in Korean!!!!!."
                    "Example response:"
                    "{“decision”: “구매”, ‘reason’: “기술적 이유\"}"
                    "{“decision”: “판매”, ‘Reason’: “기술적 이유\"}"
                    "{“decision”: “홀드”, ‘reason’: “기술적 이유\"}"
                },
                {
                    "role": "user",
                    "content": json.dumps(data)  # data를 JSON 문자열로 변환하여 전달
                }
            ]
        )

        reply = response.choices[0].message.content

        # 추출된 내용을 JSON 형식으로 반환
        return jsonify({"chatai": reply})

    except Exception as e:
        # 오류 처리 및 출력
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ `app`을 직접 가져오기 (Flask 애플리케이션 참조)
def get_app():
    from app import app  # Flask 애플리케이션 객체 가져오기
    return app

# ✅ 스케줄러 작업 함수
import json

def scheduled_task():
    app = get_app()  # Flask 애플리케이션 가져오기
    print(f"[{datetime.now()}] Running scheduled task...")

    with app.app_context():  # ✅ Flask 애플리케이션 컨텍스트 설정
        with app.test_client() as client:  # ✅ Flask Fake Request 생성
            response = client.get('/api/openai/chat-chart')  # ✅ GET 요청 실행

            try:
                json_data = response.get_json()  # ✅ JSON 데이터 추출
            except Exception as e:
                json_data = {"error": f"Failed to parse JSON: {str(e)}"}

            print(f"Scheduled task response: {json.dumps(json_data, ensure_ascii=False)}")

# **스케줄러 설정 및 실행 (app.py 실행 시 자동 실행됨)**
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_task, 'interval', minutes=1)
scheduler.start()

# **Flask 종료 시 스케줄러도 안전하게 종료**
atexit.register(lambda: scheduler.shutdown())