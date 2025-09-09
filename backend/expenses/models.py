from django.db import models
from django.conf import settings


class Expense(models.Model):
    CATEGORY_CHOICES = (
        ('inventory', 'Inventory'),
        ('utilities', 'Utilities'),
        ('rent', 'Rent'),
        ('marketing', 'Marketing'),
        ('logistics', 'Logistics'),
        ('wages', 'Wages'),
        ('other', 'Other'),
    )

    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default='other')
    date = models.DateField()
    reference = models.CharField(max_length=100, blank=True, default='')
    notes = models.TextField(blank=True, default='')

    # Optional associations
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_expenses')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.description} - {self.amount}"

