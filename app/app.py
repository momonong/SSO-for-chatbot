from flask import Flask, redirect, request, render_template, session, url_for
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import os
import logging

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
    print(f'CLIENT_ID: {CLIENT_ID}')
    print(f'CLIENT_SECRET: {CLIENT_SECRET}')
    print(f'AUTHORIZATION_BASE_URL: {AUTHORIZATION_BASE_URL}')
    print(f'TOKEN_URL: {TOKEN_URL}')
    print(f'REDIRECT_URI: {REDIRECT_URI}')
    
    ncku = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    authorization_url, state = ncku.authorization_url(AUTHORIZATION_BASE_URL, resource=RESOURCE)
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    ncku = OAuth2Session(CLIENT_ID, state=session.get('oauth_state'), redirect_uri=REDIRECT_URI)
    try:
        print(f'Authorization response: {request.url}')
        token = ncku.fetch_token(TOKEN_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, authorization_response=request.url)
        print(f'Token: {token}')
    except Exception as e:
        print(f'Error fetching token: {str(e)}')
        return f'Failed to fetch token: {str(e)}', 400

    session['oauth_token'] = token
    return redirect(url_for('fill_form'))

@app.route('/fill-form')
def fill_form():
    # 檢查 session 中是否有用戶資訊
    if 'oauth_token' not in session:
        return 'User info not found in the session', 400
    user_info = session.get('oauth_token')
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