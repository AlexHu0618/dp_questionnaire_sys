# -*- coding: utf-8 -*-
# @Time    : 8/28/19 12:11 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: views.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.0.0

from flask import render_template
from . import main


# URL for index page
@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')
