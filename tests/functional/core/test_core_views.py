"""Test features of the core views"""


def test_index_basics(client):
    """Test that the index page works and has some core html components"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.data.decode()
    # Assert links are correct
    assert '<a class="nav-link" href="#blog">Blog</a>' in data
    assert '<a class="nav-link" href="#projects">Projects</a>' in data
    assert '<a class="nav-link" href="#skills">Skills</a>' in data
    assert '<a class="nav-link" href="#about">About</a>' in data
    assert "Resume" in data
    # Assert Section headers are in index
    assert ">Welcome to Verdant Fox!</h1>" in data
    assert ">My blog</h2>" in data
    assert ">Projects</h2>" in data
    assert ">Skills</h2>" in data
    assert ">About</h2>" in data
    assert ">Thank you for visiting my portfolio! I hope you enjoyed it.</p>" in data
    # Assert login and register links (not logged in yet)
    assert 'href="/users/login?next=%2F">' in data
    assert 'href="/users/register?next=%2F">' in data


def test_index_while_logged_in(client, current_user_standard):
    """Test the altered functionality of index page while logged in"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.data.decode()
    assert f"Welcome, {current_user_standard.username}" in data
    assert f'href="/users/profile/{current_user_standard.username}">' in data
    assert 'href="/users/edit_profile">' in data
    assert 'href="/users/account_settings">' in data
    assert 'href="/users/logout' in data
