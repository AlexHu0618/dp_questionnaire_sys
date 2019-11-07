# -*- coding: utf-8 -*-
# @Time    : 9/10/19 10:54 AM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: questionnaire_manage.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.4.0


from flask_restful import Resource, reqparse, request
from flask import jsonify
import re
import uuid
import datetime
import time
from .. import db
from ..models import Questionnaire, QuestionTemp, Question, Option, QuestionnaireStruct
import ast
from app import STATE_CODE
from sqlalchemy import and_


class Argument(reqparse.Argument):
    """
    继承自 reqparse.Argument, 增加 nullable 关键字参数，
    对于值为 None 并且 nullable=False 的字段 raise TypeError
    """
    def __init__(self, name, default=None, dest=None, required=False,
                 ignore=False, type=reqparse.text_type,
                 location=('json', 'values',), choices=(),
                 action='store', help=None, operators=('=',),
                 case_sensitive=True, nullable=False):
        self.nullable = nullable
        super(Argument, self).__init__(name, default=default, dest=dest,
                                       required=required, ignore=ignore,
                                       type=type, location=location,
                                       choices=choices, action=action,
                                       help=help, operators=operators,
                                       case_sensitive=case_sensitive)

    def convert(self, value, op):
        if value is None and not self.nullable:
            raise TypeError("%s can't be null" % self.name)
        return super(Argument, self).convert(value, op)


parser = reqparse.RequestParser(argument_class=Argument)
parser.add_argument("type", type=int, location=["json", "args", "form"])
parser.add_argument("options", type=str, location=["args", "json", "form"])
parser.add_argument("remark", type=str, location=["args", "form", "json"])
parser.add_argument("id", location=["args", "json", "form"])
parser.add_argument("info", type=str, location=["args", "json", "form"])
parser.add_argument("model", type=str, location=["args", "json", "form"])
parser.add_argument("model_line", type=str, location=["args", "json", "form"])
parser.add_argument("hospital", type=int, location=["args", "json", "form"])
parser.add_argument("department", type=int, location=["args", "json", "form"])
parser.add_argument("treatment", type=str, location=["args", "json", "form"])
parser.add_argument("page", type=int, location=["args", "json", "form"])
parser.add_argument("size", type=int, location=["args", "json", "form"])


def count_time(func):
    def wrapper(*args, **kwargs):
        start_time = datetime.datetime.now()  # 程序开始时间
        func(*args, **kwargs)
        over_time = datetime.datetime.now()   # 程序结束时间
        total_time = (over_time-start_time).total_seconds()
        print('程序共计%s秒' % total_time)
    return wrapper


