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
from .. import db
from ..models.models import Questionnaire, Question, Option
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
parser.add_argument("Name", type=str, location=["json", "args"])
parser.add_argument("title", type=str, location=["json", "args", "form"])
parser.add_argument("type", type=int, location=["json", "args", "form"])
parser.add_argument("options", type=list, location=["args", "form", "json"])
parser.add_argument("remark", type=str, location=["args", "form", "json"])
parser.add_argument("id", type=int, location=["args", "json", "form"])


class Questionnaires(Resource):
    def get(self):
        rsl = Questionnaire.query.filter_by(name="Name").first()
        print(rsl)
        if rsl:
            return jsonify({'name': rsl.name})


class Questions(Resource):
    def get(self):
        id_get = parser.parse_args().get('id')
        ## query single question
        if id_get is not None:
            q = Question.query.filter_by(id=id_get).first()
            if q:
                options = [i.content for i in q.options]
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
        title = parser.parse_args().get('title')
        type = parser.parse_args().get('type')
        options = ast.literal_eval(parser.parse_args().get('options'))
        remark = parser.parse_args().get('remark')
        # args = request.get_json()
        # title = args['title']
        # type = args['type']
        # options = args['options']
        # remark = args['remark']
        q = Question(title=title, qtype=type, remark=remark)
        if options is not None:
            q.options = [Option(content=i) for i in options]
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
        print(options_put)
        print(type(options_put))
        if options_put is not None and not isinstance(options_put, list):
            options_put = ast.literal_eval(options_put)
        q = Question.query.filter_by(id=id_put).first()
        q.title = title_put
        q.qtype = type_put
        q.remark = remark_put
        rsl = db.session.commit()
        if not rsl:
            os = Option.query.filter_by(question_id=id_put).all()
            if os is not None:
                [db.session.delete(o) for o in os]
                rsl = db.session.commit()
                if not rsl:
                    if type_put != 3 and options_put is not None:
                        o = [Option(question_id=id_put, content=i) for i in options_put]
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
        id_del = parser.parse_args().get('id')
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
