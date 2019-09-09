# -*- coding: utf-8 -*-
# @Time    : 9/4/19 5:29 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: views.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.1.0

from flask import render_template, request, redirect, url_for, flash
from . import login
from .objects import UserForm
from ..models import Doctor, Patient
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from .. import login_manager
from flask_login import login_user, login_required, logout_user


@login_manager.user_loader
def load_user(user_id):
    return Doctor.query.filter_by(id=user_id).first()


@login.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # 校验用户名和密码是否填写完成
        if not all([username, password]):
            flash('请填写用户名和密码')
            return render_template('login.html')
        # 通过用户名获取用户对象
        user = Doctor.query.filter_by(name=username).first()
        # 校验密码是否正确
        if user is not None and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('用户名或者密码错误')

        return redirect(url_for('main.index'))


@login.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


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
