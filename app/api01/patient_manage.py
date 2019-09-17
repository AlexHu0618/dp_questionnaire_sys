# -*- coding: utf-8 -*-
# @Time    : 9/9/19 3:31 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: patient_manage.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.4.0


from flask_restful import Resource, reqparse
from flask import jsonify
from .. import db
from ..models.models import Patient


parser = reqparse.RequestParser()
parser.add_argument("Name", type=str, location=["json", "args"])


class Patients(Resource):
    def get(self):
        name = parser.parse_args().get('Name')
        rsl = Patient.query.filter_by(name=name).first()
        print(rsl)
        if rsl:
            return jsonify({'name': rsl.name})
