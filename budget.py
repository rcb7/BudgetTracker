#Goals: Create a budget tracker that allows users to input/remove expenses and view them in a list.

import json
import os

#Classes of expense use
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

    def edit_expense(self, index, date, description, amount, use, category):
        if 0 <= index < len(self.expenses):
            self.expenses[index].date = date
            self.expenses[index].description = description
            self.expenses[index].amount = amount
            self.expenses[index].use = use
            self.expenses[index].category = category
            print("Expense edited.")
        else:
            print("Failed to edit expense, invalid expense index.")
           
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
    
    def set_budget(self, amount):
        self.budget = amount
        print(f"Budget set to {amount}.")

    def check_budget(self):
        if self.budget is not None:
            total = self.total_expenses()
            print(f"Checking budget...")
            print(f"Remaining budget: {self.budget - total}")
            if total > self.budget:
                print(f"Budget exceeded. Total expenses: {total}, Budget: {self.budget}")
            else:
                print(f"Budget not exceeded. Total expenses: {total}, Budget: {self.budget}")
        else:
            print("Budget not set")

    def save_budget(self, filename="budget.json"):
        try:
            with open(filename, "w") as file:
                json.dump(self.budget, file)
            print("Budget saved to file.")
        except Exception as e:
            print(f"Failed to save budget to file: {e}")
    
    def load_budget(self, filename="budget.json"):
        try:
            with open(filename, "r") as file:
                self.budget = json.load(file)
            print("Budget loaded from file.")
        except FileNotFoundError:
            print("No saved budget found.")
        except Exception as e:
            print(f"Failed to load budget from file: {e}")
    
    def save_expenses(self, filename="expenses.json"):
        try:
            with open(filename, "w") as file:
                json.dump([expense.__dict__ for expense in self.expenses], file)
            print("Expenses saved to file.")
        except Exception as e:
            print(f"Failed to save expenses to file: {e}")
            
    def load_expenses(self, filename="expenses.json"):
        try:
            with open(filename, "r") as file:
                expenses_data = json.load(file)
                self.expenses = [Expense(expense["date"], expense["description"], expense["amount"], expense["use"], expense["category"]) for expense in expenses_data]
            print("Expenses loaded from file.")
        except FileNotFoundError:
            print("No saved expenses found.")
        except Exception as e:
            print(f"Failed to load expenses from file: {e}")
        

def main():
    tracker = BudgetTracker()
    
    print("Loading saved expenses...")
    tracker.load_expenses()
    print("Loading saved budget...")
    tracker.load_budget()

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("\nBudget Tracker")
        print("Select a menu")
        print("1. Budget")
        print("2. Expenses")
        print("3. Totals")      
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            print("\nBudget Menu")
            print("Select an option:")
            print("1. Set budget")
            print("2. Check budget")
            print("3. Exit")

            choice = input("Enter choice: ")

            if choice == "1":
                amount = float(input("Enter budget amount: "))
                tracker.set_budget(amount) 

            elif choice == "2":
                tracker.check_budget()   

            elif choice == "3":
                print("Exiting Budget Menu.")
                continue
        
        elif choice == "2":
            print("\nExpenses Menu")
            print("Select an option:")
            print("1. Add expense")
            print("2. Remove expense")
            print("3. Edit expense")
            print("4. View expenses")
            print("5. Exit")

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
                if len(tracker.expenses) == 0:
                    continue
                elif len(tracker.expenses) > 0:
                    index = int(input("Enter expense index number to edit: ")) - 1
                    date = input("Enter date (YYYY-MM-DD): ")
                    description = input("Enter description: ")
                    amount = float(input("Enter amount: "))
                    use = input(f"Enter use ({PERSONAL_USE}/{JOINT_USE}): ").lower()
                    category = input("Enter category: ")
                    tracker.edit_expense(index, date, description, amount, use, category)

            elif choice == "4":
                tracker.view_expenses()

            elif choice == "5":
                print("Exiting Expenses Menu.")
                continue
        
        elif choice == "3":
            print("\nTotals Menu")
            print("Select an option:")
            print("1. Total expenses")
            print("2. Total expenses by use")
            print("3. Exit")

            choice = input("Enter choice: ")

            if choice == "1":
                total = tracker.total_expenses()
                print(f"Total expenses: {total}")

            elif choice == "2":
                totals = tracker.total_expenses_by_uses()
                print(f"Total expenses by use:")
                print(f"{PERSONAL_USE}: {totals[PERSONAL_USE]}")
                print(f"{JOINT_USE}: {totals[JOINT_USE]}")

            elif choice == "3":
                print("Exiting Totals Menu.")
                continue

        elif choice == "4":
            print("Saving expenses...")
            tracker.save_expenses()
            print("Saving budget...")
            tracker.save_budget()
            print("Exiting Budget Tracker.")
            break

        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()