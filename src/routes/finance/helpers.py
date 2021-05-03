"""helpers: Helper functions and classes for finance modules"""
import math


class Calculator:
    """Calculator base class"""

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
