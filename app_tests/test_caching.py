import sys
import os
import time
import json
import unittest

# Add the parent directory to sys.path so 'app' becomes importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.app_extensions import db, cache
from app.models import User, Patient
from app.cache_utils import clear_all_cache
from app.app_config import TestConfig

# Create test database directory if it doesn't exist
TEST_DB_DIR = os.path.join(os.path.dirname(__file__), 'test_instance')
os.makedirs(TEST_DB_DIR, exist_ok=True)

@pytest.fixture
def client():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{os.path.join(TEST_DB_DIR, "test.db")}',
        'JWT_SECRET_KEY': 'test-secret',
        'JWT_TOKEN_LOCATION': ['headers'],
        'JWT_HEADER_NAME': 'Authorization',
        'JWT_HEADER_TYPE': 'Bearer',
        'JWT_ACCESS_TOKEN_EXPIRES': False,  # Disable token expiration for testing
        
        # Redis test configuration
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_HOST': 'localhost',
        'CACHE_REDIS_PORT': 6379,
        'CACHE_REDIS_DB': 0,
        'CACHE_REDIS_PASSWORD': None,
        'CACHE_DEFAULT_TIMEOUT': 2,  # 2 seconds timeout for testing
        
        # Override Redis settings to match cache settings
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': 6379,
        'REDIS_DB': 0,
        'REDIS_PASSWORD': None
    })
    
    with app.test_client() as client:
        with app.app_context():
            # Clear all cache before tests
            clear_all_cache()
            
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
            
            db.session.commit()
            
        yield client

@pytest.fixture
def auth_headers(client):
    """Get authentication headers for the test client."""
    # Login to get token
    response = client.post('/login', json={
        'username': 'dr_smith',
        'password': 'password123'
    })
    assert response.status_code == 200
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_patient_list_caching(client, auth_headers):
    """Test that patient list is cached and served from cache."""
    # First request - should hit the database
    start_time = time.time()
    response1 = client.get('/patients', headers=auth_headers)
    db_time = time.time() - start_time
    
    assert response1.status_code == 200
    data1 = response1.json
    assert len(data1) == 1
    assert data1[0]['name'] == 'Alice'
    
    # Second request - should be served from cache
    start_time = time.time()
    response2 = client.get('/patients', headers=auth_headers)
    cache_time = time.time() - start_time
    
    assert response2.status_code == 200
    data2 = response2.json
    assert data1 == data2  # Same data
    
    # Cache should be faster than database
    assert cache_time < db_time

def test_individual_patient_caching(client, auth_headers):
    """Test that individual patient data is cached."""
    # First request - should hit the database
    start_time = time.time()
    response1 = client.get('/patients/1', headers=auth_headers)
    db_time = time.time() - start_time
    
    assert response1.status_code == 200
    data1 = response1.json
    assert data1['data']['name'] == 'Alice'
    
    # Second request - should be served from cache
    start_time = time.time()
    response2 = client.get('/patients/1', headers=auth_headers)
    cache_time = time.time() - start_time
    
    assert response2.status_code == 200
    data2 = response2.json
    assert data1 == data2  # Same data
    
    # Cache should be faster than database
    assert cache_time < db_time

def test_cache_invalidation_on_create(client, auth_headers):
    """Test that cache is invalidated when creating a new patient."""
    # Get initial patient list (will be cached)
    response1 = client.get('/patients', headers=auth_headers)
    initial_count = len(response1.json)
    
    # Create a new patient
    response = client.post('/patients', 
        json={
            'name': 'Bob',
            'age': 25,
            'contact_info': 'bob@example.com'
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    
    # Get patient list again - should show new patient
    response2 = client.get('/patients', headers=auth_headers)
    new_count = len(response2.json)
    assert new_count == initial_count + 1

def test_cache_invalidation_on_update(client, auth_headers):
    """Test that cache is invalidated when updating a patient."""
    # Get initial patient data (will be cached)
    response1 = client.get('/patients/1', headers=auth_headers)
    initial_name = response1.json['data']['name']
    
    # Update patient
    response = client.put('/patients/1', 
        json={
            'name': 'Alice Smith'
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Get patient data again - should show updated name
    response2 = client.get('/patients/1', headers=auth_headers)
    new_name = response2.json['data']['name']
    assert new_name == 'Alice Smith'
    assert new_name != initial_name

def test_cache_invalidation_on_delete(client, auth_headers):
    """Test that cache is invalidated when deleting a patient."""
    # Get initial patient list (will be cached)
    response1 = client.get('/patients', headers=auth_headers)
    initial_count = len(response1.json)
    
    # Delete patient
    response = client.delete('/patients/1', headers=auth_headers)
    assert response.status_code == 200
    
    # Get patient list again - should show one less patient
    response2 = client.get('/patients', headers=auth_headers)
    new_count = len(response2.json)
    assert new_count == initial_count - 1

def test_cache_timeout(client, auth_headers):
    """Test that cache expires after timeout period."""
    # Get patient list (will be cached)
    response1 = client.get('/patients', headers=auth_headers)
    initial_data = response1.json
    
    # Wait for cache to expire (2 seconds)
    time.sleep(2.5)  # Wait slightly longer than cache timeout
    
    # Get patient list again - should hit database
    response2 = client.get('/patients', headers=auth_headers)
    new_data = response2.json
    
    # Data should still be the same, but it came from database this time
    assert initial_data == new_data 

class TestCaching(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create a test patient
        self.test_patient = Patient(
            name='Test Patient',
            email='test@example.com',
            phone='1234567890',
            address='Test Address'
        )
        db.session.add(self.test_patient)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_patient_caching(self):
        # First request - should hit the database
        response1 = self.client.get('/patients')
        self.assertEqual(response1.status_code, 200)
        data1 = response1.get_json()

        # Second request - should be served from cache
        response2 = self.client.get('/patients')
        self.assertEqual(response2.status_code, 200)
        data2 = response2.get_json()

        # Verify both responses are identical
        self.assertEqual(data1, data2)

        # Wait for cache to expire (2 seconds as per TestConfig)
        time.sleep(3)

        # Third request - should hit the database again
        response3 = self.client.get('/patients')
        self.assertEqual(response3.status_code, 200)
        data3 = response3.get_json()

        # Verify data is still the same
        self.assertEqual(data1, data3)

    def test_cache_invalidation(self):
        # Get initial patients list
        response1 = self.client.get('/patients')
        self.assertEqual(response1.status_code, 200)
        initial_data = response1.get_json()

        # Create a new patient
        new_patient = {
            'name': 'New Patient',
            'email': 'new@example.com',
            'phone': '0987654321',
            'address': 'New Address'
        }
        create_response = self.client.post('/patients', json=new_patient)
        self.assertEqual(create_response.status_code, 201)

        # Get patients list again - should be different due to cache invalidation
        response2 = self.client.get('/patients')
        self.assertEqual(response2.status_code, 200)
        updated_data = response2.get_json()

        # Verify the data has changed
        self.assertNotEqual(initial_data, updated_data)
        self.assertEqual(len(updated_data), len(initial_data) + 1)

if __name__ == '__main__':
    unittest.main() 