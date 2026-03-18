#!/usr/bin/env python
"""
Setup & Initialization Script for Capstone Project
This script automates database setup, migration, and sample data population.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, str(Path(__file__).parent))

django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from category.models import Category
from budget.models import Budget, BudgetAllocation
from expenses.models import Expense
from datetime import datetime, timedelta
from decimal import Decimal

CustomUser = get_user_model()

def run_migrations():
    """Run all pending migrations."""
    print("\n🔄 Running migrations...")
    try:
        call_command('migrate', verbosity=1)
        print("✅ Migrations completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    return True

def create_sample_users():
    """Create sample users with different roles."""
    print("\n👥 Creating sample users...")
    
    users_data = [
        {
            'username': 'john_user',
            'email': 'john@example.com',
            'password': 'Test1234!',
            'role': 'USER'
        },
        {
            'username': 'alice_moderator',
            'email': 'alice@example.com',
            'password': 'Test1234!',
            'role': 'MODERATOR'
        },
        {
            'username': 'bob_admin',
            'email': 'bob@example.com',
            'password': 'Test1234!',
            'role': 'ADMIN'
        }
    ]
    
    created_users = []
    for user_data in users_data:
        username = user_data['username']
        if not CustomUser.objects.filter(username=username).exists():
            user = CustomUser.objects.create_user(
                username=username,
                email=user_data['email'],
                password=user_data['password'],
                role=user_data['role']
            )
            created_users.append(user)
            print(f"  ✅ Created: {username} ({user_data['role']})")
        else:
            user = CustomUser.objects.get(username=username)
            created_users.append(user)
            print(f"  ℹ️  Already exists: {username}")
    
    return created_users

def create_sample_categories(user):
    """Create sample categories for a user."""
    print(f"\n📂 Creating sample categories for {user.username}...")
    
    categories_data = [
        {'name': 'Food', 'description': 'Groceries & Dining', 'is_income': False},
        {'name': 'Transport', 'description': 'Gas, Transit, Taxi', 'is_income': False},
        {'name': 'Entertainment', 'description': 'Movies, Games, Events', 'is_income': False},
        {'name': 'Salary', 'description': 'Monthly Salary', 'is_income': True},
        {'name': 'Freelance', 'description': 'Side Income', 'is_income': True},
    ]
    
    created_categories = []
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(
            name=cat_data['name'],
            user=user,
            defaults={
                'description': cat_data['description'],
                'is_income': cat_data['is_income'],
                'color': '#667eea'
            }
        )
        if created:
            print(f"  ✅ Created: {cat.name}")
        else:
            print(f"  ℹ️  Already exists: {cat.name}")
        created_categories.append(cat)
    
    return created_categories

def create_sample_expenses(user, categories):
    """Create sample expenses for a user."""
    print(f"\n💰 Creating sample expenses for {user.username}...")
    
    expenses_data = [
        {
            'amount': Decimal('1500.00'),
            'category_name': 'Food',
            'date_offset': 0,
            'description': 'Weekly groceries'
        },
        {
            'amount': Decimal('800.00'),
            'category_name': 'Transport',
            'date_offset': -2,
            'description': 'Gas fill-up'
        },
        {
            'amount': Decimal('2500.00'),
            'category_name': 'Entertainment',
            'date_offset': -5,
            'description': 'Concert tickets'
        },
        {
            'amount': Decimal('1200.00'),
            'category_name': 'Food',
            'date_offset': -7,
            'description': 'Restaurant dinner'
        },
    ]
    
    created_expenses = []
    for exp_data in expenses_data:
        category = next((c for c in categories if c.name == exp_data['category_name']), None)
        if not category:
            print(f"  ⚠️  Category not found: {exp_data['category_name']}")
            continue
        
        expense_date = datetime.now().date() + timedelta(days=exp_data['date_offset'])
        
        expense = Expense.objects.create(
            user=user,
            amount=exp_data['amount'],
            category=category,
            date=expense_date,
            description=exp_data['description'],
            is_recurring=False
        )
        created_expenses.append(expense)
        print(f"  ✅ Created: {expense.description} (${expense.amount})")
    
    return created_expenses

def create_sample_budgets(user, categories):
    """Create sample budgets for a user."""
    print(f"\n💳 Creating sample budgets for {user.username}...")
    
    today = datetime.now().date()
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    budgets_data = [
        {
            'name': 'March Monthly Budget',
            'total_amount': Decimal('5000.00'),
            'category_name': None,
            'notes': 'Overall monthly budget'
        },
        {
            'name': 'Food Budget',
            'total_amount': Decimal('2000.00'),
            'category_name': 'Food',
            'notes': 'Monthly food expenses'
        },
    ]
    
    created_budgets = []
    for bud_data in budgets_data:
        category = None
        if bud_data['category_name']:
            category = next((c for c in categories if c.name == bud_data['category_name']), None)
        
        budget = Budget.objects.create(
            user=user,
            name=bud_data['name'],
            total_amount=bud_data['total_amount'],
            start_date=month_start,
            end_date=month_end,
            notes=bud_data['notes'],
            category=category
        )
        created_budgets.append(budget)
        print(f"  ✅ Created: {budget.name} (${budget.total_amount})")
    
    return created_budgets

def create_sample_allocations(budget, categories):
    """Create sample budget allocations."""
    print(f"\n📊 Creating allocations for {budget.name}...")
    
    allocations_data = [
        {'category_name': 'Food', 'amount': Decimal('1500.00')},
        {'category_name': 'Transport', 'amount': Decimal('1000.00')},
        {'category_name': 'Entertainment', 'amount': Decimal('800.00')},
    ]
    
    for alloc_data in allocations_data:
        category = next((c for c in categories if c.name == alloc_data['category_name']), None)
        if not category:
            continue
        
        allocation, created = BudgetAllocation.objects.get_or_create(
            budget=budget,
            category=category,
            defaults={'amount': alloc_data['amount']}
        )
        if created:
            print(f"  ✅ Created: {category.name} - ${allocation.amount}")

def collect_static():
    """Collect static files."""
    print("\n📦 Collecting static files...")
    try:
        call_command('collectstatic', verbosity=0, interactive=False)
        print("✅ Static files collected!")
    except Exception as e:
        print(f"⚠️  Static collection warning: {e}")

def main():
    """Main setup function."""
    print("="*60)
    print("🚀 CAPSTONE PROJECT - SETUP & INITIALIZATION")
    print("="*60)
    
    # Step 1: Run migrations
    if not run_migrations():
        print("\n❌ Setup failed at migration step!")
        return False
    
    # Step 2: Create sample users
    users = create_sample_users()
    if not users:
        print("\n❌ Failed to create users!")
        return False
    
    # Step 3: Create sample data for each user
    for user in users[:1]:  # Only for first USER (not moderator/admin)
        categories = create_sample_categories(user)
        expenses = create_sample_expenses(user, categories)
        budgets = create_sample_budgets(user, categories)
        
        # Create allocations for the first budget
        if budgets:
            create_sample_allocations(budgets[0], categories)
    
    # Step 4: Collect static files
    collect_static()
    
    # Summary
    print("\n" + "="*60)
    print("✅ SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\n📌 Sample Users Created:")
    print("  • john_user (USER role) - Password: Test1234!")
    print("  • alice_moderator (MODERATOR role) - Password: Test1234!")
    print("  • bob_admin (ADMIN role) - Password: Test1234!")
    print("\n🌐 Access Points:")
    print("  • Home: http://localhost:8000/")
    print("  • Login: http://localhost:8000/accounts/")
    print("  • Admin: http://localhost:8000/admin/")
    print("  • Dashboard (login first): http://localhost:8000/accounts/dashboard/")
    print("\n📊 Sample Data:")
    print("  • 4 sample expenses created")
    print("  • 2 sample budgets created")
    print("  • Budget allocations configured")
    print("\n💡 Next Steps:")
    print("  1. Run: python manage.py runserver")
    print("  2. Login with: john_user / Test1234!")
    print("  3. Explore dashboard and CRUD operations")
    print("="*60 + "\n")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
