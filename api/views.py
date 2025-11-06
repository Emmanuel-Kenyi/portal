# api/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count
from datetime import datetime
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from clubs.models import Club, ClubPost, Event, Poll, PollOption
from .serializers import (
    UserSerializer,
    ProfileSerializer,
    ClubSerializer,
    ClubPostSerializer,
    EventSerializer,
    PollSerializer,
    PollOptionSerializer,
    StudentPointsSerializer,
    StudentMarkSerializer,
    StudentGPASerializer,
    CourseSerializer,
)
from clubs.reports import (
    generate_my_clubs_report,
    generate_my_events_report,
    generate_my_grades_report,
    upload_to_supabase,
    get_my_reports
)

# -------------------------
# Role Checks
# -------------------------
def is_admin(user):
    return hasattr(user, "profile") and user.profile.role == "admin"

def is_lecturer(user):
    return hasattr(user, "profile") and user.profile.role == "lecturer"

def is_student(user):
    return hasattr(user, "profile") and user.profile.role == "student"

def is_admin_or_lecturer(user):
    return hasattr(user, "profile") and user.profile.role in ("admin", "lecturer")

# -------------------------
# AUTHENTICATION
# -------------------------
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # add role and username info
        data.update({
            "role": self.user.profile.role if hasattr(self.user, "profile") else "student",
            "username": self.user.username,
            "user_id": self.user.id
        })
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class MyTokenRefreshView(TokenRefreshView):
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Return current logged-in user's info"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# -------------------------
# CLUB VIEWSET
# -------------------------
class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def toggle_membership(self, request, pk=None):
        club = self.get_object()
        user = request.user
        if not is_student(user):
            return Response({"detail": "Only students can join clubs."}, status=403)

        if user in club.members.all():
            club.members.remove(user)
            return Response({"detail": f"You have left {club.name}."})
        else:
            club.members.add(user)
            return Response({"detail": f"You have joined {club.name}."})

# -------------------------
# CLUB POST VIEWSET
# -------------------------
class ClubPostViewSet(viewsets.ModelViewSet):
    queryset = ClubPost.objects.all()
    serializer_class = ClubPostSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        club_id = request.data.get("club")
        club = get_object_or_404(Club, id=club_id)

        if request.user not in club.members.all():
            return Response({"detail": "You must be a member to post."}, status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, club=club)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# -------------------------
# EVENT VIEWSET
# -------------------------
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('date')
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def rsvp(self, request, pk=None):
        event = self.get_object()
        user = request.user
        if user in event.attendees.all():
            event.attendees.remove(user)
            return Response({"detail": f"You have cancelled your RSVP to {event.title}."})
        else:
            event.attendees.add(user)
            return Response({"detail": f"You have RSVP'd to {event.title}."})

# -------------------------
# POLL VIEWSET
# -------------------------
class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        poll = self.get_object()
        option_id = request.data.get("option")
        option = get_object_or_404(PollOption, id=option_id)

        if any(request.user in opt.votes.all() for opt in poll.options.all()):
            return Response({"detail": "You have already voted in this poll."}, status=400)

        option.votes.add(request.user)
        return Response({"detail": "Vote recorded successfully."})

# -------------------------
# STUDENT DASHBOARD
# -------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_dashboard_api(request):
    user = request.user
    if not is_student(user):
        return Response({"detail": "Not authorized."}, status=403)

    user_clubs = user.clubs.all()
    upcoming_events = Event.objects.filter(club__in=user_clubs, date__gte=timezone.now()).order_by('date')[:5]
    recent_posts = ClubPost.objects.filter(club__in=user_clubs).order_by('-created_at')[:5]
    active_polls = Poll.objects.filter(club__in=user_clubs).order_by('-created_at')[:3]

    rsvp_events_count = Event.objects.filter(attendees=user, date__gte=timezone.now()).count()
    voted_polls_count = sum(
        1 for poll in Poll.objects.filter(club__in=user_clubs)
        if any(user in opt.votes.all() for opt in poll.options.all())
    )

    data = {
        "total_clubs": user_clubs.count(),
        "upcoming_events_count": upcoming_events.count(),
        "rsvp_events": rsvp_events_count,
        "voted_polls": voted_polls_count,
        "recent_posts": ClubPostSerializer(recent_posts, many=True).data,
        "active_polls": PollSerializer(active_polls, many=True).data,
        "upcoming_events": EventSerializer(upcoming_events, many=True).data,
    }
    return Response(data)

# -------------------------
# REPORTS API
# -------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_saved_reports_api(request):
    reports = get_my_reports(request.user.id)
    return Response({"reports": reports})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_report_cloud_api(request):
    report_type = request.data.get('report_type', 'clubs')

    if report_type == 'clubs':
        csv_data = generate_my_clubs_report(request.user)
    elif report_type == 'events':
        csv_data = generate_my_events_report(request.user)
    elif report_type == 'grades':
        csv_data = generate_my_grades_report(request.user)
    else:
        return Response({"error": "Invalid report type"}, status=400)

    filename = f"student_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    result = upload_to_supabase(csv_data, filename, request.user.id)
    return Response(result)

# -------------------------
# ADMIN / LECTURER EXPORT
# -------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_all_data_api(request):
    user = request.user
    if not is_admin_or_lecturer(user):
        return Response({"detail": "Not authorized."}, status=403)

    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['=== CLUBS ==='])

    clubs = Club.objects.annotate(
        member_count=Count('members'),
        event_count=Count('events'),
        post_count=Count('posts')
    )

    for club in clubs:
        writer.writerow([club.name, club.description, club.member_count, club.event_count, club.post_count])

    output.seek(0)
    return Response({"csv": output.getvalue()})
