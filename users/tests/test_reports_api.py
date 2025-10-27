import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_admin_save_report_cloud_endpoint(client, admin_user):
    client.login(username="admin", password="testpass")
    resp = client.post(reverse("admin_save_report_cloud"), {"report_type": "clubs"})
    assert resp.status_code == 200
    data = resp.json()
    assert "success" in data