from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    donations = db.relationship('Donation', backref='user', lazy=True)
    registrations = db.relationship('DonorRegistration', backref='user', lazy=True)

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    available_days = db.Column(db.String(50))
    location = db.Column(db.String(150))
    donors = db.Column(db.Integer)
    donation_date = db.Column(db.String(50))
    availability = db.Column(db.String(50))
    patient_name = db.Column(db.String(150))
    blood_type = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class DonorRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    dob = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=False)
    recent_donation = db.Column(db.String(10), nullable=False)
    medical_conditions = db.Column(db.Text)
    consent = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)