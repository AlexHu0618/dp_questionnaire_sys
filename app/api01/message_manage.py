# -*- coding: utf-8 -*-
# @Time    : 10/21/19 2:55 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: message_manage.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.1.0

from flask_restful import Resource, reqparse, request
from flask import jsonify, session
from app import STATE_CODE
from ..models import MapPatientQuestionnaire, QuestionnaireStruct, Question, ResultShudaifu, Option
import datetime
from .. import db
import re
from sqlalchemy import text, or_, and_


parser = reqparse.RequestParser()
parser.add_argument("page", type=int, location=["form", "json", "args"])
parser.add_argument("questionnaireID", type=str, location=["form", "json", "args"])
parser.add_argument("id", type=int, location=["form", "json", "args"])
parser.add_argument("sid", type=int, location=["form", "json", "args"])
parser.add_argument("result", type=bool, location=["form", "json", "args"])
parser.add_argument("questions", type=list, location=["form", "json", "args"])


class Message(Resource):
    def get(self):
        did = session.get('did')
        page = parser.parse_args().get('page')
        size = parser.parse_args().get('size')
        rsl = MapPatientQuestionnaire.query.filter(MapPatientQuestionnaire.status == 0,
                                                   MapPatientQuestionnaire.doctor_id == did if did != 16 else text('')).paginate(page=page if page else 1, per_page=size if size else 10)
        print(rsl.items)
        if rsl:
            msgs = [{'id': m.patient.id, 'name': m.patient.name,
                     'time': None if m.dt_built is None else m.dt_built.strftime('%Y-%m-%d %H:%M:%S'),
                     'sex': m.patient.sex, 'url': m.patient.url_portrait, 'qnid': m.questionnaire_id,
                     'treatment': m.questionnaire.medicine.name} for m in rsl.items]
            resp = {'list': msgs, 'total': rsl.total}
            print(resp)
            return jsonify(dict(resp, **STATE_CODE['200']))
        else:
            return STATE_CODE['204']

    def post(self):
        """
        select qn for patient
        and then update the record map_patient_questionnaire (qn_id, dt_built, status ...)
        :return:
        """
        print(request.form)
        print(request.args)
        print(request.get_json())
        qn_id = parser.parse_args().get('questionnaireID')
        p_id = parser.parse_args().get('id')
        result = parser.parse_args().get('result')
        print(qn_id, p_id, result)
        rsl = MapPatientQuestionnaire.query.filter_by(patient_id=p_id, questionnaire_id=qn_id).one()
        if rsl:
            if not result:
                ## rejected
                MapPatientQuestionnaire.delete(rsl)
            else:
                total_day = QuestionnaireStruct.query.filter_by(questionnaire_id=qn_id).order_by(QuestionnaireStruct.day_end.desc()).first()
                max_day = total_day.day_end
                qn_struct_first = QuestionnaireStruct.query.filter_by(questionnaire_id=qn_id, respondent=0, period=1).one()
                print(qn_struct_first)
                if qn_struct_first:
                    day_start = qn_struct_first.day_start
                    day_end = qn_struct_first.day_end
                    interval = qn_struct_first.interval
                else:
                    return STATE_CODE['204']
                rsl.status = 4
                rsl.questionnaire_id = qn_id
                # rsl.dt_built = datetime.datetime.now()
                rsl.total_days = max_day
                rsl.current_period = 1
                rsl.days_remained = day_end - day_start
                rsl.interval = interval
                rsl.need_send_task_module = '582',
            try:
                db.session.commit()
                return STATE_CODE['200']
            except Exception as e:
                db.session.rollback()
                return STATE_CODE['409']
        else:
            return STATE_CODE['204']


