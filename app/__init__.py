# -*- coding: utf-8 -*-
from flask import Flask
# from flask_pymongo import PyMongo
import logging
app = Flask(__name__)
# 日志系统配置
handler = logging.FileHandler('app.log', encoding='UTF-8')
logging_format = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(logging_format)
# handler.setLevel(level=logging.DEBUG)
app.logger.addHandler(handler)
app.logger.setLevel(level=logging.DEBUG)
app.config.from_object('app.setting')

app.config["MONGO_URI"] = "mongodb://localhost:27017/wangliuqi"

# mongo = PyMongo(app)
from . import views

