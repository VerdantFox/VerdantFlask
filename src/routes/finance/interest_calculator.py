"""interest_calculator: class for calculating compound interest information"""
from math import log

from .forms import InterestForm, convert_and_populate_form
from .helpers import Calculator


class InterestCalculator(Calculator):
    """Class for performing interst calculation functions"""

    def __init__(self, form):
        self.form = form
        # Form attributes
        self.initial = form.initial.data
        self.nbr_of_years = form.nbr_of_years.data
        self.apy = form.apy.data
        self.compounding_period = int(form.compounding_period.data)
        self.apy_variance = form.apy_variance.data
        self.contributions = form.contributions.data
        self.monthly_contrib = form.monthly_contrib.data
        self.yearly_contrib = form.yearly_contrib.data

        # Attributes calculated from form attributes
        if self.contributions == "Withdrawls":
            self.monthly_contrib *= -1
            self.yearly_contrib *= -1
        self.low_apy = max(self.apy - self.apy_variance, 0)
        self.high_apy = self.apy + self.apy_variance
        self.apy_decimal = self.apy / 100
        self.low_apy_decimal = self.low_apy / 100
        self.high_apy_decimal = self.high_apy / 100
        self.compoundings_per_month = self.compounding_period / 12
        self.month_time = 1 / 12
        self.exponent = self.compoundings_per_month * self.month_time
        self.adder = self.apy_decimal / self.compoundings_per_month
        self.low_adder = self.low_apy_decimal / self.compoundings_per_month
        self.high_adder = self.high_apy_decimal / self.compoundings_per_month

        # To be calculated from functions
        self.total_balance = self.initial
        self.total_balance_low = self.initial
        self.total_balance_high = self.initial
        self.total_deposits = 0
        self.total_interest = 0
        self.doubling_period = 0  # in years
        self.breakdown = [
            {
                "year": 0,
                "balance": self.initial,
                "low balance": self.initial,
                "high balance": self.initial,
                "deposits": 0,
                "interest": 0,
                "total deposits": 0,
                "total interest": 0,
            }
        ]
        self.graph_html = "<h2>Unable to calculate graphs</h2>"

    def calculate(self):
        """Make all calculations

        Compounding formula: A = P(1+r/n)^(nt)

        A = Accrued amount (principal + interest)
        P = Principal amount
        r = Annual nominal interest rate as a decimal
        n = Number of compounding periods per year
        t = time in decimal years; e.g., 6 months is calculated as 0.5 years
        """
        for year in range(1, self.nbr_of_years + 1):
            self.calc_year(year)
        for item in (
            self.total_balance,
            self.total_balance_low,
            self.total_balance_high,
            self.total_deposits,
            self.total_interest,
        ):
            item = self.round_money(item, False)
        self.calc_doubling_period()

    def calc_doubling_period(self):
        """Calculate the standard doubling period of the given interest rate

        Doubling formula: t = (ln(2)/ln(1+(r/n)))/n

        t = Doubling time in decimal years; e.g., 6 months is calculated as 0.5 years
        r = Annual nominal interest rate as a decimal
        n = Number of compounding periods per year
        """
        self.doubling_period = (
            log(2) / log(1 + (self.apy_decimal / self.compounding_period))
        ) / self.compounding_period

    def calc_month(self, annual_breakdown):
        """Calculate one month interest"""
        balance = annual_breakdown["balance"] + self.monthly_contrib
        accrued = balance * (1 + self.adder) ** (self.exponent)
        low_balance = annual_breakdown["low balance"] + self.monthly_contrib
        low_accrued = low_balance * (1 + self.low_adder) ** self.exponent
        high_balance = annual_breakdown["high balance"] + self.monthly_contrib
        high_accrued = high_balance * (1 + self.high_adder) ** self.exponent

        annual_breakdown["deposits"] += self.monthly_contrib
        annual_breakdown["interest"] += accrued - balance
        annual_breakdown["balance"] = accrued
        annual_breakdown["low balance"] = low_accrued
        annual_breakdown["high balance"] = high_accrued

    def calc_year(self, year):
        """Calculate one year"""
        annual_breakdown = {
            "year": year,
            "balance": self.total_balance,
            "low balance": self.total_balance_low,
            "high balance": self.total_balance_high,
            "deposits": self.yearly_contrib,
            "interest": 0,
            "total deposits": self.total_deposits,
            "total interest": self.total_interest,
        }
        for _ in range(12):
            self.calc_month(annual_breakdown)

        annual_breakdown["total deposits"] += annual_breakdown["deposits"]
        annual_breakdown["total interest"] += annual_breakdown["interest"]

        self.total_balance = annual_breakdown["balance"]
        self.total_balance_low = annual_breakdown["low balance"]
        self.total_balance_high = annual_breakdown["high balance"]
        self.total_deposits = annual_breakdown["total deposits"]
        self.total_interest = annual_breakdown["total interest"]

        for key, val in annual_breakdown.items():
            if key == "year":
                continue
            annual_breakdown[key] = self.round_money(val, False)
        self.breakdown.append(annual_breakdown)


def fill_form_from_request():
    """Fills interest form from request args"""
    conversions = {
        "initial": int,
        "nbr_of_years": int,
        "apy": float,
        "compounding_period": int,
        "apy_variance": float,
        "contributions": str,
        "monthly_contrib": int,
        "yearly_contrib": int,
    }
    return convert_and_populate_form(InterestForm, conversions)
