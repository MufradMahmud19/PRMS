import sys
import os
import json
from datetime import datetime

# Add the parent directory to sys.path so 'app' becomes importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.app_extensions import db
from app.models import User, Patient, Visit, Prescription, Report
from flask_jwt_extended import create_access_token
from datetime import datetime

# Create test database directory if it doesn't exist
TEST_DB_DIR = os.path.join(os.path.dirname(__file__), 'test_instance')
os.makedirs(TEST_DB_DIR, exist_ok=True)

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(TEST_DB_DIR, "test.db")}'
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Disable token expiration for testing
    
    with app.test_client() as client:
        with app.app_context():
            # Drop all tables and recreate them
            db.drop_all()
            db.create_all()
            
            # Create a test doctor
            doctor = User(username='dr_smith', role='doctor')
            doctor.set_password('password123')
            db.session.add(doctor)
            
            # Create a test patient
            patient = Patient(name='Alice', age=30, contact_info='alice@example.com')
            db.session.add(patient)
            
            db.session.flush()
            
            # Create a test visit
            visit = Visit(
                visit_date=datetime(2023, 1, 1),
                diagnosis='Flu',
                doctor_id=doctor.user_id,
                patient_id=patient.patient_id
            )
            db.session.add(visit)
            
            # Create a test prescription
            prescription = Prescription(
                patient_id=patient.patient_id,
                doctor_id=doctor.user_id,
                visit_id=visit.visit_id,
                drug_name='Paracetamol',
                dosage='500mg',
                duration='7 days'
            )
            db.session.add(prescription)
            
            # Create a test report
            report = Report(
                patient_id=patient.patient_id,
                report_type='Blood Test',
                report_data='Normal'
            )
            db.session.add(report)
            
            db.session.commit()
            
        yield client

# Auth Routes Tests
def test_login_success(client):
    res = client.post('/login', json={'username': 'dr_smith', 'password': 'password123'})
    assert res.status_code == 200
    assert 'access_token' in res.json
    assert 'user' in res.json
    assert res.json['user']['username'] == 'dr_smith'

def test_login_failure(client):
    res = client.post('/login', json={'username': 'wronguser', 'password': 'wrongpass'})
    assert res.status_code == 401
    assert 'error' in res.json

def test_protected_route(client):
    # Login to get token
    res = client.post('/login', json={'username': 'dr_smith', 'password': 'password123'})
    token = res.json['access_token']

    # Access protected route
    protected = client.get('/protected', headers={
        'Authorization': f'Bearer {token}'
    })
    assert protected.status_code == 200
    assert 'user' in protected.json
    assert protected.json['user']['username'] == 'dr_smith'
    assert protected.json['user']['role'] == 'doctor'

# Patient Routes Tests
def test_get_patient(client):
    res = client.get('/patients/1')
    assert res.status_code == 200
    data = res.json['data']
    assert data['name'] == 'Alice'
    assert 'created_at' in data
    assert 'updated_at' in data
    assert '_links' in res.json

def test_create_patient(client):
    res = client.post('/patients', json={
        'name': 'Bob',
        'age': 25,
        'contact_info': 'bob@example.com'
    })
    assert res.status_code == 201
    assert 'id' in res.json
    assert 'created_at' in res.json
    assert 'updated_at' in res.json
    assert res.json['name'] == 'Bob'
    assert res.json['age'] == 25
    assert res.json['contact_info'] == 'bob@example.com'

def test_update_patient(client):
    # Get original updated_at timestamp
    original = client.get('/patients/1').json['data']
    original_updated_at = original['updated_at']

    res = client.put('/patients/1', json={
        'name': 'Alice Smith',
        'age': 31
    })
    assert res.status_code == 200
    assert res.json['message'] == 'Patient updated'
    
    # Verify the update
    updated = client.get('/patients/1').json['data']
    assert updated['name'] == 'Alice Smith'
    assert updated['age'] == 31
    assert updated['updated_at'] != original_updated_at
    assert updated['created_at'] == original['created_at']

def test_delete_patient(client):
    res = client.delete('/patients/1')
    assert res.status_code == 200
    assert res.json['message'] == 'Patient deleted'

def test_get_all_patients(client):
    res = client.get('/patients')
    assert res.status_code == 200
    assert len(res.json) > 0
    for patient in res.json:
        assert 'name' in patient
        assert 'created_at' in patient
        assert 'updated_at' in patient

# Visit Routes Tests
def test_get_visit(client):
    res = client.get('/visits/1')
    assert res.status_code == 200
    assert res.json['data']['diagnosis'] == 'Flu'
    assert '_links' in res.json

def test_create_visit(client):
    # First create a new patient
    patient_res = client.post('/patients', json={
        'name': 'New Patient',
        'age': 35,
        'contact_info': 'new@example.com'
    })
    patient_id = patient_res.json['patient_id']
    
    # Then create a visit for this patient
    res = client.post('/visits', json={
        'patient_id': patient_id,
        'doctor_id': 1,  # dr_smith's ID
        'visit_date': '2023-02-01T00:00:00',
        'diagnosis': 'Cold'
    })
    assert res.status_code == 201
    assert 'visit_id' in res.json

def test_update_visit(client):
    res = client.put('/visits/1', json={
        'diagnosis': 'Severe Flu'
    })
    assert res.status_code == 200
    assert res.json['message'] == 'Visit updated'

def test_delete_visit(client):
    res = client.delete('/visits/1')
    assert res.status_code == 200
    assert res.json['message'] == 'Visit deleted'

def test_get_all_visits(client):
    res = client.get('/visits')
    assert res.status_code == 200
    assert len(res.json) > 0
    assert 'diagnosis' in res.json[0]

# Prescription Routes Tests
def test_create_prescription(client):
    res = client.post('/prescriptions', json={
        'patient_id': 1,
        'doctor_id': 1,
        'visit_id': 1,
        'drug_name': 'Ibuprofen',
        'dosage': '400mg',
        'duration': '5 days'
    })
    assert res.status_code == 201
    assert 'prescription_id' in res.json

def test_update_prescription(client):
    res = client.put('/prescriptions/1', json={
        'dosage': '600mg',
        'duration': '10 days'
    })
    assert res.status_code == 200
    assert res.json['message'] == 'Prescription updated'

def test_delete_prescription(client):
    res = client.delete('/prescriptions/1')
    assert res.status_code == 200
    assert res.json['message'] == 'Prescription deleted'

def test_get_all_prescriptions(client):
    res = client.get('/prescriptions')
    assert res.status_code == 200
    assert len(res.json) > 0
    assert 'drug_name' in res.json[0]

# Report Routes Tests
def test_create_report(client):
    res = client.post('/reports', json={
        'patient_id': 1,
        'report_type': 'X-Ray',
        'report_data': 'No fractures'
    })
    assert res.status_code == 201
    assert 'report_id' in res.json

def test_update_report(client):
    res = client.put('/reports/1', json={
        'report_type': 'MRI Scan',
        'report_data': 'Normal'
    })
    assert res.status_code == 200
    assert res.json['message'] == 'Report updated'

def test_delete_report(client):
    res = client.delete('/reports/1')
    assert res.status_code == 200
    assert res.json['message'] == 'Report deleted'

def test_get_all_reports(client):
    res = client.get('/reports')
    assert res.status_code == 200
    assert len(res.json) > 0
    assert 'report_type' in res.json[0]