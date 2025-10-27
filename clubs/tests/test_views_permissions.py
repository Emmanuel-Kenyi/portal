import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_download_clubs_requires_login(client):
    url = reverse("download_clubs_report")
    resp = client.get(url)
    assert resp.status_code == 302 and "/login/" in resp.url

# Test admin/lecturer access:
@pytest.mark.django_db
def test_download_clubs_as_admin(client, admin_user):
    client.login(username="admin", password="testpass")
    resp = client.get(reverse("download_clubs_report"))
    assert resp.status_code in (200, 302)