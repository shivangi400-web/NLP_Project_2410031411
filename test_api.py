import pytest
from numilex.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_currency(client):
    response = client.post('/api/analyze', json={'text': 'The laptop costs ₹55,000 and has 16GB RAM.'})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    categories = [item['category'] for item in payload['expressions']]
    assert 'Currency' in categories
    assert 'Measurement' in categories


def test_percentage(client):
    response = client.post('/api/analyze', json={'text': 'The growth rate is 18.5% in the last quarter.'})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert any(item['expression'] == '18.5%' for item in payload['expressions'])


def test_quantity(client):
    response = client.post('/api/analyze', json={'text': 'The workshop enrolled 500 students and 12 countries.'})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert any(item['category'] == 'Quantity' for item in payload['expressions'])


def test_measurement(client):
    response = client.post('/api/analyze', json={'text': 'The monitor is 15.6 inch and the server runs at 3.2 GHz.'})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert any(item['category'] == 'Measurement' for item in payload['expressions'])


def test_ranking(client):
    response = client.post('/api/analyze', json={'text': 'The product ranked 4.5/5 in the review.'})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert any(item['category'] == 'Ranking' for item in payload['expressions'])


def test_date(client):
    response = client.post('/api/analyze', json={'text': 'The launch happened on 15 August 2025.'})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert any(item['category'] == 'Date' for item in payload['expressions'])


def test_multiple_expressions_same_sentence(client):
    response = client.post('/api/analyze', json={'text': 'The laptop costs ₹55,000 and has 16GB RAM with a 4.5/5 rating.'})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert payload['statistics']['total'] >= 3


def test_mixed_categories(client):
    response = client.post('/api/analyze', json={'text': 'Revenue reached ₹12.5 crore in 2025, with 18.5% growth and 500 employees.'})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    categories = {item['category'] for item in payload['expressions']}
    assert {'Currency', 'Quantity', 'Percentage'} <= categories


def test_no_numerical_expressions(client):
    response = client.post('/api/analyze', json={'text': 'The meeting will happen tomorrow at noon.'})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert payload['statistics']['total'] == 0


def test_empty_input(client):
    response = client.post('/api/analyze', json={'text': ''})
    assert response.status_code == 400
    payload = response.get_json()
    assert payload['success'] is False


def test_ambiguous_year(client):
    response = client.post('/api/analyze', json={'text': 'The report was published in 2025 without a specific date mention.'})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['success'] is True
    assert any(item['category'] == 'Quantity' for item in payload['expressions'])


def test_invalid_request(client):
    response = client.post('/api/analyze', data='not-json')
    assert response.status_code == 400
    payload = response.get_json()
    assert payload['success'] is False
