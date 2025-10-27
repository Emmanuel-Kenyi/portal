import pytest
from django.utils import timezone
from clubs.models import Club, Event
from django.contrib.auth.models import User
from users.models import Profile  # adjust if your profile is in a different app


# -----------------------------
# Club fixture
# -----------------------------
@pytest.fixture
def club(db):
    """
    Creates a sample Club instance with optional members and events.
    """
    club = Club.objects.create(
        name="AI Club",
        description="Artificial Intelligence enthusiasts",
        location="Tech Building 2",
        created_at=timezone.now() if hasattr(Club, "created_at") else None,
    )

    # Add a sample member if the Club model has a ManyToManyField to User
    user = User.objects.create_user(username='student1', password='test123')
    if hasattr(club, "members"):
        club.members.add(user)

    # Add a sample event if Event has a ForeignKey to Club
    if hasattr(club, "event_set"):
        Event.objects.create(
            title="AI Workshop",
            club=club,
            date=timezone.now() + timezone.timedelta(days=7),
            location="Tech Building 2",
        )

    return club


# -----------------------------
# User fixtures
# -----------------------------
@pytest.fixture
def student_user(db, django_user_model):
    user = django_user_model.objects.create_user(username="alice", password="testpass")
    # Ensure profile exists
    Profile.objects.create(user=user, role="student")
    return user

@pytest.fixture
def lecturer_user(db, django_user_model):
    user = django_user_model.objects.create_user(username="bob", password="testpass")
    Profile.objects.create(user=user, role="lecturer")
    return user

@pytest.fixture
def admin_user(db, django_user_model):
    user = django_user_model.objects.create_superuser(username="admin", password="testpass")
    Profile.objects.create(user=user, role="admin")
    return user
