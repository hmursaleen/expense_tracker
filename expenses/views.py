from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from .models import Expense
from .serializers import ExpenseSerializer
from django.utils import timezone
from datetime import timedelta, datetime
import logging

#logger = logging.getLogger(__name__)

class ExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk=None):
        """
        Get the expense object and verify ownership.
        If pk is None, returns all expenses for the user.
        """
        try:
            if pk is None:
                return Expense.objects.select_related('user').filter(user=self.request.user)
            
            expense = Expense.objects.select_related('user').get(pk=pk)
            if expense.user != self.request.user:
                raise NotFound("Expense not found.")
            return expense
        except Expense.DoesNotExist:
            raise NotFound("Expense not found.")

    def _apply_filters(self, queryset):
        """
        Apply date-based filtering to the queryset.
        """
        filter_type = self.request.query_params.get('filter')
        if not filter_type:
            return queryset

        today = timezone.now().date()
        date_filters = {
            'past_week': today - timedelta(days=7),
            'past_month': today - timedelta(days=30),
            'last_3_months': today - timedelta(days=90)
        }

        if filter_type in date_filters:
            return queryset.filter(date__gte=date_filters[filter_type])
        
        if filter_type == 'custom':
            return self._apply_custom_date_filter(queryset)
        
        return queryset

    def _apply_custom_date_filter(self, queryset):
        """
        Apply custom date range filtering to the queryset.
        """
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')

        if not (start_date_str and end_date_str):
            raise ValidationError({
                "detail": "Both start_date and end_date are required for custom date filtering."
            })

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if start_date > end_date:
                raise ValidationError({
                    "detail": "start_date cannot be later than end_date."
                })
            
            return queryset.filter(date__range=[start_date, end_date])
            
        except ValueError:
            raise ValidationError({
                "detail": "Invalid date format. Use YYYY-MM-DD format for dates."
            })

    def _apply_search_and_ordering(self, queryset):
        """
        Apply search and ordering to the queryset.
        """
        # Apply ordering
        ordering = self.request.query_params.get('ordering', '-date')
        if ordering.lstrip('-') in ['date', 'amount', 'created_at']:
            queryset = queryset.order_by(ordering)
        
        # Apply search if provided
        search_query = self.request.query_params.get('search', '')
        if search_query:
            queryset = queryset.filter(
                description__icontains=search_query
            ) | queryset.filter(
                category__icontains=search_query
            )
        
        return queryset

    def get(self, request, pk=None):
        """
        List all expenses or retrieve a specific expense.
        """
        try:
            if pk is None:
                # List all expenses
                queryset = self.get_object()
                queryset = self._apply_filters(queryset)
                queryset = self._apply_search_and_ordering(queryset)
                serializer = ExpenseSerializer(queryset, many=True)
            else:
                # Retrieve specific expense
                expense = self.get_object(pk)
                serializer = ExpenseSerializer(expense)
            
            return Response(serializer.data)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in ExpenseView.get: {str(e)}")
            return Response(
                {"detail": "An error occurred while fetching expenses."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        Create a new expense.
        """
        try:
            serializer = ExpenseSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in ExpenseView.post: {str(e)}")
            return Response(
                {"detail": "An error occurred while creating the expense."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, pk):
        """
        Update an expense (full update).
        """
        try:
            expense = self.get_object(pk)
            serializer = ExpenseSerializer(expense, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in ExpenseView.put: {str(e)}")
            return Response(
                {"detail": "An error occurred while updating the expense."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, pk):
        """
        Update an expense (partial update).
        """
        try:
            expense = self.get_object(pk)
            serializer = ExpenseSerializer(expense, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in ExpenseView.patch: {str(e)}")
            return Response(
                {"detail": "An error occurred while updating the expense."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        """
        Delete an expense.
        """
        try:
            expense = self.get_object(pk)
            expense.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in ExpenseView.delete: {str(e)}")
            return Response(
                {"detail": "An error occurred while deleting the expense."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
