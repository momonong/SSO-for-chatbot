# poetry add pysaml2 requests_oauthlib

from flask import Flask, redirect, request, render_template, session, url_for
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('No secret key set for Flask application')
app.secret_key = SECRET_KEY

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
    authorization_url, _ = ncku.authorization_url(AUTHORIZATION_BASE_URL)
    # 將用戶重定向到 NCKU 進行認證
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    ncku = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    ncku.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=request.url)
    # 存取 token 資料到 session 中，可用於後續認證
    session['oauth_token'] = ncku.token
    # 重定向到表單填寫頁面
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
    app.run(debug=True, port=8000)
