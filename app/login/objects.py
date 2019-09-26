# -*- coding: utf-8 -*-
# @Time    : 9/5/19 11:44 AM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: objects.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.1.0

from .. import db
from ..models import Doctor
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo


class UserForm(FlaskForm):
    """
    登录注册表单验证
    """
    username = StringField('用户名', validators=[DataRequired()])
    password = StringField('密码', validators=[DataRequired()])
    password2 = StringField('确认密码', validators=[DataRequired(), EqualTo('password', '密码不一致')])
    submit = SubmitField('提交')

    def validate_username(self, field):
        # 验证用户名是否重复
        if db.session.query(Doctor).filter(Doctor.name == field.data).first():
            raise ValidationError('用户名已存在')

        # 对用户名长度进行判断
        if len(field.data) < 3:
            raise ValidationError('用户名长度不能少于3个字符')
        if len(field.data) > 6:
            raise ValidationError('用户名长度不能大于6个字符')