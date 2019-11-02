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
from flask_login import login_required, current_user


# URL for index page
@main.route('/', methods=['GET'])
# @login_required
def index():
    return render_template('index.html')
    # return render_template('index.html', current_user=current_user)



