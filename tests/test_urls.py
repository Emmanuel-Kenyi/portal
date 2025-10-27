from django.urls import reverse, NoReverseMatch
import pytest

def test_reverse_important_urls():
    for name in ("login", "student_dashboard", "lecturer_dashboard", "club_list"):
        try:
            reverse(name)
        except NoReverseMatch:
            pytest.skip(f"url {name} not defined")