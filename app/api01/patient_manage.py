# -*- coding: utf-8 -*-
# @Time    : 9/9/19 3:31 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: patient_manage.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.4.0


from flask_restful import Resource, reqparse
from flask import jsonify, session
from app import STATE_CODE
from ..models import MapPatientQuestionnaire, Questionnaire, ResultShudaifu, Question, Option
import datetime
from sqlalchemy import text
import re
from .. import db


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
        did = session.get('did')
        print('did = ', did)
        ## query single patient
        if id_get is not None:
            rsl = MapPatientQuestionnaire.query.filter_by(patient_id=id_get).first()
            if rsl:
                p = rsl.patient
                d = rsl.doctor
                which_day_on = (datetime.datetime.now() - rsl.dt_built).days
                records = self.getRecord4patient(id_get)
                qn = {'status': rsl.status, 'date': which_day_on, 'cycle': rsl.total_days,
                      'start': datetime.datetime.strftime(rsl.dt_built, '%Y-%m-%d'), 'records': records}
                resp = {'name': p.name, 'sex': p.sex, 'birthday': datetime.datetime.strftime(p.birthday, '%Y-%m-%d'),
                        'nation': p.nation, 'phone': p.tel, 'avatarUrl': p.url_portrait,
                        'email': p.email, 'age': rsl.age, 'height': rsl.height, 'weight': rsl.weight, 'pid': p.id,
                        'smoking': rsl.is_smoking, 'drinking': rsl.is_drink, 'surgery': rsl.is_operated,
                        'hospital': d.department.hospital.name, 'subject': d.department.name, 'treatment': rsl.questionnaire.medicine.name,
                        'reviewer': d.name, 'reviewTime': datetime.datetime.strftime(rsl.dt_built, '%Y-%m-%d'), 'questionnaire': qn}
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
                                                       MapPatientQuestionnaire.doctor_id == did if did != 16 else text(''),
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

    def dateRange(self, begindate, enddate):
        dates = []
        dt = begindate.date()
        date = begindate.date()
        while date <= enddate.date():
            dates.append(date)
            dt = dt + datetime.timedelta(1)
            date = dt
        return dates

    def getRecord4patient(self, pid):
        records = []
        rsl_r = db.session.query(ResultShudaifu, Question).join(Question, ResultShudaifu.question_id == Question.id).filter(
            ResultShudaifu.patient_id == pid).order_by(ResultShudaifu.is_doctor, ResultShudaifu.dt_answer).all()
        print(db.session.query(ResultShudaifu, Question).join(Question, ResultShudaifu.question_id == Question.id).filter(
            ResultShudaifu.patient_id == pid).order_by(ResultShudaifu.is_doctor, ResultShudaifu.dt_answer))
        if rsl_r:  # [(R, Q), ...]
            print(rsl_r)
            dt_min = rsl_r[0][0].dt_answer
            dt_max = rsl_r[-1][0].dt_answer
            date_list = self.dateRange(dt_min, dt_max)
            print(date_list)
            records = []
            for date in date_list:  # search every day from begin to end
                clock = False
                is_doctor = False
                questions = []
                flag = 0
                for r in rsl_r:  # search every record for matching date
                    if r[0].dt_answer.date() == date:
                        clock = True
                        if r[0].is_doctor != flag:
                            record = {'index': date_list.index(date) + 1, 'clock': clock, 'isDoctor': is_doctor,
                                      'questions': questions}
                            records.append(record)
                            questions = []
                            is_doctor = True
                            flag = 1
                        answer = self.getOption4oneQ(r[0].answer, r[0].type)
                        item = {'ask': r[1].title, 'answer': answer}
                        questions.append(item)
                    elif r[0].dt_answer.date() < date:
                        continue
                    else:
                        break
                record = {'index': date_list.index(date) + 1, 'clock': clock, 'isDoctor': is_doctor, 'questions': questions}
                records.append(record)
            else:
                pass
            print(records)
        return records

    def getOption4oneQ(self, option_str, qtype):
        option = []
        if qtype == 2:  # multiple choice
            opt_str = re.split(',', option_str)
            opt_id_list = list(map(int, opt_str))
            rsl = Option.query.filter(Option.id.in_(opt_id_list)).all()
            if rsl:
                option = [o.content for o in rsl]
        else:  # single choice or filling
            rsl = Option.query.filter(Option.id == int(option_str)).one_or_none()
            if rsl:
                option = [rsl.content]
        return option
