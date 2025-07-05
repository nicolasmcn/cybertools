def test_analyze_requires_auth(client):
    response = client.get('/analyze?domain=example.com')
    assert response.status_code == 401