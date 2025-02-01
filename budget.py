#Goals: Create a budget tracker that allows users to input/remove expenses and view them in a list.
#       The user should be able to view the total amount of expenses and the total amount of expenses for a specific use.
#       The user should be able to view the total amount of expenses for a specific day, week, month, or year.
#       The user should be able to classify the view by uses, i.e personal food vs joint food expenses.
# define, add, remove, view, total for the expenses. Should be able to view by day, week, month, year, use (joint/ personal) and category.
# Maybe add a budget feature that allows the user to set a budget for a specific use and category.
# add a main function that allows the user to interact with the budget tracker.
# find a way to save the expenses to a file so that the user can view them later and not lose them when the program is closed.

PERSONAL_USE = "Personal"
JOINT_USE = "Joint"

class Expense:
    def __init__(self, date, description, amount, use, category):
        self.date = date
        self.description = description
        self.amount = amount
        self.use = use
        self.category = category   

class BudgetTracker:
    def __init__(self):
        self.expenses = []
    
    def add_expense(self, expense):
        self.expenses.append(expense)

    def remove_expense(self, index):
        if 0 <= index < len(self.expenses):
            del self.expenses[index]
            print("Expense removed.")
        else:
            print("Failed to remove expense, invalid expense index.")

    def view_expenses(self):
        if len(self.expenses) == 0:
            print("No expenses found.")
        else:
            print("Expenses list:")
            for index, expense in enumerate(self.expenses, start=1):
                print(f"{index}. Date: {expense.date}, Description: {expense.description}, Amount: {expense.amount}, Use: {expense.use}, Category: {expense.category}")
           
    def total_expenses(self) -> float:
        total = sum(expense.amount for expense in self.expenses)
        return total
    
    def total_expenses_by_use(self, use) -> float:
        total = sum(expense.amount for expense in self.expenses if expense.use.lower() == use.lower())
        return total

    def total_expenses_by_uses(self) -> dict:
        totals = {
            PERSONAL_USE: self.total_expenses_by_use(PERSONAL_USE),
            JOINT_USE: self.total_expenses_by_use(JOINT_USE)
        }
        return totals
    
def main():
    tracker = BudgetTracker()

    while True:
        print("\nBudget Tracker Menu:")
        print("1. Add Expense")
        print("2. Remove Expense")
        print("3. View Expenses")
        print("4. View Total Expenses")
        print("5. View Total Expenses by Use")
        print("6. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            date = input("Enter date (YYYY-MM-DD): ")
            description = input("Enter description: ")
            amount = float(input("Enter amount: "))
            use = input(f"Enter use ({PERSONAL_USE}/{JOINT_USE}): ").lower()
            category = input("Enter category: ")
            expense = Expense(date, description, amount, use, category)
            tracker.add_expense(expense)
            print("Expense succesfully added.")

        elif choice == "2":
            tracker.view_expenses()
            index = int(input("Enter expense index number to remove: ")) - 1
            tracker.remove_expense(index)

        elif choice == "3":
            tracker.view_expenses()

        elif choice == "4":
            total = tracker.total_expenses()
            print(f"Total expenses: {total}")

        elif choice == "5":
            totals = tracker.total_expenses_by_uses()
            print(f"Total expenses by use:")
            print(f"{PERSONAL_USE}: {totals[PERSONAL_USE]}")
            print(f"{JOINT_USE}: {totals[JOINT_USE]}")

        elif choice == "6":
            print("Exiting Budget Tracker.")
            break

        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()

            


