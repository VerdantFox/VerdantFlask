"""conftest: pytest configuration file"""
import pytest
from bson.objectid import ObjectId

# from src.routes.finance.budget_helpers import DEFAULT_BUDGET
from src.routes.finance.models import Budget
from tests.conftest import STANDARD_USER

AUTHOR = ""
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


@pytest.fixture(scope="module")
def load_3_budgets_mod(client_module):
    """Loads 3 blogposts into database"""
    budget1 = Budget(**BUDGET_1)
    budget1.save()
    budget2 = Budget(**BUDGET_2)
    budget2.save()
    budget_other = Budget(**BUDGET_OTHER_USER)
    budget_other.save()

    yield budget1, budget2, budget_other

    budget1 = Budget.objects(id=budget1.id)
    budget1.delete()
    budget2 = Budget.objects(id=budget2.id)
    budget2.delete()
    budget_other = Budget.objects(id=budget_other.id)
    budget_other.delete()
