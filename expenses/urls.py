from django.urls import path
from .views import ExpenseView

urlpatterns = [
    path('expenses/', ExpenseView.as_view(), name='expense-list'),
    path('expenses/<int:pk>/', ExpenseView.as_view(), name='expense-detail'),
]