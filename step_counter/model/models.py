from step_counter import db
from datetime import datetime
from marshmallow import Schema, fields
from sqlalchemy.exc import IntegrityError

from step_counter.exceptions.bad_request import BadRequestError


class StepCounter(db.Model):
    __tablename__ = 'step_counter'
    __table_args__ = (db.UniqueConstraint("name", "date"),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date = db.Column(db.String(255))
    steps = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.date = data.get('date')
        self.steps = data.get('steps')

    def save(self):
        assert self.id is None, 'Id must be None'

        db.session.add(self)

        try:
            db.session.commit()
        except IntegrityError as e:
            raise BadRequestError('Name and date combination already exists. Forbidden..') from e

    @classmethod
    def get_user_by_name(cls, name) -> list['StepCounter']:
        return cls.query.filter(cls.name == name)

    @classmethod    
    def get_all(cls) -> list:
        return cls.query.all()

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'


class StepCounterSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(dump_only=True)
    date = fields.String(dump_only=True)
    steps = fields.Int(dump_only=True)
