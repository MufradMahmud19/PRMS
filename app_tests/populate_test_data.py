import sys
import os
from datetime import datetime

# Add the parent directory to sys.path so 'app' becomes importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.app_extensions import db
from app.models import User, Patient, Visit, Prescription, Report

def populate_test_data():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app/instance/hospital.db'  # Use the same path as the app
    
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        
        print("Creating doctors...")
        # Create doctors
        doctors = [
            User(username='dr_smith', role='doctor'),
            User(username='dr_jones', role='doctor'),
            User(username='dr_wilson', role='doctor')
        ]
        
        for doctor in doctors:
            doctor.set_password('password123')
            db.session.add(doctor)
        
        try:
            db.session.flush()
            print("Doctors created successfully!")
            print(f"Dr. Smith ID: {doctors[0].user_id}")
        except Exception as e:
            print(f"Error creating doctors: {str(e)}")
            return
        
        print("Creating patients...")
        # Create patients
        patients = [
            Patient(name='Alice Johnson', age=30, contact_info='alice@example.com'),
            Patient(name='Bob Wilson', age=45, contact_info='bob@example.com'),
            Patient(name='Carol Davis', age=28, contact_info='carol@example.com'),
            Patient(name='David Brown', age=60, contact_info='david@example.com')
        ]
        
        for patient in patients:
            db.session.add(patient)
        
        try:
            db.session.flush()
            print("Patients created successfully!")
            print(f"First patient ID: {patients[0].patient_id}")
        except Exception as e:
            print(f"Error creating patients: {str(e)}")
            return
        
        print("Creating visits...")
        # Create visits
        visits = [
            Visit(
                patient_id=patients[0].patient_id,
                doctor_id=doctors[0].user_id,
                visit_date=datetime(2023, 1, 1),
                diagnosis='Flu'
            ),
            Visit(
                patient_id=patients[1].patient_id,
                doctor_id=doctors[1].user_id,
                visit_date=datetime(2023, 1, 15),
                diagnosis='Cold'
            ),
            Visit(
                patient_id=patients[2].patient_id,
                doctor_id=doctors[2].user_id,
                visit_date=datetime(2023, 2, 1),
                diagnosis='Allergy'
            ),
            Visit(
                patient_id=patients[3].patient_id,
                doctor_id=doctors[0].user_id,
                visit_date=datetime(2023, 2, 15),
                diagnosis='Hypertension'
            )
        ]
        
        for visit in visits:
            db.session.add(visit)
        
        try:
            db.session.flush()
            print("Visits created successfully!")
            print(f"First visit ID: {visits[0].visit_id}")
        except Exception as e:
            print(f"Error creating visits: {str(e)}")
            return
        
        print("Creating prescriptions...")
        # Create prescriptions
        prescriptions = [
            Prescription(
                patient_id=patients[0].patient_id,
                doctor_id=doctors[0].user_id,
                visit_id=visits[0].visit_id,
                drug_name='Paracetamol',
                dosage='500mg',
                duration='7 days'
            ),
            Prescription(
                patient_id=patients[1].patient_id,
                doctor_id=doctors[1].user_id,
                visit_id=visits[1].visit_id,
                drug_name='Ibuprofen',
                dosage='400mg',
                duration='5 days'
            ),
            Prescription(
                patient_id=patients[2].patient_id,
                doctor_id=doctors[2].user_id,
                visit_id=visits[2].visit_id,
                drug_name='Antihistamine',
                dosage='10mg',
                duration='14 days'
            ),
            Prescription(
                patient_id=patients[3].patient_id,
                doctor_id=doctors[0].user_id,
                visit_id=visits[3].visit_id,
                drug_name='Lisinopril',
                dosage='10mg',
                duration='30 days'
            )
        ]
        
        for prescription in prescriptions:
            db.session.add(prescription)
        
        try:
            db.session.flush()
            print("Prescriptions created successfully!")
            print(f"First prescription ID: {prescriptions[0].prescription_id}")
        except Exception as e:
            print(f"Error creating prescriptions: {str(e)}")
            return
        
        print("Creating reports...")
        # Create reports
        reports = [
            Report(
                patient_id=patients[0].patient_id,
                report_type='Blood Test',
                report_data='Normal CBC, slightly elevated WBC'
            ),
            Report(
                patient_id=patients[1].patient_id,
                report_type='X-Ray',
                report_data='Clear lungs, no abnormalities'
            ),
            Report(
                patient_id=patients[2].patient_id,
                report_type='Allergy Test',
                report_data='Positive for pollen and dust mites'
            ),
            Report(
                patient_id=patients[3].patient_id,
                report_type='Blood Pressure',
                report_data='140/90 mmHg, elevated'
            )
        ]
        
        for report in reports:
            db.session.add(report)
        
        try:
            db.session.flush()
            print("Reports created successfully!")
            print(f"First report ID: {reports[0].report_id}")
        except Exception as e:
            print(f"Error creating reports: {str(e)}")
            return
        
        try:
            print("Committing all changes...")
            db.session.commit()
            print("All changes committed successfully!")
        except Exception as e:
            print(f"Error committing changes: {str(e)}")
            return
        
        print("\nTest data populated successfully!")
        print("\nSample credentials for testing:")
        print("Doctors:")
        for doctor in doctors:
            print(f"Username: {doctor.username}, Password: password123")
        print("\nPatient IDs:")
        for patient in patients:
            print(f"Name: {patient.name}, ID: {patient.patient_id}")

if __name__ == '__main__':
    populate_test_data() 