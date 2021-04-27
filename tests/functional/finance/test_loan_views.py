"""test_loan_views: test loan related views"""
from tests.conftest import get_and_decode


def test_loan_views_default(client):
    """Test default GET of the loan page"""
    data = get_and_decode(client, "/finance/loan")
    assert "<h1>Loan Calculator</h1>" in data
    assert "$5,594" in data
    assert data.count("bk-root", 4)


def test_loan_views_filled(client):
    """Test default GET of the loan page"""
    query_string = {
        "principal": "100000",
        "interest_rate": "7.0",
        "period": "225",
        "period_type": "1",
        "extra_monthly": "100.0",
        "extra_yearly": "500.0",
        "extra_yearly_month": "10",
        "start_date": "2021-04-15",
    }
    data = get_and_decode(client, "/finance/loan", query_string)
    assert "<h1>Loan Calculator</h1>" in data
    assert "$799.28" in data
    assert "$899.28" in data
    assert "February 15, 2035" in data
    assert data.count("bk-root", 4)
