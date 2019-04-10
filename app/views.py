# -*- coding: utf-8 -*-
from . import app
from flask import redirect, url_for, render_template, request
from .v1 import wxchat


@app.route('/')
def redict():
    return redirect(url_for('v1.login'))


@app.route('/test')
def test():

    return render_template('test.html')


app.register_blueprint(wxchat, url_prefix='/wechat')