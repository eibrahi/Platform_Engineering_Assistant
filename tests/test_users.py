USER = {'name': 'Elvir', 'email': 'elvir@example.com'}


def create_user(client, **overrides):
    response = client.post('/api/users', json={**USER, **overrides})
    assert response.status_code == 201, response.text
    return response.json()


def test_create_user_uses_defaults(client):
    user = create_user(client)

    assert user['id'] > 0
    assert user['role'] == 'viewer'
    assert user['is_active'] is True
    assert user['created_at']


def test_create_user_duplicate_email_conflicts(client):
    create_user(client)

    response = client.post('/api/users', json={**USER, 'name': 'Jemand anderes'})

    assert response.status_code == 409


def test_create_user_rejects_invalid_email(client):
    assert client.post('/api/users', json={**USER, 'email': 'keine-mail'}).status_code == 422


def test_create_user_rejects_unknown_role(client):
    assert client.post('/api/users', json={**USER, 'role': 'superuser'}).status_code == 422


def test_list_users_filters_by_role(client):
    create_user(client, email='a@example.com', role='admin')
    create_user(client, email='b@example.com', role='viewer')

    admins = client.get('/api/users', params={'role': 'admin'}).json()

    assert [u['email'] for u in admins] == ['a@example.com']


def test_get_user(client):
    user = create_user(client)

    response = client.get(f"/api/users/{user['id']}")

    assert response.status_code == 200
    assert response.json() == user


def test_get_missing_user_returns_404(client):
    assert client.get('/api/users/999999').status_code == 404


def test_update_user_role(client):
    user = create_user(client)

    response = client.put(f"/api/users/{user['id']}", json={'role': 'platform_engineer'})

    assert response.status_code == 200
    assert response.json()['role'] == 'platform_engineer'
    assert response.json()['email'] == user['email']


def test_update_user_rejects_null_for_required_field(client):
    user = create_user(client)

    assert client.put(f"/api/users/{user['id']}", json={'email': None}).status_code == 422


def test_update_user_to_existing_email_conflicts(client):
    create_user(client, email='taken@example.com')
    user = create_user(client, email='other@example.com')

    response = client.put(f"/api/users/{user['id']}", json={'email': 'taken@example.com'})

    assert response.status_code == 409


def test_delete_user_deactivates_instead_of_removing(client):
    user = create_user(client)

    assert client.delete(f"/api/users/{user['id']}").status_code == 204

    assert client.get('/api/users').json() == []
    inactive = client.get('/api/users', params={'include_inactive': True}).json()
    assert [u['id'] for u in inactive] == [user['id']]
    assert client.get(f"/api/users/{user['id']}").json()['is_active'] is False


def test_reactivate_user(client):
    user = create_user(client)
    client.delete(f"/api/users/{user['id']}")

    response = client.put(f"/api/users/{user['id']}", json={'is_active': True})

    assert response.json()['is_active'] is True


def test_delete_missing_user_returns_404(client):
    assert client.delete('/api/users/999999').status_code == 404
