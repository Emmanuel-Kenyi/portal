from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import Profile, StudentPoints, StudentMark, StudentGPA, Course
from clubs.models import Club, Event, ClubPost, Poll, PollOption

# -------------------------
# USER & PROFILE
# -------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_active", "date_joined"]

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = "__all__"

# -------------------------
# CLUBS
# -------------------------
class ClubSerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField(source='members.count', read_only=True)
    
    class Meta:
        model = Club
        fields = "__all__"

# -------------------------
# EVENTS
# -------------------------
class EventSerializer(serializers.ModelSerializer):
    attendees_count = serializers.IntegerField(source='attendees.count', read_only=True)
    
    class Meta:
        model = Event
        fields = "__all__"

# -------------------------
# CLUB POSTS
# -------------------------
class ClubPostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    club_name = serializers.CharField(source='club.name', read_only=True)

    class Meta:
        model = ClubPost
        fields = "__all__"

# -------------------------
# POLLS
# -------------------------
class PollOptionSerializer(serializers.ModelSerializer):
    votes_count = serializers.IntegerField(source='votes.count', read_only=True)
    
    class Meta:
        model = PollOption
        fields = "__all__"

class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Poll
        fields = "__all__"

# -------------------------
# STUDENT ACADEMIC
# -------------------------
class StudentPointsSerializer(serializers.ModelSerializer):
    club_name = serializers.CharField(source='club.name', read_only=True)
    awarded_by_username = serializers.CharField(source='awarded_by.username', read_only=True)
    
    class Meta:
        model = StudentPoints
        fields = "__all__"

class StudentMarkSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source='student.username', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = StudentMark
        fields = "__all__"

class StudentGPASerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source='student.username', read_only=True)
    
    class Meta:
        model = StudentGPA
        fields = "__all__"

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"
