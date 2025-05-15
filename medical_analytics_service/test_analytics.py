import pytest
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_patient_statistics(client, monkeypatch):
    # Mock API response
    mock_patients = [
        {'id': 1, 'name': 'John', 'age': 25},
        {'id': 2, 'name': 'Jane', 'age': 35},
        {'id': 3, 'name': 'Bob', 'age': 45}
    ]
    
    def mock_get_api_data(endpoint, params=None):
        return mock_patients
    
    monkeypatch.setattr('app.get_api_data', mock_get_api_data)
    
    response = client.get('/analytics/patient-stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total_patients'] == 3
    assert data['average_age'] == 35.0

def test_visit_trends(client, monkeypatch):
    # Mock API response
    mock_visits = [
        {'visit_id': 1, 'visit_date': '2024-01-01T10:00:00'},
        {'visit_id': 2, 'visit_date': '2024-01-01T11:00:00'},
        {'visit_id': 3, 'visit_date': '2024-01-02T10:00:00'}
    ]
    
    def mock_get_api_data(endpoint, params=None):
        return mock_visits
    
    monkeypatch.setattr('app.get_api_data', mock_get_api_data)
    
    response = client.get('/analytics/visit-trends?days=2')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total_visits'] == 3

def test_prescription_analysis(client, monkeypatch):
    # Mock API response
    mock_prescriptions = [
        {'drug_name': 'Aspirin', 'duration': 7},
        {'drug_name': 'Aspirin', 'duration': 7},
        {'drug_name': 'Ibuprofen', 'duration': 5}
    ]
    
    def mock_get_api_data(endpoint, params=None):
        return mock_prescriptions
    
    monkeypatch.setattr('app.get_api_data', mock_get_api_data)
    
    response = client.get('/analytics/prescription-analysis')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total_prescriptions'] == 3
    assert data['unique_drugs'] == 2

def test_doctor_workload(client, monkeypatch):
    # Mock API response
    mock_visits = [
        {'doctor_id': 1, 'visit_id': 1, 'diagnosis': 'Cold'},
        {'doctor_id': 1, 'visit_id': 2, 'diagnosis': 'Fever'},
        {'doctor_id': 2, 'visit_id': 3, 'diagnosis': 'Cold'}
    ]
    
    def mock_get_api_data(endpoint, params=None):
        return mock_visits
    
    monkeypatch.setattr('app.get_api_data', mock_get_api_data)
    
    response = client.get('/analytics/doctor-workload')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total_doctors'] == 2 