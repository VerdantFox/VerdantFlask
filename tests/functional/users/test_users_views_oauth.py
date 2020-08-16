"""Test users oauth views"""
import pytest

from src.routes.users.models import User
from tests.functional.users.conftest import USER1, USER2

# -------------------------------------------------------------------------
# Parameters
# -------------------------------------------------------------------------
OAUTH_CLIENTS = ["Facebook", "Google", "GitHub"]


# -------------------------------------------------------------------------
# Mocks
# -------------------------------------------------------------------------
def fake_authomatic_login_name_taken(adapter, oauth_client):
    """Fake authomatic login for name taken by other user"""
    return FakeResult(oauth_client, name_taken=True, id_taken=False, fail_user=False)


def fake_authomatic_login_id_taken(adapter, oauth_client):
    """Fake authomatic login for oauth id taken by other user"""
    return FakeResult(oauth_client, name_taken=False, id_taken=True, fail_user=False)


def fake_authomatic_user_fail(adapter, oauth_client):
    """Fake authomatic login returning failed login"""
    return FakeResult(oauth_client, name_taken=False, id_taken=False, fail_user=True)


def fake_authomatic_result_fail(adapter, oauth_client):
    """Fake authomatic login returning failed result"""
    return None


def fake_authomatic_login_success(adapter, oauth_client):
    """Fake authomatic login for success with no conflicts"""
    return FakeResult(oauth_client, name_taken=False, id_taken=False, fail_user=False)


class FakeOauthUser:
    """Fake authomatic result.user"""

    def __init__(self, oauth_client, name_taken, id_taken, fail_user):
        self.oauth_client = oauth_client.lower()
        self.name_taken = name_taken
        self.id_taken = id_taken
        self.name = None
        self.id = None
        self.expected_username = None
        self.fail_user = fail_user

    def __repr__(self):
        if self.fail_user:
            return None
        else:
            return "FakeOauthUser repr"

    def update(self):
        """Update the fake user with fake data"""
        if self.name_taken:
            self.name = USER1["username"].capitalize() + " Lastname"
            self.expected_username = f'{USER1["username"]}2'
        else:
            self.name = "Oauthname Superfresh"
            self.expected_username = "oauthname"
        if self.id_taken:
            self.id = USER2[f"{self.oauth_client}_id"]
        else:
            if self.oauth_client in ("facebook", "google"):
                self.id = "somefreshoauthid"
            else:
                self.id = 9876543210
        return self


class FakeResult:
    """Fake authomatic result object returned by authomatic.login"""

    def __init__(self, oauth_client, name_taken, id_taken, fail_user):
        self.user = (
            None
            if fail_user
            else FakeOauthUser(oauth_client, name_taken, id_taken, fail_user)
        )


