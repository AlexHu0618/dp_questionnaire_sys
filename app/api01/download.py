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
from ..models import ResultShudaifu, MapPatientQuestionnaire, Patient, Option
from .. import db
import xlsxwriter
import os
from flask import make_response, send_from_directory, jsonify
import datetime
import shutil
from decimal import *


parser = reqparse.RequestParser()
parser.add_argument("qnid", type=str, location=["form", "json", "args"])
parser.add_argument("pid", type=str, location=["form", "json", "args"])


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
    content = {}

    def get(self):
        pid = parser.parse_args().get('pid')
        pid = int(pid) if pid else None
        # qnid = parser.parse_args().get('qnid')
        qnid = 'ec0569f4-eff7-11e9-9d9c-000c2918b20d'
        print(pid, qnid)
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
        self.get_basic_info(pid=pid, qnid=qnid)
        self.append_record_data(qnid=qnid)  # just for SDF
        print(self.content)
        row_index = 2
        for record in self.content.values():
            self.worksheet.write_row('A' + str(row_index), record)
            row_index = row_index + 1


    def get_basic_info(self, pid, qnid):
        print(pid, qnid)
        if pid:  # query single info
            rsl_mappqn = [MapPatientQuestionnaire.query.filter(MapPatientQuestionnaire.patient_id == pid,
                                                              MapPatientQuestionnaire.questionnaire_id == qnid).one_or_none()]
        else:  # query all info
            rsl_mappqn = MapPatientQuestionnaire.query.filter(MapPatientQuestionnaire.questionnaire_id == qnid,
                                                              MapPatientQuestionnaire.status != 0).all()
        if rsl_mappqn:
            print(rsl_mappqn)
            for mpqn in rsl_mappqn:
                name = mpqn.patient.name
                sex = 'M' if mpqn.patient.sex == 1 else 'F'
                age = mpqn.age
                nation = mpqn.patient.nation
                weight = mpqn.weight
                height = mpqn.height
                is_smoking = '是' if mpqn.is_smoking else '否'
                is_drink = '是' if mpqn.is_drink else '否'
                # hospital = mpqn.doctor.department.hospital.name
                hospital_code = '00' + str(mpqn.doctor.department.hospital.id)
                tel = mpqn.patient.tel
                col_a2j = [name, sex, age, nation, weight, height, is_smoking, is_drink, hospital_code, tel]
                self.content[mpqn.patient_id] = col_a2j
        else:
            print('rsl_mappqn is None', rsl_mappqn)
        
    def append_record_data(self, qnid):
        qid_rep = [422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432]
        qid_7d = [433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443]
        qid_14d = [444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454]
        qid_28d = [455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465]
        qid_6w = [466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476]
        qid_list_list = [qid_rep, qid_7d, qid_14d, qid_28d, qid_6w]
        if self.content:
            for pid in self.content.keys():
                rsl_r = ResultShudaifu.query.filter_by(patient_id=pid, is_doctor=0).order_by(ResultShudaifu.dt_answer).all()
                if rsl_r:
                    qid_in_record = [r.question_id for r in rsl_r]
                    for qid_list in qid_list_list:
                        scores = []
                        if set(qid_list) & set(qid_in_record):  # the records is existed
                            for qid in qid_list:
                                for r in rsl_r:
                                    if qid == r.question_id:
                                        if r.type == 1:
                                            scores.append(r.score)
                                        else:
                                            rsl_o = Option.query.filter_by(id=int(r.answer)).one_or_none()
                                            if rsl_o:
                                                scores.append(int(rsl_o.content))
                                            else:
                                                scores.append(None)
                                    else:
                                        continue
                            total_haemorrhoids = scores[0] + scores[1] + scores[2] + scores[3] + scores[4]
                            total_EQ = Decimal.from_float(0.978).quantize(Decimal('0.000')) - scores[5] - scores[6] - scores[7] - scores[8] - scores[9]
                            total_VAS = scores[10]
                            scores.insert(5, total_haemorrhoids)
                            scores.insert(11, total_EQ)
                        else:  # the recores is not existed
                            score = [None] * 13
                            scores += score
                        self.content[pid] += scores
                else:
                    print('no result for patient_id=', pid)
                    continue
                ## add datetime for curing first and others
                rsl_m = MapPatientQuestionnaire.query.filter_by(patient_id=pid, questionnaire_id=qnid).one_or_none()
                if rsl_m:
                    first_cure = datetime.datetime.strftime(rsl_m.dt_built, "%Y-%m-%d")
                else:
                    first_cure = None
                self.content[pid].insert(23, first_cure)
                total_usage = 0
                is_continuous = True
                is_time_enough = True
                dt_improvement = None
                dt_disappeared = None
                date_all = []
                is_40min_list = []
                for r in rsl_r:
                    if r.question_id == 419:
                        total_usage += 1
                        date_all.append(r.dt_answer.date())
                        if r.answer == 1391:
                            is_40min_list.append(True)
                        else:
                            is_40min_list.append(False)
                    elif r.question_id == 420:
                        dt_str = datetime.datetime.strftime(r.dt_answer, "%Y-%m-%d")
                        if r.answer == 1395:
                            dt_improvement = dt_str
                        elif r.answer == 1396:
                            dt_disappeared = dt_str
                        else:
                            pass
                    else:
                        continue
                print(rsl_r)
                date_list = self.dateRange(rsl_r[0].dt_answer, rsl_r[-1].dt_answer)
                if set(date_list[:10]) - set(date_all[:10]):  # not continuous just for 10 days
                    is_continuous = False
                self.content[pid].insert(24, total_usage)
                self.content[pid].insert(25, '是' if is_continuous else '否')
                if False in is_40min_list[:10] or not is_continuous:
                    is_time_enough = False
                self.content[pid].insert(26, '是' if is_time_enough else '否')
                self.content[pid].insert(27, dt_improvement)
                self.content[pid].insert(28, dt_disappeared)
        else:
            pass

    def dateRange(self, begindate, enddate):
        dates = []
        dt = begindate.date()
        date = begindate.date()
        while date <= enddate.date():
            dates.append(date)
            dt = dt + datetime.timedelta(1)
            date = dt
        return dates