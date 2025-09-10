from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import ExtendedUser
from .serializers import ExtendedUserSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Simple login endpoint that works with Dashboard.User model
    
    Expected input:
    {
        "username": "user123",
        "password": "password123"
    }
    
    Returns success or error response
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Validate input data
        if not username or not password:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Login attempt for username: {username}")
        
        # Import Dashboard User model
        from Dashboard.models import User as DashboardUser
        
        # Try to find user
        try:
            dashboard_user = DashboardUser.objects.get(username=username)
            
            # Simple password check (Note: In production, use proper hashing)
            if dashboard_user.password == password:
                logger.info(f"Login successful for user: {username}")
                
                # Create token for API access
                token, created = Token.objects.get_or_create(
                    user_id=dashboard_user.id,
                    defaults={'key': Token.generate_key()}
                )
                
                # Get or create extended user for role information
                try:
                    extended_user = ExtendedUser.objects.get(user=dashboard_user)
                    role = extended_user.role
                    company_id = extended_user.company.id if extended_user.company else None
                except ExtendedUser.DoesNotExist:
                    # Create default extended user profile
                    logger.info(f"Creating default ExtendedUser for: {username}")
                    extended_user = ExtendedUser.objects.create(user=dashboard_user, role='HR')
                    role = 'HR'
                    company_id = None
                
                return Response({
                    'message': 'Login successful',
                    'token': token.key,
                    'user_id': dashboard_user.id,
                    'username': dashboard_user.username,
                    'role': role,
                    'company_id': company_id,
                    'first_name': dashboard_user.first_names,
                    'last_name': dashboard_user.last_names,
                }, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Invalid password for user: {username}")
                return Response({
                    'error': 'Invalid username or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except DashboardUser.DoesNotExist:
            logger.warning(f"User not found: {username}")
            return Response({
                'error': 'Invalid username or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    except Exception as e:
        logger.error(f"Login error for {username}: {str(e)}")
        return Response({
            'error': 'Authentication failed. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    """
    Simple signup endpoint for creating new users
    
    Expected input:
    {
        "username": "user123",
        "email": "user@example.com", 
        "password": "password123",
        "first_names": "John",
        "last_names": "Doe",
        "phone_number": "1234567890",
        "role": "HR|Admin|Director"
    }
    
    Returns success or error response
    """
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_names', 'last_names', 'phone_number']
        for field in required_fields:
            if not data.get(field):
                return Response({
                    'error': f'{field} is required'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        username = data['username']
        email = data['email']
        password = data['password']
        first_names = data['first_names']
        last_names = data['last_names']
        phone_number = data['phone_number']
        role = data.get('role', 'HR')  # Default to HR role
        
        logger.info(f"Signup attempt for username: {username}")
        
        # Import Dashboard User model
        from Dashboard.models import User as DashboardUser
        
        # Check if user already exists
        if DashboardUser.objects.filter(username=username).exists():
            return Response({
                'error': 'Username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if DashboardUser.objects.filter(email=email).exists():
            return Response({
                'error': 'Email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate role
        valid_roles = ['Admin', 'HR', 'Director']
        if role not in valid_roles:
            return Response({
                'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create Dashboard user
        dashboard_user = DashboardUser.objects.create(
            username=username,
            email=email,
            password=password,  # Note: In production, this should be hashed
            first_names=first_names,
            last_names=last_names,
            phone_number=phone_number
        )
        
        logger.info(f"Created Dashboard user: {username}")
        
        # Create extended user profile with role
        extended_user = ExtendedUser.objects.create(
            user=dashboard_user,
            role=role
        )
        
        logger.info(f"Created ExtendedUser with role {role} for: {username}")
        
        return Response({
            'message': 'User created successfully',
            'user_id': dashboard_user.id,
            'username': dashboard_user.username,
            'email': dashboard_user.email,
            'role': role,
            'first_names': dashboard_user.first_names,
            'last_names': dashboard_user.last_names
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return Response({
            'error': f'Error creating user: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def logout_view(request):
    """
    Simple logout endpoint
    """
    try:
        # Note: Since we're using simple token auth, we can just delete the token
        token_key = request.META.get('HTTP_AUTHORIZATION', '').replace('Token ', '')
        if token_key:
            try:
                token = Token.objects.get(key=token_key)
                token.delete()
                return Response({'message': 'Logged out successfully'})
            except Token.DoesNotExist:
                return Response({'message': 'Already logged out'})
        else:
            return Response({'message': 'No token provided'})
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response({'error': 'Logout failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def profile_view(request):
    """
    Simple profile endpoint
    """
    try:
        # Note: This is a simplified profile view
        return Response({
            'message': 'Profile endpoint - implementation needed'
        })
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return Response({'error': 'Profile retrieval failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
