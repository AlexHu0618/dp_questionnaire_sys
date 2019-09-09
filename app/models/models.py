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


t_map_option_record = db.Table(
    'map_option_record', db.metadata,
    db.Column('pq_id', db.ForeignKey('map_patient_questionnaire.id'), nullable=False, index=True),
    db.Column('option_id', db.ForeignKey('info_option.id'), nullable=False, index=True)
)


class Doctor(db.Model, UserMixin):
    __tablename__ = 'info_doctor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), server_default=db.FetchedValue())
    department = db.Column(db.String(50), server_default=db.FetchedValue())
    hospital = db.Column(db.String(50), server_default=db.FetchedValue())
    medicine = db.Column(db.String(50), server_default=db.FetchedValue())
    role_id = db.Column(db.ForeignKey('info_role.id'), index=True)
    nickname = db.Column(db.String(20))
    password = db.Column(db.String(128))

    role = db.relationship('Role', primaryjoin='Doctor.role_id == Role.id', backref=db.backref('info_doctors'))
    patients = db.relationship('Patient', secondary=t_map_doctor_patient, backref=db.backref('info_doctors'))
    questionnaires = db.relationship('Questionnaire', secondary=t_map_doctor_questionnaire, backref=db.backref('info_doctors'))

    def get(self, id):
        doctor = Doctor.query.filter_by(id=id).first()
        return doctor

    def set(self, doctor):
        db.session.add(doctor)
        db.session.commit()


class Option(db.Model):
    __tablename__ = 'info_option'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.ForeignKey('info_question.id'), nullable=False, index=True)
    content = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Float(8, 2), nullable=False)
    total_votes = db.Column(db.Integer, server_default=db.FetchedValue())

    question = db.relationship('Question', primaryjoin='Option.question_id == Question.id', backref=db.backref('info_options'))
    pqs = db.relationship('MapPatientQuestionnaire', secondary=t_map_option_record, backref=db.backref('info_options'))


class Patient(db.Model):
    __tablename__ = 'info_patient'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), server_default=db.FetchedValue())
    sex = db.Column(db.Integer)
    age = db.Column(db.Integer)
    nation = db.Column(db.String(5), server_default=db.FetchedValue())
    weight = db.Column(db.Float(8, 2))
    height = db.Column(db.Integer)
    year_smoking = db.Column(db.Integer)
    year_drink = db.Column(db.Integer)
    tel = db.Column(db.String(20), server_default=db.FetchedValue())
    dt_register = db.Column(db.DateTime)
    dt_login = db.Column(db.DateTime)
    wechat_openid = db.Column(db.String(30))


class Result1(Patient):
    __tablename__ = 'info_result1'

    patient_id = db.Column(db.ForeignKey('info_patient.id'), primary_key=True)
    period = db.Column(db.Integer)
    filtration_number = db.Column(db.String(50))
    estimate_6w = db.Column(db.Integer)
    is_drug_combination = db.Column(db.Integer)
    drug_combination = db.Column(db.String(80))
    is_adverse_event = db.Column(db.Integer)
    adverse_event = db.Column(db.String(150))


class Qtype(db.Model):
    __tablename__ = 'info_qtype'

    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(50))


class Question(db.Model):
    __tablename__ = 'info_question'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    need_answer = db.Column(db.SmallInteger)
    questionnaire_id = db.Column(db.ForeignKey('info_questionnaire.id'), nullable=False, index=True)
    qtype_id = db.Column(db.ForeignKey('info_qtype.id'), index=True)

    qtype = db.relationship('Qtype', primaryjoin='Question.qtype_id == Qtype.id', backref=db.backref('info_questions'))
    questionnaire = db.relationship('Questionnaire', primaryjoin='Question.questionnaire_id == Questionnaire.id', backref=db.backref('info_questions'))


class Questionnaire(db.Model):
    __tablename__ = 'info_questionnaire'

    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    sub_title = db.Column(db.String(50))
    direction = db.Column(db.String(50))
    dt_created = db.Column(db.DateTime)
    dt_modified = db.Column(db.DateTime)
    thanks_msg = db.Column(db.String(50))
    medicine = db.Column(db.String(50))
    result_table_name = db.Column(db.String(50))


class Role(db.Model):
    __tablename__ = 'info_role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), server_default=db.FetchedValue())


class MapPatientQuestionnaire(db.Model):
    __tablename__ = 'map_patient_questionnaire'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.ForeignKey('info_patient.id'), nullable=False, index=True)
    questionnaire_id = db.Column(db.ForeignKey('info_questionnaire.id'), nullable=False, index=True)
    total_days = db.Column(db.Integer, server_default=db.FetchedValue())
    score = db.Column(db.Float(8, 2), server_default=db.FetchedValue())
    doctor_id = db.Column(db.ForeignKey('info_doctor.id'), nullable=False, index=True)
    register_state = db.Column(db.Integer, nullable=False)
    dt_built = db.Column(db.DateTime)
    dt_lasttime = db.Column(db.DateTime)

    doctor = db.relationship('Doctor', primaryjoin='MapPatientQuestionnaire.doctor_id == Doctor.id', backref=db.backref('map_patient_questionnaires'))
    patient = db.relationship('Patient', primaryjoin='MapPatientQuestionnaire.patient_id == Patient.id', backref=db.backref('map_patient_questionnaires'))
    questionnaire = db.relationship('Questionnaire', primaryjoin='MapPatientQuestionnaire.questionnaire_id == Questionnaire.id', backref=db.backref('map_patient_questionnaires'))
