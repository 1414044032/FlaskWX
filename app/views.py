# -*- coding: utf-8 -*-
from . import app
from flask import redirect, url_for
from .v1 import wxchart


@app.route('/')
def redict():
    return redirect(url_for('v1.login'))


app.register_blueprint(wxchart, url_prefix='/wechat')