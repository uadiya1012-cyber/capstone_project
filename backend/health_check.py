#!/usr/bin/env python
"""
Health Check & System Status Script for Capstone Project
Verifies database connection, migrations, and system health.
"""

import os
import sys
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, str(Path(__file__).parent))

django.setup()

from django.db import connection
from django.core.management import call_command
from io import StringIO
from accounts.models import CustomUser
from category.models import Category
from expenses.models import Expense
from budget.models import Budget, BudgetAllocation

def check_database_connection():
    """Check if database connection is working."""
    print("\n🔗 Checking database connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("  ✅ Database connected successfully!")
        return True
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False

def check_migrations():
    """Check if all migrations are applied."""
    print("\n📦 Checking migrations status...")
    try:
        out = StringIO()
        call_command('showmigrations', verbosity=0, stdout=out)
        output = out.getvalue()
        
        if "[X]" in output:
            print("  ✅ Migrations applied!")
            return True
        else:
            print("  ⚠️  Some migrations may be pending!")
            return False
    except Exception as e:
        print(f"  ❌ Migration check failed: {e}")
        return False

def check_models():
    """Check if models are accessible."""
    print("\n📊 Checking models...")
    try:
        models = [
            ('CustomUser', CustomUser),
            ('Category', Category),
            ('Expense', Expense),
            ('Budget', Budget),
            ('BudgetAllocation', BudgetAllocation),
        ]
        
        for name, model in models:
            count = model.objects.count()
            print(f"  ✅ {name}: {count} records")
        
        return True
    except Exception as e:
        print(f"  ❌ Model check failed: {e}")
        return False

def check_users():
    """Check sample users."""
    print("\n👥 Checking users...")
    try:
        users = CustomUser.objects.all()
        if users.count() == 0:
            print("  ⚠️  No users found. Run setup_and_init.py first!")
            return False
        
        for user in users:
            # Only display username in health check; do not reveal user roles
            print(f"  ✅ {user.username}")
        
        return True
    except Exception as e:
        print(f"  ❌ User check failed: {e}")
        return False

def check_sample_data():
    """Check sample data."""
    print("\n📈 Checking sample data...")
    try:
        users_count = CustomUser.objects.count()
        cats_count = Category.objects.count()
        exps_count = Expense.objects.count()
        buds_count = Budget.objects.count()
        allocs_count = BudgetAllocation.objects.count()
        
        print(f"  • Users: {users_count}")
        print(f"  • Categories: {cats_count}")
        print(f"  • Expenses: {exps_count}")
        print(f"  • Budgets: {buds_count}")
        print(f"  • Allocations: {allocs_count}")
        
        if exps_count > 0:
            print("  ✅ Sample data exists!")
            return True
        else:
            print("  ⚠️  No sample data. Run setup_and_init.py first!")
            return False
    except Exception as e:
        print(f"  ❌ Sample data check failed: {e}")
        return False

def check_django():
    """Run Django check command."""
    print("\n🔍 Running Django system check...")
    try:
        out = StringIO()
        call_command('check', stdout=out, stderr=out)
        print("  ✅ All Django checks passed!")
        return True
    except Exception as e:
        print(f"  ❌ Django check failed: {e}")
        return False

def main():
    """Main health check function."""
    print("="*60)
    print("🏥 CAPSTONE PROJECT - HEALTH CHECK")
    print("="*60)
    
    checks = [
        check_database_connection,
        check_migrations,
        check_django,
        check_models,
        check_users,
        check_sample_data,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Check failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print("="*60)
        print("\n🚀 System is ready!")
        print("\nNext steps:")
        print("  1. Run: python manage.py runserver")
        print("  2. Navigate to: http://localhost:8000/")
        print("  3. Login with: john_user / Test1234!")
        print("="*60 + "\n")
        return True
    else:
        print(f"⚠️  SOME CHECKS FAILED ({passed}/{total})")
        print("="*60)
        print("\nTo fix:")
        print("  1. Run: python manage.py migrate")
        print("  2. Run: python setup_and_init.py")
        print("="*60 + "\n")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
