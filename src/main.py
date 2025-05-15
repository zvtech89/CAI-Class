import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import datetime
from database import Database
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Manager")
        self.root.geometry("800x600")
        self.db = Database()
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create tabs
        self.transactions_frame = ttk.Frame(self.notebook)
        self.budget_frame = ttk.Frame(self.notebook)
        self.reports_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.transactions_frame, text='Transactions')
        self.notebook.add(self.budget_frame, text='Budget')
        self.notebook.add(self.reports_frame, text='Reports')
        
        self.setup_transactions_tab()
        self.setup_budget_tab()
        self.setup_reports_tab()

    def setup_transactions_tab(self):
        # Transaction entry form
        entry_frame = ttk.LabelFrame(self.transactions_frame, text="Add Transaction", padding="10")
        entry_frame.pack(fill='x', padx=5, pady=5)

        # Date picker
        ttk.Label(entry_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = DateEntry(entry_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Transaction type
        ttk.Label(entry_frame, text="Type:").grid(row=0, column=2, padx=5, pady=5)
        self.type_var = tk.StringVar(value="expense")
        ttk.Radiobutton(entry_frame, text="Expense", variable=self.type_var,
                       value="expense").grid(row=0, column=3)
        ttk.Radiobutton(entry_frame, text="Income", variable=self.type_var,
                       value="income").grid(row=0, column=4)

        # Category
        ttk.Label(entry_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar()
        categories = ["Food", "Transport", "Housing", "Utilities", "Entertainment", "Shopping",
                     "Healthcare", "Salary", "Investment", "Other"]
        self.category_combo = ttk.Combobox(entry_frame, textvariable=self.category_var,
                                         values=categories)
        self.category_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        # Amount
        ttk.Label(entry_frame, text="Amount:").grid(row=1, column=3, padx=5, pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(entry_frame, textvariable=self.amount_var)
        self.amount_entry.grid(row=1, column=4, padx=5, pady=5)

        # Description
        ttk.Label(entry_frame, text="Description:").grid(row=2, column=0, padx=5, pady=5)
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(entry_frame, textvariable=self.desc_var, width=40)
        self.desc_entry.grid(row=2, column=1, columnspan=4, padx=5, pady=5)

        # Add button
        ttk.Button(entry_frame, text="Add Transaction",
                  command=self.add_transaction).grid(row=3, column=0, columnspan=5, pady=10)

        # Transaction list
        list_frame = ttk.LabelFrame(self.transactions_frame, text="Recent Transactions", padding="10")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Treeview for transactions
        self.tree = ttk.Treeview(list_frame, columns=("Date", "Type", "Category", "Amount", "Description"),
                                show="headings")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Description", text="Description")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.refresh_transactions()

    def setup_budget_tab(self):
        # Budget entry form
        entry_frame = ttk.LabelFrame(self.budget_frame, text="Set Monthly Budget", padding="10")
        entry_frame.pack(fill='x', padx=5, pady=5)

        # Category selection
        ttk.Label(entry_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5)
        self.budget_category_var = tk.StringVar()
        categories = ["Food", "Transport", "Housing", "Utilities", "Entertainment",
                     "Shopping", "Healthcare", "Other"]
        self.budget_category_combo = ttk.Combobox(entry_frame,
                                                textvariable=self.budget_category_var,
                                                values=categories)
        self.budget_category_combo.grid(row=0, column=1, padx=5, pady=5)

        # Amount entry
        ttk.Label(entry_frame, text="Amount:").grid(row=0, column=2, padx=5, pady=5)
        self.budget_amount_var = tk.StringVar()
        self.budget_amount_entry = ttk.Entry(entry_frame, textvariable=self.budget_amount_var)
        self.budget_amount_entry.grid(row=0, column=3, padx=5, pady=5)

        # Set budget button
        ttk.Button(entry_frame, text="Set Budget",
                  command=self.set_budget).grid(row=0, column=4, padx=5, pady=5)

        # Budget overview
        overview_frame = ttk.LabelFrame(self.budget_frame, text="Budget Overview", padding="10")
        overview_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Add budget overview visualization here
        self.budget_canvas_frame = ttk.Frame(overview_frame)
        self.budget_canvas_frame.pack(fill='both', expand=True)
        self.update_budget_overview()

    def setup_reports_tab(self):
        # Report controls
        control_frame = ttk.LabelFrame(self.reports_frame, text="Report Controls", padding="10")
        control_frame.pack(fill='x', padx=5, pady=5)

        # Date range selection
        ttk.Label(control_frame, text="From:").grid(row=0, column=0, padx=5, pady=5)
        self.report_start_date = DateEntry(control_frame, width=12)
        self.report_start_date.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(control_frame, text="To:").grid(row=0, column=2, padx=5, pady=5)
        self.report_end_date = DateEntry(control_frame, width=12)
        self.report_end_date.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(control_frame, text="Generate Report",
                  command=self.generate_report).grid(row=0, column=4, padx=5, pady=5)

        # Report display area
        self.report_frame = ttk.Frame(self.reports_frame)
        self.report_frame.pack(fill='both', expand=True, padx=5, pady=5)

    def add_transaction(self):
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError("Amount must be positive")
                
            self.db.add_transaction(
                self.date_entry.get_date().strftime("%Y-%m-%d"),
                self.type_var.get(),
                self.category_var.get(),
                amount,
                self.desc_var.get()
            )
            
            # Clear form
            self.amount_var.set("")
            self.desc_var.set("")
            self.refresh_transactions()
            messagebox.showinfo("Success", "Transaction added successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add transaction: {str(e)}")

    def refresh_transactions(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Get recent transactions
        transactions = self.db.get_transactions()
        
        # Add to treeview
        for transaction in transactions:
            self.tree.insert("", "end", values=(
                transaction[1],  # date
                transaction[2],  # type
                transaction[3],  # category
                f"${transaction[4]:.2f}",  # amount
                transaction[5]   # description
            ))

    def set_budget(self):
        try:
            amount = float(self.budget_amount_var.get())
            if amount <= 0:
                raise ValueError("Budget amount must be positive")
                
            category = self.budget_category_var.get()
            if not category:
                raise ValueError("Please select a category")
                
            current_date = datetime.datetime.now()
            self.db.set_budget(category, amount, current_date.month, current_date.year)
            
            self.budget_amount_var.set("")
            self.update_budget_overview()
            messagebox.showinfo("Success", "Budget set successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set budget: {str(e)}")

    def update_budget_overview(self):
        # Clear existing widgets
        for widget in self.budget_canvas_frame.winfo_children():
            widget.destroy()

        # Create figure for matplotlib
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)

        # Get current month's data
        current_date = datetime.datetime.now()
        summary = self.db.get_monthly_summary(current_date.month, current_date.year)
        
        # Prepare data for plotting
        categories = []
        spent = []
        budgeted = []
        
        for category in ["Food", "Transport", "Housing", "Utilities", "Entertainment",
                        "Shopping", "Healthcare", "Other"]:
            categories.append(category)
            # Get spent amount
            category_spent = sum(amount for cat, type_, amount in summary
                               if cat == category and type_ == "expense")
            spent.append(category_spent)
            # Get budget amount
            budget = self.db.get_budget(category, current_date.month, current_date.year)
            budgeted.append(budget)

        # Create grouped bar chart
        x = range(len(categories))
        width = 0.35

        ax.bar([i - width/2 for i in x], spent, width, label='Spent', color='red')
        ax.bar([i + width/2 for i in x], budgeted, width, label='Budgeted', color='green')

        ax.set_ylabel('Amount ($)')
        ax.set_title('Monthly Budget Overview')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45)
        ax.legend()

        # Create canvas and draw
        canvas = FigureCanvasTkAgg(fig, master=self.budget_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def generate_report(self):
        start_date = self.report_start_date.get_date().strftime("%Y-%m-%d")
        end_date = self.report_end_date.get_date().strftime("%Y-%m-%d")
        
        # Clear existing widgets
        for widget in self.report_frame.winfo_children():
            widget.destroy()

        # Get transactions for the period
        transactions = self.db.get_transactions(start_date, end_date)
        
        if not transactions:
            messagebox.showinfo("No Data", "No transactions found for the selected period")
            return

        # Create figure for matplotlib
        fig = Figure(figsize=(10, 6))
        
        # Expense by category pie chart
        ax1 = fig.add_subplot(121)
        expense_data = {}
        for transaction in transactions:
            if transaction[2] == "expense":  # type is expense
                category = transaction[3]
                amount = transaction[4]
                expense_data[category] = expense_data.get(category, 0) + amount

        if expense_data:
            ax1.pie(expense_data.values(), labels=expense_data.keys(), autopct='%1.1f%%')
            ax1.set_title('Expenses by Category')

        # Income vs Expense bar chart
        ax2 = fig.add_subplot(122)
        income = sum(t[4] for t in transactions if t[2] == "income")
        expense = sum(t[4] for t in transactions if t[2] == "expense")
        ax2.bar(['Income', 'Expense'], [income, expense])
        ax2.set_title('Income vs Expense')
        ax2.set_ylabel('Amount ($)')

        # Adjust layout
        fig.tight_layout()

        # Create canvas and draw
        canvas = FigureCanvasTkAgg(fig, master=self.report_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

        # Add summary text
        summary_text = f"Total Income: ${income:.2f}\n"
        summary_text += f"Total Expenses: ${expense:.2f}\n"
        summary_text += f"Net: ${(income - expense):.2f}"
        
        summary_label = ttk.Label(self.report_frame, text=summary_text, padding="10")
        summary_label.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop() 