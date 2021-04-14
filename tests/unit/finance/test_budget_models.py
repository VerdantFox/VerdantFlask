"""test_budget_models: test that the budget models behave as expected"""
import mongoengine
import pytest
from bson.objectid import ObjectId

from src.routes.finance.budget_helpers import DEFAULT_BUDGET
from src.routes.finance.models import Budget
from tests.mongodb_helpers import list_indexes

BUDGETS_COLLECTION = "budget"
BUDGET_MODEL_DEFAULTS = {
    # field: [default, indexed]
    "author": [None, True],
    "name": [None, True],
    "period": [12, False],
    "budget": [None, False],
}
GOOD_BUDGETS = [
    pytest.param(
        {
            "author": ObjectId(),
            "name": "Test Budget",
            "period": 12,
            "budget": DEFAULT_BUDGET,
        },
        id="everything",
    ),
    pytest.param(
        {"budget": {}},
        id="minimum",
    ),
]


@pytest.mark.parametrize("budget_dict", GOOD_BUDGETS)
def test_new_budget_good_succeeds(client, delete_budgets, budget_dict):
    """
    GIVEN a Budget model
    WHEN a new Budget is created
    THEN check the fields are created correctly
    """
    new_budget = Budget(**budget_dict)
    new_budget.save()
    new_budget = Budget.objects(id=new_budget.id).first()
    assert (
        str(new_budget)
        == f"Budget(id: {new_budget.id}, author: {new_budget.author}, name: {new_budget.name})"
    )
    for key in budget_dict:
        assert new_budget[key] == budget_dict[key]
    for key in BUDGET_MODEL_DEFAULTS:
        default_value = BUDGET_MODEL_DEFAULTS[key][0]
        if budget_dict.get(key) is None and default_value is not None:
            # Assert the default value was set properly
            assert new_budget[key] == default_value
    indexed_fields = {
        key
        for key, value in BUDGET_MODEL_DEFAULTS.items()
        if value[1] is True and budget_dict.get(key) is not None
    }
    indexs_found = set(list_indexes(BUDGETS_COLLECTION))
    assert indexed_fields.issubset(indexs_found)


BAD_BUDGETS = [
    pytest.param(
        {"name": "a" * 31},
        id="name_too_long",
    ),
    pytest.param(
        {"period": "bad_period"},
        id="period_not_int",
    ),
]


@pytest.mark.parametrize("budget_dict", BAD_BUDGETS)
def test_new_budget_bad_fails(client, delete_budgets, budget_dict):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check user fails when fields don't match model rules
    """
    new_user = Budget(**budget_dict)
    with pytest.raises(mongoengine.errors.ValidationError):
        new_user.save()
