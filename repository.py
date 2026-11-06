import os

from account import BankAccount
from errors import StorageError


class AccountRepository:
    """Stores the accounts in a text file, one 'name,balance' record per line."""

    def __init__(self, file_name="accounts.txt"):
        self.file_name = file_name

    def _read_all(self):
        """Return a dict {name: balance} with every record stored in the file."""
        accounts = {}
        if not os.path.exists(self.file_name):
            return accounts
        try:
            with open(self.file_name, "r", encoding="utf-8") as file:
                for number, line in enumerate(file, start=1):
                    line = line.strip()
                    if not line:
                        continue  # blank lines are ignored
                    try:
                        name, balance = line.split(",")
                        accounts[name] = float(balance)
                    except ValueError as error:
                        raise StorageError(
                            f"Corrupt record in {self.file_name}, line {number}: {line!r}"
                        ) from error
        except OSError as error:
            raise StorageError(f"Could not read {self.file_name}: {error}") from error
        return accounts

    def load(self, name):
        """Return the stored BankAccount for this name, or None if it does not exist."""
        balance = self._read_all().get(name)
        if balance is None:
            return None
        return BankAccount(name, balance)

    def save(self, account):
        """Write the account record in the file (atomic write)."""
        accounts = self._read_all()
        accounts[account.holder_name] = account.balance
        temp_file = self.file_name + ".tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as file:
                for name, balance in accounts.items():
                    file.write(f"{name},{balance}\n")
            os.replace(temp_file, self.file_name)
        except OSError as error:
            raise StorageError(f"Could not write {self.file_name}: {error}") from error