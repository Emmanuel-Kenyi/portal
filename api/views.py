from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """
    Returns role-based dashboard data for authenticated users
    """
    try:
        user = request.user
        profile = user.profile
        
        # Base response data
        data = {
            'profile': {
                'name': profile.name,
                'role': profile.role,
                'email': user.email,
                'username': user.username
            }
        }
        
        # Role-specific data
        if profile.role == 'admin':
            # Admin dashboard data
            from clubs.models import Club
            
            data['summary'] = {
                'total_users': User.objects.count(),
                'total_students': User.objects.filter(profile__role='student').count(),
                'total_lecturers': User.objects.filter(profile__role='lecturer').count(),
                'total_clubs': Club.objects.count(),
            }
            
        elif profile.role == 'student':
            # Student dashboard data
            data['clubs'] = list(profile.clubs.values('id', 'name', 'description'))
            # Add more student-specific data (marks, courses, etc.)
            
        elif profile.role == 'lecturer':
            # Lecturer dashboard data
            from clubs.models import Club
            data['clubs'] = list(Club.objects.filter(advisor=user).values('id', 'name'))
            # Add more lecturer-specific data
            
        return Response(data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Returns current user's profile information
    """
    user = request.user
    profile = user.profile
    
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'name': profile.name,
        'role': profile.role,
    }
    
    return Response(data, status=status.HTTP_200_OK)