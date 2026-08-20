"""
Management command to automatically create recurring expenses.
Run via: python manage.py auto_recurring
Schedule with cron for daily execution.
"""
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from expenses.models import Expense


class Command(BaseCommand):
    help = 'Давтамжтай зардлуудыг автоматаар шинээр үүсгэнэ (daily, weekly, monthly)'

    def handle(self, *args, **options):
        today = date.today()
        created_count = 0

        # Find all recurring expenses that are due
        recurring_expenses = Expense.objects.filter(
            is_recurring=True,
            recurring_interval__in=['daily', 'weekly', 'monthly'],
            next_recurrence_date__lte=today,
        )

        for expense in recurring_expenses:
            # Create a new expense copy
            Expense.objects.create(
                user=expense.user,
                amount=expense.amount,
                category=expense.category,
                date=today,
                description=f"[Автомат] {expense.description}",
                budget=expense.budget,
                is_recurring=False,  # The copy is not recurring itself
                recurring_interval='',
            )

            # Update next recurrence date on the original
            if expense.recurring_interval == 'daily':
                expense.next_recurrence_date = today + timedelta(days=1)
            elif expense.recurring_interval == 'weekly':
                expense.next_recurrence_date = today + timedelta(weeks=1)
            elif expense.recurring_interval == 'monthly':
                # Move to same day next month
                month = expense.next_recurrence_date.month
                year = expense.next_recurrence_date.year
                if month == 12:
                    next_month = 1
                    next_year = year + 1
                else:
                    next_month = month + 1
                    next_year = year
                try:
                    expense.next_recurrence_date = expense.next_recurrence_date.replace(
                        year=next_year, month=next_month
                    )
                except ValueError:
                    # Handle months with fewer days (e.g. Jan 31 -> Feb 28)
                    import calendar
                    last_day = calendar.monthrange(next_year, next_month)[1]
                    expense.next_recurrence_date = expense.next_recurrence_date.replace(
                        year=next_year, month=next_month, day=last_day
                    )

            expense.save(update_fields=['next_recurrence_date'])
            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Амжилттай! {created_count} давтамжтай зардал автоматаар үүсгэгдлээ.'
        ))
