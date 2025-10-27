import pytest

def compute_gpa(grade_points):
    """Compute GPA given a list of grade points."""
    if not grade_points:
        return 0.0
    return sum(grade_points) / len(grade_points)

@pytest.mark.django_db
def test_gpa_computation():
    """Test GPA calculation logic."""
    grades = [4.0, 3.0, 3.5]
    gpa = compute_gpa(grades)
    assert round(gpa, 2) == 3.5

@pytest.mark.django_db
def test_gpa_empty_list():
    """GPA should be 0.0 if no grades are provided."""
    gpa = compute_gpa([])
    assert gpa == 0.0

@pytest.mark.django_db
def test_gpa_varied_grades():
    """Test GPA computation with varied grade points."""
    grades = [2.5, 3.0, 3.5, 4.0]
    gpa = compute_gpa(grades)
    assert round(gpa, 2) == 3.25
