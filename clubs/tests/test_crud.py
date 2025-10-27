import pytest
from django.urls import reverse
from clubs.models import Club

# -----------------------------
# CRUD Tests for Clubs
# -----------------------------

@pytest.mark.django_db
def test_create_club(club):
    assert Club.objects.count() == 1
    assert club.name == "AI Club"

@pytest.mark.django_db
def test_update_club(club):
    club.name = "Robotics Club"
    club.save()
    club.refresh_from_db()
    assert club.name == "Robotics Club"

@pytest.mark.django_db
def test_delete_club(club):
    pk = club.pk
    club.delete()
    assert Club.objects.filter(pk=pk).count() == 0

@pytest.mark.django_db
def test_list_clubs(client, create_user, club):
    # authenticate since club_list view requires login
    user = create_user("viewer", role="student")
    client.login(username="viewer", password="testpass")

    url = reverse("club_list")
    response = client.get(url)
    assert response.status_code == 200
    assert club.name.encode() in response.content
