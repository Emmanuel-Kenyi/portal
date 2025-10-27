import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from clubs.models import Club

User = get_user_model()

# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def create_user(db, django_user_model):
    """Factory fixture to create users with optional profile role."""
    def make_user(username, password="testpass", role=None, email=None, is_superuser=False):
        email = email or f"{username}@example.com"
        user = django_user_model.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_superuser=is_superuser,
            is_staff=is_superuser
        )

        # If a Profile model exists on the user, ensure role is set
        try:
            if hasattr(user, "profile") and role:
                user.profile.role = role
                user.profile.save()
        except Exception:
            # ignore if profile relationship is not present / not configured
            pass

        return user
    return make_user

@pytest.fixture
def student_user(create_user):
    return create_user("alice", role="student")

@pytest.fixture
def lecturer_user(create_user):
    return create_user("bob", role="lecturer")

@pytest.fixture
def admin_user(create_user, db):
    # try to ensure Profile exists if app provides it, otherwise rely on create_user
    user = create_user("admin", role="admin", is_superuser=True)
    try:
        from users.models import Profile
        if not hasattr(user, "profile"):
            Profile.objects.create(user=user, role="admin")
    except Exception:
        pass
    return user

@pytest.fixture
def club(db):
    # create club with fields present in clubs.models (name, description, meeting_time)
    return Club.objects.create(
        name="AI Club",
        description="Artificial Intelligence enthusiasts",
        meeting_time="Wednesdays 17:00"
    )

# -----------------------------
# Authentication Tests
# -----------------------------
@pytest.mark.django_db
def test_user_can_login(client, student_user):
    assert client.login(username="alice", password="testpass") is True

@pytest.mark.django_db
def test_login_view(client, student_user):
    url = reverse("login")  # adjust if your URL name differs
    resp = client.post(url, {"username": "alice", "password": "testpass"})
    assert resp.status_code in (200, 302)

# -----------------------------
# Authorization / Access Tests
# -----------------------------
@pytest.mark.django_db
def test_unauthorized_student_dashboard_redirect(client):
    url = reverse("student_dashboard")
    resp = client.get(url)
    assert resp.status_code == 302
    assert "/login/" in resp.url

@pytest.mark.django_db
def test_student_dashboard_access(client, student_user):
    client.login(username="alice", password="testpass")
    url = reverse("student_dashboard")
    resp = client.get(url)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_lecturer_dashboard_access(client, lecturer_user):
    client.login(username="bob", password="testpass")
    url = reverse("lecturer_dashboard")
    resp = client.get(url)
    assert resp.status_code == 200

@pytest.mark.django_db
def test_admin_manage_clubs_access(client, admin_user):
    client.login(username="admin", password="testpass")
    url = reverse("manage_clubs")
    resp = client.get(url)
    # admin should be allowed (200) or redirected to admin dashboard (302) depending on your view
    assert resp.status_code in (200, 302)