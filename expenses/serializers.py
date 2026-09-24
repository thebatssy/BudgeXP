from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Expense, Budget
from decimal import Decimal


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class ExpenseSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Expense
        fields = ['id', 'user', 'amount', 'category', 'date', 'note', 'created_at']


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'monthly_limit', 'month', 'year', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
        
    def validate_month(self, val):
        if not (1 <= val <= 12):
            raise serializers.ValidationError("Month must be an integer between 1 and 12.")
        return val
        
    def validate_year(self, val):
        if not (2000 <= val <= 2100):
            raise serializers.ValidationError("Year must be between 2000 and 2100.")
        return val
    
    def validate_monthly_limit(self, val):
        if val <= Decimal('0.00'):
            raise serializers.ValidationError("Monthly budget limit must be greater than 0.")
        return val