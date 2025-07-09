from flask_login import UserMixin
from sqlalchemy.sql import func
from website import db

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    data = db.Column(db.Text)
    date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_note_user_id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    user_type = db.Column(db.String(20), nullable=False, default='student')
    complaints = db.relationship('Complaint', backref='student', lazy=True)
    responses = db.relationship('Response', backref='admin', lazy=True)
    last_sent_date = db.Column(db.DateTime)  # Last comp
    messages_today = db.Column(db.Integer, default=0)  # number of massages for today


class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    responses = db.relationship('Response', backref='complaint', lazy=True)
    rating = db.Column(db.Integer, nullable=True)



class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    response_text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id', name='fk_response_complaint_id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_response_admin_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=True)