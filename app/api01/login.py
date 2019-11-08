# -*- coding: utf-8 -*-
# @Time    : 9/5/19 11:33 AM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: login.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.2.1

from flask_restful import Resource, reqparse, request
from flask import jsonify, session
from app import STATE_CODE
from ..models import Doctor

parser = reqparse.RequestParser()
parser.add_argument("username", type=str, location=["form", "json", "args"])
parser.add_argument("password", type=str, location=["form", "json", "args"])


class Login(Resource):
    def post(self):
        print(request.get_json())
        print(request.headers)
        print(request.cookies)
        username = parser.parse_args().get('username')
        password = parser.parse_args().get('password')
        rsl_d = Doctor.query.filter(Doctor.name == username, Doctor.password == password).one_or_none()
        if rsl_d:
            session['did'] = rsl_d.id
            resp = {'id': rsl_d.id, 'name': rsl_d.name}
            return jsonify(dict(resp, **STATE_CODE['200']))
        else:
            return STATE_CODE['401']

    def delete(self):
        session.pop('did')
