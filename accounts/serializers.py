from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate





class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, data):
        #ensure both password fields match
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        return data

    def create(self, validated_data):
        '''
        Use Django’s built-in create_user method to create a new user.
        This method automatically hashes the password.
        '''
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user










class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        #Authenticate the user using Django's built-in authentication.
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Wrong credentials.")
        
        else:
            raise serializers.ValidationError("Username or password can't be empty")

        data['user'] = user
        return data 


