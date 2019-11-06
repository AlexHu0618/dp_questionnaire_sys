# -*- coding: utf-8 -*-
# @Time    : 9/4/19 3:55 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: __init__.py.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.2.0

from flask import Blueprint

api_bp = Blueprint('api01', __name__, url_prefix='/api')  # the 2 arg is Blueprint name and which package the Blueprint belong to


from flask_restful import Api
from . import login
from .patient_manage import Patients
from .questionnaire_manage import Questionnaires, QuestionTemps
from .util import Util
from .message_manage import Message, Task
from .download import Download


api = Api(api_bp)

api.add_resource(Questionnaires, '/questionnaire')
api.add_resource(QuestionTemps, '/question')
api.add_resource(Patients, '/patient')
api.add_resource(Util, '/util')
api.add_resource(Message, '/msg')
api.add_resource(Task, '/task')
api.add_resource(Download, '/download/excel')
