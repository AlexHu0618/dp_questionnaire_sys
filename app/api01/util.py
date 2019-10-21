# -*- coding: utf-8 -*-
# @Time    : 10/21/19 12:26 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: util.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.1.0

from flask_restful import Resource
from flask import jsonify
from app import STATE_CODE
from ..models import Hospital, Department, Medicine


class Util(Resource):
    def get(self):
        hospitals = []
        rsl = Hospital.query.all()
        if rsl:
            for h in rsl:
                rsl_d = Department.query.filter(Department.hospital_id == h.id).all()
                if rsl_d:
                    departments = [{'id': d.id, 'name': d.name} for d in rsl_d]
                else:
                    departments = []
                hospital = {'id': h.id, 'name': h.name, 'subjects': departments}
                hospitals.append(hospital)
        else:
            return STATE_CODE['204']
        rsl = Medicine.query.all()
        if rsl:
            medicines = [{'id': m.id, 'name': m.name} for m in rsl]
        else:
            return STATE_CODE['204']
        resp = {'hospitals': hospitals, 'treatment': medicines}
        return jsonify(dict(resp, **STATE_CODE['200']))


