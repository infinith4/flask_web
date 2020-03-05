from application import app
from flask import request, redirect, url_for, render_template, flash
from application.bip39mnemonic import Bip39Mnemonic

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
    bsv_mnemonic = request.form["mnemonic"]#app.config['TESTNET_MNEMONIC']
    bip39Mnemonic = Bip39Mnemonic(bsv_mnemonic, passphrase="", network="test")
    html = render_template('mnemonic.html', privatekey_wif = bip39Mnemonic.privatekey_wif, title="mnemonic")
    return html