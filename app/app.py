from flask import Flask, redirect, request, render_template, session, url_for, jsonify
from requests_oauthlib import OAuth2Session
from flask_session import Session
from datetime import timedelta
from dotenv import load_dotenv
import requests
import logging
import base64
import json
import os
import httpx
import asyncio


# 設置日誌記錄
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用於安全地簽名session

load_dotenv()  # 加載 .env 文件中的變量

# Flask-Session配置
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=4)
app.config["SESSION_FILE_DIR"] = os.path.join(app.instance_path, "session_files")
Session(app)

# OAuth 配置
CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID")
CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET")
AUTHORIZATION_BASE_URL = os.getenv("OAUTH2_AUTHORIZATION_URL")
TOKEN_URL = os.getenv("OAUTH2_TOKEN_URL")
REDIRECT_URI = os.getenv("OAUTH2_REDIRECT_URI")
RESOURCE = os.getenv("OAUTH2_RESOURCE")
USER_INFO_URL = os.getenv("OAUTH2_USER_INFO_URL")
LOGOUT_URL = os.getenv("OAUTH2_LOGOUT_URL")


def clear_token():
    if "oauth_token" in session:
        del session["oauth_token"]


def decode_token(access_token):
    try:
        jwt_parts = access_token.split(".")
        if len(jwt_parts) != 3:
            raise ValueError("Invalid token format")
        payload_encoded = jwt_parts[1]
        payload_encoded += "=" * (4 - len(payload_encoded) % 4)
        payload_decoded = base64.urlsafe_b64decode(payload_encoded)
        payload = json.loads(payload_decoded)
        return payload
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        return {}


def normalize_name(display_name, student_en_name):
    """
    Normalize the display name and student English name to ensure consistent formatting.
    """
    if student_en_name.lower() not in display_name.lower():
        full_name = f"{display_name} {student_en_name}"
    else:
        full_name = display_name
    return full_name


# @app.route("/", methods=["GET"])
# def index():
#     chat_id = request.args.get("chat_id")
#     if chat_id:
#         # 在這裡處理接收到的 chat_id，比如保存到數據庫或其他操作
#         print(f"\n\nReceived chat_id: {chat_id}\n\n")
#         session["chat_id"] = chat_id
#     else:
#         print(f"Did not receive chat_id")

#     # Perform logout first
#     logout_redirect = f"https://fs.ncku.edu.tw/adfs/ls/?wa=wsignout1.0&wreply=https://chatbot.oia.ncku.edu.tw/start-auth"
#     response = redirect(logout_redirect)

#     return response


@app.route("/", methods=["GET"])
def index():
    chat_id = request.args.get("chat_id")
    if chat_id:
        # 在這裡處理接收到的 chat_id，比如保存到數據庫或其他操作
        print(f"\n\nReceived chat_id: {chat_id}\n\n")
        session["chat_id"] = chat_id
    else:
        print(f"Did not receive chat_id")

    return render_template("index.html")  # 渲染主页，不清除session


@app.route("/logout")
def logout():
    # Clear current user's session and token during logout
    session.clear()
    logout_redirect = f"https://fs.ncku.edu.tw/adfs/ls/?wa=wsignout1.0&wreply=https://chatbot.oia.ncku.edu.tw/start-auth"
    return redirect(logout_redirect)


@app.route("/start-auth")
def start_auth():
    chat_id = session.get("chat_id")
    if chat_id:
        print(f"\n\nUsing chat_id from session: {chat_id}\n\n")
    else:
        return "No chat_id found in session", 400

    ncku = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    authorization_url, state = ncku.authorization_url(
        AUTHORIZATION_BASE_URL, resource=RESOURCE
    )
    session["oauth_state"] = state
    session["chat_id"] = chat_id  # 再次保存 chat_id
    print(f"\n\noauth state: {state}\nChat ID: {chat_id}\n\n")
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
            print(f"\n\nAccess token: {token}\n\n")
            print(f"\n\nSession: {session}\n\n")
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
    user_info = decode_token(token["access_token"])
    user_info["normalized_name"] = normalize_name(
        user_info["DisplayName"], user_info["studentStuEnName"]
    )
    print(f"\n\nUser info: {user_info}\n\n")
    return render_template("fill_form.html", user_info=user_info)


@app.route("/submit-info", methods=["POST"])
def submit_info():
    name = request.form.get("name")
    department = request.form.get("department")
    student_id = request.form.get("student_id")
    nationality = request.form.get("nationality")
    chat_id = session.get("chat_id")

    # 打印所有提交的表單數據
    print("\n所有提交的表單數據:")
    for key, value in request.form.items():
        print(f"{key}: {value}")
    print("\n\n")
    redirect_url = f"https://3dd1-140-116-249-221.ngrok-free.app/sign_up/{nationality}&{student_id}&{name}&{department}&{chat_id}"

    # Asynchronous request
    response = asyncio.run(send_async_request(redirect_url))
    if response:
        print(f"\n\nredirect_url: {redirect_url}\n\n")
        return render_template("submission_success.html")
    else:
        return "資料提交失敗，請稍後再試。", 500


async def send_async_request(url):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                print("Data successfully sent to the API.")
                return response.text
            else:
                print(f"Failed to send data to the API: {response.status_code}")
                return (
                    f"Failed to send data to the API: {response.status_code}",
                    response.status_code,
                )
        except Exception as e:
            print(f"Error sending data to the API: {str(e)}")
            return f"Error sending data to the API: {str(e)}", 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
