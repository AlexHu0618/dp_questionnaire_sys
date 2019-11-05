# -*- coding: utf-8 -*-
# @Time    : 8/28/19 12:11 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: views.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.0.0

from flask import render_template, make_response, send_from_directory
from . import main
from flask_login import login_required, current_user
import os


# URL for index page
@main.route('/', methods=['GET'])
# @login_required
def index():
    return render_template('index.html')
    # return render_template('index.html', current_user=current_user)


@main.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = os.path.abspath(os.path.dirname(__file__)) + '/download/'  # 获取当前文件所在目录
    print(directory)
    response = make_response(send_from_directory(directory, filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
    return response
