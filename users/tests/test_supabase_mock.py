import pytest
from unittest.mock import patch

@pytest.mark.django_db
def test_upload_to_supabase_called(client, admin_user):
    client.login(username="admin", password="testpass")
    with patch("users.views.upload_to_supabase") as mock_upload:
        mock_upload.return_value = {"success": True, "url": "https://supabase/fake"}
        resp = client.post("/users/reports/admin-save/", {"report_type": "clubs"})
        assert resp.status_code == 200
        mock_upload.assert_called_once()