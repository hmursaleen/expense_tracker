from django.urls import path
from .views import ExpenseView

urlpatterns = [
    path('/', ExpenseView.as_view(), name='expense-list'),
    path('/<int:pk>/', ExpenseView.as_view(), name='expense-detail'),
]