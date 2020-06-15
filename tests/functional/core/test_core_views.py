"""Test features of the core views"""
import pytest


def test_index_basics(client):
    """Test that the index page works and has some core html components"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.data
    # Assert links are correct
    assert b'<a class="nav-link" href="#blog">Blog</a>' in data
    assert b'<a class="nav-link" href="#projects">Projects</a>' in data
    assert b'<a class="nav-link" href="#skills">Skills</a>' in data
    assert b'<a class="nav-link" href="#about">About</a>' in data
    assert b"Resume" in data
    # Assert Section headers are in index
    assert b">Welcome to Verdant Fox!</h1>" in data
    assert b">My blog</h2>" in data
    assert b">Projects</h2>" in data
    assert b">Skills</h2>" in data
    assert b">About</h2>" in data
    assert b">Thank you for visiting my portfolio! I hope you enjoyed it.</p>" in data
    # Assert login and register links (not logged in yet)
    assert b'href="/users/login?next=%2F">' in data
    assert b'href="/users/register?next=%2F">' in data


@pytest.mark.skip
def test_index_while_logged_in(client):
    """Test the altered functionality of index page while logged in"""
    pass
