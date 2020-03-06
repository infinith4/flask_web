from application import app
from flask import request, redirect, url_for, render_template, flash, make_response
from application.bip39mnemonic import Bip39Mnemonic
import os
# ファイル名をチェックする関数
from werkzeug.utils import secure_filename
import polyglot  # pip3 install polyglot-bitcoin
import numpy as np
import requests
import json
import binascii

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

@app.route("/download", methods=["GET", "POST"])
def download():
    if request.method == "GET":
        html = render_template('download.html', title="download")
        return html
    elif request.method == "POST":
        txid = request.form["transaction"]
        url = "https://api.whatsonchain.com/v1/bsv/test/tx/hash/" + txid
        headers = {"content-type": "application/json"}
        r = requests.get(url, headers=headers)
        data = r.json()
        print(json.dumps(data, indent=4))
        op_return = data['vout'][0]['scriptPubKey']['opReturn']
        print(json.dumps(op_return, indent=4))  ## bcat.bico.media
        print(op_return['parts'][0])
        upload_data = data['vout'][0]['scriptPubKey']['asm'].split()[3] ##uploaddata (charactor)
        upload_mimetype = op_return['parts'][1] ##MEDIA_Type:  image/png, image/jpeg, text/plain, text/html, text/css, text/javascript, application/pdf, audio/mp3
        upload_charset = op_return['parts'][2] ##ENCODING: binary, utf-8 (Definition polyglot/upload.py)
        upload_filename = op_return['parts'][3] ##filename
        print("upload_mimetype: " + upload_mimetype)
        print("upload_charset: " + upload_charset)
        print("upload_filename: " + upload_filename)
        download_path = './application/download'

        # if not os.path.isdir(download_path):
        #     os.mkdir(download_path)
        # path_w = os.path.join(download_path, txid)
        # with open(path_w, mode='wb') as f:
        #     f.write(binascii.unhexlify(binary))
        response = make_response()
        if upload_charset == 'binary':  #c09f039ca4a919aec0d33fbf3931c35989240892b3f29da11fc66ed65695f967
            #print(binascii.hexlify(upload_data))
            response.data = binascii.unhexlify(upload_data)
        elif upload_charset == 'utf-8':  #cc80675a9a64db116c004b79d22756d824b16d485990a7dfdf46d4a183b752b2
            response.data = op_return['parts'][0]
        else:
            response.data = ''
        downloadFilename = upload_filename
        response.headers["Content-Disposition"] = 'attachment; filename=' + downloadFilename
        response.mimetype = upload_mimetype
        return response


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == 'GET':
        html = render_template('upload.html', title="upload")
        return html
    # リクエストがポストかどうかの判別
    elif request.method == 'POST':
        bsv_mnemonic = request.form["mnemonic"]  #app.config['TESTNET_MNEMONIC']
        bip39Mnemonic = Bip39Mnemonic(bsv_mnemonic, passphrase="", network="test")
        
        # ファイルがなかった場合の処理
        if 'file' not in request.files:
            print('ファイルがありません')
            flash('ファイルがありません')
            return redirect(request.url)
        # データの取り出し
        req_file = request.files['file']
        print(req_file)
        stream = req_file.stream
        #img_array = np.asarray(bytearray(stream.read()), dtype=np.uint8)

        # ファイル名がなかった時の処理
        if req_file.filename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        # ファイルのチェック
        if req_file and allwed_file(req_file.filename):
            # 危険な文字を削除（サニタイズ処理）
            #filename = secure_filename(req_file.filename)
            # ファイルの保存
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], req_file.filename)
            #req_file.save(filepath)
            uploader = polyglot.Upload(bip39Mnemonic.privatekey_wif, 'test')
            print(uploader.network)
            req_file_bytearray = bytearray(stream.read())
            print(req_file_bytearray)
            #transaction = uploader.bcat_parts_send_from_binary(req_file_bytearray)
            media_type = uploader.get_media_type_for_file_name(req_file.filename)
            encoding = uploader.get_encoding_for_file_name(req_file.filename)
            print(media_type)
            print(encoding)
            rawtx = uploader.b_create_rawtx_from_binary(req_file_bytearray, media_type, encoding, req_file.filename)
            txid = uploader.send_rawtx(rawtx)
            #transaction = uploader.upload_b(filepath)
            #['5cd293a25ecf0b346ede712ceb716f35f1f78e2c5245852eb8319e353780c615']
            print(txid)
            # アップロード後のページに転送
            html = render_template(
                'uploaded.html', 
                transaction = txid, 
                privatekey_wif = bip39Mnemonic.privatekey_wif,
                title="mnemonic")

            return html
        else:
            html = render_template(
                'uploaded.html', 
                transaction = "error", 
                privatekey_wif = bip39Mnemonic.privatekey_wif,
                title="mnemonic")
            return html

# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif', 'txt'])

def allwed_file(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS