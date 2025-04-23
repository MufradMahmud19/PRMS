
import sys
import os

# Add the parent directory to sys.path so 'app' becomes importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.app_extensions import db
from app.models import User, Patient, Visit
from flask_jwt_extended import create_access_token
from datetime import datetime

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Seed test data
            user = User(username='testuser', role='doctor')  # Add role
            user.set_password('testpass')
            db.session.add(user)

            patient = Patient(name='Alice', age=30, contact_info='alice@example.com')
            db.session.add(patient)

            db.session.flush()  # Assigns user.id and patient.id

            visit = Visit(
                visit_date=datetime(2023, 1, 1),
                diagnosis='Flu',
                doctor_id=user.user_id,  # Use .user_id not .id
                patient_id=patient.patient_id
            )
            db.session.add(visit)
            db.session.commit()
        yield client

def test_get_patient(client):
    res = client.get('/patients/1')
    assert res.status_code == 200
    assert res.json['data']['name'] == 'Alice'

def test_get_visit(client):
    res = client.get('/visits/1')
    assert res.status_code == 200
    assert res.json['data']['diagnosis'] == 'Flu'

def test_login_success(client):
    res = client.post('/login', json={'username': 'testuser', 'password': 'testpass'})
    assert res.status_code == 200
    assert 'access_token' in res.json

def test_login_failure(client):
    res = client.post('/login', json={'username': 'wronguser', 'password': 'wrongpass'})
    assert res.status_code == 401
    assert 'error' in res.json

def test_protected_route(client):
    # Login to get token
    res = client.post('/login', json={'username': 'testuser', 'password': 'testpass'})
    token = res.json['access_token']

    # Access protected route
    protected = client.get('/protected', headers={
        'Authorization': f'Bearer {token}'
    })
    assert protected.status_code == 200
    assert 'user_id' in protected.json