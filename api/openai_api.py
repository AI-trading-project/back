# from flask import Blueprint, request, jsonify
# import openai
# from dotenv import load_dotenv
# import os

# # 환경 변수 로드
# load_dotenv()

# # Blueprint 생성
# openai_bp = Blueprint('openai', __name__)

# # OpenAI API 키 설정
# openai.api_key = os.getenv("OPENAI_API_KEY")

# print(os.getenv(openai.api_key))

# @openai_bp.route('/chat', methods=['POST'])
# def chat():
#     try:
#         data = request.get_json()
#         if not data or "message" not in data:
#             return jsonify({"error": "Invalid input"}), 400

#         user_input = data["message"]

#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": user_input}]
#         )
#         reply = response["choices"][0]["message"]["content"]

#         return jsonify({"reply": reply})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500 


# from flask import Blueprint, request, jsonify
# from openai import OpenAI
# from dotenv import load_dotenv
# import os

# load_dotenv()

# openai_api_key = os.getenv("OPENAI_API_KEY")

# client = OpenAI(api_key=openai_api_key)

# openai_bp = Blueprint('openai', __name__)

# @openai_bp.route('/chat', methods=['POST'])
# def chat():
#     try:
#         data = request.get_json()
#         if not data or "message" not in data:
#             return jsonify({"error": "Invalid input"}), 400

#         user_input = data["message"]

#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": user_input}]
#         )
#         reply = response.choices[0].message.content

#         return jsonify({"reply": reply})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

from flask import Blueprint,request, jsonify
from flask.wrappers import Response
from openai import OpenAI
from api import upbit_connect
from dotenv import load_dotenv
import os
import json

# 환경 변수 로드
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key)

openai_bp = Blueprint('openai', __name__)

# 데이터 제공하고 JSON 형식으로 받는 API
@openai_bp.route('/chat-chart', methods=['GET'])
def get_chat_chart():
    try:
        # 'api'가 무엇인지 정확히 정의되지 않아서, 적절히 수정해줍니다.
        # 예를 들어, upbit_connect나 upbit_trading에서 chart를 가져오는 함수가 있을 수 있습니다.
        
        # 데이터 가져오기
        data = upbit_connect.get_chart()
        print(f"Received data: {data}")

        # Flask Response 객체 처리
        if isinstance(data, Response):  # Flask Response 객체인지 확인
            try:
                # JSON 형식으로 파싱 시도
                data = data.get_json()
                print(f"Parsed JSON data: {data}")
            except Exception as e:
                # JSON 파싱 실패 시, 텍스트로 읽기
                data = data.get_data(as_text=True)
                print(f"Raw text data: {data}")

                # 텍스트를 JSON으로 변환 시도
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
                    "content": "You're a Bitcoin or stock investing expert. "
                               "Tell me whether I should buy, sell, or hold at the moment based on the chart data provided or the information given. "
                               "Response in JSON format. Example: "
                               "{\"decision\": \"buy\", \"reason\": \"some technical reason\"}"
                },
                {
                    "role": "user",
                    "content": json.dumps(data)  # data를 JSON 문자열로 변환하여 전달
                }
            ]
        )

        # 응답에서 'choices' -> 'message' -> 'content'를 추출
        # reply = response['choices'][0]['message']['content']
        reply = response.choices[0].message.content

        # 추출된 내용을 JSON 형식으로 반환
        return jsonify({"reply": reply})

    except Exception as e:
        # 오류 처리 및 출력
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
