from flask import Flask
import os

app = Flask(__name__)

CERT_FOLDER = os.path.abspath('/etc/ssl/')
CERT_PATH = os.path.join(CERT_FOLDER, 'certificate.pem')
KEY_PATH = os.path.join(CERT_FOLDER, 'private.pem')

@app.route('/')
def index():
    return '歡迎來到我的Flask應用！'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    # app.run(ssl_context=(CERT_PATH, KEY_PATH), debug=True, host='0.0.0.0', port=8080)