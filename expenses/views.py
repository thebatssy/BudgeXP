from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum
from django.utils import timezone
from .filters import ExpenseFilter

from .models import Expense, Budget
from .serializers import ExpenseSerializer, BudgetSerializer, UserRegisterSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    
    # Using custom filterset class instead of basic filterset_fields
    filterset_class = ExpenseFilter
    search_fields = ['note', 'category']
    ordering_fields = ['amount', 'date', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        # select_related('user') solves the N+1 problem by doing an INNER/LEFT JOIN on auth_user
        return Expense.objects.select_related('user').filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    
    # Disable pagination so frontend gets all active budgets in a clean list
    pagination_class = None

    def get_queryset(self):
        # Optimization added here as well
        return Budget.objects.select_related('user').filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
       
        now = timezone.now()
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