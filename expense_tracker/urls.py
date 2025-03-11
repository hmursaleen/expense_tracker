from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configure the schema view for Swagger and ReDoc documentation.
schema_view = get_schema_view(
    openapi.Info(
        title="Expense Tracker API",
        default_version='v1',
        description="API documentation for the Expense Tracker application.",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # API version 1 endpoints
    path('api/v1/auth/', include('accounts.urls')),      # User registration and login endpoints
    path('api/v1/expenses/', include('expenses.urls')),    # Expense CRUD endpoints

    # API documentation endpoints
    path('api/v1/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/v1/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
