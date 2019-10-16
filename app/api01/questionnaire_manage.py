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
from .. import db
from ..models.models import Questionnaire, Question, Option, QuestionnaireStruct
import ast
from app import STATE_CODE


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
            q = Questionnaire.query.filter_by(id=id_get).first()
            if q:
                info = {'code': q.code, 'cycle': q.total_days, 'title': q.title, 'mintitle': q.sub_title,
                        'hospitalID': q.hospital_id, 'hospital': q.hospitals.name, 'subjectID': q.department_id,
                        'subject': q.departments.name, 'treatmentID': q.medicine_id, 'treatment': q.medicines.name, 'remark': q.direction,
                        'createMan': q.creator, 'createTime': q.dt_created.strftime('%Y-%m-%d %H:%M:%S'),
                        'editMan': q.modifier, 'editTime': q.dt_modified.strftime('%Y-%m-%d %H:%M:%S')}
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
                                        q_dict = {'id': j, 'title': q.title, 'type': q.qtype,
                                                  'options': [{'id': o.id, 'option': o.content, 'score': str(round(o.score, 2)),
                                                               'goto': o.goto} for o in q.options]}
                                        questions.append(q_dict)
                            ms = {'start': i.day_start, 'end': i.day_end, 'time': i.time.strftime('%H:%M:%S'), 'interval': i.interval,
                                  'title': i.title, 'questions': questions, 'active': False, 'scoreSwitch': False,
                                  'id': i.id, 'for': respondent}
                            temp.append(ms)
                resp = {'id': q.id, 'info': info, 'model': model, 'model_line': model_line}
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
                q = Questionnaire.query.paginate(page, size)
                q_total = Questionnaire.query.count()
                medicine_count = Questionnaire.query.with_entities(Questionnaire.medicine_id).distinct().count()
            else:
                q = Questionnaire.query.filter_by(hospital_id=hospital_id if hospital_id is not None else '',
                                                  department_id=department_id if department_id is not None else '',
                                                  medicine=medicine if medicine is not None else '').paginate(page, size)
            if q:
                print(q.items)
                print(q.page)
                print(q.pages)
                q_list = []
                for i in q.items:
                    q_s = {'id': i.id, 'title': i.title, 'mintitle': i.sub_title, 'code': i.code, 'treatmentID': i.medicine_id,
                           'treatment': i.medicines.name, 'hospitalID': i.hospital_id, 'hospital': i.hospitals.name, 'subjectID': i.department_id,
                           'subject': i.departments.name, 'creator': i.creator,
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
            q = Questionnaire(id=quuid, title=info['title'], sub_title=info['mintitle'], direction=info['remark'],
                              dt_created=dt_created, dt_modified=dt_modified, total_days=info['cycle'],
                              medicine_id=info['treatmentID'], code=info['code'], hospital_id=info['hospitalID'],
                              department_id=info['subjectID'], creator=creator, modifier=modifier)
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
        # id_put = parser.parse_args().get('id')
        # info = ast.literal_eval(parser.parse_args().get('info'))
        # model_line = parser.parse_args().get('model_line')
        # model = parser.parse_args().get('model')
        if info is None:
            return STATE_CODE['400']
        ## update questionnaire
        q = Questionnaire.query.filter_by(id=id_put).first()
        q.title = info['title']
        q.sub_title = info['mintitle']
        q.direction = info['remark']
        q.dt_modified = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        q.total_days = info['cycle']
        q.medicine_id = info['treatmentID']
        q.hospital_id = info['hospitalID']
        q.department_id = info['subjectID']
        q.modifier = 'mod_tester'
        q.code = info['code']
        t0 = datetime.datetime.now()
        rsl = db.session.commit()
        print("create ", datetime.datetime.now() - t0)
        if not rsl:
            ## update all model
            if model_line or model:
                param = []
                if model_line:
                    param.append('model_line')
                if model:
                    param.append('model')
                ## delete all the struct about this questionnaire_id
                if q.struct:
                    t1 = datetime.datetime.now()
                    [db.session.delete(s) for s in q.struct]
                    rsl = db.session.commit()
                    print("delete structs ", datetime.datetime.now() - t1)
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
                    for m in model_list:
                        if p == 'model':
                            respondent = m['for']
                            process_type = 1
                        qs = m['questions']
                        day_start = m['start']
                        day_end = m['end']
                        interval = m['interval']
                        title = m['title']
                        print('day_start', day_start)
                        print('index', startdays_sorted.index(day_start))
                        period = startdays_sorted.index(day_start) + 1
                        print('period', period)
                        time = m['time']
                        q_list = [i['id'] for i in qs]
                        q_list = list(map(str, q_list))
                        q_list_str = ','.join(q_list)
                        struct = QuestionnaireStruct(day_start=day_start, day_end=day_end, interval=interval, title=title,
                                                     time=time, questionnaire_id=id_put, question_id_list=q_list_str,
                                                     process_type=process_type, respondent=respondent, period=period)
                        t2 = datetime.datetime.now()
                        rsl = QuestionnaireStruct.save(struct)
                        print("build one struct ", datetime.datetime.now() - t2)
                        if not rsl:
                            return STATE_CODE['203']
                        else:
                            ## update process model
                            t3 = datetime.datetime.now()
                            for os_dict in qs:
                                os_list = os_dict['options']
                                if os_list is not None:
                                    ## it is not the gap filling
                                    for o in os_list:
                                        option = Option.query.filter_by(id=o['id']).first()
                                        option.score = o['score']
                                        if 'goto' in o.keys():
                                            if isinstance(o['goto'], int):
                                                option.goto = o['goto']
                                        rsl = db.session.commit()
                                        if rsl:
                                            ## fail to update data
                                            db.session.rollback()
                                            return STATE_CODE['203']
                                elif os_dict['type'] == 3:
                                    pass
                                else:
                                    db.session.rollback()
                                    return STATE_CODE['203']
                            print("build option ", datetime.datetime.now() - t3)
            return STATE_CODE['200']
        else:
            db.session.rollback()
            return STATE_CODE['203']

    def delete(self):
        id_del = parser.parse_args().get('id')
        ## delete others
        ## MapPatientQuestionnaire, .....
        ## delete others
        q = Questionnaire.query.filter_by(id=id_del).first()
        if q:
            rsl = q.delete()
            if rsl:
                return STATE_CODE['200']
            else:
                return STATE_CODE['204']
        else:
            return STATE_CODE['203']


class Questions(Resource):
    """
    Restful API for Question
    """
    def get(self):
        id_get = parser.parse_args().get('id')
        ## query single question
        if id_get is not None:
            q = Question.query.filter_by(id=id_get).first()
            if q:
                options = [{'id': i.id, 'content': i.content} for i in q.options]
                resp = {'id': q.id, 'title': q.title, 'type': q.qtype, 'options': options, 'remark': q.remark}
                return jsonify(dict(resp, **STATE_CODE['200']))
            else:
                return STATE_CODE['204']
        ## query all questions
        else:
            qs = Question.query.all()
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
        # title = parser.parse_args().get('title')
        # type = parser.parse_args().get('type')
        # options = ast.literal_eval(parser.parse_args().get('options'))
        # remark = parser.parse_args().get('remark')
        args = request.get_json()
        title = args['title']
        type = args['type']
        options = args['options']
        remark = args['remark']
        q = Question(title=title, qtype=type, remark=remark)
        if options is not None:
            q.options = [Option(content=i['content']) for i in options]
        else:
            return STATE_CODE['400']
        rsl = q.save()
        if rsl:
            return STATE_CODE['200']
        else:
            return STATE_CODE['204']

    def put(self):
        args = request.get_json()
        id_put = args['id']
        title_put = args['title']
        type_put = args['type']
        options_put = args['options']
        remark_put = args['remark']
        # id_put = parser.parse_args().get('id')
        # title_put = parser.parse_args().get('title')
        # type_put = parser.parse_args().get('type')
        # options_put = parser.parse_args().get('options')
        # remark_put = parser.parse_args().get('remark')
        if options_put is not None and not isinstance(options_put, list):
            options_put = ast.literal_eval(options_put)
        q = Question.query.filter_by(id=id_put).first()
        q.title = title_put
        q.qtype = type_put
        q.remark = remark_put
        rsl = db.session.commit()
        if not rsl:
            ## delete all the options about question_id
            os = Option.query.filter_by(question_id=id_put).all()
            if os is not None:
                [db.session.delete(o) for o in os]
                rsl = db.session.commit()
                if rsl:
                    ## fail to delete all options
                    db.session.rollback()
                    return STATE_CODE['203']
            ## the current question is not a gap filling
            if type_put != 3 and options_put is not None:
                o = [Option(question_id=id_put, content=i['content']) for i in options_put]
                rsl = Option.save_all(o)
                if rsl:
                    return STATE_CODE['200']
                else:
                    return STATE_CODE['204']
            elif type_put == 3:
                return STATE_CODE['200']
            else:
                return STATE_CODE['203']
        else:
            return STATE_CODE['203']

    def delete(self):
        print(request.form)
        print(request.args)
        id_del = int(parser.parse_args().get('id'))
        options = Option.query.filter_by(question_id=id_del).all()
        q = Question.query.filter_by(id=id_del).first()
        if q:
            [db.session.delete(o) for o in options]
            db.session.delete(q)
            rsl = db.session.commit()
            if not rsl:
                return STATE_CODE['200']
            else:
                return STATE_CODE['204']
        else:
            return STATE_CODE['203']
