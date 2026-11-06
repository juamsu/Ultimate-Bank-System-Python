import math

from errors import InsufficientFundsError, InvalidAmountError, InvalidNameError

MAX_NAME_LENGTH = 30


def validate_name(name):
    """Return the cleaned name or raise InvalidNameError.

    Commas and line breaks are rejected because they are the separators of
    the accounts file and would corrupt it.
    """
    name = name.strip()
    if not name:
        raise InvalidNameError("The name cannot be empty.")
    if len(name) > MAX_NAME_LENGTH:
        raise InvalidNameError(f"The name cannot be longer than {MAX_NAME_LENGTH} characters.")
    if "," in name or "\n" in name or "\r" in name:
        raise InvalidNameError("The name cannot contain commas or line breaks.")
    return name


def validate_amount(amount, allow_zero=False):
    """Raise InvalidAmountError if the amount is not a usable money value."""
    if not math.isfinite(amount):
        raise InvalidAmountError("Invalid amount! It must be a finite number.")
    if amount < 0:
        raise InvalidAmountError("Invalid amount! Negative values are not allowed.")
    if amount == 0 and not allow_zero:
        raise InvalidAmountError("Invalid amount! It must be greater than zero.")


class BankAccount:
    """Business rules of an account. It does not print or touch any file."""

    def __init__(self, holder_name, balance=0):
        validate_amount(balance, allow_zero=True)
        self.holder_name = validate_name(holder_name)
        self.__balance = balance

    @property
    def balance(self):
        return self.__balance

    def deposit(self, amount):
        validate_amount(amount)
        self.__balance += amount

    def withdraw(self, amount):
        validate_amount(amount)
        if amount > self.__balance:
            raise InsufficientFundsError("Insufficient funds! Transaction failed.")
        self.__balance -= amount