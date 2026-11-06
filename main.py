import copy

from account import BankAccount, validate_name
from errors import BankError, InvalidAmountError, InvalidNameError
from repository import FileAccountRepository

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


def show_balance(account):
    print(f"📊 Current Balance for {account.holder_name}: ${account.balance}")


def transaction(account, repository, operation, amount):
    """Apply the operation to a copy, save it, and only then update the real account.

    This way, if the file cannot be written, the balance shown does not change.
    """
    updated = copy.copy(account)
    operation(updated, amount)
    repository.save(updated)
    operation(account, amount)


def handle_deposit(account, repository):
    amount = float(input("💰 Enter amount to deposit: "))
    transaction(account, repository, BankAccount.deposit, amount)
    print(f"💰 Successfully deposited ${amount} | New Balance: ${account.balance}")


def handle_withdraw(account, repository):
    amount = float(input("💸 Enter amount to withdraw: "))
    transaction(account, repository, BankAccount.withdraw, amount)
    print(f"💸 Withdrawn: ${amount} | Remaining Balance: ${account.balance}")


def handle_balance(account, repository):
    show_balance(account)


def open_account(repository):
    """Ask for the holder's name; load the account or create a new one.

    Invalid input is reported and the question is repeated.
    """
    while True:
        try:
            name = validate_name(input("👤 Enter Account Holder's Name: "))
            account = repository.load(name)
            if account is None:
                initial_balance = float(input("💵 Enter Initial Balance (or 0): "))
                account = BankAccount(name, initial_balance)
                repository.save(account)
                print(f"\n✅ New Account for {account.holder_name} created successfully! 🏦")
            else:
                print(f"\n🔄 Welcome back, {account.holder_name}! Your account is loaded successfully.")
            show_balance(account)
            return account
        except ValueError:
            print("⚠️ Error: Please enter a valid number.")
        except (InvalidNameError, InvalidAmountError) as error:
            print(f"❌ {error}")


def run_menu(account, repository):
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
                action(account, repository)
        except ValueError:
            print("⚠️ Error: Please enter a valid number.")
        except BankError as error:
            print(f"❌ {error}")


def main():
    print("\n🌟 Welcome to the Ultimate Bank System! 🌟")
    repository = FileAccountRepository()
    try:
        account = open_account(repository)
        run_menu(account, repository)
    except BankError as error:
        print(f"❌ {error}")


if __name__ == "__main__":
    main()