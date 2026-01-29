# tests/test_api.py
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert b'operational' in response.data

def test_mock_analyze(client):
    response = client.post('/mock-analyze', data={
        'patient_id': 'test123',
        'patient_name': 'Test',
        'age': '5'
    })
    assert response.status_code == 200
    assert b'risk' in response.data