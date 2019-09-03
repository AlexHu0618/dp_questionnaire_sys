# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql.types import BIT
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class InfoDoctor(Base):
    __tablename__ = 'info_doctor'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), server_default=FetchedValue())
    department = Column(String(50), server_default=FetchedValue())
    hospital = Column(String(50), server_default=FetchedValue())
    medicine = Column(String(50), server_default=FetchedValue())
    role_id = Column(ForeignKey('info_role.id'), index=True)
    nickname = Column(String(20))
    password = Column(String(128))

    role = relationship('InfoRole', primaryjoin='InfoDoctor.role_id == InfoRole.id', backref='info_doctors')


class InfoOption(Base):
    __tablename__ = 'info_option'

    id = Column(Integer, primary_key=True)
    question_id = Column(ForeignKey('info_question.id'), nullable=False, index=True)
    content = Column(String(50), nullable=False, server_default=FetchedValue())
    score = Column(Float, nullable=False, server_default=FetchedValue())
    total_votes = Column(Integer, server_default=FetchedValue())

    question = relationship('InfoQuestion', primaryjoin='InfoOption.question_id == InfoQuestion.id', backref='info_options')


class InfoOptionRecord(Base):
    __tablename__ = 'info_option_record'

    pq_id = Column(Integer, primary_key=True)
    option_id = Column(ForeignKey('info_option.id'), nullable=False, index=True)

    option = relationship('InfoOption', primaryjoin='InfoOptionRecord.option_id == InfoOption.id', backref='info_option_records')


class InfoPatient(Base):
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


class InfoResult1(InfoPatient):
    __tablename__ = 'info_result1'

    patient_id = Column(ForeignKey('info_patient.id'), primary_key=True)
    period = Column(Integer)
    filtration_number = Column(String(50))
    estimate_6w = Column(Integer)
    is_drug_combination = Column(Integer)
    drug_combination = Column(String(80))
    is_adverse_event = Column(Integer)
    adverse_event = Column(String(150))


class InfoQtype(Base):
    __tablename__ = 'info_qtype'

    id = Column(Integer, primary_key=True)
    topic_name = Column(String(50))


class InfoQuestion(Base):
    __tablename__ = 'info_question'

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    need_answer = Column(BIT(1))
    questionnaire_id = Column(ForeignKey('info_questionnaire.id'), nullable=False, index=True)
    qtype_id = Column(ForeignKey('info_qtype.id'), index=True)

    qtype = relationship('InfoQtype', primaryjoin='InfoQuestion.qtype_id == InfoQtype.id', backref='info_questions')
    questionnaire = relationship('InfoQuestionnaire', primaryjoin='InfoQuestion.questionnaire_id == InfoQuestionnaire.id', backref='info_questions')


class InfoQuestionnaire(Base):
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


class InfoRole(Base):
    __tablename__ = 'info_role'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), server_default=FetchedValue())


class MapDoctorPatient(Base):
    __tablename__ = 'map_doctor_patient'

    id = Column(Integer, primary_key=True)
    doctor_id = Column(ForeignKey('info_doctor.id'), nullable=False, index=True)
    patient_id = Column(ForeignKey('info_patient.id'), nullable=False, index=True)

    doctor = relationship('InfoDoctor', primaryjoin='MapDoctorPatient.doctor_id == InfoDoctor.id', backref='map_doctor_patients')
    patient = relationship('InfoPatient', primaryjoin='MapDoctorPatient.patient_id == InfoPatient.id', backref='map_doctor_patients')


class MapDoctorQuestionnaire(Base):
    __tablename__ = 'map_doctor_questionnaire'

    id = Column(Integer, primary_key=True)
    doctor_id = Column(ForeignKey('info_doctor.id'), nullable=False, index=True)
    questionnaire_id = Column(ForeignKey('info_questionnaire.id'), nullable=False, index=True)

    doctor = relationship('InfoDoctor', primaryjoin='MapDoctorQuestionnaire.doctor_id == InfoDoctor.id', backref='map_doctor_questionnaires')
    questionnaire = relationship('InfoQuestionnaire', primaryjoin='MapDoctorQuestionnaire.questionnaire_id == InfoQuestionnaire.id', backref='map_doctor_questionnaires')


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

    doctor = relationship('InfoDoctor', primaryjoin='MapPatientQuestionnaire.doctor_id == InfoDoctor.id', backref='map_patient_questionnaires')
    patient = relationship('InfoPatient', primaryjoin='MapPatientQuestionnaire.patient_id == InfoPatient.id', backref='map_patient_questionnaires')
    questionnaire = relationship('InfoQuestionnaire', primaryjoin='MapPatientQuestionnaire.questionnaire_id == InfoQuestionnaire.id', backref='map_patient_questionnaires')
