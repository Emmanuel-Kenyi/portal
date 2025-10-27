import pytest

from django.contrib.auth import get_user_model
from clubs.models import Club

User = get_user_model()


@pytest.fixture
def club(db, django_user_model):
    """Create a Club using fields present in clubs.models."""
    creator = django_user_model.objects.create_user(username="creator", password="testpass")
    return Club.objects.create(
        name="AI Club",  # test expectations expect "AI Club"
        description="A club for artificial intelligence enthusiasts.",
        meeting_time="Wednesdays 17:00",
        # do NOT include unknown fields such as location or created_at
    )


@pytest.fixture
def create_user(db, django_user_model):
    """Factory fixture to create users with optional profile role for tests."""
    def make_user(username, password="testpass", role=None, email=None, is_superuser=False):
        email = email or f"{username}@example.com"
        user = django_user_model.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_superuser=is_superuser,
            is_staff=is_superuser
        )
        # if your project uses a Profile model attached to User, set role if present
        try:
            if hasattr(user, "profile") and role:
                user.profile.role = role
                user.profile.save()
        except Exception:
            # ignore if Profile relation not configured in tests
            pass
        return user
    return make_user
