from flask import Flask

app = Flask(__name__)
app.config.from_object('application.config')

import application.views

# 画像のアップロード先のディレクトリ
UPLOAD_FOLDER = './application/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

