# coding: utf-8
from .. import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def get_user(ident):
    return Doctor.query.get(int(ident))


t_map_doctor_patient = db.Table(
    'map_doctor_patient', db.metadata,
    db.Column('doctor_id', db.ForeignKey('info_doctor.id'), nullable=False, index=True),
    db.Column('patient_id', db.ForeignKey('info_patient.id'), nullable=False, index=True)
)


t_map_doctor_questionnaire = db.Table(
    'map_doctor_questionnaire', db.metadata,
    db.Column('doctor_id', db.ForeignKey('info_doctor.id'), nullable=False, index=True),
    db.Column('questionnaire_id', db.ForeignKey('info_questionnaire.id'), nullable=False, index=True)
)


# t_map_option_record = db.Table(
#     'map_option_record', db.metadata,
#     db.Column('pq_id', db.ForeignKey('map_patient_questionnaire.id'), nullable=False, index=True),
#     db.Column('option_id', db.ForeignKey('info_option.id'), nullable=False, index=True)
# )


class Base:
    def save(self):
        try:
            db.session.add(self)  # self实例化对象代表就是u对象
            db.session.commit()
            return 1
        except Exception as e:
            db.session.rollback()
            print(e)
            return None

    # 定义静态类方法接收List参数
    @staticmethod
    def save_all(obj_list):
        try:
            db.session.add_all(obj_list)
            db.session.commit()
            return len(obj_list)
        except Exception as e:
            db.session.rollback()
            print(e)
            return None

    # 定义删除方法
    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return 1
        except Exception as e:
            db.session.rollback()
            print(e)
            return None

    @staticmethod
    def delete_all(obj_list):
        try:
            [db.session.delete(i) for i in obj_list]
            db.session.commit()
            return 1
        except Exception as e:
            db.session.rollback()
            print(e)
            return None


class Hospital(db.Model, Base):
    __tablename__ = 'info_hospital'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    departments = db.relationship('Department', backref='hospital')
    questionnaires = db.relationship('Questionnaire', backref=db.backref('hospital'))


class Department(db.Model, Base):
    __tablename__ = 'info_department'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    hospital_id = db.Column(db.ForeignKey('info_hospital.id'))

    questionnaires = db.relationship('Questionnaire', backref=db.backref('department'))


class Doctor(db.Model, UserMixin, Base):
    __tablename__ = 'info_doctor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), server_default=db.FetchedValue())
    department_id = db.Column(db.Integer, db.ForeignKey('info_department.id'))
    hospital_id = db.Column(db.Integer)
    medicine_id = db.Column(db.Integer)
    role_id = db.Column(db.ForeignKey('info_role.id'), index=True)
    nickname = db.Column(db.String(20))
    password = db.Column(db.String(128))

    department = db.relationship('Department', backref=db.backref('doctors'))
    role = db.relationship('Role', primaryjoin='Doctor.role_id == Role.id', backref=db.backref('info_doctors'))
    # patients = db.relationship('Patient', secondary=t_map_doctor_patient, backref=db.backref('doctors'))
    # questionnaires = db.relationship('Questionnaire', secondary=t_map_doctor_questionnaire, backref=db.backref('doctors'))


class Option(db.Model, Base):
    __tablename__ = 'info_option'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.ForeignKey('info_question.id'))
    content = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Float(8, 3))
    total_votes = db.Column(db.Integer, server_default=db.FetchedValue())
    goto = db.Column(db.Integer)

    # question = db.relationship('Question', back_populates='options')
    # question = db.relationship('Question', primaryjoin='Option.question_id == Question.id', backref=db.backref('options'))
    # pqs = db.relationship('MapPatientQuestionnaire', secondary=t_map_option_record, backref=db.backref('info_options'))


class Patient(db.Model, Base):
    __tablename__ = 'info_patient'

    id = db.Column(db.Integer, primary_key=True)
    gzh_openid = db.Column(db.String(50))
    minip_openid = db.Column(db.String(50))
    unionid = db.Column(db.String(50), nullable=False, unique=True)
    url_portrait = db.Column(db.String(255))
    name = db.Column(db.String(20), server_default=db.FetchedValue())
    sex = db.Column(db.Integer)
    birthday = db.Column(db.Date)
    weight = db.Column(db.Integer)
    height = db.Column(db.Integer)
    nation = db.Column(db.String(5), server_default=db.FetchedValue())
    email = db.Column(db.String(100))
    dt_subscribe = db.Column(db.DateTime)
    dt_unsubscribe = db.Column(db.DateTime)
    dt_register = db.Column(db.DateTime)
    dt_login = db.Column(db.DateTime)
    tel = db.Column(db.String(20), server_default=db.FetchedValue())

    doctors = db.relationship('Doctor', secondary=t_map_doctor_patient, backref='patients')


# class ResultShudaifu(db.Model, Base):
#     __tablename__ = 'info_result_shudaifu'
#
#     patient_id = db.Column(db.ForeignKey('info_patient.id'), primary_key=True)
#     period = db.Column(db.Integer)
#     filtration_number = db.Column(db.String(50))
#     estimate_6w = db.Column(db.Integer)
#     is_drug_combination = db.Column(db.Integer)
#     drug_combination = db.Column(db.String(80))
#     is_adverse_event = db.Column(db.Integer)
#     adverse_event = db.Column(db.String(150))