class Questionnaires(Resource):
    """
    Restful API for Questionnaire
    """
    def get(self):
        # args = request.get_json()
        # id_get = args['id']
        id_get = parser.parse_args().get('id')
        ## query single questionnaire
        if id_get is not None:
            qn = Questionnaire.query.filter(and_(Questionnaire.id == id_get, Questionnaire.status < 2)).first()
            if qn:
                info = {'code': qn.code, 'cycle': qn.total_days, 'title': qn.title, 'mintitle': qn.sub_title,
                        'hospitalID': qn.hospital_id, 'hospital': qn.hospital.name, 'subjectID': qn.department_id,
                        'subject': qn.department.name, 'treatmentID': qn.medicine_id, 'treatment': qn.medicine.name, 'remark': qn.direction,
                        'createMan': qn.creator, 'createTime': qn.dt_created.strftime('%Y-%m-%d %H:%M:%S'),
                        'editMan': qn.modifier, 'editTime': qn.dt_modified.strftime('%Y-%m-%d %H:%M:%S')}
                model_line = []
                model = []
                temp = model_line
                process_type = 0
                respondent = 0
                for model_type in ['model_line', 'model']:
                    if model_type == 'model':
                        process_type = 1
                        temp = model
                    m_rsl = QuestionnaireStruct.query.filter_by(questionnaire_id=id_get, process_type=process_type).all()
                    if m_rsl:
                        for i in m_rsl:
                            questions = []
                            if i.question_id_list != '':
                                qs_str = re.split(',', i.question_id_list)
                                qs_id = list(map(int, qs_str))
                                if model_type == 'model':
                                    respondent = i.respondent
                                for j in qs_id:
                                    q = Question.query.filter_by(id=j).first()
                                    if q:
                                        ## 这里传前端的问题ID为模板ID，为了在修改时间用户创建问题
                                        q_dict = {'id': q.template_id, 'title': q.title, 'type': q.qtype,
                                                  'options': [{'id': o.id, 'option': o.content, 'score': str(round(o.score, 2) if o.score else 0),
                                                               'goto': o.goto} for o in q.options]}
                                        questions.append(q_dict)
                            ms = {'start': i.day_start, 'end': i.day_end, 'time': i.time.strftime('%H:%M:%S') if i.time else '', 'interval': i.interval,
                                  'title': i.title, 'questions': questions, 'active': False, 'scoreSwitch': False,
                                  'id': i.id, 'for': respondent}
                            temp.append(ms)
                resp = {'id': qn.id, 'info': info, 'model': model, 'model_line': model_line}
                return jsonify(dict(resp, **STATE_CODE['200']))
            else:
                return STATE_CODE['204']
        ## query all quetionnaire
        else:
            hospital_id = parser.parse_args().get('hospital')
            department_id = parser.parse_args().get('department')
            medicine = parser.parse_args().get('treatment')
            page = parser.parse_args().get('page')
            size = parser.parse_args().get('size')
            page_default = 1
            size_default = 10
            q_total = 0
            medicine_count = 0
            if page is None:
                page = page_default
            if size is None:
                size = size_default
            if hospital_id is None and department_id is None and medicine is None:
                q = Questionnaire.query.filter(Questionnaire.status < 2).paginate(page, size)
                q_total = Questionnaire.query.filter(Questionnaire.status < 2).count()
                medicine_count = Questionnaire.query.with_entities(Questionnaire.medicine_id).distinct().count()
            else:
                q = Questionnaire.query.filter(Questionnaire.hospital_id == hospital_id if hospital_id is not None else '',
                                               Questionnaire.department_id == department_id if department_id is not None else '',
                                               Questionnaire.medicine == medicine if medicine is not None else '',
                                               Questionnaire.status < 2).paginate(page, size)
            if q:
                print(q.items)
                print(q.page)
                print(q.pages)
                q_list = []
                for i in q.items:
                    q_s = {'id': i.id, 'title': i.title, 'mintitle': i.sub_title, 'code': i.code, 'treatmentID': i.medicine_id,
                           'treatment': i.medicine.name, 'hospitalID': i.hospital_id, 'hospital': i.hospital.name, 'subjectID': i.department_id,
                           'subject': i.department.name, 'creator': i.creator,
                           'time_creation': i.dt_created.strftime('%Y-%m-%d %H:%M:%S'), 'editor': i.modifier,
                           'time_edit': i.dt_modified.strftime('%Y-%m-%d %H:%M:%S')}
                    q_list.append(q_s)
                resp = {'list': q_list, 'page': q.page, 'total': q_total, 'kind': medicine_count}
                return jsonify(dict(resp, **STATE_CODE['200']))
            else:
                return STATE_CODE['204']

    def post(self):
        info = ast.literal_eval(parser.parse_args().get('info'))
        model_line = parser.parse_args().get('model_line')
        model = parser.parse_args().get('model')
        if info is not None:
            print(info)
            quuid = str(uuid.uuid1())
            dt_created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dt_modified = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            creator = 'test'
            modifier = 'test'
            table_result = 'subtab_result_shudaifu'
            q = Questionnaire(id=quuid, title=info['title'], sub_title=info['mintitle'], direction=info['remark'],
                              dt_created=dt_created, dt_modified=dt_modified, total_days=info['cycle'],
                              medicine_id=info['treatmentID'], code=info['code'], hospital_id=info['hospitalID'],
                              department_id=info['subjectID'], creator=creator, modifier=modifier,
                              result_table_name=table_result)
            rsl = q.save()
            ## save info successful
            if rsl:
                return STATE_CODE['200']
            else:
                return STATE_CODE['204']
        if model_line is not None:
            pass
        if model is not None:
            pass

    @count_time
    def put(self):
        args = request.get_json()
        id_put = args['id']
        info = args['info']
        model_line = args['model_line']
        model = args['model']
        print(info)
        print(model)
        if info is None:
            return STATE_CODE['400']
        ## update questionnaire
        qn = Questionnaire.query.filter(Questionnaire.id == id_put, Questionnaire.status == 0).one()
        if qn is None:
            return STATE_CODE['204']
        qn.title = info['title']
        qn.sub_title = info['mintitle']
        qn.direction = info['remark']
        qn.dt_modified = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        qn.total_days = info['cycle']
        qn.medicine_id = info['treatmentID']
        qn.hospital_id = info['hospitalID']
        qn.department_id = info['subjectID']
        qn.modifier = 'mod_tester'
        qn.code = info['code']
        rsl = db.session.commit()
        if not rsl:
            ## update all model
            if model_line or model:
                param = []
                if model_line:
                    param.append('model_line')
                if model:
                    param.append('model')
                ## delete all the struct about this questionnaire_id
                if qn.struct:
                    qid_list = []
                    for s in qn.struct:
                        qs_str = re.split(',', s.question_id_list)
                        qs_id = list(map(int, qs_str))
                        qid_list += qs_id
                    opts = Option.query.filter(Option.question_id.in_(qid_list)).all()
                    Option.delete_all(opts)
                    qs = Question.query.filter(Question.id.in_(qid_list)).all()
                    Question.delete_all(qs)
                    [db.session.delete(s) for s in qn.struct]
                    rsl = db.session.commit()
                    if rsl:
                        ## fail to delete all structs
                        db.session.rollback()
                        return STATE_CODE['203']
                ## update all models
                model_list = model_line
                respondent = 0
                process_type = 0
                for p in param:
                    if p == 'model':
                        model_list = model
                    ## sort the period
                    startdays_sorted = sorted([i['start'] for i in model_list])
                    print('period []', startdays_sorted)
                    m_list = []
                    for m in model_list:
                        qid_list = []
                        qs = m['questions']
                        print(qs)
                        day_start = m['start']
                        day_end = m['end']
                        interval = m['interval']
                        title = m['title']
                        period = startdays_sorted.index(day_start) + 1
                        time = m['time']
                        if p == 'model':
                            respondent = m['for']
                            process_type = 1
                            period = None
                            time = None
                        ## build question and option
                        # q_max_id = Question.query.order_by(Question.id.desc()).first()
                        # max_id = q_max_id.id
                        qid_list = []
                        for q in qs:
                            q_temp = QuestionTemp.query.filter_by(id=q['id']).one()
                            if q_temp:
                                q_new = Question(title=q_temp.title, need_answer=q_temp.need_answer,
                                                 questionnaire_id=qn.id, qtype=q_temp.qtype, remark=q_temp.remark,
                                                 template_id=q_temp.id)
                                q_rsl = Question.save(q_new)
                                if q_rsl is not None:
                                    rsl = Question.query.order_by(Question.id.desc()).first()
                                    if rsl:
                                        q_id = rsl.id
                                        ## save options for one question
                                        opt_list = []
                                        if q_temp.qtype!= 3:
                                            options_str = re.split(r'[**]', q_temp.options)
                                            options_list = list(options_str)
                                            for o in q['options']:
                                                score = float(o['score'] if o['score'] else 0)
                                                goto = o['goto'] if o['goto'] else 0
                                                opt = Option(question_id=q_id, content=o['option'], score=score, goto=goto)
                                                opt_list.append(opt)
                                        else:
                                            goto = 0
                                            opt = Option(question_id=q_id, content='', score=0, goto=goto)
                                            opt_list.append(opt)
                                        rsl = Option.save_all(opt_list)
                                        if rsl:
                                            qid_list.append(q_id)
                                            continue
                                        else:
                                            return STATE_CODE['203']
                                    else:
                                        return STATE_CODE['203']
                            else:
                                return STATE_CODE['203']
                        ## save module
                        qid_list_str = list(map(str, qid_list))
                        qids_list = ','.join(qid_list_str)
                        struct = QuestionnaireStruct(day_start=day_start, day_end=day_end, interval=interval,
                                                     title=title, time=time, questionnaire_id=id_put,
                                                     question_id_list=qids_list, process_type=process_type,
                                                     respondent=respondent, period=period)
                        rsl_s = QuestionnaireStruct.save(struct)
                        if rsl_s:
                            continue
                        else:
                            return STATE_CODE['203']
            return STATE_CODE['200']
        else:
            return STATE_CODE['203']


    def delete(self):
        id_del = parser.parse_args().get('id')
        #################################
        ## delete others
        ## MapPatientQuestionnaire, .....
        ## delete others
        #################################
        q = Questionnaire.query.filter_by(id=id_del).one()
        # delete it and other involved data if the status is unrelease--0, else just change the status to forbidden--2
        if q:
            if q.status == 0:
                qn_struct = QuestionnaireStruct.query.filter_by(questionnaire_id=id_del).all()
                rsl_struct = QuestionnaireStruct.delete_all(qn_struct)
                if rsl_struct:
                    rsl = q.delete()
                    if rsl:
                        return STATE_CODE['200']
                    else:
                        return STATE_CODE['204']
            elif q.status == 1:
                q.status = 2
                db.session.commit()
                return STATE_CODE['200']
            else:
                return STATE_CODE['200']
        else:
            return STATE_CODE['203']


