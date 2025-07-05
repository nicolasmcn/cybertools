from app import db, User

def test_register_user(client):
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'Azerty12@'  # Mot de passe valide avec 2 chiffres et 1 spécial
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Compte cr' in response.data  # Message de succès

def test_register_user_weak_password(client):
    response = client.post('/register', data={
        'email': 'fail@example.com',
        'password': 'short'  # Trop faible
    }, follow_redirects=True)
    assert b'Le mot de passe doit contenir' in response.data  # Message d'erreur attendu