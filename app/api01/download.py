# -*- coding: utf-8 -*-
# @Time    : 11/4/19 6:09 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: download.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.1.0

from flask_restful import Resource, reqparse, request
from app import STATE_CODE
from ..models import ResultShudaifu, MapPatientQuestionnaire, Patient
from .. import db
import xlsxwriter
import os
from flask import make_response, send_from_directory, jsonify
import datetime
import shutil


parser = reqparse.RequestParser()
parser.add_argument("qnid", type=str, location=["form", "json", "args"])
parser.add_argument("pid", type=int, location=["form", "json", "args"])


class Download(Resource):
    workbook = None
    worksheet = None
    filename = 'recordData.xlsx'   # the filename should not use symbol '_', or it will be wrong while downloading as the url,
                                   # and it must be different name for every file, because the broswer will cache the same file
    headings = ['姓名', '性别', '年龄', '民族', '体重', '身高', '吸烟史', '饮酒史', '就诊医院', '联系电话', 'Pre—便后出血',
                'Pre-肛门脱出', 'Pre-痔疮疼痛', 'Pre-肛门瘙痒或不适', 'Pre-肛门不洁污染内裤', 'Pre-痔疮总分', 'Pre-行动',
                'Pre-自己照顾自己', 'Pre-日常活动', 'Pre-疼痛/不舒服', 'Pre-焦虑', 'Pre-EQ总分', 'Pre-VAS', '首次使用器械日期',
                '器械使用总次数', '器械使用是否连续', '器械使用时间是否足够', '症状明显改善时间', '症状消失时间', '7d—便后出血',
                '7d-肛门脱出', '7d-痔疮疼痛', '7d-肛门瘙痒或不适', '7d-肛门不洁污染内裤', '7d-痔疮总分', '7d-行动',
                '7d-自己照顾自己', '7d-日常活动', '7d-疼痛/不舒服', '7d-焦虑', '7d-EQ总分', '7d-VAS', '14d—便后出血',
                '14d-肛门脱出', '14d-痔疮疼痛', '14d-肛门瘙痒或不适', '14d-肛门不洁污染内裤', '14d-痔疮总分', '14d-行动',
                '14d-自己照顾自己', '14d-日常活动', '14d-疼痛/不舒服', '14d-焦虑', '14d-EQ总分', '14d-VAS', '28d—便后出血',
                '28d-肛门脱出', '28d-痔疮疼痛', '28d-肛门瘙痒或不适', '28d-肛门不洁污染内裤', '28d-痔疮总分', '28d-行动',
                '28d-自己照顾自己', '28d-日常活动', '28d-疼痛/不舒服', '28d-焦虑', '28d-EQ总分', '28d-VAS', '6w—便后出血',
                '6w-肛门脱出', '6w-痔疮疼痛', '6w-肛门瘙痒或不适', '6w-肛门不洁污染内裤', '6w-痔疮总分', '6w-行动',
                '6w-自己照顾自己', '6w-日常活动', '6w-疼痛/不舒服', '6w-焦虑', '6w-EQ总分', '6w-VAS']

    def get(self):
        pid = parser.parse_args().get('pid')
        qnid = parser.parse_args().get('qnid')
        self.init_excel()
        self.fill_data(pid, qnid)
        self.workbook.close()
        resp = {'fname': self.filename}
        return jsonify(dict(resp, **STATE_CODE['200']))

    def init_excel(self):
        directory = os.path.abspath(os.path.dirname(__file__))  # 获取当前文件所在目录
        path = os.path.abspath(os.path.dirname('.')) + '/app/main/download/'
        dt_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.filename = 'RecordData_' + dt_str + '.xlsx'
        file_path = path + self.filename
        if os.path.exists(file_path):
            os.remove(file_path)
            print('remove old excel first')
        self.workbook = xlsxwriter.Workbook(file_path)  #可以生成.xls文件但是会报错
        self.worksheet = self.workbook.add_worksheet('Sheet1')  #工作页
        ## 准备测试数据
        bold = self.workbook.add_format({'bold': 1})
        ## border：边框，align:对齐方式，bg_color：背景颜色，font_size：字体大小，bold：字体加粗
        head_style = self.workbook.add_format({'border': 3, 'align': 'center', 'bg_color': 'cccccc', 'font_size': 8,
                                               'bold': True})  #设置单元格格式
        self.worksheet.set_column('A:CC', 15)
        self.worksheet.write_row('A1', self.headings, head_style)

    def fill_data(self, pid, qnid):
        if pid:
            rsl_mappqn = [MapPatientQuestionnaire.query.filter(MapPatientQuestionnaire.patient_id == pid).one()]
        else:
            rsl_mappqn = MapPatientQuestionnaire.query.all()
        if rsl_mappqn:
            print(rsl_mappqn)
            row_index = 2
            for mpqn in rsl_mappqn:
                name = mpqn.patient.name
                sex = 'M' if mpqn.patient.sex else 'F'
                age = str(mpqn.age)
                nation = mpqn.patient.nation
                weight = str(mpqn.weight)
                height = str(mpqn.height)
                is_smoking = '是' if mpqn.is_smoking else '否'
                is_drink = '是' if mpqn.is_drink else '否'
                # hospital = mpqn.doctor.department.hospital.name
                hospital_code = '00' + str(mpqn.doctor.department.hospital.id)
                tel = mpqn.patient.tel
                rsl_r = ResultShudaifu.query.filter(ResultShudaifu.patient_id == mpqn.patient_id).order_by(ResultShudaifu.dt_answer).all()
                if rsl_r:
                    col_a2j = [name, sex, age, nation, weight, height, is_smoking, is_drink, hospital_code, tel]
                    self.worksheet.write_row('A' + str(row_index), col_a2j)
                row_index = row_index + 1
        else:
            pass
