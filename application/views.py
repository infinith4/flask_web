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
def mnemonic():
    bsv_mnemonic = app.config['TESTNET_MNEMONIC']
    bip39Mnemonic = Bip39Mnemonic(bsv_mnemonic, passphrase="", network="test")
    html = render_template('index.html', a = bip39Mnemonic.privatekey_wif, title="mnemonic")
    return html
