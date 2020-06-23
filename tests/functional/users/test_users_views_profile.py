"""Test users profile view"""
from tests.functional.users.conftest import date_str_fmt, no_whitespace


def test_profile_filled_logged_in(client, logged_in_user1_mod):
    """Test showing profile of filled out user from user perspective"""
    response = client.get(f"/users/profile/{logged_in_user1_mod.username}")
    assert response.status_code == 200
    data = response.data.decode()
    data_no_spaces = no_whitespace(data)
    assert f"<h1>{logged_in_user1_mod.username} User Profile</h1>" in data
    assert (
        f"<h4>Name:{no_whitespace(logged_in_user1_mod.full_name)}</h4>"
        in data_no_spaces
    )
    assert f'<img src="{logged_in_user1_mod.avatar_location}"' in data
    assert f"<h4>Email:{logged_in_user1_mod.email}</h4>" in data_no_spaces
    assert f"<p>{no_whitespace(logged_in_user1_mod.bio)}</p>" in data_no_spaces
    assert (
        f"<h4>BirthDate:{no_whitespace(date_str_fmt(logged_in_user1_mod.birth_date))}</h4>"
        in data_no_spaces
    )
    assert f"<h4>Timezone:{logged_in_user1_mod.timezone}</h4>" in data_no_spaces


def test_profile_filled_logged_out(client, user1_mod, logged_in_user2_mod):
    """Test showing profile of filled out user from other user perspective"""
    response = client.get(f"/users/profile/{user1_mod.username}", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    data_no_spaces = no_whitespace(data)
    assert f"<h1>{user1_mod.username} User Profile</h1>" in data
    assert f"<h4>Name:{no_whitespace(user1_mod.full_name)}</h4>" in data_no_spaces
    assert f'<img src="{user1_mod.avatar_location}"' in data
    assert f"<h4>Email:{user1_mod.email}</h4>" in data_no_spaces
    assert f"<p>{no_whitespace(user1_mod.bio)}</p>" in data_no_spaces
    assert (
        f"<h4>BirthDate:{no_whitespace(date_str_fmt(user1_mod.birth_date))}</h4>"
        in data_no_spaces
    )
    assert f"<h4>Timezone:{user1_mod.timezone}</h4>" in data_no_spaces


def test_profile_unfilled_logged_in(client, logged_in_user2_mod):
    """Test showing profile of un-filled out user from user's perspective"""
    response = client.get(f"/users/profile/{logged_in_user2_mod.username}")
    assert response.status_code == 200
    data = response.data.decode()
    data_no_spaces = no_whitespace(data)
    assert f"<h1>{logged_in_user2_mod.username} User Profile</h1>" in data
    assert (
        f"<h4>Name:{no_whitespace(logged_in_user2_mod.full_name)}"
        f'<spanclass="text-muted">(hiddentopublic)</span></h4>' in data_no_spaces
    )
    assert f'<img src="{logged_in_user2_mod.avatar_location}"' in data
    assert (
        f"<h4>Email:{no_whitespace(logged_in_user2_mod.email)}"
        f'<spanclass="text-muted">(hiddentopublic)</span>' in data_no_spaces
    )
    assert f"<p>{no_whitespace(logged_in_user2_mod.bio)}</p>" in data_no_spaces
    assert (
        f"<h4>BirthDate:{no_whitespace(date_str_fmt(logged_in_user2_mod.birth_date))}"
        f'<spanclass="text-muted">(hiddentopublic)</span></h4>' in data_no_spaces
    )
    assert (
        f"<h4>Timezone:{no_whitespace(logged_in_user2_mod.timezone)}"
        f'<spanclass="text-muted">(hiddentopublic)</span></h4>' in data_no_spaces
    )


def test_profile_unfilled_logged_out(client, user2_mod, logged_in_user1_mod):
    """Test showing profile of un-filled out user from other user's perspective"""
    response = client.get(f"/users/profile/{user2_mod.username}")
    assert response.status_code == 200
    data = response.data.decode()
    data_no_spaces = no_whitespace(data)
    assert f"<h1>{user2_mod.username} User Profile</h1>" in data
    assert user2_mod.full_name not in data
    assert f'<img src="{user2_mod.avatar_location}"' in data
    assert user2_mod.email not in data
    assert f"<p>{no_whitespace(user2_mod.bio)}</p>" in data_no_spaces
    assert date_str_fmt(user2_mod.birth_date) not in data
    assert user2_mod.timezone not in data


def test_profile_user_doesnt_exist(client, logged_in_user1_mod):
    """Test trying to get profile of non-existent user"""
    response = client.get("/users/profile/fake_user", follow_redirects=True)
    assert response.status_code == 404
    assert b"User not found." in response.data
