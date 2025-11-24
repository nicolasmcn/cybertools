from app.models import User, PasswordHistory

def test_save_password(client):
    # Create a User
    client.post('/register', data={
        'email': 'pwhist@example.com',
        'password': 'Azertyuiop12@'
    }, follow_redirects=True)
    client.post('/login', data={
        'email': 'pwhist@example.com',
        'password': 'Azertyuiop12@'
    }, follow_redirects=True)

    # Send a Password
    response = client.post('/save-password', json={
        'password': 'Azertyuiop12@',
        'strength': 'Fort'
    })
    assert response.status_code == 200
    assert b'success' in response.data