class ResultShudaifu(db.Model, Base):
    __tablename__ = 'subtab_result_shudaifu'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.ForeignKey('info_patient.id'))
    question_id = db.Column(db.ForeignKey('info_question.id'))
    dt_answer = db.Column(db.DateTime)
    is_doctor = db.Column(db.Integer)
    answer = db.Column(db.String(255))
    type = db.Column(db.Integer)
    score = db.Column(db.Float(8, 3))


class QuestionnaireStruct(db.Model, Base):
    __tablename__ = 'info_questionnaire_struct'

    id = db.Column(db.Integer, primary_key=True)
    question_id_list = db.Column(db.String(255))
    period = db.Column(db.Integer)
    day_start = db.Column(db.Integer)
    day_end = db.Column(db.Integer)
    interval = db.Column(db.Integer)
    respondent = db.Column(db.Integer)
    questionnaire_id = db.Column(db.ForeignKey('info_questionnaire.id'))
    process_type = db.Column(db.Integer)
    title = db.Column(db.String(100))
    time = db.Column(db.Time)


class QuestionTemp(db.Model, Base):
    __tablename__ = 'info_question_template'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    need_answer = db.Column(db.SmallInteger)
    questionnaire_id = db.Column(db.ForeignKey('info_questionnaire.id'), nullable=False, index=True)
    qtype = db.Column(db.Integer)
    remark = db.Column(db.String(200))
    options = db.Column(db.String(255))

    questionnaires = db.relationship('Questionnaire', primaryjoin='QuestionTemp.questionnaire_id == Questionnaire.id', backref=db.backref('question_template'))


class Question(db.Model, Base):
    __tablename__ = 'info_question'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    need_answer = db.Column(db.SmallInteger)
    questionnaire_id = db.Column(db.ForeignKey('info_questionnaire.id'), nullable=False, index=True)
    qtype = db.Column(db.Integer)
    remark = db.Column(db.String(200))
    template_id = db.Column(db.Integer)

    # options = db.relationship('Option', back_populates='question')
    options = db.relationship('Option', backref=db.backref('question'))
    questionnaire = db.relationship('Questionnaire', backref=db.backref('questions'))


class Medicine(db.Model, Base):
    __tablename__ = 'info_medicine'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    questionnaires = db.relationship('Questionnaire', backref=db.backref('medicine'))


class Questionnaire(db.Model, Base):
    __tablename__ = 'info_questionnaire'

    id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    sub_title = db.Column(db.String(50))
    direction = db.Column(db.String(50))
    dt_created = db.Column(db.DateTime)
    dt_modified = db.Column(db.DateTime)
    total_days = db.Column(db.Integer)
    medicine_id = db.Column(db.ForeignKey('info_medicine.id'))
    result_table_name = db.Column(db.String(100))
    hospital_id = db.Column(db.ForeignKey('info_hospital.id'))
    department_id = db.Column(db.ForeignKey('info_department.id'))
    creator = db.Column(db.String(30))
    modifier = db.Column(db.String(30))
    code = db.Column(db.String(255))
    status = db.Column(db.Integer)

    struct = db.relationship('QuestionnaireStruct', backref=db.backref('questionnaires'))
    doctors = db.relationship('Doctor', secondary=t_map_doctor_questionnaire, backref='questionnaires')


class Role(db.Model, Base):
    __tablename__ = 'info_role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), server_default=db.FetchedValue())


class MapPatientQuestionnaire(db.Model, Base):
    __tablename__ = 'map_patient_questionnaire'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.ForeignKey('info_patient.id'), unique=True, nullable=False, index=True)
    questionnaire_id = db.Column(db.ForeignKey('info_questionnaire.id'), nullable=False, index=True)
    weight = db.Column(db.Integer)
    height = db.Column(db.Integer)
    is_smoking = db.Column(db.Integer)
    is_drink = db.Column(db.Integer)
    is_operated = db.Column(db.Integer)
    total_days = db.Column(db.Integer, server_default=db.FetchedValue())
    score = db.Column(db.Float(8, 3), server_default=db.FetchedValue())
    doctor_id = db.Column(db.ForeignKey('info_doctor.id'), nullable=False, index=True)
    status = db.Column(db.Integer, nullable=False)
    dt_built = db.Column(db.DateTime)
    dt_lasttime = db.Column(db.DateTime)
    current_period = db.Column(db.Integer)
    days_remained = db.Column(db.Integer)
    interval = db.Column(db.Integer)
    need_send_task_module = db.Column(db.String(100), server_default=db.FetchedValue())
    need_answer_module = db.Column(db.String(100), server_default=db.FetchedValue())

    doctor = db.relationship('Doctor', primaryjoin='MapPatientQuestionnaire.doctor_id == Doctor.id', backref=db.backref('map_patient_questionnaires'))
    patient = db.relationship('Patient', primaryjoin='MapPatientQuestionnaire.patient_id == Patient.id', backref=db.backref('map_patient_questionnaires'))
    questionnaire = db.relationship('Questionnaire', primaryjoin='MapPatientQuestionnaire.questionnaire_id == Questionnaire.id', backref=db.backref('map_patient_questionnaires'))