class Task(Resource):
    def get(self):
        did = session.get('did')
        mpqn_id = parser.parse_args().get('id')
        s_id = parser.parse_args().get('sid')
        if mpqn_id and s_id :
            ## query single task detail
            rsl = MapPatientQuestionnaire.query.filter_by(id=mpqn_id).one()
            if rsl:
                rsl_qs = QuestionnaireStruct.query.filter_by(id=s_id).one()
                if rsl_qs:
                    question_str = re.split(',', rsl_qs.question_id_list)
                    question_list = list(map(int, question_str))
                    questions = []
                    for i in question_list:
                        rsl_q = Question.query.filter_by(id=i).one()
                        if rsl_q:
                            q = {'id': rsl_q.id, 'title': rsl_q.title, 'type': rsl_q.qtype, 'answer': '', 'text': '',
                                 'options': [{'id': o.id, 'option': o.content} for o in rsl_q.options]}
                            questions.append(q)
                        else:
                            return STATE_CODE['204']
                    resp = {'sex': rsl.patient.sex, 'url': rsl.patient.url_portrait, 'timeStart': rsl.dt_built,
                            'treatment': rsl.questionnaire.medicine.name, 'modelName': rsl_qs.title,
                            'questions': questions}
                    print(resp)
                return jsonify(dict(resp, **STATE_CODE['200']))
            else:
                return STATE_CODE['204']
        else:
            ## query all task list
            # task_list = []
            # rsl_q_struct = QuestionnaireStruct.query.filter(QuestionnaireStruct.respondent == 1,
            #                                        QuestionnaireStruct.process_type == 1).all()
            # if rsl_q_struct:
            #     for s in rsl_q_struct:
            #         dt_built_start = (datetime.datetime.now() - datetime.timedelta(days=s.day_end - 1)).date()
            #         dt_built_end = (datetime.datetime.now() - datetime.timedelta(days=s.day_start - 2)).date()
            #         print(s.questionnaire_id, dt_built_start, dt_built_end)
            #         rsl = MapPatientQuestionnaire.query.filter(MapPatientQuestionnaire.questionnaire_id == s.questionnaire_id,
            #                                                    MapPatientQuestionnaire.need_send_task_module.isnot(None),
            #                                                    MapPatientQuestionnaire.doctor_id == did if did != 16 else text(''),
            #                                                    MapPatientQuestionnaire.dt_built.between(dt_built_start, dt_built_end)).all()
            #         if rsl:
            #             p_qn_list = [{'id': i.id, 'sid': s.id, 'name': i.patient.name, 'modelName': s.title,
            #                           'time': i.dt_built.strftime('%Y-%m-%d %H:%M:%S'), 'sex': i.patient.sex,
            #                           'url': i.patient.url_portrait, 'treatment': i.questionnaire.medicine.name} for i in rsl]
            #             task_list += p_qn_list
            #     resp = {'list': task_list}
            #     print(resp)
            #     return jsonify(dict(resp, **STATE_CODE['200']))
            # else:
            #     return STATE_CODE['204']
            task_list = []
            rsl = MapPatientQuestionnaire.query.filter(MapPatientQuestionnaire.need_send_task_module.isnot(None),
                                                       MapPatientQuestionnaire.doctor_id == did if did != 16 else text('')).all()
            if rsl:
                for r in rsl:
                    modules_str = re.split(',', r.need_send_task_module)
                    module_id_list = list(map(int, modules_str))
                    for mid in module_id_list:
                        rsl_s = QuestionnaireStruct.query.filter_by(id=mid).one_or_none()
                        if rsl_s:
                            p_qn_dict = {'id': r.id, 'sid': rsl_s.id, 'name': r.patient.name, 'modelName': rsl_s.title,
                                          'time': r.dt_built.strftime('%Y-%m-%d %H:%M:%S'), 'sex': r.patient.sex,
                                          'url': r.patient.url_portrait, 'treatment': r.questionnaire.medicine.name}
                            task_list.append(p_qn_dict)
                        else:
                            continue
                resp = {'list': task_list}
                print(resp)
                return jsonify(dict(resp, **STATE_CODE['200']))
            else:
                return STATE_CODE['204']

    def post(self):
        args = request.get_json()
        print(args)
        mpqn_id = args['id']
        questions = args['questions']
        if mpqn_id and questions:
            ## both args are not None
            rsl = MapPatientQuestionnaire.query.filter_by(id=mpqn_id).one()
            if rsl:
                patient_id = rsl.patient_id
                rsl_table = rsl.questionnaire.result_table_name
                dt_answer = datetime.datetime.now()
                for q in questions:
                    q_id = q['questionID']
                    opt_list = q['optionsID']
                    text = q['text']
                    if opt_list:
                        ## it is a choice question
                        for oid in opt_list:
                            # is_existed = ResultShudaifu.query
                            rsl_r = ResultShudaifu(patient_id=patient_id, answer=oid, dt_answer=dt_answer, is_doctor=1,
                                                 question_id=q_id, type=1)
                            db.session.add(rsl_r)
                            # if rsl_r.save():
                            #     continue
                            # else:
                            #     return STATE_CODE['203']
                    else:
                        ## it is a filtering quetion
                        if text:
                            opt = Option(question_id=q_id, content=text)
                            rsl_id = opt.save()
                            if rsl_id:
                                rsl_oid = Option.query.filter_by(question_id=q_id, content=text).order_by(Option.id.desc()).first()
                                if rsl_oid:
                                    rsl_sdf = ResultShudaifu(patient_id=patient_id, answer=rsl_oid.id, dt_answer=dt_answer, is_doctor=1,
                                                         question_id=q_id, type=3)
                                    db.session.add(rsl_sdf)
                                    # if rsl_sdf.save():
                                    #     continue
                                    # else:
                                    #     return STATE_CODE['203']
                                else:
                                    return STATE_CODE['203']
                            else:
                                return STATE_CODE['203']
                        else:
                            return STATE_CODE['400']
                rsl.need_send_task_module = None
                try:
                    db.session.commit()
                    return STATE_CODE['200']
                except Exception as e:
                    db.session.rollback()
                    return STATE_CODE['409']
            else:
                return STATE_CODE['204']
        else:
            return STATE_CODE['400']
