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
from ..models import Hospital, Department, Medicine, Questionnaire, Doctor


class Util(Resource):
    def get(self):
        ## hospitals
        hospitals = []
        rsl_h = Hospital.query.all()
        if rsl_h:
            for h in rsl_h:
                rsl_d = Department.query.filter(Department.hospital_id == h.id).all()
                departments = []
                if rsl_d:
                    for d in rsl_d:
                        rsl = Doctor.query.filter_by(department_id=d.id).all()
                        if rsl:
                            doctors = [{'id': i.id, 'name': i.name} for i in rsl]
                        else:
                            doctors = []
                        department = {'id': d.id, 'name': d.name, 'doctors': doctors}
                        departments.append(department)
                hospital = {'id': h.id, 'name': h.name, 'subjects': departments}
                hospitals.append(hospital)
        else:
            return STATE_CODE['204']
        ## medicine
        medicines = []
        rsl = Medicine.query.all()
        if rsl:
            for m in rsl:
                rsl_qn = Questionnaire.query.filter(Questionnaire.medicine_id == m.id).all()
                if rsl_qn:
                    questionnaires = [{'id': q.id, 'name': q.title} for q in rsl_qn]
                else:
                    questionnaires = []
                medicine = {'id': m.id, 'name': m.name, 'questionnaires': questionnaires}
                medicines.append(medicine)
        else:
            return STATE_CODE['204']

        resp = {'hospitals': hospitals, 'treatments': medicines}
        return jsonify(dict(resp, **STATE_CODE['200']))
