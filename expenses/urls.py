from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, ExpenseViewSet, BudgetViewSet, BudgetSummaryView, ThrottledTokenObtainPairView, ThrottledTokenRefreshView

router = DefaultRouter()
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'budgets', BudgetViewSet, basename='budget')

    
urlpatterns = [
    # auth endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', ThrottledTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', ThrottledTokenRefreshView.as_view(), name='token_refresh'),

    # analytics endpoint
    path('budget-summary/', BudgetSummaryView.as_view(), name='budget_summary'),

    # viewset router urls
    path('', include(router.urls)),
]