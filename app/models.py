# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql.types import BIT
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Doctor(Base):
    __tablename__ = 'info_doctor'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), server_default=FetchedValue())
    department = Column(String(50), server_default=FetchedValue())
    hospital = Column(String(50), server_default=FetchedValue())
    medicine = Column(String(50), server_default=FetchedValue())
    role_id = Column(ForeignKey('info_role.id'), index=True)
    nickname = Column(String(20))
    password = Column(String(128))

    role = relationship('Role', primaryjoin='Doctor.role_id == Role.id', backref='info_doctors')
    patients = relationship('Patient', secondary='t_map_doctor_patient', backref='info_doctors')
    questionnaires = relationship('Questionnaire', secondary='t_map_doctor_questionnaire', backref='info_doctors')


class Option(Base):
    __tablename__ = 'info_option'

    id = Column(Integer, primary_key=True)
    question_id = Column(ForeignKey('info_question.id'), nullable=False, index=True)
    content = Column(String(50), nullable=False, server_default=FetchedValue())
    score = Column(Float, nullable=False, server_default=FetchedValue())
    total_votes = Column(Integer, server_default=FetchedValue())

    question = relationship('Question', primaryjoin='Option.question_id == Question.id', backref='info_options')
    pqs = relationship('MapPatientQuestionnaire', secondary='t_map_option_record', backref='info_options')


class Patient(Base):
    __tablename__ = 'info_patient'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), server_default=FetchedValue())
    sex = Column(Integer)
    age = Column(Integer)
    nation = Column(String(5), server_default=FetchedValue())
    weight = Column(Float)
    height = Column(Integer)
    year_smoking = Column(Integer)
    year_drink = Column(Integer)
    tel = Column(String(20), server_default=FetchedValue())
    dt_register = Column(DateTime)
    dt_login = Column(DateTime)
    wechat_openid = Column(String(30))


class Result1(Patient):
    __tablename__ = 'info_result1'

    patient_id = Column(ForeignKey('info_patient.id'), primary_key=True)
    period = Column(Integer)
    filtration_number = Column(String(50))
    estimate_6w = Column(Integer)
    is_drug_combination = Column(Integer)
    drug_combination = Column(String(80))
    is_adverse_event = Column(Integer)
    adverse_event = Column(String(150))


class Qtype(Base):
    __tablename__ = 'info_qtype'

    id = Column(Integer, primary_key=True)
    topic_name = Column(String(50))


class Question(Base):
    __tablename__ = 'info_question'

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    need_answer = Column(BIT(1))
    questionnaire_id = Column(ForeignKey('info_questionnaire.id'), nullable=False, index=True)
    qtype_id = Column(ForeignKey('info_qtype.id'), index=True)

    qtype = relationship('Qtype', primaryjoin='Question.qtype_id == Qtype.id', backref='info_questions')
    questionnaire = relationship('Questionnaire', primaryjoin='Question.questionnaire_id == Questionnaire.id', backref='info_questions')


class Questionnaire(Base):
    __tablename__ = 'info_questionnaire'

    id = Column(String(50), primary_key=True)
    title = Column(String(50), nullable=False)
    sub_title = Column(String(50))
    direction = Column(String(50))
    dt_created = Column(DateTime)
    dt_modified = Column(DateTime)
    thanks_msg = Column(String(50))
    medicine = Column(String(50))
    result_table_name = Column(String(50))


class Role(Base):
    __tablename__ = 'info_role'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), server_default=FetchedValue())


t_map_doctor_patient = Table(
    'map_doctor_patient', metadata,
    Column('doctor_id', ForeignKey('info_doctor.id'), nullable=False, index=True),
    Column('patient_id', ForeignKey('info_patient.id'), nullable=False, index=True)
)


t_map_doctor_questionnaire = Table(
    'map_doctor_questionnaire', metadata,
    Column('doctor_id', ForeignKey('info_doctor.id'), nullable=False, index=True),
    Column('questionnaire_id', ForeignKey('info_questionnaire.id'), nullable=False, index=True)
)


t_map_option_record = Table(
    'map_option_record', metadata,
    Column('pq_id', ForeignKey('map_patient_questionnaire.id'), nullable=False, index=True),
    Column('option_id', ForeignKey('info_option.id'), nullable=False, index=True)
)


class MapPatientQuestionnaire(Base):
    __tablename__ = 'map_patient_questionnaire'

    id = Column(Integer, primary_key=True)
    patient_id = Column(ForeignKey('info_patient.id'), nullable=False, index=True)
    questionnaire_id = Column(ForeignKey('info_questionnaire.id'), nullable=False, index=True)
    total_days = Column(Integer, server_default=FetchedValue())
    score = Column(Float, server_default=FetchedValue())
    doctor_id = Column(ForeignKey('info_doctor.id'), nullable=False, index=True)
    register_state = Column(Integer, nullable=False)
    dt_built = Column(DateTime)
    dt_lasttime = Column(DateTime)

    doctor = relationship('Doctor', primaryjoin='MapPatientQuestionnaire.doctor_id == Doctor.id', backref='map_patient_questionnaires')
    patient = relationship('Patient', primaryjoin='MapPatientQuestionnaire.patient_id == Patient.id', backref='map_patient_questionnaires')
    questionnaire = relationship('Questionnaire', primaryjoin='MapPatientQuestionnaire.questionnaire_id == Questionnaire.id', backref='map_patient_questionnaires')
