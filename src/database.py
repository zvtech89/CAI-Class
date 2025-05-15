import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'finance.db')
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create budget table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                UNIQUE(category, month, year)
            )
        ''')

        conn.commit()
        conn.close()

    def add_transaction(self, date, type_, category, amount, description=""):
        """Add a new transaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions (date, type, category, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, type_, category, amount, description))
        
        conn.commit()
        conn.close()

    def get_transactions(self, start_date=None, end_date=None, category=None):
        """Get transactions with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if category:
            query += " AND category = ?"
            params.append(category)
            
        query += " ORDER BY date DESC"
        
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        conn.close()
        return transactions

    def set_budget(self, category, amount, month, year):
        """Set or update budget for a category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO budgets (category, amount, month, year)
            VALUES (?, ?, ?, ?)
        ''', (category, amount, month, year))
        
        conn.commit()
        conn.close()

    def get_budget(self, category, month, year):
        """Get budget for a specific category and month"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT amount FROM budgets
            WHERE category = ? AND month = ? AND year = ?
        ''', (category, month, year))
        
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0.0

    def get_monthly_summary(self, month, year):
        """Get monthly summary of transactions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                category,
                type,
                SUM(amount) as total
            FROM transactions
            WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
            GROUP BY category, type
        ''', (f"{month:02d}", str(year)))
        
        summary = cursor.fetchall()
        conn.close()
        return summary 