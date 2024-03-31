# pip install pysaml2

from flask import Flask, request, render_template, session, redirect, url_for
from saml2 import BINDING_HTTP_POST
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('No secret key set for Flask application')
app.secret_key = SECRET_KEY

# 示例路徑，請根據實際存放元數據的位置進行調整
metadata_path = 'config/sp_metadata.xml'
# 在創建SAML客戶端之前，不使用url_for
acs_url = 'http://localhost:5000/saml/acs/'

# 這裡配置您的 SAML
saml_config = {
    'entityid': 'http://localhost:5000/saml/metadata',
    'service': {
        'sp': {
            'endpoints': {
                'assertion_consumer_service': [
                    # 終端URL應該和SP metadata中聲明的相匹配，使用url_for生成完整URL
                    (acs_url, BINDING_HTTP_POST),
                ],
            },
            # ...（其他服務提供者設定，例如要求的名稱ID格式等）...
        },
    },
    'metadata': {
        'local': [metadata_path],
    },
    # 其他 SAML 配置，例如證書、加密等...
}

# 確保 SAML 客戶端實例化時使用你的配置
saml_client = Saml2Client(Saml2Config(saml_config))

@app.route('/')
def index():
    # 啟動 SSO 登入流程
    authn_request = saml_client.prepare_for_authenticate()
    redirect_url = authn_request[1]['headers'][0][1]
    return redirect(redirect_url)

@app.route('/saml/acs/', methods=['POST'])
def acs():
    # 獲取POST請求中的SAMLResponse
    saml_response = request.form.get('SAMLResponse')
    if not saml_response:
        return 'SAMLResponse not found in the request.', 400

    try:
        authn_response = saml_client.parse_authn_request_response(
            saml_response, BINDING_HTTP_POST
        )
    except Exception as e:
        app.logger.error(f'Failed to parse SAML response: {e}')
        return 'Failed to authenticate.', 400
    
    # 獲取用戶信息
    user_info = authn_response.get_identity()
    
    # 將用戶信息保存在會話中
    session['user_info'] = user_info
    
    # 重定向到表單填寫頁
    return redirect(url_for('fill_form'))

@app.route('/fill-form')
def fill_form():
    # 檢查用戶信息是否已經保存在會話中
    if 'user_info' not in session:
        return 'User info not found in the session', 400
    
    user_info = session['user_info']
    
    # 渲染帶有用戶信息的填寫表單頁面
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
    app.run(debug=True, port=5000)