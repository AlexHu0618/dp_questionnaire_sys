# -*- coding: utf-8 -*-
# @Time    : 9/4/19 5:29 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: views.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.1.0

from flask import render_template, request, redirect, url_for
from . import login
from .objects import UserForm
from ..models import Doctor, Patient
from werkzeug.security import generate_password_hash
from .. import db


@login.route('/', methods=['GET'])
def login1():
    return render_template('login.html')


@login.route('/register', methods=['GET', 'POST'])
def register1():
    form = UserForm()
    if request.method == 'GET':
        return render_template('register.html', form=form)

    if request.method == 'POST':
        # 判断表单中的数据是否通过验证
        if form.validate_on_submit():
            # 获取验证通过后的数据
            username = form.username.data
            password = form.password.data
            # save
            user = Doctor()
            user.name = username
            user.patients = [Patient(name='p1')]
            # encrypt
            user.password = generate_password_hash(password)
            savedb(user)
            return redirect(url_for('login.login1'))
        return render_template('register.html', form=form)


def savedb(obj):
    db.session.add(obj)
    db.session.commit()