# -------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------
@pytest.mark.parametrize("oauth_client", OAUTH_CLIENTS)
def test_logged_in_connect_fresh_oauth_succeeds(
    mocker, client, logged_in_user1, oauth_client
):
    """Test connecting to fresh oauth while logged in succeeds"""
    mocker.patch(
        "src.routes.users.views.authomatic.login", fake_authomatic_login_success
    )
    oauth_lower = oauth_client.lower()
    response = client.get(f"/users/{oauth_lower}_oauth", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert f"Connected to {oauth_client}!" in data
    user = User.objects(id=logged_in_user1.id).first()
    oauth_user = fake_authomatic_login_success(None, oauth_client).user.update()
    assert user[f"{oauth_lower}_id"] == oauth_user.id


@pytest.mark.parametrize("oauth_client", OAUTH_CLIENTS)
def test_register_user_fresh_oauth_succeeds(mocker, delete_users, client, oauth_client):
    """Test registering via oauth with fresh oauth id succeeds"""
    mocker.patch(
        "src.routes.users.views.authomatic.login", fake_authomatic_login_success
    )
    oauth_lower = oauth_client.lower()
    response = client.get(f"/users/{oauth_lower}_oauth", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    oauth_user = fake_authomatic_login_success(None, oauth_client).user.update()
    assert f"Thanks for registering, {oauth_user.expected_username}!" in data
    assert f"Welcome {oauth_user.expected_username}!" in data
    query = {f"{oauth_lower}_id": oauth_user.id}
    user = User.objects(**query).first()
    assert user is not None


@pytest.mark.parametrize("oauth_client", OAUTH_CLIENTS)
def test_register_user_repeat_username_oauth_succeeds(
    mocker, delete_users, user1, user3, client, oauth_client
):
    """Test registering via oauth with fresh oauth id succeeds"""
    mocker.patch(
        "src.routes.users.views.authomatic.login", fake_authomatic_login_name_taken
    )
    oauth_lower = oauth_client.lower()
    response = client.get(f"/users/{oauth_lower}_oauth", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    oauth_user = fake_authomatic_login_name_taken(None, oauth_client).user.update()
    assert f"Thanks for registering, {oauth_user.expected_username}!" in data
    assert f"Welcome {oauth_user.expected_username}!" in data
    query = {f"{oauth_lower}_id": oauth_user.id}
    user = User.objects(**query).first()
    assert user is not None
    assert user.username == oauth_user.expected_username


@pytest.mark.parametrize("oauth_client", OAUTH_CLIENTS)
def test_login_registered_oauth_user_succeeds(
    mocker, delete_users, user2, client, oauth_client
):
    """Test logging in registered user via oauth succeeds"""
    mocker.patch(
        "src.routes.users.views.authomatic.login", fake_authomatic_login_id_taken
    )
    oauth_lower = oauth_client.lower()
    response = client.get(f"/users/{oauth_lower}_oauth", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert f"Welcome {user2.username}!" in data


@pytest.mark.parametrize("oauth_client", OAUTH_CLIENTS)
def test_logged_in_connect_existing_oauth_fails(
    mocker, client, user2, logged_in_user1, oauth_client
):
    """Test connecting to existing oauth while logged in fails"""
    mocker.patch(
        "src.routes.users.views.authomatic.login", fake_authomatic_login_id_taken
    )
    oauth_lower = oauth_client.lower()
    response = client.get(f"/users/{oauth_lower}_oauth", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert (
        f"That {oauth_client} account is already linked with an account. "
        f"Please log in to that account through {oauth_client} and un-link it "
        "from that account to link it to this account." in data
    )
    user = User.objects(id=logged_in_user1.id).first()
    assert user[f"{oauth_lower}_id"] is None


@pytest.mark.parametrize("oauth_client", OAUTH_CLIENTS)
def test_no_result_returns_response_obj(mocker, client, oauth_client):
    """Test no oauth result object returns response object"""
    mocker.patch("src.routes.users.views.authomatic.login", fake_authomatic_result_fail)
    oauth_lower = oauth_client.lower()
    response = client.get(f"/users/{oauth_lower}_oauth", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert data == ""


@pytest.mark.parametrize("oauth_client", OAUTH_CLIENTS)
def test_no_result_user_fails(mocker, client, oauth_client):
    """Test oauth result object without returned user fails"""
    mocker.patch("src.routes.users.views.authomatic.login", fake_authomatic_user_fail)
    oauth_lower = oauth_client.lower()
    response = client.get(f"/users/{oauth_lower}_oauth", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "Login failed, try again with another method." in data


@pytest.mark.parametrize("oauth_client", OAUTH_CLIENTS)
def test_oauth_disconnect_success(client, oauth_client, logged_in_user2):
    """Test oauth disconnect success"""
    oauth_lower = oauth_client.lower()
    user = User.objects(id=logged_in_user2.id).first()
    assert user[f"{oauth_lower}_id"] == logged_in_user2[f"{oauth_lower}_id"]
    response = client.get(
        f"/users/{oauth_lower}_oauth_disconnect", follow_redirects=True
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert f"Disconnected from {oauth_client}!" in data
    user = User.objects(id=logged_in_user2.id).first()
    assert user[f"{oauth_lower}_id"] is None


@pytest.mark.parametrize("oauth_client", OAUTH_CLIENTS)
def test_oauth_disconnect_with_orphaned_login_fails(
    mocker, client, oauth_client, user3
):
    """Test oauth disconnect fails if disconnect would orphan user login"""
    mocker.patch(
        "src.routes.users.views.authomatic.login", fake_authomatic_login_success
    )
    oauth_user = fake_authomatic_login_success(None, oauth_client).user.update()
    oauth_lower = oauth_client.lower()
    # Save oauth id to account that will be retrieved for login
    user3 = User.objects(id=user3.id).first()
    user3[f"{oauth_lower}_id"] = oauth_user.id
    user3.save()
    # Login user with oauth id just saved to account
    response = client.get(f"/users/{oauth_lower}_oauth", follow_redirects=True)
    assert response.status_code == 200
    # Attempt to disconnect but fail because "can_oauth_disconnect()" returns False
    response = client.get(
        f"/users/{oauth_lower}_oauth_disconnect", follow_redirects=True
    )
    assert response.status_code == 200
    data = response.data.decode()
    assert f"Disconnected from {oauth_client}!" not in data
    assert (
        data.count("You must set an email and password before disconnecting oauth.")
        == 2
    )
    user = User.objects(id=user3.id).first()
    assert user[f"{oauth_lower}_id"] is not None
