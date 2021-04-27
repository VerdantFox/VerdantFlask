"""conftest: pytest configuration file"""
import pytest
from bson.objectid import ObjectId

from src.routes.finance.models import Budget
from tests.conftest import STANDARD_USER, get_and_decode, post_and_decode

SIMPLE_INNER_BUDGET_STR = (
    '{"Income":{"Wages":{"value":500,"period":12,"pos":true}},'
    '"Expenses":{"Spending":{"value":300,"period":12,"pos":false}}}'
)
SIMPLE_BUDGET_FORM = {
    "budget_id": None,
    "budget_name": "My budget",
    "budget_view_period": 1,
    "budget_json": SIMPLE_INNER_BUDGET_STR,
}
SMALL_INNER_BUDGET_1 = {
    "category1": {"item1": {"value": 123, "period": 12, "pos": True}}
}
SMALL_INNER_BUDGET_2 = {
    "category2": {"item2": {"value": 345, "period": 1, "pos": False}}
}
SMALL_INNER_BUDGET_3 = {
    "category3": {"item3": {"value": 678, "period": 52, "pos": False}}
}
BUDGET_1 = {
    "author": STANDARD_USER["id"],
    "name": "Budget 1",
    "period": 12,
    "budget": SMALL_INNER_BUDGET_1,
}
BUDGET_2 = {
    "author": STANDARD_USER["id"],
    "name": "Budget 2",
    "period": 52,
    "budget": SMALL_INNER_BUDGET_2,
}
BUDGET_OTHER_USER = {
    "author": ObjectId(),
    "name": "Budget other",
    "period": 52,
    "budget": SMALL_INNER_BUDGET_3,
}


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------
@pytest.fixture
def budget1():
    """Load budget 1"""
    budget = Budget(**BUDGET_1)
    budget.save()

    yield budget

    budget = Budget.objects(id=budget.id)
    budget.delete()


@pytest.fixture
def budget2():
    """Load budget 2"""
    budget = Budget(**BUDGET_2)
    budget.save()

    yield budget

    budget = Budget.objects(id=budget.id)
    budget.delete()


@pytest.fixture
def budget_other():
    """Load budget 2"""
    budget = Budget(**BUDGET_OTHER_USER)
    budget.save()

    yield budget

    budget = Budget.objects(id=budget.id)
    budget.delete()


@pytest.fixture
def load_3_budgets(delete_budgets):
    """Loads 3 blogposts into database"""
    budget1 = Budget(**BUDGET_1)
    budget1.save()
    budget2 = Budget(**BUDGET_2)
    budget2.save()
    budget_other = Budget(**BUDGET_OTHER_USER)
    budget_other.save()

    yield budget1, budget2, budget_other


# --------------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------------
def retrieve_budget(client, budget, status_code=200):
    """Call retrieve_budget view on a budget"""
    form_data = {
        "budget_id": None,
        "budget_name": "",
        "budget_view_period": 12,
        "budget_json": "{}",
    }
    return post_and_decode(
        client,
        f"/finance/budget/retrieve/{budget.id}",
        form_data,
        status_code=status_code,
    )


def update_budget(client, form_data, status_code=200):
    """Call update_budget view on a budget"""
    return post_and_decode(
        client, "/finance/budget/update", form_data, status_code=status_code
    )


def get_budget(client, status_code=200):
    """Call get_budget"""
    return get_and_decode(client, "/finance/budget", status_code=status_code)
