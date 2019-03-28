# -*- coding: utf-8 -*-
from app import app

if __name__ == '__main__':
    print(app.url_map)
    app.run(host="0.0.0.0", port=8089)