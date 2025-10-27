import pytest
from clubs.models import Club

@pytest.mark.django_db
def test_club_str_and_fields(club):
    assert str(club) == club.name
    assert club.meeting_time  # not blank