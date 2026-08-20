from rest_framework import serializers
from .models import Budget, BudgetAllocation
from category.models import Category
from category.serializers import CategorySerializer

class BudgetAllocationSerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = BudgetAllocation
        fields = ['id', 'budget', 'category', 'category_details', 'amount']
        read_only_fields = ['id']

    def validate(self, data):
        user = self.context['request'].user
        budget = data.get('budget')
        category = data.get('category')

        # Validate budget ownership
        if budget and budget.user != user:
            raise serializers.ValidationError({"budget": "You do not have permission to modify allocations for this budget."})

        # Validate category ownership/accessibility
        if category and category.user is not None and category.user != user:
            raise serializers.ValidationError({"category": "You do not have permission to use this category."})

        return data


class BudgetSerializer(serializers.ModelSerializer):
    allocations = BudgetAllocationSerializer(many=True, read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = Budget
        fields = [
            'id', 'user', 'name', 'total_amount', 'start_date', 
            'end_date', 'notes', 'category', 'category_details', 
            'created_at', 'allocations'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def validate(self, data):
        user = self.context['request'].user
        category = data.get('category')

        # Validate category ownership/accessibility
        if category and category.user is not None and category.user != user:
            raise serializers.ValidationError({"category": "You do not have permission to use this category."})

        return data
