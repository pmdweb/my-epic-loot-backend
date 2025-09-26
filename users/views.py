from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from google.auth.transport import requests
from google.oauth2 import id_token
import logging
import os

User = get_user_model()
logger = logging.getLogger(__name__)

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Health check endpoint for users service"""
    return Response({"status": "ok"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Simple endpoint to get current user info."""
    user = request.user
    return Response({
        "authenticated": True, 
        "username": user.username,
        "id": user.id,
        "email": user.email
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def google_oauth_test(request):
    """
    Test endpoint that simulates Google OAuth without real Google validation.
    FOR DEVELOPMENT ONLY - Remove in production!
    """
    try:
        # Simulate successful Google OAuth response
        fake_user_data = {
            'sub': '123456789',  # Google ID
            'email': 'test@example.com',
            'given_name': 'Test',
            'family_name': 'User',
            'name': 'Test User',
            'picture': 'https://via.placeholder.com/150',
            'email_verified': True,
        }
        
        # Use the same logic as real OAuth
        google_id = fake_user_data['sub']
        email = fake_user_data['email']
        first_name = fake_user_data.get('given_name', '')
        last_name = fake_user_data.get('family_name', '')
        name = fake_user_data.get('name', '')
        avatar_url = fake_user_data.get('picture', '')
        email_verified = fake_user_data.get('email_verified', False)
        
        # Generate username from email
        username = email.split('@')[0]
        
        # Check if user already exists or create new
        user = None
        try:
            user = User.objects.get(google_id=google_id)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=email)
                user.google_id = google_id
                user.save()
            except User.DoesNotExist:
                # Ensure username is unique
                original_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    google_id=google_id,
                    avatar_url=avatar_url,
                    is_email_verified=email_verified,
                    is_active=True
                )
                logger.info(f"Created test user: {user.username}")
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Prepare user data for response
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'avatar_url': user.avatar_url,
            'is_premium': user.is_premium,
            'subscription_tier': user.subscription_tier,
            'is_email_verified': user.is_email_verified,
            'date_joined': user.date_joined.isoformat(),
        }
        
        return Response({
            'access': str(access_token),
            'refresh': str(refresh),
            'user': user_data,
            'test_mode': True  # Indicate this is test mode
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in test OAuth: {str(e)}")
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def google_oauth(request):
    """
    Handle Google OAuth authentication.
    
    Expected payload:
    {
        "token": "google_oauth_token",
        "clientId": "your_google_client_id"
    }
    
    Returns:
    {
        "access": "jwt_access_token",
        "refresh": "jwt_refresh_token",
        "user": {
            "id": 1,
            "username": "user",
            "email": "user@example.com",
            "first_name": "First",
            "last_name": "Last",
            "avatar_url": "https://...",
            "is_premium": false,
            "subscription_tier": "basic"
        }
    }
    """
    try:
        token = request.data.get('token')
        client_id = request.data.get('clientId')
        
        if not token:
            return Response(
                {'error': 'Google token is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not client_id:
            return Response(
                {'error': 'Google Client ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify the Google token
        try:
            # Specify the CLIENT_ID of the app that accesses the backend
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), client_id
            )
            
            # Verify that the token is issued by Google
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
                
        except ValueError as e:
            logger.error(f"Invalid Google token: {str(e)}")
            return Response(
                {'error': 'Invalid Google token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Extract user information from Google
        google_id = idinfo['sub']
        email = idinfo['email']
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')
        name = idinfo.get('name', '')
        avatar_url = idinfo.get('picture', '')
        email_verified = idinfo.get('email_verified', False)
        
        # Generate username from email or name
        if email:
            username = email.split('@')[0]
        else:
            username = name.replace(' ', '').lower()
        
        # Check if user already exists
        user = None
        try:
            # First, try to find user by Google ID
            user = User.objects.get(google_id=google_id)
            
            # Update user info in case it changed
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.avatar_url = avatar_url
            user.is_email_verified = email_verified
            user.save()
            
        except User.DoesNotExist:
            try:
                # Try to find user by email
                user = User.objects.get(email=email)
                
                # Link this Google account to existing user
                user.google_id = google_id
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name
                user.avatar_url = avatar_url or user.avatar_url
                user.is_email_verified = email_verified
                user.save()
                
            except User.DoesNotExist:
                # Create new user
                # Ensure username is unique
                original_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    google_id=google_id,
                    avatar_url=avatar_url,
                    is_email_verified=email_verified,
                    is_active=True
                )
                logger.info(f"Created new user via Google OAuth: {user.username}")
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Prepare user data for response
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'avatar_url': user.avatar_url,
            'is_premium': user.is_premium,
            'subscription_tier': user.subscription_tier,
            'is_email_verified': user.is_email_verified,
            'date_joined': user.date_joined.isoformat(),
        }
        
        return Response({
            'access': str(access_token),
            'refresh': str(refresh),
            'user': user_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in Google OAuth: {str(e)}")
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get current user profile information.
    Requires authentication.
    """
    user = request.user
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'avatar_url': user.avatar_url,
        'is_premium': user.is_premium,
        'subscription_tier': user.subscription_tier,
        'is_email_verified': user.is_email_verified,
        'date_joined': user.date_joined.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None,
    }
    
    return Response(user_data)
