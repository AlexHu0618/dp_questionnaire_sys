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
from app import STATE_CODE
from ..models import MapPatientQuestionnaire, Questionnaire
import datetime
from sqlalchemy import text


parser = reqparse.RequestParser()
parser.add_argument("name", type=str, location=["form", "json", "args"])
parser.add_argument("id", type=int, location=["args", "json", "form"])
parser.add_argument("sex", type=int, location=["form", "json", "args"])
parser.add_argument("time", type=str, location=["form", "json", "args"])
parser.add_argument("responsibility", type=dict, location=["form", "json", "args"])
parser.add_argument("size", type=int, location=["form", "json", "args"])
parser.add_argument("page", type=int, location=["form", "json", "args"])


class Patients(Resource):
    def get(self):
        """
        get single patient or all patients
        :return:
        """
        id_get = parser.parse_args().get('id')
        ## query single patient
        if id_get is not None:
            rsl = MapPatientQuestionnaire.query.filter_by(patient_id=id_get).first()
            if rsl:
                p = rsl.patient
                d = rsl.doctor
                which_day_on = (datetime.datetime.now() - rsl.dt_built).days
                qn = {'status': rsl.status, 'date': which_day_on, 'cycle': rsl.total_days, 'start': rsl.dt_built,
                     'records': {}}
                resp = {'name': p.name, 'sex': p.sex, 'birthday': p.birthday, 'nation': p.nation, 'phone': p.tel,
                        'email': p.email, 'age': rsl.age, 'height': rsl.height, 'weight': rsl.weight, 'pid': p.id,
                        'smoking': rsl.is_smoking, 'drinking': rsl.is_drinking, 'surgery': rsl.is_operated,
                        'hospital': d.hospital_id, 'subject': d.department_id, 'treatment': d.medicine_id,
                        'reviewer': d.name, 'reviewTime': rsl.dt_built, 'questionnaire': qn}
                return jsonify(dict(resp, **STATE_CODE['200']))
            else:
                return STATE_CODE['204']
        ## query all patients list
        else:
            name = parser.parse_args().get('name')
            date_str = parser.parse_args().get('time')
            date_built = None
            if date_str:
                date_built = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            reqp = parser.parse_args().get('responsibility')
            size = parser.parse_args().get('size')
            page = parser.parse_args().get('page')
            sql = MapPatientQuestionnaire.query.filter(MapPatientQuestionnaire.patient.name == name if name else text(''),
                                                       MapPatientQuestionnaire.status.in_([1, 3]))
            if date_built:
                sql = sql.filter(MapPatientQuestionnaire.dt_built.between(date_built['start'], date_built['end'])).order_by(
                    desc(MapPatientQuestionnaire.dt_built))
            if reqp:
                rsl_qn = Questionnaire.query(Questionnaire.id).filter(
                    Questionnaire.hospital_id == reqp['hospitalID'] if reqp['hospitalID'] else '',
                    Questionnaire.department_id == reqp['subjectID'] if reqp['subjectID'] else '',
                    Questionnaire.medicine_id == reqp['treatmentID'] if reqp['treatmentID'] else '').all()
                if rsl_qn:
                    qn_id = [i[0] for i in rsl_qn]
                    sql = sql.filter(MapPatientQuestionnaire.questionnaire_id.in_(qn_id))
            rsl = sql.paginate(page=page if page else 1, per_page=size if size else 10)
            if rsl:
                items = [{'name': i.patient.name, 'hospital': i.questionnaire.hospital.name, 'subject': i.questionnaire.department.name,
                         'treatment': i.questionnaire.medicine.name, 'sex': i.patient.sex, 'url': i.patient.url_portrait,
                         'start': i.dt_built.strftime('%Y-%m-%d'), 'status': i.status, 'pid': i.patient_id,
                          'qnid': i.questionnaire_id} for i in rsl.items]
                resp = {'total': rsl.total, 'page': rsl.pages, 'items': items}
                print(resp)
                return jsonify(dict(resp, **STATE_CODE['200']))
            else:
                return STATE_CODE['204']
