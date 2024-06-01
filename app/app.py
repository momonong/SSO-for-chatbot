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

@app.route('/')
def index():
    # 啟動 OAuth 登入流程
    ncku = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    authorization_url, state = ncku.authorization_url(AUTHORIZATION_BASE_URL)
    # 將狀態存儲在 session 中以進行後續驗證
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    if 'oauth_state' not in session:
        app.logger.debug('State not found in session')
        return 'State not found in session', 400

    ncku = OAuth2Session(CLIENT_ID, state=session['oauth_state'], redirect_uri=REDIRECT_URI)
    try:
        token = ncku.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=request.url)
    except Exception as e:
        app.logger.error(f'Failed to fetch token: {str(e)}')
        return f'Failed to fetch token: {str(e)}', 400

    session['oauth_token'] = token
    app.logger.debug(f'Token: {token}')
    return redirect(url_for('fill_form'))

@app.route('/fill-form')
def fill_form():
    # 檢查 session 中是否有用戶資訊
    if 'oauth_token' not in session:
        return 'User info not found in the session', 400
    return render_template('fill_form.html', user_info=session.get('oauth_token'))

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