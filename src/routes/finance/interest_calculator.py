"""interest_calculator: class for calculating compound interest information"""
from .forms import InterestForm, convert_and_populate_form
from .helpers import Calculator


class InterestCalculator(Calculator):
    """Class for performing interst calculation functions"""

    def __init__(self, form):
        self.form = form

        # Form attributes

        # Attributes calculated from form attributes

        # To be calculated from functions

    def calculate(self):
        """Make all calculations"""

    pass


def fill_form_from_request():
    """Fills interest form from request args"""
    conversions = {
        "initial": float,
        "nbr_of_years": int,
        "apy": float,
        "compounding_period": int,
        "apy_variance": float,
        "contributions": str,
        "monthly": float,
        "yearly": float,
    }
    return convert_and_populate_form(InterestForm, conversions)
