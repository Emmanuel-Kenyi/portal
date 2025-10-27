# utils.py

def get_grade_point(mark):
    """Return grade point, letter grade, and remarks based on Makerere University grading system."""
    if mark >= 90:
        return 5.0, 'A+', 'Outstanding'
    elif mark >= 80:
        return 5.0, 'A', 'Excellent'
    elif mark >= 75:
        return 4.5, 'B+', 'Very Good'
    elif mark >= 70:
        return 4.0, 'B', 'Good'
    elif mark >= 65:
        return 3.5, 'C+', 'Fairly Good'
    elif mark >= 60:
        return 3.0, 'C', 'Fair'
    elif mark >= 55:
        return 2.5, 'D+', 'Pass'
    elif mark >= 50:
        return 2.0, 'D', 'Marginal Pass'
    elif mark >= 45:
        return 1.5, 'E', 'Fail'
    elif mark >= 40:
        return 1.0, 'F', 'Fail'
    else:
        return 0.0, 'F', 'Fail'


def calculate_gpa(marks_list):
    """
    Calculate GPA for one semester.
    marks_list: list of dicts, each with 'mark' and 'credit_units' keys
    Example:
        [
            {'mark': 85, 'credit_units': 3},
            {'mark': 73, 'credit_units': 4},
            {'mark': 62, 'credit_units': 2},
        ]
    """
    total_weighted_points = 0
    total_credits = 0

    for course in marks_list:
        grade_point, _, _ = get_grade_point(course['mark'])
        total_weighted_points += grade_point * course['credit_units']
        total_credits += course['credit_units']

    if total_credits == 0:
        return 0.0

    gpa = total_weighted_points / total_credits
    return round(gpa, 2)


def calculate_cgpa(all_semesters):
    """
    Calculate CGPA across multiple semesters.
    all_semesters: list of semester dicts, each containing a 'marks' list
    Example:
        [
            {'marks': [{'mark': 80, 'credit_units': 3}, {'mark': 70, 'credit_units': 4}]},
            {'marks': [{'mark': 65, 'credit_units': 3}, {'mark': 50, 'credit_units': 2}]}
        ]
    """
    total_weighted_points = 0
    total_credits = 0

    for semester in all_semesters:
        for course in semester['marks']:
            grade_point, _, _ = get_grade_point(course['mark'])
            total_weighted_points += grade_point * course['credit_units']
            total_credits += course['credit_units']

    if total_credits == 0:
        return 0.0

    cgpa = total_weighted_points / total_credits
    return round(cgpa, 2)
