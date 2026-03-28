import pytest
from app import app
from utils.validation import validate_and_sanitize_input

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Health Insights AI' in rv.data

def test_validation_empty():
    valid, _, _ = validate_and_sanitize_input("")
    assert valid is False

def test_validation_too_short():
    valid, _, _ = validate_and_sanitize_input("pain")
    assert valid is False

def test_validation_xss():
    valid, sanitized, _ = validate_and_sanitize_input("<script>alert(1)</script> chest pain")
    assert valid is True
    assert "<script>" not in sanitized
    assert "chest pain" in sanitized

def test_analyze_no_input(client):
    rv = client.post('/api/analyze', json={})
    assert rv.status_code == 400

def test_analyze_empty_input(client):
    rv = client.post('/api/analyze', json={"text": "   "})
    assert rv.status_code == 400

def test_analyze_too_long(client):
    rv = client.post('/api/analyze', json={"text": "a" * 1500})
    assert rv.status_code == 400

def test_caching_headers(client):
    rv = client.get('/static/style.css')
    if rv.status_code == 200:
        assert 'Cache-Control' in rv.headers
        assert 'public' in rv.headers['Cache-Control']
