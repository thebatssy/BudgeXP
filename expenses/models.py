from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('FOOD', 'Food & Dining'),
        ('TRANSPORT', 'Transportation'),
        ('UTILITIES', 'Bills & Utilities'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('SHOPPING', 'Shopping'),
        ('OTHER', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    date = models.DateField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date'] # desc
    
    def __str__(self):
        return f"{self.user.username} - {self.category}: ₹{self.amount}"
    

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField() 
    year = models.IntegerField() 
    
    class Meta:
        unique_together = ['user', 'month', 'year']
    
    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year}: ₹{self.monthly_limit}"
