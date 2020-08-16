"""Tests for src/utils methods"""
import math

import pytest

from src.globals import db
from src.utils import get_slug, list_from_string, setup_pagination
from tests.mongodb_helpers import delete_all_docs

TEST_STRINGS = [
    pytest.param("hello world", "hello-world", id="standard"),
    pytest.param("My wEiRD cAPS", "my-weird-caps", id="rem_caps"),
    pytest.param(
        "  fix  weird\n whitespace", "fix-weird-whitespace", id="fix_whitespace"
    ),
    pytest.param(
        "Bad chars )(*&^%$#@!`~?/.,<> go bye-bye",
        "bad-chars-go-bye-bye",
        id="rem_badchars",
    ),
]


@pytest.mark.parametrize("before, after", TEST_STRINGS)
def test_getslug(before, after):
    """
    GIVEN a string
    THEN string should turn into a slug
    """
    assert get_slug(before) == after


TEST_STRINGS = [
    pytest.param(
        "standard,list,of,items",
        ["standard", "list", "of", "items"],
        False,
        id="standard",
    ),
    pytest.param(
        "[with, brackets, and, spaces]",
        ["with", "brackets", "and", "spaces"],
        None,
        id="with_brackets_and_spaces",
    ),
    pytest.param("(and, with, tuples)", ["and", "with", "tuples"], None, id="tuples",),
    pytest.param(
        '["double", "quoted", "list"]',
        ["double", "quoted", "list"],
        None,
        id="double_quoted",
    ),
    pytest.param(
        "['single', 'quoted', 'list']",
        ["single", "quoted", "list"],
        None,
        id="single_quoted",
    ),
    pytest.param("Keep,UpPeR,CASE", ["Keep", "UpPeR", "CASE"], None, id="keep_casing",),
    pytest.param(
        "Remove,UpPeR,CASE", ["remove", "upper", "case"], True, id="remove_upper_case",
    ),
]


@pytest.mark.parametrize("before, after, lowercase", TEST_STRINGS)
def test_list_from_string(before, after, lowercase):
    """
    GIVEN a list like string
    THEN string should become a list mimicking that string
    """
    if lowercase is None:
        assert list_from_string(before) == after
    else:
        assert list_from_string(before, lowercase) == after


PAGINATOR_SETUP = [
    (1, 10),
    (1, 25),
    (0, 10),
    (3, 10),
    (2, 5),
    (3, 2),
]


@pytest.mark.parametrize("page, results_per_page", PAGINATOR_SETUP)
def test_setup_pagination(set_up_models, page, results_per_page):
    """
    GIVEN page, results_per_page and mongo_query
    THEN return a valid paginator object at correct page
    """
    objects = SimpleModel.objects()
    paginator = setup_pagination(page, results_per_page, objects)
    actual_results_per_page = results_per_page if results_per_page < 20 else 20
    max_pages = math.ceil(20 / actual_results_per_page)
    assert paginator.total == 20
    assert paginator.pages == max_pages
    if page <= 1:
        assert paginator.page == 1
        assert paginator.has_prev is False
        assert len(paginator.items) == actual_results_per_page
    elif page >= max_pages:
        assert paginator.page == max_pages
        assert paginator.has_next is False
        assert len(paginator.items) <= actual_results_per_page
    else:
        assert paginator.page == page
        assert paginator.has_prev is True
        assert paginator.has_next is True
        assert len(paginator.items) == actual_results_per_page


@pytest.fixture
def set_up_models(client):
    """Build some models for testing paginator"""
    models = []
    for i in range(20):
        model = SimpleModel(field=str(i),)
        model.save()
        models.append(model)
    yield models
    delete_all_docs("simplemodels")


class SimpleModel(db.Document):
    """Simple mongodb model for testing paginator"""

    field = db.StringField(index=False)
    meta = {"collection": "simplemodels"}

    def __str__(self):
        return f"SimpleModel(field: {self.field})"
