from django.db import models
from django.conf import settings
from django.utils import timezone

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('GROCERIES', 'Groceries'),
        ('LEISURE', 'Leisure'),
        ('ELECTRONICS', 'Electronics'),
        ('UTILITIES', 'Utilities'),
        ('CLOTHING', 'Clothing'),
        ('HEALTH', 'Health'),
        ('OTHERS', 'Others'),
    ]

    #Link the expense to a specific user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True) #Avoid null=True for string fields
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True) #auto now add: Sets the field value only when the model is first created
    updated_at = models.DateTimeField(auto_now=True) #auto_now: Updates the field value every time the model is saved. Field is always updated, even if you don't explicitly set it

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.amount}"


'''
Use blank=True when you want to make a field optional in forms
Use null=True when you want to allow NULL values in database
For string fields, prefer blank=True over null=True
For non-string fields, use both when you want optional fields
For required fields, use neither
Remember:
blank is for form validation
null is for database storage
String fields should avoid null=True
'''