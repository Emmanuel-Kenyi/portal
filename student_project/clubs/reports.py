import csv
import io
from datetime import datetime
from django.conf import settings

# -------------------------
# SUPABASE CLIENT
# -------------------------
try:
    from supabase import create_client
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
except Exception:
    supabase = None

# -------------------------
# CSV GENERATORS
# -------------------------

def generate_my_clubs_report(user):
    """Generate CSV of student's clubs"""
    from clubs.models import Club

    user_clubs = Club.objects.filter(members=user)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Club Name', 'Members Count', 'Status'])

    for club in user_clubs:
        writer.writerow([
            club.name,
            club.members.count(),
            'Active'
        ])

    return output.getvalue()


def generate_my_events_report(user):
    """Generate CSV of student's events"""
    from clubs.models import Event

    events = Event.objects.filter(attendees=user).select_related('club')
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Event Name', 'Club', 'Date', 'Location'])

    for e in events:
        writer.writerow([
            e.name,
            e.club.name,
            e.date.strftime('%Y-%m-%d'),
            getattr(e, 'location', getattr(e, 'venue', 'TBD'))
        ])

    return output.getvalue()


def generate_my_grades_report(user):
    """Generate CSV of student's grades"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Course Name', 'Marks', 'Grade', 'Semester'])

    try:
        courses = []
        # Try multiple possible models
        for model_name in ['StudentCourse', 'Grade', 'Mark']:
            try:
                model = __import__('users.models', fromlist=[model_name]).__dict__[model_name]
                courses = model.objects.filter(student=user)
                if courses.exists():
                    break
            except Exception:
                continue

        if not courses:
            writer.writerow(['No courses found for this student', '', '', ''])
        else:
            for c in courses:
                course_name = getattr(c, 'course', getattr(c, 'course_name', 'N/A'))
                if hasattr(course_name, 'name'):
                    course_name = course_name.name

                writer.writerow([
                    course_name,
                    getattr(c, 'marks', getattr(c, 'mark', 'N/A')),
                    getattr(c, 'grade_letter', getattr(c, 'grade', 'N/A')),
                    getattr(c, 'semester', 'N/A')
                ])

    except Exception as e:
        writer.writerow([f'Error: {str(e)}', '', '', ''])

    return output.getvalue()


# -------------------------
# SUPABASE STORAGE FUNCTIONS
# -------------------------

def upload_to_supabase(csv_data, filename, user_id):
    """Upload CSV to Supabase Storage using service role key"""
    if not supabase:
        return {'success': False, 'error': 'Supabase not configured'}

    try:
        bucket_name = "student-reports"
        file_path = f"student_{user_id}/{filename}"

        # Upload file
        supabase.storage.from_(bucket_name).upload(
            path=file_path,
            file=csv_data.encode('utf-8')
        )

        # Get public URL (returned as a string now)
        url = supabase.storage.from_(bucket_name).get_public_url(file_path)

        return {'success': True, 'url': url}

    except Exception as e:
        return {'success': False, 'error': str(e)}



def get_my_reports(user_id):
    """List all reports for a student"""
    if not supabase:
        return []

    try:
        folder = f"student_{user_id}"
        bucket_name = "student-reports"
        files = supabase.storage.from_(bucket_name).list(folder)

        for file in files:
            file['url'] = supabase.storage.from_(bucket_name).get_public_url(
                f"{folder}/{file['name']}"
            ).public_url

        return files
    except Exception as e:
        print(f"Error listing files: {e}")
        return []
