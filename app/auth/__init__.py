# -*- coding: utf-8 -*-
# @Time    : 9/2/19 10:38 AM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: __init__.py.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.1.0

# define route by Blueprint

from flask import Blueprint

auth = Blueprint('auth', __name__, url_prefix='/login')  # the 2 arg is Blueprint name and which package the Blueprint belong to

from . import views   # the route actually in the model views.py, import it that can \
                                # relevance route and Blueprint, must be imported at the end of Blueprint