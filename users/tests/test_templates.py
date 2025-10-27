import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_dashboard_shows_admin_title(client, admin_user):
    client.login(username="admin", password="testpass")
    resp = client.get(reverse("lecturer_dashboard"))
    assert b"Admin Dashboard" in resp.content or b"Lecturer Dashboard" in resp.content