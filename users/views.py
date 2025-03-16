from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import json

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# User Registration
@api_view(['POST'])
def register(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return JsonResponse({'error': 'All fields are required'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        tokens = get_tokens_for_user(user)
        return JsonResponse({'message': 'User registered successfully', 'tokens': tokens}, status=201)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

# User Login
@api_view(['POST'])
def login(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Both username and password are required'}, status=400)

        user = authenticate(username=username, password=password)

        if user:
            tokens = get_tokens_for_user(user)
            return JsonResponse({'message': 'Login successful', 'tokens': tokens}, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

# Get User Profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }
    return JsonResponse(user_data, status=200)