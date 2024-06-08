from flask import Flask, redirect, request, render_template, session, url_for
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import os
import logging
import requests

# 設置日誌記錄
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用於安全地簽名session

load_dotenv()  # 加載 .env 文件中的變量

# OAuth 配置
CLIENT_ID = os.getenv('OAUTH2_CLIENT_ID')
CLIENT_SECRET = os.getenv('OAUTH2_CLIENT_SECRET')
AUTHORIZATION_BASE_URL = os.getenv('OAUTH2_AUTHORIZATION_URL')
TOKEN_URL = os.getenv('OAUTH2_TOKEN_URL')
REDIRECT_URI = os.getenv('OAUTH2_REDIRECT_URI')
RESOURCE = 'https://chatbot.oia.ncku.edu.tw/callback'  # Update with your actual resource identifier


def clear_token():
    if 'oauth_token' in session:
        del session['oauth_token']

@app.route('/')
def index():
    clear_token()  # 清除舊的token
    ncku = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    authorization_url, state = ncku.authorization_url(AUTHORIZATION_BASE_URL, resource=RESOURCE)
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    authorization_code = request.args.get('code')
    # print(f'Authorization code: {authorization_code}')
    
    # Build request body
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    # Send POST request
    response = requests.post(TOKEN_URL, data=data)

    # Check request result
    if response.status_code == 200:
        token = response.json()
        # print(f'Token: {token}')
        session['access_token'] = token
        return redirect(url_for('fill_form'))
    else:
        # print(f'Error fetching token: {response.json()}')
        return f'Failed to fetch token: {response.json()}', 400


@app.route('/fill-form')
def fill_form():
    # 檢查 session 中是否有用戶資訊
    if 'access_token' not in session:
        return f'User info not found in the session \n{session["access_token"]}, {session}', 400
    user_info = session.get('oauth_token')
    print(user_info)
    return render_template('fill_form.html', user_info=user_info)

@app.route('/submit-info', methods=['POST'])
def submit_info():
    # 從表單中獲取資料
    name = request.form.get('name')
    department = request.form.get('department')
    student_id = request.form.get('student_id')
    nationality = request.form.get('nationality')
    # 處理這些資料，例如儲存到資料庫或發送到另一個 API
    print(f'姓名: {name}, 系級: {department}, 學號: {student_id}, 國籍: {nationality}')
    # 回應提交成功的訊息
    return '資料提交成功！'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)