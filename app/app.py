from flask import Flask, redirect, request, render_template, session, url_for
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import requests
import logging
import base64
import json
import os

# 設置日誌記錄
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用於安全地簽名session

load_dotenv()  # 加載 .env 文件中的變量

# OAuth 配置
CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID")
CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET")
AUTHORIZATION_BASE_URL = os.getenv("OAUTH2_AUTHORIZATION_URL")
TOKEN_URL = os.getenv("OAUTH2_TOKEN_URL")
REDIRECT_URI = os.getenv("OAUTH2_REDIRECT_URI")
RESOURCE = os.getenv("OAUTH2_RESOURCE")
USER_INFO_URL = "https://fs.ncku.edu.tw/adfs/userinfo"  # 更新的 UserInfo 端點
LOGOUT_URL = "https://fs.ncku.edu.tw/adfs/ls/?wa=wsignout1.0&wreply=https://chatbot.oia.ncku.edu.tw"


def clear_token():
    if "oauth_token" in session:
        del session["oauth_token"]

# @app.route("/")
# def index():
#     clear_token()  # 清除舊的token
#     ncku = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
#     authorization_url, state = ncku.authorization_url(AUTHORIZATION_BASE_URL, resource=RESOURCE)
#     session["oauth_state"] = state
#     return redirect(authorization_url)

@app.route("/")
def index():
    # Perform logout first
    logout_redirect = f"https://fs.ncku.edu.tw/adfs/ls/?wa=wsignout1.0&wreply=https://chatbot.oia.ncku.edu.tw/start-auth"
    return redirect(logout_redirect)

@app.route("/start-auth")
def start_auth():
    # Clear existing session and token after logout
    session.clear()
    clear_token()
    
    # Start the OAuth authorization process
    ncku = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    authorization_url, state = ncku.authorization_url(AUTHORIZATION_BASE_URL, resource=RESOURCE)
    session["oauth_state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    authorization_code = request.args.get("code")
    try:
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
        response = requests.post(TOKEN_URL, data=data)
        if response.status_code == 200:
            token = response.json()
            session["access_token"] = token
            return redirect(url_for("fill_form"))
        else:
            return f"Failed to fetch token: {response.json()}", 400
    except Exception as e:
        return f"Failed to fetch token: {str(e)}", 400

@app.route("/fill-form")
def fill_form():
    if "access_token" not in session:
        return "User info not found in the session", 400
    token = session.get("access_token")
    user_info = decode_token(token['access_token'])
    print(f"\n\n\nUser info: {user_info}\n\n\n")
    return render_template("fill_form.html", user_info=user_info)

def decode_token(access_token):
    try:
        jwt_parts = access_token.split('.')
        if len(jwt_parts) != 3:
            raise ValueError("Invalid token format")
        payload_encoded = jwt_parts[1]
        payload_encoded += '=' * (4 - len(payload_encoded) % 4)
        payload_decoded = base64.urlsafe_b64decode(payload_encoded)
        payload = json.loads(payload_decoded)
        return payload
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        return {}

@app.route("/submit-info", methods=["POST"])
def submit_info():
    name = request.form.get("name")
    department = request.form.get("department")
    student_id = request.form.get("student_id")
    nationality = request.form.get("nationality")
    print(f"姓名: {name}, 系級: {department}, 學號: {student_id}, 國籍: {nationality}")
    
    # 打印所有提交的表單數據
    print("\n所有提交的表單數據:")
    for key, value in request.form.items():
        print(f"{key}: {value}")
    return f"資料提交成功！\n姓名: {name}, 系級: {department}, 學號: {student_id}, 國籍: {nationality}"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
