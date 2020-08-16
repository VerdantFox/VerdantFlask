"""Test features of the error handlers"""
import pytest
from flask import abort

from root.routes.core import views


def test_404(client):
    """Test that 404 produces desired error page"""
    response = client.get("/some-fake-page")
    assert response.status_code == 404
    data = response.data.decode()
    assert "Oops! The page you requested was not found." in data


ERRORS = [
    pytest.param(
        500,
        "Something went wrong. It's not you, it's us...".replace("'", "&#39;"),
        id="500",
    ),
    pytest.param(
        401,
        "The server could not verify that you are authorized to access the URL requested.",
        id="401",
    ),
    pytest.param(
        403,
        "You don't have the permission to access the requested resource.".replace(
            "'", "&#39;"
        ),
        id="403",
    ),
]


@pytest.mark.parametrize("code, message", ERRORS)
def test_various_errors(monkeypatch, client, code, message):
    """ Test errors that require mock to produce return desired html """

    def fake_query_and_paginate_blog():
        """ Replaces method with one that will return desired error """
        abort(code)

    monkeypatch.setattr(views, "query_and_paginate_blog", fake_query_and_paginate_blog)

    response = client.get("/", follow_redirects=True)
    assert response.status_code == code
    data = response.data.decode()
    assert message in data
