# -*- coding: utf-8 -*-
# @Time    : 9/4/19 3:55 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: __init__.py.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.2.0

from flask import Blueprint

api_bp = Blueprint('api01', __name__, url_prefix='/api01')  # the 2 arg is Blueprint name and which package the Blueprint belong to


from flask_restful import Api
from . import login
from .patient_manage import Patients
from .questionnaire_manage import Questionnaires, Questions


api = Api(api_bp)

api.add_resource(Questionnaires, '/questionnaire')
api.add_resource(Questions, '/question')
api.add_resource(Patients, '/patient')