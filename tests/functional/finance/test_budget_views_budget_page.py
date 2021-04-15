"""test_budget_views_budget_page: test budget_page view"""


def test_budget_views_budget_page_not_logged_in(client):
    """Test standard GET of the budget page route while not logged in"""
    response = client.get("/finance/budget", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "<h1>Budget</h1>" in data
    assert "<h2>Graphs unavailable</h2>" in data
    assert '<a href="/users/login?next=%2Ffinance%2Fbudget">Log in</a>' in data
    assert data.count("disabled") == 6
    assert '<input id="budget_json" name="budget_json" type="hidden" value="">' in data


def test_budget_views_budget_page_standard_user(
    client, load_3_budgets_mod, current_user_standard
):
    """Test standard GET of the budget page route while standard user"""
    response = client.get("/finance/budget", follow_redirects=True)
    assert response.status_code == 200
    data = response.data.decode()
    assert "<h1>Budget</h1>" in data
    assert "<h2>Graphs unavailable</h2>" in data
    assert '<a href="/users/login?next=%2Ffinance%2Fbudget">Log in</a>' not in data
    assert data.count("disabled") == 0
    assert '<input id="budget_json" name="budget_json" type="hidden" value="">' in data
    assert load_3_budgets_mod[0].name in data
    assert load_3_budgets_mod[1].name in data
    assert load_3_budgets_mod[2].name not in data
