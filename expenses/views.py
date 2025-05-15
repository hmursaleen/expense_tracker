from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
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
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def get_object(self, pk=None):
        #Get the expense object and verify ownership. If pk is None, returns all expenses for the user.
        
        try:
            if pk is None:
                return Expense.objects.filter(user=self.request.user)
            expense = Expense.objects.get(pk=pk, user=self.request.user)
            return expense
        except Expense.DoesNotExist:
            raise NotFound("Expense not found.")

    def get(self, request, pk=None):
        try:
            queryset = self.get_object(pk)
            
            if pk is None:
                # Apply filters
                filter_type = request.query_params.get('filter')
                if filter_type:
                    today = timezone.now().date()
                    if filter_type == 'past_week':
                        queryset = queryset.filter(date__gte=today - timedelta(days=7))
                    elif filter_type == 'past_month':
                        queryset = queryset.filter(date__gte=today - timedelta(days=30))
                    elif filter_type == 'last_3_months':
                        queryset = queryset.filter(date__gte=today - timedelta(days=90))
                    elif filter_type == 'custom':
                        start_date = request.query_params.get('start_date')
                        end_date = request.query_params.get('end_date')
                        if start_date and end_date:
                            queryset = queryset.filter(date__range=[start_date, end_date])
                
                # Apply search
                search = request.query_params.get('search')
                if search:
                    queryset = queryset.filter(description__icontains=search) | queryset.filter(category__icontains=search)
                
                # Apply ordering
                ordering = request.query_params.get('ordering', '-date')
                if ordering.lstrip('-') in ['date', 'amount', 'created_at']:
                    queryset = queryset.order_by(ordering)
                
                serializer = ExpenseSerializer(queryset, many=True)
                return Response({
                    'status': 'success',
                    'message': 'Expenses retrieved successfully',
                    'data': serializer.data,
                    'count': queryset.count()
                }, status=status.HTTP_200_OK)
            else:
                serializer = ExpenseSerializer(queryset)
                return Response({
                    'status': 'success',
                    'message': 'Expense retrieved successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
        except Exception as Error:
            #logger.error(f"Error in ExpenseView.get: {Error=} {type(Error)=}")
            return Response(
                {"detail": "An error occurred while fetching expenses."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        try:
            serializer = ExpenseSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as Error:
            #logger.error(f"Error in ExpenseView.post: {Error=} {type(Error)=}")
            return Response(
                {"detail": "An error occurred while creating the expense."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, pk):
        try:
            expense = self.get_object(pk)
            serializer = ExpenseSerializer(expense, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Expense updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as Error:
            #logger.error(f"Error in ExpenseView.put: {Error=} {type(Error)=}")
            return Response(
                {"detail": "An error occurred while updating the expense."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, pk):
        try:
            expense = self.get_object(pk)
            serializer = ExpenseSerializer(expense, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Expense partially updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as Error:
            #logger.error(f"Error in ExpenseView.patch: {Error=} {type(Error)=}")
            return Response(
                {"detail": "An error occurred while updating the expense."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        try:
            expense = self.get_object(pk)
            expense.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as Error:
            #logger.error(f"Error in ExpenseView.delete: {Error=} {type(Error)=}")
            return Response(
                {"detail": "An error occurred while deleting the expense."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
