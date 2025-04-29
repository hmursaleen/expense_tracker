from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from rest_framework.permissions import AllowAny
#import logging
#logger = logging.getLogger(__name__)




class UserRegistrationView(APIView):
    #DRF settings enforce the IsAuthenticated permission by default. This means every endpoint requires authentication unless you explicitly override it. Since registration should be open to unauthenticated users, you need to override the permission for the registration view.
    
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successfull."}, status=status.HTTP_201_CREATED)
        
        #logger.info("Registration failed: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)










class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user) #log the user in using Django's session system
            #we optionally call Django’s login() method if you plan to use session-based authentication. Later, when integrating JWT, the authentication mechanism will change.
            return Response({"message": "Login successful."}, status=status.HTTP_200_OK)
        
        #logger.info("Login failed: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
