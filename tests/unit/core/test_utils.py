"""Tests for root/utils methods"""
import pytest

from root.utils import get_slug, list_from_string

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


def test_list_from_string():
    """
    GIVEN a list like string
    THEN string should become a list mimicking that string
    """
    test_strings = {
        "standard,list,of,items": ["standard", "list", "of", "items"],
        "[with, brackets, and, spaces]": ["with", "brackets", "and", "spaces"],
        "(and, with, tuples)": ["and", "with", "tuples"],
        '["double", "quoted", "list"]': ["double", "quoted", "list"],
        "['single', 'quoted', 'list']": ["single", "quoted", "list"],
        "Keep,UpPeR,CASE": ["Keep", "UpPeR", "CASE"],
    }
    for before, after in test_strings.items():
        assert list_from_string(before) == after
    assert list_from_string("Remove,UpPeR,CASE", True) == ["remove", "upper", "case"]


@pytest.mark.skip
def test_setup_pagination():
    """
    GIVEN page, results_per_page and mongo_query
    THEN return a valid paginator object at correct page
    """
    pass  # TODO implement test (might require mocking mongo_query)
