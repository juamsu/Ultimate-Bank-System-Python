class BankError(Exception):
    """Base class for all the errors raised by this application."""


class InvalidAmountError(BankError):
    """The amount is not valid for the requested operation."""


class InvalidNameError(BankError):
    """The account holder's name is not valid."""


class InsufficientFundsError(BankError):
    """The account does not have enough balance for the withdrawal."""


class StorageError(BankError):
    """The accounts file could not be read, written or is corrupt."""