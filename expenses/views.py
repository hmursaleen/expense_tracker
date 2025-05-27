from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from django.db.models import Q
from .models import Expense
from .serializers import ExpenseSerializer
from django.utils import timezone
from datetime import timedelta, datetime
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def handle_exceptions_and_ownership(func):
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        try:
            if kwargs.get('pk') is not None:
                expense = self.get_object(kwargs['pk'])
                if expense.user != request.user:
                    raise PermissionDenied("You do not have permission to access this expense.")
                #kwargs['expense'] = expense  # Pass the verified expense to the view method
            
            return func(self, request, *args, **kwargs)
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except NotFound as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            return Response(
                {"detail": f"An error occurred while {func.__name__.replace('_', ' ')}."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper

class ExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk=None):
        try:
            if pk is None:
                return Expense.objects.filter(user=self.request.user)
            return Expense.objects.get(pk=pk, user=self.request.user)
        except Expense.DoesNotExist:
            raise NotFound("Expense not found.")

    def validate_date_range(self, start_date_str, end_date_str):
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if start_date > end_date:
                raise ValidationError("Start date cannot be later than end date.")
            
            if end_date > timezone.now().date():
                raise ValidationError("End date cannot be in the future.")
            
            return start_date, end_date
        except ValueError:
            raise ValidationError("Invalid date format. Use YYYY-MM-DD format for dates.")

    def apply_filters(self, queryset, params):
        # Apply date filters
        filter_type = params.get('filter')
        if filter_type:
            today = timezone.now().date()
            if filter_type == 'past_week':
                queryset = queryset.filter(date__gte=today - timedelta(days=7))
            elif filter_type == 'past_month':
                queryset = queryset.filter(date__gte=today - timedelta(days=30))
            elif filter_type == 'last_3_months':
                queryset = queryset.filter(date__gte=today - timedelta(days=90))
            elif filter_type == 'custom':
                start_date = params.get('start_date')
                end_date = params.get('end_date')
                if not (start_date and end_date):
                    raise ValidationError("Both start_date and end_date are required for custom date filtering.")
                
                start_date, end_date = self.validate_date_range(start_date, end_date)
                queryset = queryset.filter(date__range=[start_date, end_date])
        
        # Apply search
        search = params.get('search')
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) | 
                Q(category__icontains=search)
            )
        
        # Apply category filter
        category = params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Apply amount range filter
        min_amount = params.get('min_amount')
        max_amount = params.get('max_amount')
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)
        
        return queryset

    @handle_exceptions_and_ownership
    def get(self, request, pk=None):
        queryset = self.get_object(pk)
        
        if pk is None:
            # Apply filters
            queryset = self.apply_filters(queryset, request.query_params)
            
            # Apply ordering
            ordering = request.query_params.get('ordering', '-date')
            if ordering.lstrip('-') in ['date', 'amount', 'created_at']:
                queryset = queryset.order_by(ordering)
            
            serializer = ExpenseSerializer(queryset, many=True)

        else:
            serializer = ExpenseSerializer(queryset)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions_and_ownership
    def post(self, request):
        serializer = ExpenseSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @handle_exceptions_and_ownership
    def put(self, request, pk):
        expense = self.get_object(pk)
        serializer = ExpenseSerializer(expense, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions_and_ownership
    def patch(self, request, pk):
        expense = self.get_object(pk)
        serializer = ExpenseSerializer(expense, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions_and_ownership
    def delete(self, request, pk):
        expense = self.get_object(pk)
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
