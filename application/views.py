from application import app
from flask import request, redirect, url_for, render_template, flash
from application.bip39mnemonic import Bip39Mnemonic
import os
# ファイル名をチェックする関数
from werkzeug.utils import secure_filename

@app.route('/')
def index():
    html = render_template('index.html', a = 'index', title="Index")
    return html

@app.route('/hello')
def hello():
    html = render_template('index.html', a = 'aaaa', title="HelloTitle")
    return html

@app.route('/mnemonic')
def get_mnemonic():
    html = render_template('mnemonic.html', title="mnemonic")
    return html

@app.route("/mnemonic", methods=["POST"])
def post_mnemonic():
    bsv_mnemonic = request.form["mnemonic"]  #app.config['TESTNET_MNEMONIC']
    bip39Mnemonic = Bip39Mnemonic(bsv_mnemonic, passphrase="", network="test")
    html = render_template('mnemonic.html', privatekey_wif = bip39Mnemonic.privatekey_wif, title="mnemonic")
    return html

@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == 'GET':
        html = render_template('upload.html', title="upload")
        return html
    # リクエストがポストかどうかの判別
    if request.method == 'POST':
        # ファイルがなかった場合の処理
        if 'file' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        # データの取り出し
        file = request.files['file']
        # ファイル名がなかった時の処理
        if file.filename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        # ファイルのチェック
        if file and allwed_file(file.filename):
            # 危険な文字を削除（サニタイズ処理）
            filename = secure_filename(file.filename)
            # ファイルの保存
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # アップロード後のページに転送
            return redirect(request.url)

# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])

def allwed_file(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS