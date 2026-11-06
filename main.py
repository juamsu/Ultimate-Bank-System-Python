import os

class BankAccount:
    FILE_NAME = "accounts.txt"  # File to store account records

    def __init__(self, holder_name, balance=0, existing=False):
        """Initialize the bank account with the holder's name and balance."""
        self.holder_name = holder_name
        self.__balance = balance

        if not existing:
            print(f"\n✅ New Account for {self.holder_name} created successfully! 🏦")
        else:
            print(f"\n🔄 Welcome back, {self.holder_name}! Your account is loaded successfully.")

        self.display_balance()
        self.update_account_file()

    def deposit(self, amount):
        """Deposit money into the account and update the file."""
        if amount > 0:
            self.__balance += amount
            print(f"💰 Successfully deposited ${amount} | New Balance: ${self.__balance}")
            self.update_account_file()
        else:
            print("❌ Invalid deposit amount! Please enter a positive number.")

    def withdraw(self, amount):
        """Withdraw money if sufficient balance is available and update the file."""
        if amount > self.__balance:
            print("❌ Insufficient funds! Transaction failed.")
        elif amount <= 0:
            print("❌ Invalid withdrawal amount! Please enter a positive number.")
        else:
            self.__balance -= amount
            print(f"💸 Withdrawn: ${amount} | Remaining Balance: ${self.__balance}")
            self.update_account_file()

    def display_balance(self):
        """Show current account balance."""
        print(f"📊 Current Balance for {self.holder_name}: ${self.__balance}")

    def update_account_file(self):
        """Update the account record in the file."""
        accounts = {}

        # Read existing accounts
        if os.path.exists(self.FILE_NAME):
            with open(self.FILE_NAME, "r") as file:
                for line in file:
                    name, balance = line.strip().split(",")
                    accounts[name] = float(balance)

        # Update or create new account record
        accounts[self.holder_name] = self.__balance

        # Write back updated accounts
        with open(self.FILE_NAME, "w") as file:
            for name, balance in accounts.items():
                file.write(f"{name},{balance}\n")

    @classmethod
    def load_account(cls, name):
        """Check if the account exists in the file and load balance if found."""
        if os.path.exists(cls.FILE_NAME):
            with open(cls.FILE_NAME, "r") as file:
                for line in file:
                    stored_name, balance = line.strip().split(",")
                    if stored_name == name:
                        return cls(name, float(balance), existing=True)
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
    """Ask for the holder's name; load the account or create a new one."""
    name = input("👤 Enter Account Holder's Name: ")
    account = BankAccount.load_account(name)
    if account is None:
        initial_balance = float(input("💵 Enter Initial Balance (or 0): "))
        account = BankAccount(name, initial_balance)
    return account


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


def main():
    print("\n🌟 Welcome to the Ultimate Bank System! 🌟")
    account = open_account()
    run_menu(account)


if __name__ == "__main__":
    main()