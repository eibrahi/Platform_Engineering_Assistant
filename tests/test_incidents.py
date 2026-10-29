import pytest


@pytest.fixture
def platform(client):
    response = client.post('/api/platforms', json={'name': 'customer360-prod', 'environment': 'prod'})
    assert response.status_code == 201, response.text
    return response.json()


def create_incident(client, platform_id, **overrides):
    data = {'platform_id': platform_id, 'title': 'Job customer_load schlägt fehl', **overrides}
    response = client.post('/api/incidents', json=data)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_incident_starts_open(client, platform):
    incident = create_incident(client, platform['id'], description='Seit 06:00 Uhr')

    assert incident['platform_id'] == platform['id']
    assert incident['status'] == 'open'
    assert incident['severity'] == 'medium'
    assert incident['resolved_at'] is None
    assert incident['created_at']


def test_create_incident_ignores_status_in_body(client, platform):
    incident = create_incident(client, platform['id'], status='resolved')

    assert incident['status'] == 'open'


def test_create_incident_for_unknown_platform_is_rejected(client):
    response = client.post('/api/incidents', json={'platform_id': 999999, 'title': 'x'})

    assert response.status_code == 422
    assert 'Plattform' in response.text


def test_create_incident_rejects_unknown_severity(client, platform):
    response = client.post(
        '/api/incidents', json={'platform_id': platform['id'], 'title': 'x', 'severity': 'urgent'}
    )

    assert response.status_code == 422


def test_list_incidents_filters_and_newest_first(client, platform):
    first = create_incident(client, platform['id'], title='erster', severity='low')
    second = create_incident(client, platform['id'], title='zweiter', severity='critical')

    all_ids = [i['id'] for i in client.get('/api/incidents').json()]
    critical = client.get('/api/incidents', params={'severity': 'critical'}).json()
    by_platform = client.get('/api/incidents', params={'platform_id': platform['id']}).json()
    resolved = client.get('/api/incidents', params={'status': 'resolved'}).json()

    assert all_ids == [second['id'], first['id']]
    assert [i['id'] for i in critical] == [second['id']]
    assert len(by_platform) == 2
    assert resolved == []


def test_get_missing_incident_returns_404(client):
    assert client.get('/api/incidents/999999').status_code == 404


def test_resolving_sets_resolved_at_and_reopening_clears_it(client, platform):
    incident = create_incident(client, platform['id'])
    url = f"/api/incidents/{incident['id']}"

    resolved = client.put(url, json={'status': 'resolved', 'root_cause': 'Cluster-Quota erreicht'}).json()
    reopened = client.put(url, json={'status': 'investigating'}).json()

    assert resolved['status'] == 'resolved'
    assert resolved['resolved_at'] is not None
    assert resolved['root_cause'] == 'Cluster-Quota erreicht'
    assert reopened['resolved_at'] is None
    assert reopened['root_cause'] == 'Cluster-Quota erreicht'


def test_update_cannot_change_platform(client, platform):
    incident = create_incident(client, platform['id'])

    response = client.put(f"/api/incidents/{incident['id']}", json={'platform_id': 999999})

    assert response.status_code == 200
    assert response.json()['platform_id'] == platform['id']


def test_update_rejects_null_for_required_field(client, platform):
    incident = create_incident(client, platform['id'])

    assert client.put(f"/api/incidents/{incident['id']}", json={'status': None}).status_code == 422


def test_update_missing_incident_returns_404(client):
    assert client.put('/api/incidents/999999', json={'status': 'resolved'}).status_code == 404


def test_incidents_cannot_be_deleted(client, platform):
    incident = create_incident(client, platform['id'])

    assert client.delete(f"/api/incidents/{incident['id']}").status_code == 405


def test_deleting_platform_removes_its_incidents(client, platform):
    incident = create_incident(client, platform['id'])

    client.delete(f"/api/platforms/{platform['id']}")

    assert client.get(f"/api/incidents/{incident['id']}").status_code == 404
