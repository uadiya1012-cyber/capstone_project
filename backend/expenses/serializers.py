from rest_framework import serializers
from .models import Expense
from category.models import Category
from budget.models import Budget
from category.serializers import CategorySerializer

class ExpenseSerializer(serializers.ModelSerializer):
    # For representation, we can show nested category info
    category_details = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'user', 'amount', 'category', 'category_details', 'date', 
            'description', 'receipt', 'budget', 'is_recurring', 
            'recurring_interval', 'next_recurrence_date', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'next_recurrence_date', 'created_at']

    def validate(self, data):
        user = self.context['request'].user
        category = data.get('category')
        budget = data.get('budget')

        # Validate category
        if category and category.user is not None and category.user != user:
            raise serializers.ValidationError({"category": "You do not have permission to use this category."})

        # Validate budget
        if budget and budget.user != user:
            raise serializers.ValidationError({"budget": "You do not have permission to allocate to this budget."})

        return data
