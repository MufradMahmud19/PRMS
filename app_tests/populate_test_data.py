import sys
import os
from datetime import datetime

# Add the parent directory to sys.path so 'app' becomes importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import User, Patient, Visit, Prescription, Report
from app.app_extensions import db

# Create test database directory if it doesn't exist
TEST_DB_DIR = os.path.join(os.path.dirname(__file__), 'test_instance')
os.makedirs(TEST_DB_DIR, exist_ok=True)

def populate_test_data():
    print("Populating test database...")
    
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(TEST_DB_DIR, "test.db")}'
    
    with app.app_context():
        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating all tables...")
        db.create_all()
        
        # Create doctors
        print("Creating doctors...")
        doctors = [
            User(username='dr_smith', role='doctor'),
            User(username='dr_jones', role='doctor'),
            User(username='dr_wilson', role='doctor')
        ]
        
        for doctor in doctors:
            doctor.set_password('password123')
            db.session.add(doctor)
        
        db.session.flush()
        
        # Create patients
        print("Creating patients...")
        patients = [
            Patient(name='John Doe', age=35, contact_info='john@example.com'),
            Patient(name='Jane Smith', age=28, contact_info='jane@example.com'),
            Patient(name='Bob Wilson', age=45, contact_info='bob@example.com'),
            Patient(name='Alice Brown', age=52, contact_info='alice@example.com'),
            Patient(name='Charlie Davis', age=31, contact_info='charlie@example.com')
        ]
        
        for patient in patients:
            db.session.add(patient)
        
        db.session.flush()
        
        # Create visits
        print("Creating visits...")
        visits = [
            Visit(
                patient_id=patients[0].patient_id,
                doctor_id=doctors[0].user_id,
                visit_date=datetime(2023, 1, 1),
                diagnosis='Common cold'
            ),
            Visit(
                patient_id=patients[1].patient_id,
                doctor_id=doctors[1].user_id,
                visit_date=datetime(2023, 1, 2),
                diagnosis='Flu'
            ),
            Visit(
                patient_id=patients[2].patient_id,
                doctor_id=doctors[2].user_id,
                visit_date=datetime(2023, 1, 3),
                diagnosis='Headache'
            )
        ]
        
        for visit in visits:
            db.session.add(visit)
        
        db.session.flush()
        
        # Create prescriptions
        print("Creating prescriptions...")
        prescriptions = [
            Prescription(
                patient_id=patients[0].patient_id,
                doctor_id=doctors[0].user_id,
                visit_id=visits[0].visit_id,
                drug_name='Aspirin',
                dosage='500mg',
                duration='3 days'
            ),
            Prescription(
                patient_id=patients[1].patient_id,
                doctor_id=doctors[1].user_id,
                visit_id=visits[1].visit_id,
                drug_name='Tamiflu',
                dosage='75mg',
                duration='5 days'
            ),
            Prescription(
                patient_id=patients[2].patient_id,
                doctor_id=doctors[2].user_id,
                visit_id=visits[2].visit_id,
                drug_name='Ibuprofen',
                dosage='400mg',
                duration='2 days'
            )
        ]
        
        for prescription in prescriptions:
            db.session.add(prescription)
        
        db.session.flush()
        
        # Create reports
        print("Creating reports...")
        reports = [
            Report(
                patient_id=patients[0].patient_id,
                report_type='Blood Test',
                report_data='Normal blood count'
            ),
            Report(
                patient_id=patients[1].patient_id,
                report_type='X-Ray',
                report_data='Clear chest X-ray'
            ),
            Report(
                patient_id=patients[2].patient_id,
                report_type='MRI',
                report_data='No abnormalities detected'
            )
        ]
        
        for report in reports:
            db.session.add(report)
        
        # Commit all changes
        db.session.commit()
        print("Test database populated successfully!")

if __name__ == '__main__':
    populate_test_data() 