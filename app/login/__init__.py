# -*- coding: utf-8 -*-
# @Time    : 9/4/19 5:29 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: __init__.py.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.2.0

from flask import Blueprint

login = Blueprint('login', __name__, url_prefix='/login', template_folder='templates')  # the 2 arg is Blueprint name and which package the Blueprint belong to

from . import views
