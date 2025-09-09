from rest_framework import serializers
from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            'id', 'description', 'amount', 'category', 'date',
            'reference', 'notes', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ExpenseSummarySerializer(serializers.Serializer):
    total_expenses = serializers.DecimalField(max_digits=14, decimal_places=2)
    count = serializers.IntegerField()

