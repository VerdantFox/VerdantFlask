"""Test users profile view"""


def test_profile_filled_logged_in(client, logged_in_user):
    """Test showing profile of filled out user from user perspective"""
    response = client.get(f"/users/profile/{logged_in_user.username}")
    assert response.status_code == 200
    data = response.data.decode()
    data_no_spaces = "".join(data.split())
    assert f"<h1>{logged_in_user.username} User Profile</h1>" in data
    assert (
        f"<h4>Name:{logged_in_user.full_name.replace(' ', '')}</h4>" in data_no_spaces
    )
    assert f'<img src="{logged_in_user.avatar_location}"' in data
    assert f"<h4>Email:{logged_in_user.email}</h4>" in data_no_spaces
    assert f'<p>{logged_in_user.bio.replace(" ", "")}</p>' in data_no_spaces
    assert (
        f'<h4>BirthDate:{date_str_fmt(logged_in_user.birth_date).replace(" ", "")}</h4>'
        in data_no_spaces
    )
    assert f"<h4>Timezone:{logged_in_user.timezone}</h4>" in data_no_spaces


def test_profile_filled_logged_out(client, user, logged_in_user2):
    """Test showing profile of filled out user from other user perspective"""
    response = client.get(f"/users/profile/{user.username}", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    data_no_spaces = "".join(data.split())
    assert f"<h1>{user.username} User Profile</h1>" in data
    assert f"<h4>Name:{user.full_name.replace(' ', '')}</h4>" in data_no_spaces
    assert f'<img src="{user.avatar_location}"' in data
    assert f"<h4>Email:{user.email}</h4>" in data_no_spaces
    assert f'<p>{user.bio.replace(" ", "")}</p>' in data_no_spaces
    assert (
        f'<h4>BirthDate:{date_str_fmt(user.birth_date).replace(" ", "")}</h4>'
        in data_no_spaces
    )
    assert f"<h4>Timezone:{user.timezone}</h4>" in data_no_spaces


def test_profile_unfilled_logged_in(client, logged_in_user2):
    """Test showing profile of un-filled out user from user's perspective"""
    response = client.get(f"/users/profile/{logged_in_user2.username}")
    assert response.status_code == 200
    data = response.data.decode()
    data_no_spaces = "".join(data.split())
    assert f"<h1>{logged_in_user2.username} User Profile</h1>" in data
    assert (
        f'<h4>Name:{logged_in_user2.full_name.replace(" ", "")}'
        f'<spanclass="text-muted">(hiddentopublic)</span></h4>' in data_no_spaces
    )
    assert f'<img src="{logged_in_user2.avatar_location}"' in data
    assert (
        f'<h4>Email:{logged_in_user2.email.replace(" ", "")}'
        f'<spanclass="text-muted">(hiddentopublic)</span>' in data_no_spaces
    )
    assert f'<p>{logged_in_user2.bio.replace(" ", "")}</p>' in data_no_spaces
    assert (
        f'<h4>BirthDate:{date_str_fmt(logged_in_user2.birth_date).replace(" ", "")}'
        f'<spanclass="text-muted">(hiddentopublic)</span></h4>' in data_no_spaces
    )
    assert (
        f'<h4>Timezone:{logged_in_user2.timezone.replace(" ", "")}'
        f'<spanclass="text-muted">(hiddentopublic)</span></h4>' in data_no_spaces
    )


def test_profile_unfilled_logged_out(client, user2, logged_in_user):
    """Test showing profile of un-filled out user from other user's perspective"""
    response = client.get(f"/users/profile/{user2.username}")
    assert response.status_code == 200
    data = response.data.decode()
    data_no_spaces = "".join(data.split())
    assert f"<h1>{user2.username} User Profile</h1>" in data
    assert user2.full_name not in data
    assert f'<img src="{user2.avatar_location}"' in data
    assert user2.email not in data
    assert f'<p>{user2.bio.replace(" ", "")}</p>' in data_no_spaces
    assert date_str_fmt(user2.birth_date) not in data
    assert user2.timezone not in data


def test_profile_user_doesnt_exist(client, logged_in_user):
    """Test trying to get profile of non-existent user"""
    response = client.get(f"/users/profile/fake_user", follow_redirects=True)
    assert response.status_code == 404
    assert b"User not found." in response.data


def date_str_fmt(datetime_obj):
    """Conver datetime to a string object in the format used in this page"""
    return datetime_obj.strftime("%B %d, %Y")
