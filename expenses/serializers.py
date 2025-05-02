from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    valid_categories = None #Cache the valid categories

    class Meta:
        model = Expense
        fields = ['id', 'user', 'amount', 'date', 'description', 'category', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("The expense amount must be greater than zero.")
        return value

    def validate_category(self, value):
        if self._valid_categories is None:
            self._valid_categories = [choice[0] for choice in Expense.CATEGORY_CHOICES]
        
        if value not in self._valid_categories:
            raise serializers.ValidationError(
                f"Category must be one of the following: {', '.join(self._valid_categories)}."
            )
        return value

    def create(self, validated_data):
        """
        Automatically assign the user from the request context.
        The client should not be allowed to specify the user.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)
