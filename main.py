import math
import os

MAX_NAME_LENGTH = 30


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
    FILE_NAME = "accounts.txt"  # File to store account records

    def __init__(self, holder_name, balance=0):
        """Initialize the bank account with the holder's name and balance."""
        validate_amount(balance, allow_zero=True)
        self.holder_name = validate_name(holder_name)
        self.__balance = balance

    def deposit(self, amount):
        """Deposit money into the account and update the file."""
        validate_amount(amount)
        self._save_balance(self.__balance + amount)
        print(f"💰 Successfully deposited ${amount} | New Balance: ${self.__balance}")

    def withdraw(self, amount):
        """Withdraw money if sufficient balance is available and update the file."""
        validate_amount(amount)
        if amount > self.__balance:
            raise InsufficientFundsError("Insufficient funds! Transaction failed.")
        self._save_balance(self.__balance - amount)
        print(f"💸 Withdrawn: ${amount} | Remaining Balance: ${self.__balance}")

    def display_balance(self):
        """Show current account balance."""
        print(f"📊 Current Balance for {self.holder_name}: ${self.__balance}")

    def _save_balance(self, new_balance):
        """Change the balance and persist it; undo the change if saving fails."""
        previous = self.__balance
        self.__balance = new_balance
        try:
            self.update_account_file()
        except StorageError:
            self.__balance = previous
            raise

    @classmethod
    def _read_accounts(cls):
        """Return a dict {name: balance} with every record stored in the file."""
        accounts = {}
        if not os.path.exists(cls.FILE_NAME):
            return accounts
        try:
            with open(cls.FILE_NAME, "r", encoding="utf-8") as file:
                for number, line in enumerate(file, start=1):
                    line = line.strip()
                    if not line:
                        continue  # blank lines are ignored
                    try:
                        name, balance = line.split(",")
                        accounts[name] = float(balance)
                    except ValueError as error:
                        raise StorageError(
                            f"Corrupt record in {cls.FILE_NAME}, line {number}: {line!r}"
                        ) from error
        except OSError as error:
            raise StorageError(f"Could not read {cls.FILE_NAME}: {error}") from error
        return accounts

    def update_account_file(self):
        """Update the account record in the file (atomic write)."""
        accounts = self._read_accounts()
        accounts[self.holder_name] = self.__balance

        temp_file = self.FILE_NAME + ".tmp"
        try:
            with open(temp_file, "w", encoding="utf-8") as file:
                for name, balance in accounts.items():
                    file.write(f"{name},{balance}\n")
            os.replace(temp_file, self.FILE_NAME)
        except OSError as error:
            raise StorageError(f"Could not write {self.FILE_NAME}: {error}") from error

    @classmethod
    def load_account(cls, name):
        """Return the stored account for this name, or None if it does not exist."""
        accounts = cls._read_accounts()
        if name in accounts:
            return cls(name, accounts[name])
        return None


# --- Menu options ---
OPTION_DEPOSIT = 1
OPTION_WITHDRAW = 2
OPTION_BALANCE = 3
OPTION_EXIT = 4


def show_menu():
    print("\n📌 MAIN MENU")
    print("1️⃣ Deposit")
    print("2️⃣ Withdraw")
    print("3️⃣ Check Balance")
    print("4️⃣ Exit")


def handle_deposit(account):
    amount = float(input("💰 Enter amount to deposit: "))
    account.deposit(amount)


def handle_withdraw(account):
    amount = float(input("💸 Enter amount to withdraw: "))
    account.withdraw(amount)


def handle_balance(account):
    account.display_balance()


def open_account():
    """Ask for the holder's name; load the account or create a new one.

    Invalid input is reported and the question is repeated.
    """
    while True:
        try:
            name = validate_name(input("👤 Enter Account Holder's Name: "))
            account = BankAccount.load_account(name)
            if account is None:
                initial_balance = float(input("💵 Enter Initial Balance (or 0): "))
                account = BankAccount(name, initial_balance)
                account.update_account_file()
                print(f"\n✅ New Account for {account.holder_name} created successfully! 🏦")
            else:
                print(f"\n🔄 Welcome back, {account.holder_name}! Your account is loaded successfully.")
            account.display_balance()
            return account
        except ValueError:
            print("⚠️ Error: Please enter a valid number.")
        except (InvalidNameError, InvalidAmountError) as error:
            print(f"❌ {error}")


def run_menu(account):
    """Menu loop: each option is mapped to its handler function."""
    actions = {
        OPTION_DEPOSIT: handle_deposit,
        OPTION_WITHDRAW: handle_withdraw,
        OPTION_BALANCE: handle_balance,
    }
    while True:
        show_menu()
        try:
            choice = int(input("👉 Enter your choice: "))
            if choice == OPTION_EXIT:
                print("\n👋 Thank you for using Ultimate Bank System! See you again!")
                break
            action = actions.get(choice)
            if action is None:
                print("⚠️ Invalid choice! Please enter a number between 1 and 4.")
            else:
                action(account)
        except ValueError:
            print("⚠️ Error: Please enter a valid number.")
        except BankError as error:
            print(f"❌ {error}")


def main():
    print("\n🌟 Welcome to the Ultimate Bank System! 🌟")
    try:
        account = open_account()
        run_menu(account)
    except BankError as error:
        print(f"❌ {error}")


if __name__ == "__main__":
    main()