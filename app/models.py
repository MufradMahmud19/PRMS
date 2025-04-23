from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'doctor', 'nurse', 'admin'
    
    visits = db.relationship('Visit', backref='doctor', lazy=True)
    prescriptions = db.relationship('Prescription', backref='prescribing_doctor', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role
        }

class Patient(db.Model):
    __tablename__ = 'patient'
    patient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    contact_info = db.Column(db.String(100))
    
    visits = db.relationship('Visit', backref='patient', cascade="all, delete-orphan")
    prescriptions = db.relationship('Prescription', backref='patient', cascade="all, delete-orphan")
    reports = db.relationship('Report', backref='patient', cascade="all, delete-orphan")

class Visit(db.Model):
    __tablename__ = 'visit'
    visit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    visit_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    diagnosis = db.Column(db.Text)
    
    prescriptions = db.relationship('Prescription', backref='visit', lazy=True)

class Prescription(db.Model):
    __tablename__ = 'prescription'
    prescription_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visit.visit_id'))
    drug_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in days

class Report(db.Model):
    __tablename__ = 'report'
    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # 'lab', 'xray', etc.
    report_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