class QuestionTemps(Resource):
    """
    Restful API for Question template
    """
    def get(self):
        id_get = parser.parse_args().get('id')
        ## query single question
        if id_get is not None:
            q = QuestionTemp.query.filter_by(id=id_get).one()
            if q:
                if q.options:
                    options_str = re.split('[?*]', q.options)
                    options_list = [x for x in options_str if x]
                else:
                    options_list = []
                options = [{'id': q.id, 'content': o} for o in options_list]
                resp = {'id': q.id, 'title': q.title, 'type': q.qtype, 'options': options, 'remark': q.remark}
                return jsonify(dict(resp, **STATE_CODE['200']))
            else:
                return STATE_CODE['204']
        ## query all questions
        else:
            qs = QuestionTemp.query.all()
            print(qs)
            if qs is not None:
                resp = {'item': [{'id': q.id, 'title': q.title, 'type': q.qtype} for q in qs]}
                return jsonify(dict(resp, **STATE_CODE['200']))
            else:
                return STATE_CODE['204']

    def post(self):
        print(request.form)
        print(request.args)
        print(request.get_json())
        args = request.get_json()
        title = args['title']
        type = args['type']
        options = args['options']
        remark = args['remark']
        q = QuestionTemp(title=title, qtype=type, remark=remark)
        if options is not None:
            options_list = [i['content'] for i in options]
            opts_list = list(map(str, options_list))
            opts_list_str = '**'.join(opts_list)
            q.options = opts_list_str
            # q.options = [Option(content=i['content']) for i in options]
        else:
            return STATE_CODE['400']
        rsl = q.save()
        if rsl:
            return STATE_CODE['200']
        else:
            return STATE_CODE['204']

    def put(self):
        args = request.get_json()
        print(args)
        id_put = args['id']
        title_put = args['title']
        type_put = args['type']
        options_put = args['options']
        remark_put = args['remark']
        q = QuestionTemp.query.filter_by(id=id_put).one()
        if q:
            q.title = title_put
            q.qtype = type_put
            q.remark = remark_put
            ## the current question is not a gap filling
            if type_put != 3 and options_put is not None:
                options_list = [i['content'] for i in options_put]
                opts_list = list(map(str, options_list))
                opts_list_str = '**'.join(opts_list)
                q.options = opts_list_str
            else:
                q.options = ''
            rsl = db.session.commit()
            if not rsl:
                return STATE_CODE['200']
            else:
                return STATE_CODE['204']
        else:
            return STATE_CODE['203']
        # if options_put is not None and not isinstance(options_put, list):
        #     options_put = ast.literal_eval(options_put)
        # q = QuestionTemp.query.filter_by(id=id_put).first()
        # q.title = title_put
        # q.qtype = type_put
        # q.remark = remark_put
        # rsl = db.session.commit()
        # if not rsl:
        #     ## delete all the options about question_id
        #     os = Option.query.filter_by(question_id=id_put).all()
        #     if os is not None:
        #         [db.session.delete(o) for o in os]
        #         rsl = db.session.commit()
        #         if rsl:
        #             ## fail to delete all options
        #             db.session.rollback()
        #             return STATE_CODE['203']
        #     ## the current question is not a gap filling
        #     if type_put != 3 and options_put is not None:
        #         o = [Option(question_id=id_put, content=i['content']) for i in options_put]
        #         rsl = Option.save_all(o)
        #         if rsl:
        #             return STATE_CODE['200']
        #         else:
        #             return STATE_CODE['204']
        #     elif type_put == 3:
        #         return STATE_CODE['200']
        #     else:
        #         return STATE_CODE['203']
        # else:
        #     return STATE_CODE['203']

    def delete(self):
        print(request.form)
        print(request.args)
        id_del = int(parser.parse_args().get('id'))
        q = QuestionTemp.query.filter_by(id=id_del).delete()
        if q:
            return STATE_CODE['200']
        else:
            return STATE_CODE['203']
