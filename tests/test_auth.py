from app import db
from app.models import User

def test_register_user(client):
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'Azertyuiop12@'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Compte cr' in response.data

def test_register_user_weak_password(client):
    response = client.post('/register', data={
        'email': 'fail@example.com',
        'password': 'short'
    }, follow_redirects=True)
    assert b'Le mot de passe doit contenir' in response.data