import os
import tempfile
import unittest

from account import BankAccount, validate_name
from errors import (InsufficientFundsError, InvalidAmountError,
                    InvalidNameError, StorageError)
from main import transaction
from repository import AccountRepository, FileAccountRepository


class InMemoryRepository(AccountRepository):
    """Fake storage: lets the logic be tested without touching the disk."""

    def __init__(self, fail=False):
        self.data = {}
        self.fail = fail

    def load(self, name):
        balance = self.data.get(name)
        return None if balance is None else BankAccount(name, balance)

    def save(self, account):
        if self.fail:
            raise StorageError("disk error")
        self.data[account.holder_name] = account.balance


class AccountTests(unittest.TestCase):
    def test_deposit_and_withdraw(self):
        account = BankAccount("Test", 100)
        account.deposit(50)
        account.withdraw(20)
        self.assertEqual(account.balance, 130)

    def test_withdraw_more_than_balance(self):
        with self.assertRaises(InsufficientFundsError):
            BankAccount("Test", 10).withdraw(50)

    def test_rejects_nan_inf_negative_and_zero(self):
        account = BankAccount("Test", 100)
        for bad in (float("nan"), float("inf"), -5, 0):
            with self.assertRaises(InvalidAmountError):
                account.deposit(bad)
            with self.assertRaises(InvalidAmountError):
                account.withdraw(bad)
        self.assertEqual(account.balance, 100)

    def test_rejects_invalid_names(self):
        for bad in ("", "   ", "Luis,5", "a\nb", "x" * 31):
            with self.assertRaises(InvalidNameError):
                validate_name(bad)

    def test_rejects_negative_initial_balance(self):
        with self.assertRaises(InvalidAmountError):
            BankAccount("Pedro", -500)


class TransactionTests(unittest.TestCase):
    def test_saves_and_updates_account(self):
        repo = InMemoryRepository()
        account = BankAccount("Test", 100)
        transaction(account, repo, BankAccount.deposit, 50)
        self.assertEqual(account.balance, 150)
        self.assertEqual(repo.data["Test"], 150)

    def test_balance_unchanged_if_saving_fails(self):
        repo = InMemoryRepository(fail=True)
        account = BankAccount("Test", 100)
        with self.assertRaises(StorageError):
            transaction(account, repo, BankAccount.withdraw, 30)
        self.assertEqual(account.balance, 100)


class FileRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "accounts.txt")
        self.repo = FileAccountRepository(self.path)

    def write(self, text):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(text)

    def test_save_and_load(self):
        self.repo.save(BankAccount("Test", 130))
        self.assertEqual(self.repo.load("Test").balance, 130)
        self.assertIsNone(self.repo.load("Nobody"))

    def test_blank_lines_are_ignored(self):
        self.write("Muawiya,12.0\n\n\n")
        self.assertEqual(self.repo.load("Muawiya").balance, 12)
        self.assertIsNone(self.repo.load("Nuevo"))

    def test_corrupt_file_raises_storage_error(self):
        self.write("esto-no-es-valido\n")
        with self.assertRaises(StorageError):
            self.repo.load("Test")


if __name__ == "__main__":
    unittest.main()