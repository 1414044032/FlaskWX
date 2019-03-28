# -*- coding: utf-8 -*-
from . import app
from .v1 import wxchart

app.register_blueprint(wxchart, url_prefix='/wechat')