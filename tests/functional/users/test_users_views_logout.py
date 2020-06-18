"""Test users logout view"""


def test_logout_basic(client, logged_in_user1_mod):
    """Test logging out a logged in user"""
    response = client.get("/users/logout", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "You have logged out." in data


def test_logout_when_not_logged_in(client):
    """Test logging out a logged in user"""
    response = client.get("/users/logout", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "Please log in to access this page." in data
