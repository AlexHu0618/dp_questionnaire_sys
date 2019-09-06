# -*- coding: utf-8 -*-
# @Time    : 9/2/19 10:41 AM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: views.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.1.0

from . import auth
from flask import render_template


@auth.route('/', methods=['GET'])
def login():
    return render_template('indexMine.html')
