"""Test users delete view"""
from root.routes.users.models import User


def test_delete_account_succeeds(client, logged_in_user1):
    """Test the delete view for logged in user"""
    response = client.get("/users/delete_account", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "Account deleted!" in data
    user = User.objects(id=logged_in_user1.id).first()
    assert user is None
