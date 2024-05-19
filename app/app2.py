from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '歡迎來到我的Flask應用！'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
