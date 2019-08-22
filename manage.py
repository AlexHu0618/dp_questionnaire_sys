# -*- coding: utf-8 -*-
# @Time    : 8/22/19 5:48 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: manage.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.0.0

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
