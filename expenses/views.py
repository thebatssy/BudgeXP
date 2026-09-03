from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum
from datetime import datetime

from .models import Expense, Budget
from .serializers import ExpenseSerializer, BudgetSerializer, UserRegisterSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Expense.objects.filter(user=self.request.user)
        
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        category = self.request.query_params.get('category')

        if month:
            queryset = queryset.filter(date__month=month)
        if year:
            queryset = queryset.filter(date__year=year)
        if category:
            queryset = queryset.filter(category=category)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
       
        now = datetime.now()
        month = request.query_params.get('month', now.month)
        year = request.query_params.get('year', now.year)

        total_expenses = Expense.objects.filter(
            user=user,
            date__month=month,
            date__year=year
        ).aggregate(Sum('amount'))['amount__sum'] or 0.00

        budget_obj = Budget.objects.filter(user=user, month=month, year=year).first()
        monthly_limit = float(budget_obj.monthly_limit) if budget_obj else 0.00
        total_exp_float = float(total_expenses)
        
        remaining_budget = monthly_limit - total_exp_float
        if monthly_limit > 0:
            is_over_budget = total_exp_float > monthly_limit
        else:
            is_over_budget = total_exp_float > 0

        return Response({
            'month': int(month),
            'year': int(year),
            'monthly_limit': monthly_limit,
            'total_expenses': total_exp_float,
            'remaining_budget': remaining_budget,
            'is_over_budget': is_over_budget
        }, status=status.HTTP_200_OK)