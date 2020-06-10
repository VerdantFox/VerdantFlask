"""Tests for root/utils methods"""
from root.utils import get_slug, list_from_string


def test_getslug():
    """
    GIVEN a string
    THEN string should turn into a slug
    """
    test_strings = {
        "hello world": "hello-world",
        "My  sUpeR Cool   blog pOsT": "my-super-cool-blog-post",
        "Even fix\nnew lines": "even-fix-new-lines",
        "Bad chars )(*&^%$#@!`~?/.,<> go bye-bye": "bad-chars-go-bye-bye",
    }
    for before, after in test_strings.items():
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


def test_setup_pagination():
    """
    GIVEN page, results_per_page and mongo_query
    THEN return a valid paginator object at correct page
    """
    pass  # TODO implement test (might require mocking mongo_query)
