PLATFORM = {
    'name': 'customer360-dev',
    'environment': 'dev',
    'azure_region': 'westeurope',
    'databricks_workspace_url': 'https://adb-123.azuredatabricks.net',
}


def create_platform(client, **overrides):
    response = client.post('/api/platforms', json={**PLATFORM, **overrides})
    assert response.status_code == 201, response.text
    return response.json()


def test_health(client):
    assert client.get('/health').json() == {'status': 'ok'}


def test_create_platform_uses_defaults(client):
    platform = create_platform(client)

    assert platform['id'] > 0
    assert platform['name'] == 'customer360-dev'
    assert platform['cloud_provider'] == 'azure'
    assert platform['status'] == 'unknown'
    assert platform['created_at'] and platform['updated_at']


def test_create_platform_duplicate_name_conflicts(client):
    create_platform(client)

    response = client.post('/api/platforms', json=PLATFORM)

    assert response.status_code == 409


def test_create_platform_rejects_unknown_environment(client):
    response = client.post('/api/platforms', json={**PLATFORM, 'environment': 'staging'})

    assert response.status_code == 422


def test_list_platforms_filters_by_environment(client):
    create_platform(client, name='a-dev', environment='dev')
    create_platform(client, name='b-prod', environment='prod')

    all_names = [p['name'] for p in client.get('/api/platforms').json()]
    prod_names = [p['name'] for p in client.get('/api/platforms', params={'environment': 'prod'}).json()]

    assert all_names == ['a-dev', 'b-prod']
    assert prod_names == ['b-prod']


def test_get_platform(client):
    platform = create_platform(client)

    response = client.get(f"/api/platforms/{platform['id']}")

    assert response.status_code == 200
    assert response.json() == platform


def test_get_missing_platform_returns_404(client):
    assert client.get('/api/platforms/999999').status_code == 404


def test_update_platform_changes_only_given_fields(client):
    platform = create_platform(client)

    response = client.put(f"/api/platforms/{platform['id']}", json={'status': 'healthy'})

    assert response.status_code == 200
    updated = response.json()
    assert updated['status'] == 'healthy'
    assert updated['name'] == platform['name']
    assert updated['azure_region'] == platform['azure_region']


def test_update_platform_rejects_null_for_required_field(client):
    platform = create_platform(client)

    response = client.put(f"/api/platforms/{platform['id']}", json={'name': None})

    assert response.status_code == 422


def test_update_platform_to_existing_name_conflicts(client):
    create_platform(client, name='taken')
    platform = create_platform(client, name='other')

    response = client.put(f"/api/platforms/{platform['id']}", json={'name': 'taken'})

    assert response.status_code == 409


def test_update_missing_platform_returns_404(client):
    assert client.put('/api/platforms/999999', json={'status': 'down'}).status_code == 404


def test_delete_platform(client):
    platform = create_platform(client)

    assert client.delete(f"/api/platforms/{platform['id']}").status_code == 204
    assert client.get(f"/api/platforms/{platform['id']}").status_code == 404


def test_delete_missing_platform_returns_404(client):
    assert client.delete('/api/platforms/999999').status_code == 404
