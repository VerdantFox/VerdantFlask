"""loan_helpers: helper functions for loans view"""
import math

from dateutil.relativedelta import relativedelta

from .forms import LoanForm, convert_and_populate_form, convert_dt
from .loan_charts import produce_loan_graphs


class LoanCalculator:
    """Class for performing loan calculation functions"""

    def __init__(self, form):
        self.form = form

        # Form attributes
        self.principal = self.round_money(form.principal.data, False)
        self.interest_rate = form.interest_rate.data
        self.period = form.period.data
        self.period_type = int(form.period_type.data)
        self.extra_monthly = self.round_money(form.extra_monthly.data)
        self.extra_yearly = self.round_money(form.extra_yearly.data)
        self.extra_yearly_month = form.extra_yearly_month.data
        self.start_date = form.start_date.data

        # Attributes calculated from form attributes
        self.start_month = self.start_date.month
        self.nbr_of_payments = self.period * self.period_type
        self.interest_per_year = self.interest_rate / 100
        self.interest_per_month = self.interest_per_year / 12
        self.start_month = self.start_date.month

        # To be calculated from functions
        self.min_payment = 0
        self.payment_with_extra = 0
        self.total_interest = 0
        self.total_cost = 0
        self.payoff_date = None
        self.amortization_schedule = []
        self.graph_html = "<h2>Unable to calculate graphs</h2>"
        self.prev_year = None
        self.year_index = -1
        self.years = []
        self.principal_per_year = []
        self.interest_per_year = []
        self.payment_per_year = []

    def calculate(self):
        """Make all calculations"""
        self.calculate_minimum_payment()
        self.calculate_payment_with_extra()
        self.calculate_amortization_schedule()
        self.graphs_html = produce_loan_graphs(self)

    def str_money(self, amount, cents=True):
        """String format's money"""
        money = self.round_money(amount, cents)
        if cents:
            return f"${money:,.2f}"
        else:
            return f"${money:,.0f}"

    @staticmethod
    def round_money(amount, cents=True):
        """Ceiling money, with cents if cents=True"""
        if cents:
            return math.ceil(amount * 100) / 100
        else:
            return math.ceil(amount)

    def calculate_minimum_payment(self):
        """Calculate minimum payment from form input

        Formula A = P * (r(1+r)**n) / ((1+r)**n - 1)
        where:
        - A = monthly payment
        - P = Initial principal interest (loan amount)
        - r = interest rate per period
        - n = total number of payments or periods
        """
        rate_period = (1 + self.interest_per_month) ** self.nbr_of_payments
        minimum_payment = (
            self.principal * (self.interest_per_month * rate_period) / (rate_period - 1)
        )
        self.min_payment = self.round_money(minimum_payment)

    def calculate_payment_with_extra(self):
        """Calculate the payment_with_extra"""
        self.payment_with_extra = self.round_money(
            self.min_payment + self.extra_monthly
        )

    def calculate_amortization_schedule(self):
        """Calculate the amortization schedule"""
        remaining_principal = self.principal
        current_date = self.start_date - relativedelta(months=1)
        # (payment_date, payment, principal, interest, total_interest, remaining_principal)
        while remaining_principal > 0:
            current_date += relativedelta(months=1)
            current_month = current_date.month
            current_year = str(current_date.year)
            if current_year != self.prev_year:
                self.prev_year = current_year
                self.year_index += 1
                self.years.append(current_year)
                self.principal_per_year.append(0)
                self.interest_per_year.append(0)
                self.payment_per_year.append(0)
            month_interest = self.round_money(
                remaining_principal * self.interest_per_month
            )
            self.total_interest += month_interest
            month_payment = self.payment_with_extra
            if int(current_month) == int(self.extra_yearly_month):
                month_payment = self.round_money(month_payment + self.extra_yearly)
            month_payment = self.round_money(month_payment)
            month_principal = self.round_money(month_payment - month_interest)
            if month_principal <= 0:  # pragma: no cover
                raise RuntimeError("Improper minimum payment, principal not shrinking.")
            remaining_principal -= month_principal
            if remaining_principal <= 0:
                month_payment += remaining_principal
                month_principal += remaining_principal
                remaining_principal = 0
                self.payoff_date = current_date.strftime("%B %d, %Y")
                self.total_interest = self.round_money(self.total_interest)
            self.total_cost += month_payment
            self.principal_per_year[self.year_index] += month_principal
            self.interest_per_year[self.year_index] += month_interest
            self.payment_per_year[self.year_index] += month_payment
            amortization_tuple_str = (
                current_date,
                self.round_money(month_payment),
                self.round_money(month_principal),
                self.round_money(month_interest),
                self.round_money(self.total_interest),
                self.round_money(remaining_principal),
            )
            self.amortization_schedule.append(amortization_tuple_str)
        self.principal_per_year = [
            self.round_money(val) for val in self.principal_per_year
        ]
        self.interest_per_year = [
            self.round_money(val) for val in self.interest_per_year
        ]
        self.payment_per_year = [self.round_money(val) for val in self.payment_per_year]


def fill_loan_form_from_request():
    """Fills loan form from request args"""
    conversions = {
        "principal": int,
        "interest_rate": float,
        "period": int,
        "period_type": int,
        "extra_monthly": float,
        "extra_yearly": float,
        "extra_yearly_month": int,
        "start_date": convert_dt,
    }
    return convert_and_populate_form(LoanForm, conversions)
