from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import Expense
from .serializers import ExpenseSerializer
from django.utils import timezone
from datetime import timedelta, datetime
import logging
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


#logger = logging.getLogger(__name__)
'''
We import Python’s built-in logging module and create a logger with 
logger = logging.getLogger(__name__). This allows us to record errors 
(for example, invalid date formats) which can be invaluable during debugging
and monitoring.
'''


class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Expense.objects.filter(user=self.request.user)
        filter_type = self.request.query_params.get('filter')  # e.g., past_week, past_month, last_3_months, custom

        if filter_type:
            today = timezone.now().date()

            if filter_type == 'past_week':
                start_date = today - timedelta(days=7)
                queryset = queryset.filter(date__gte=start_date)
            elif filter_type == 'past_month':
                start_date = today - timedelta( days=30)
                queryset = queryset.filter(date__gte=start_date)
            elif filter_type == 'last_3_months':
                start_date = today - timedelta(days=90)
                queryset = queryset.filter(date__gte=start_date)
            elif filter_type == 'custom':
                #custom date range with start_date and end_date query parameters in YYYY-MM-DD format
                start_date_str = self.request.query_params.get('start_date')
                end_date_str = self.request.query_params.get('end_date')
                if start_date_str and end_date_str:
                    try:
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                        queryset = queryset.filter(date__range=[start_date, end_date])
                    except ValueError as e:
                        # Log the error with details and raise a validation error.
                        #logger.error("Invalid date format in custom filter: %s", e)
                        raise ValidationError({"detail": "Invalid date format provided. Expected YYYY-MM-DD for start_date and end_date."})
        return queryset

    def get_serializer_context(self):
        """
        Add the request context so the serializer can automatically assign the expense's user.
        """
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context










class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Only allow access to an expense if it belongs to the authenticated user.
        """
        return Expense.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
