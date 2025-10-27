from unittest.mock import patch
import pytest

def test_report_tasks_starts_thread():
    with patch("users.report_tasks.threading.Thread") as mock_thread:
        from users import report_tasks
        report_tasks.start_report_worker()  # whatever function triggers thread
        mock_thread.assert_called()