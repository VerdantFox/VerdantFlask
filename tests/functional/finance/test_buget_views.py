"""test_budget_views_budget_page: test all budget related views"""
import json

from tests.conftest import get_and_decode, post_and_decode

from .conftest import (
    SIMPLE_BUDGET_FORM,
    SMALL_INNER_BUDGET_1,
    SMALL_INNER_BUDGET_2,
    get_budget,
    retrieve_budget,
    update_budget,
)


def test_budget_views_budget_page_not_logged_in(client):
    """Test standard GET of the budget page route while not logged in"""
    data = get_budget(client)
    assert "<h1>Budget</h1>" in data
    assert "<h2>Graphs unavailable</h2>" in data
    assert '<a href="/users/login?next=%2Ffinance%2Fbudget">Log in</a>' in data
    assert data.count("disabled") == 6
    assert '<input id="budget_json" name="budget_json" type="hidden" value="">' in data


def test_budget_views_budget_page_standard_user(
    client, load_3_budgets, current_user_standard
):
    """Test standard GET of the budget page route while standard user"""
    budget1, budget2, budget3 = load_3_budgets
    data = get_budget(client)
    assert "<h1>Budget</h1>" in data
    assert "<h2>Graphs unavailable</h2>" in data
    assert '<a href="/users/login?next=%2Ffinance%2Fbudget">Log in</a>' not in data
    assert data.count("disabled") == 0
    assert '<input id="budget_json" name="budget_json" type="hidden" value="">' in data
    assert budget1.name in data
    assert budget2.name in data
    assert budget3.name not in data


def test_budget_views_retrieve_budget(client, load_3_budgets, current_user_standard):
    """Test standard POST of the retrieve_budget view"""
    budget1, budget2, budget3 = load_3_budgets
    data = retrieve_budget(client, budget1)
    assert "item1" in data
    assert "123" in data
    data = get_budget(client)
    assert "item1" in data
    assert "123" in data


def test_budget_views_copy_budget_after_retrieve(
    client, load_3_budgets, current_user_standard
):
    """Test copy_budget copies stashed budget"""
    budget1, budget2, budget3 = load_3_budgets
    retrieve_budget(client, budget1)
    data = post_and_decode(client, "/finance/budget/copy", {})
    assert "Budget 1 (copy)" in data
    assert "item1" in data
    assert "123" in data


def test_budget_views_new_budget_not_logged_in(client):
    """Test getting a new budget while not logged in"""
    update_budget(client, SIMPLE_BUDGET_FORM)
    data = get_budget(client)
    assert SIMPLE_BUDGET_FORM["budget_name"] in data
    data = get_and_decode(client, "/finance/budget/new")
    assert SIMPLE_BUDGET_FORM["budget_name"] not in data


def test_budget_views_new_budget_after_retrieve(
    client, load_3_budgets, current_user_standard
):
    """Test new budget resets even after retrieve budget"""
    budget1, budget2, budget3 = load_3_budgets
    retrieve_budget(client, budget1)
    data = get_and_decode(client, "/finance/budget/new")
    assert "item1" not in data
    assert "123" not in data
    data = get_budget(client)
    assert "item1" not in data
    assert "123" not in data


def test_budget_views_update_budget(client):
    """Test standard GET of the budget page route while not logged in"""
    data = update_budget(client, SIMPLE_BUDGET_FORM)
    assert data.count("docs_json") == 8
    assert "It looks like your income is greater than your spending." in data


def test_budget_views_save_budget_not_logged_in(client, load_3_budgets):
    """Test the save_budget view while not logged in"""
    update_budget(client, SIMPLE_BUDGET_FORM)
    data = post_and_decode(client, "/finance/budget/save", {})
    assert "Please log in to access this page." in data


def test_budget_views_save_budget_succeeds(
    client, load_3_budgets, current_user_standard
):
    """Test the save_budget view while not logged in"""
    update_budget(client, SIMPLE_BUDGET_FORM)
    data = post_and_decode(client, "/finance/budget/save", {})
    assert "My budget" in data
    data = get_budget(client)
    # "My budget" in "select" dropdown
    assert "<span>My budget</span>" in data


def test_budget_views_save_default_budget(
    client, load_3_budgets, current_user_standard
):
    """Test saving the default budget saves nothing"""
    data = post_and_decode(client, "/finance/budget/save", {})
    data = get_budget(client)
    # Only the 2 original budgets assigned to user exist in "select" dropdown
    assert data.count("/finance/budget/retrieve/") == 2


def test_budget_views_delete_current_budget(
    client, load_3_budgets, current_user_standard
):
    """Test view for deleting the current budget"""
    budget1, budget2, budget3 = load_3_budgets
    data = retrieve_budget(client, budget1)
    assert f'value="{budget1.name}"' in data
    assert f"<span>{budget1.name}</span>" in data
    form = {
        "budget_id": budget1.id,
        "budget_name": budget1.name,
        "budget_view_period": budget1.period,
        "budget_json": json.dumps(SMALL_INNER_BUDGET_1),
    }
    data = post_and_decode(client, f"/finance/budget/delete/{budget1.id}", form)
    assert f'value="{budget1.name}"' not in data
    assert f"<span>{budget1.name}</span>" not in data


def test_budget_views_delete_other_budget(
    client, load_3_budgets, current_user_standard
):
    """Test view for deleting a budget that is not the current budget"""
    budget1, budget2, budget3 = load_3_budgets
    data = retrieve_budget(client, budget2)
    assert f'value="{budget2.name}"' in data
    assert f"<span>{budget2.name}</span>" in data
    assert f"<span>{budget1.name}</span>" in data
    form = {
        "budget_id": budget2.id,
        "budget_name": budget2.name,
        "budget_view_period": budget2.period,
        "budget_json": json.dumps(SMALL_INNER_BUDGET_2),
    }
    data = post_and_decode(client, f"/finance/budget/delete/{budget1.id}", form)
    assert f'value="{budget2.name}"' in data
    assert f"<span>{budget2.name}</span>" in data
    assert f"<span>{budget1.name}</span>" not in data


def test_budget_views_post_share(client, load_3_budgets, current_user_standard):
    """Test view for sharing budget with POST"""
    budget1, budget2, budget3 = load_3_budgets
    data = retrieve_budget(client, budget1)
    form = {
        "budget_id": budget1.id,
        "budget_name": budget1.name,
        "budget_view_period": budget1.period,
        "budget_json": json.dumps(SMALL_INNER_BUDGET_1),
    }
    data = post_and_decode(client, f"/finance/budget/share/{budget1.id}", form)
    assert f"Budget name: {budget1.name}" in data


def test_budget_views_get_share(client, load_3_budgets, current_user_standard):
    """Test view for sharing budget with GET"""
    budget1, budget2, budget3 = load_3_budgets
    retrieve_budget(client, budget1)
    data = get_and_decode(client, f"/finance/budget/share/{budget1.id}")
    assert f"Budget name: {budget1.name}" in data
