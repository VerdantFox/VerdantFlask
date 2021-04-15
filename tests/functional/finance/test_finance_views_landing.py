"""test_finance_views_landing: test the landing page of the finance package"""


def test_landing_get(client):
    """Test standard GET of the finance landing page"""
    response = client.get("/finance", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "Finance page" in data
