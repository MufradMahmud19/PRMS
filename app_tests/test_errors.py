def test_404_recovery_links(client):
    response = client.get('/patients/999')
    assert response.status_code == 404
    assert 'hospital:search' in response.json['_links']
    
def test_400_validation_help(client):
    response = client.post('/patients', json={"age": "invalid"})
    assert 'hospital:validation-help' in response.json['_links']
