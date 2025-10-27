import os
import json
import threading
from datetime import datetime, timedelta   # added timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.contrib.auth.models import User
from clubs.models import Club, Event, Poll, ClubPost, PollOption
from .models import Profile, StudentPoints, Course, StudentMark, StudentGPA
from .utils import calculate_gpa, get_grade_point as get_grade_and_point


# -------------------------
# Custom Login View
# -------------------------
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


# -------------------------
# Role-based dashboards
# -------------------------
@login_required
def dashboard_redirect(request):
    profile = getattr(request.user, "profile", None)
    if not profile:
        profile = Profile.objects.create(
            user=request.user, role="student", name=request.user.username
        )

    role = profile.role.lower()
    if role == "student":
        return redirect("student_dashboard")
    elif role == "lecturer":
        return redirect("lecturer_dashboard")
    elif role == "admin":
        return redirect("admin_dashboard")
    return redirect("login")

@login_required
def student_dashboard(request):
    user = request.user
    user_clubs = user.clubs.all()
    upcoming_events = Event.objects.filter(
        club__in=user_clubs, date__gte=timezone.now()
    ).order_by('date')[:5]
    recent_posts = ClubPost.objects.filter(club__in=user_clubs).order_by('-created_at')[:5]
    active_polls = Poll.objects.filter(club__in=user_clubs).order_by('-created_at')[:3]
    total_clubs = user_clubs.count()
    upcoming_events_count = upcoming_events.count()
    rsvp_events = Event.objects.filter(attendees=user, date__gte=timezone.now()).count()
    voted_polls = sum(
        1 for poll in Poll.objects.filter(club__in=user_clubs)
        if poll.options.filter(votes=user).exists()
    )
    
    # Fetch student's marks and GPA record
    student_courses = StudentMark.objects.filter(student=user).select_related('course')
    gpa_record = StudentGPA.objects.filter(student=user).last()
    gpa = gpa_record.gpa if gpa_record else 0.0
    cgpa = gpa_record.cgpa if gpa_record else 0.0

    context = {
        'user_clubs': user_clubs,
        'upcoming_events': upcoming_events,
        'recent_posts': recent_posts,
        'active_polls': active_polls,
        'total_clubs': total_clubs,
        'upcoming_events_count': upcoming_events_count,
        'rsvp_events': rsvp_events,
        'voted_polls': voted_polls,
        'student_courses': student_courses,
        'gpa': gpa,
        'cgpa': cgpa,
    }
    return render(request, "users/student_dashboard.html", context)


@login_required
def lecturer_dashboard(request):
    clubs = Club.objects.all()
    total_clubs = clubs.count()
    total_students = Profile.objects.filter(role='student').count()
    active_polls = Poll.objects.all()
    active_polls_count = active_polls.count()
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    upcoming_events_count = upcoming_events.count()
    recent_posts = ClubPost.objects.all().order_by('-created_at')

    context = {
        'clubs': clubs,
        'total_clubs': total_clubs,
        'total_students': total_students,
        'active_polls': active_polls,
        'active_polls_count': active_polls_count,
        'upcoming_events': upcoming_events,
        'upcoming_events_count': upcoming_events_count,
        'recent_posts': recent_posts,
    }
    return render(request, "users/lecturer_dashboard.html", context)


@login_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_students = Profile.objects.filter(role='student').count()
    total_lecturers = Profile.objects.filter(role='lecturer').count()
    total_admins = Profile.objects.filter(role='admin').count()
    total_clubs = Club.objects.count()
    total_events = Event.objects.count()
    total_posts = ClubPost.objects.count()
    clubs = Club.objects.all()
    recent_posts = ClubPost.objects.all().order_by('-created_at')
    active_sessions = User.objects.filter(is_active=True).count()

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'total_admins': total_admins,
        'total_clubs': total_clubs,
        'total_events': total_events,
        'total_posts': total_posts,
        'clubs': clubs,
        'recent_posts': recent_posts,
        'active_sessions': active_sessions,
    }
    return render(request, "users/admin_dashboard.html", context)


# -------------------------
# Manage Posts (Admin/Lecturer)
# -------------------------
@login_required
def manage_posts(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() not in ['admin', 'lecturer']:
        messages.error(request, "You do not have permission to manage posts.")
        return redirect('dashboard')

    search_query = request.GET.get('search', '')
    club_filter = request.GET.get('club', '')
    author_filter = request.GET.get('author', '')

    posts = ClubPost.objects.all().order_by('-created_at')

    if search_query:
        posts = posts.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    if club_filter:
        posts = posts.filter(club__id=club_filter)
    if author_filter:
        posts = posts.filter(author__id=author_filter)

    total_posts = ClubPost.objects.count()
    today_posts = ClubPost.objects.filter(created_at__date=timezone.now().date()).count()
    week_posts = ClubPost.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    total_clubs = Club.objects.count()

    active_clubs = Club.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:5]
    active_authors = User.objects.annotate(post_count=Count('clubpost')).order_by('-post_count')[:5]

    clubs = Club.objects.all()
    authors = User.objects.all()

    context = {
        'posts': posts,
        'total_posts': total_posts,
        'today_posts': today_posts,
        'week_posts': week_posts,
        'total_clubs': total_clubs,
        'active_clubs': active_clubs,
        'active_authors': active_authors,
        'clubs': clubs,
        'authors': authors,
        'search_query': search_query,
        'club_filter': club_filter,
        'author_filter': author_filter,
    }
    return render(request, 'users/manage_posts.html', context)


@login_required
def delete_post(request, post_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() not in ['admin', 'lecturer']:
        messages.error(request, "You do not have permission to delete posts.")
        return redirect('dashboard')

    post = get_object_or_404(ClubPost, id=post_id)
    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect('manage_posts')


# -------------------------
# Student Activity & Events
# -------------------------
@login_required
def my_activity(request):
    user = request.user
    user_clubs = user.clubs.all().annotate(
        post_count=Count('posts', filter=Q(posts__author=user))
    )
    rsvp_events = Event.objects.filter(attendees=user).order_by('date')
    voted_polls = [poll for poll in Poll.objects.filter(club__in=user_clubs)
                   if poll.options.filter(votes=user).exists()]
    user_posts = ClubPost.objects.filter(author=user).order_by('-created_at')

    context = {
        'user_clubs': user_clubs,
        'rsvp_events': rsvp_events,
        'voted_polls': voted_polls,
        'user_posts': user_posts,
    }
    return render(request, 'users/my_activity.html', context)


@login_required
def events_list(request):
    user = request.user
    user_clubs = user.clubs.all()
    all_events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    my_clubs_events = all_events.filter(club__in=user_clubs)
    rsvp_events = all_events.filter(attendees=user)

    context = {
        'all_events': all_events,
        'my_clubs_events': my_clubs_events,
        'rsvp_events': rsvp_events,
    }
    return render(request, 'users/events_list.html', context)


@login_required
def send_feedback(request):
    if request.method == 'POST':
        messages.success(request, 'Your feedback has been submitted successfully!')
        return redirect('student_dashboard')
    return render(request, 'users/send_feedback.html')


# -------------------------
# Poll Management (Lecturer)
# -------------------------
@login_required
def create_poll(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'lecturer':
        messages.error(request, 'Only lecturers can create polls.')
        return redirect('dashboard')

    if request.method == 'POST':
        club_id = request.POST.get('club')
        question = request.POST.get('question')
        options = [v.strip() for k, v in request.POST.items() if k.startswith('option_') and v.strip()]

        if club_id and question and len(options) >= 2:
            club = get_object_or_404(Club, id=club_id)
            poll = Poll.objects.create(club=club, question=question, created_by=request.user)
            for option_text in options:
                PollOption.objects.create(poll=poll, text=option_text)
            messages.success(request, f'Poll "{question}" created successfully with {len(options)} options!')
            return redirect('lecturer_dashboard')
        else:
            messages.error(request, 'Please fill in the club, question, and at least 2 options.')

    clubs = Club.objects.all()
    return render(request, 'users/create_poll.html', {'clubs': clubs})


# -------------------------
# Announcements, Reports & Analytics
# -------------------------
@login_required
def announcements(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'lecturer':
        messages.error(request, 'Only lecturers can post announcements.')
        return redirect('dashboard')
    return render(request, 'clubs/post_announcement.html')



@login_required
def reports(request):
    # Only lecturers can view
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'lecturer':
        messages.error(request, 'Only lecturers can view reports.')
        return redirect('dashboard')

    # Fetch clubs and annotate counts
    clubs = Club.objects.all().annotate(
        member_count=Count('members'),
        event_count=Count('events'),
        post_count=Count('posts'),
        poll_count=Count('polls')
    )

    # Calculate raw engagement score for each club
    for club in clubs:
        club.raw_score = (
            club.member_count * 0.2 +
            club.event_count * 0.3 +
            club.post_count * 0.3 +
            club.poll_count * 0.2
        )

    # Normalize scores to 100%
    max_score = max([club.raw_score for club in clubs], default=1)  # prevent division by zero
    for club in clubs:
        club.engagement_percentage = (club.raw_score / max_score) * 100

    # Total RSVPs
    total_rsvps = Event.objects.aggregate(total=Count('attendees'))['total'] or 0

    # Recent events & polls
    recent_events = Event.objects.order_by('-date')[:5]
    recent_polls = Poll.objects.order_by('-created_at')[:5]
    for poll in recent_polls:
        poll.total_votes = sum(option.votes.count() for option in poll.options.all())

    context = {
        'clubs': clubs,
        'total_clubs': clubs.count(),
        'total_students': Profile.objects.filter(role='student').count(),
        'total_events': Event.objects.count(),
        'total_polls': Poll.objects.count(),
        'total_rsvps': total_rsvps,
        'recent_events': recent_events,
        'recent_polls': recent_polls,
    }

    return render(request, 'users/reports.html', context)


# -------------------------
# Student Points
# -------------------------
@login_required
def award_points(request, club_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'lecturer':
        messages.error(request, 'Only lecturers can award points.')
        return redirect('dashboard')

    club = get_object_or_404(Club, id=club_id)
    if request.method == 'POST':
        student_id = request.POST.get('student')
        points = request.POST.get('points')
        reason = request.POST.get('reason')
        if student_id and points and reason:
            student = get_object_or_404(User, id=student_id)
            StudentPoints.objects.create(
                student=student, club=club, points=int(points), reason=reason, awarded_by=request.user
            )
            messages.success(request, f'Successfully awarded {points} points to {student.username}!')
            return redirect('award_points', club_id=club_id)

    members = club.members.all()
    recent_awards = StudentPoints.objects.filter(club=club).order_by('-awarded_at')[:10]
    return render(request, 'users/award_points.html', {'club': club, 'members': members, 'recent_awards': recent_awards})


@login_required
def student_points_summary(request):
    user = request.user
    points_history = StudentPoints.objects.filter(student=user).order_by('-awarded_at')
    total_points = sum(p.points for p in points_history)
    points_by_club = StudentPoints.objects.filter(student=user).values('club__name').annotate(total=Sum('points')).order_by('-total')

    return render(request, 'users/student_points.html', {
        'points_history': points_history,
        'total_points': total_points,
        'points_by_club': points_by_club,
    })


# -------------------------
# User Management (Admin)
# -------------------------
@login_required
def manage_users(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'admin':
        messages.error(request, 'Only admins can manage users.')
        return redirect('dashboard')

    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    users = User.objects.all().order_by('-date_joined')
    if search_query:
        users = users.filter(Q(username__icontains=search_query) | Q(profile__name__icontains=search_query))
    if role_filter:
        users = users.filter(profile__role=role_filter)
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

    recent_users = User.objects.all().order_by('-date_joined')[:5]
    week_ago = timezone.now() - timedelta(days=7)
    active_this_week = User.objects.filter(last_login__gte=week_ago).count()

    return render(request, 'users/manage_users.html', {
        'users': users,
        'total_users': User.objects.count(),
        'total_students': Profile.objects.filter(role='student').count(),
        'total_lecturers': Profile.objects.filter(role='lecturer').count(),
        'total_admins': Profile.objects.filter(role='admin').count(),
        'recent_users': recent_users,
        'active_this_week': active_this_week,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
    })


@login_required
def edit_user(request, user_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'admin':
        messages.error(request, 'Only admins can edit users.')
        return redirect('dashboard')

    user_to_edit = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        role = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'

        user_to_edit.profile.name = name
        user_to_edit.profile.role = role
        user_to_edit.profile.save()
        user_to_edit.is_active = is_active
        user_to_edit.save()

        messages.success(request, f'User {user_to_edit.username} updated successfully!')
        return redirect('manage_users')

    return render(request, 'users/edit_user.html', {'user_to_edit': user_to_edit})


@login_required
def delete_user(request, user_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'admin':
        messages.error(request, 'Only admins can delete users.')
        return redirect('dashboard')

    user_to_delete = get_object_or_404(User, id=user_id)
    if user_to_delete.id == request.user.id:
        messages.error(request, 'You cannot delete your own account!')
        return redirect('manage_users')

    username = user_to_delete.username
    user_to_delete.delete()
    messages.success(request, f'User {username} has been deleted successfully!')
    return redirect('manage_users')


# -------------------------
# Signup view
# -------------------------
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, role="student", name=user.username)
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


# -------------------------
# Custom LogoutView
# -------------------------
class CustomLogoutView(LogoutView):
    next_page = "login"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

# -------------------------
# Academic (GPA/Marks)
# -------------------------
@login_required
def student_grades(request):
    user = request.user
    marks = StudentMark.objects.filter(student=user).select_related('course')
    gpa_record = StudentGPA.objects.filter(student=user).last()
    return render(request, "users/student_grades.html", {
        'marks': marks,
        'gpa': gpa_record.gpa if gpa_record else 0.0,
        'cgpa': gpa_record.cgpa if gpa_record else 0.0,
    })


@login_required
def lecturer_add_mark(request):
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role.lower() != "lecturer":
        messages.error(request, "Only lecturers can add marks.")
        return redirect("dashboard")

    # Handle POST (save marks)
    if request.method == "POST":
        student_id = request.POST.get("student")
        course_id = request.POST.get("course")
        marks = request.POST.get("marks")

        if not (student_id and course_id and marks):
            messages.error(request, "All fields are required.")
            return redirect("lecturer_add_mark")

        try:
            student = User.objects.get(id=student_id)
            course = Course.objects.get(id=course_id)
        except (User.DoesNotExist, Course.DoesNotExist):
            messages.error(request, "Invalid student or course.")
            return redirect("lecturer_add_mark")

        # Convert marks and calculate grade details
        marks = float(marks)
        grade_point, grade_letter, remarks = get_grade_and_point(marks)

        # Save or update the student's mark
        StudentMark.objects.update_or_create(
            student=student,
            course=course,
            defaults={
                "marks": marks,
                "grade_point": grade_point,
                "grade_letter": grade_letter,
                "remarks": remarks,
            },
        )

        messages.success(
            request,
            f"Mark for {student.profile.name} in {course.name} saved successfully ({grade_letter})."
        )
        return redirect("lecturer_add_mark")

    # GET — load form
    students = User.objects.filter(profile__role="student").select_related("profile").order_by("profile__name")
    courses = Course.objects.all().order_by("name")
    student_marks = StudentMark.objects.all().select_related("student__profile", "course")

    context = {
        "students": students,
        "courses": courses,
        "student_marks": student_marks,
    }
    return render(request, "users/lecturer_add_mark.html", context)


@login_required
def edit_mark(request, mark_id):
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role.lower() != "lecturer":
        messages.error(request, "Only lecturers can edit marks.")
        return redirect("dashboard")

    mark = get_object_or_404(StudentMark, id=mark_id)

    if request.method == "POST":
        marks = request.POST.get("marks")
        if not marks:
            messages.error(request, "Marks are required.")
            return redirect("edit_mark", mark_id=mark_id)

        marks = float(marks)
        grade_point, grade_letter, remarks = get_grade_and_point(marks)

        mark.marks = marks
        mark.grade_point = grade_point
        mark.grade_letter = grade_letter
        mark.remarks = remarks
        mark.save()

        messages.success(request, f"Mark updated successfully for {mark.student.profile.name} in {mark.course.name}.")
        return redirect("lecturer_add_mark")

    context = {
        "mark": mark
    }
    return render(request, "users/edit_mark.html", context)


@login_required
def delete_mark(request, mark_id):
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role.lower() != "lecturer":
        messages.error(request, "Only lecturers can delete marks.")
        return redirect("dashboard")

    mark = get_object_or_404(StudentMark, id=mark_id)
    mark.delete()
    messages.success(request, f"Mark for {mark.student.profile.name} in {mark.course.name} deleted successfully!")
    return redirect("lecturer_add_mark")

@login_required
def grade_panel(request):
    user = request.user
    student_courses = StudentMark.objects.filter(student=user).select_related('course')
    gpa_record = StudentGPA.objects.filter(student=user).last()
    context = {
        'student_courses': student_courses,
        'gpa': gpa_record.gpa if gpa_record else 0.0,
        'cgpa': gpa_record.cgpa if gpa_record else 0.0,
    }
    return render(request, 'users/grade_panel.html', context)


# -------------------------
# Admin: Asynchronous Club Reports
# -------------------------
def generate_report_file(file_path):
    """Generate a detailed School Clubs Management report asynchronously."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from datetime import datetime

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(150, height - 50, "School Clubs Management System Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = height - 120

    # Section 1: Clubs Summary
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "1. Clubs Overview")
    y -= 25

    clubs = Club.objects.all()
    if not clubs.exists():
        c.setFont("Helvetica", 12)
        c.drawString(70, y, "No clubs found in the system.")
        y -= 20
    else:
        for club in clubs:
            members = club.members.count()
            events = Event.objects.filter(club=club).count()
            posts = ClubPost.objects.filter(club=club).count()
            polls = Poll.objects.filter(club=club).count()

            c.setFont("Helvetica-Bold", 12)
            c.drawString(70, y, f"- {club.name}")
            y -= 15

            c.setFont("Helvetica", 11)
            c.drawString(90, y, f"Description: {club.description[:80]}...")
            y -= 12
            c.drawString(90, y, f"Meeting Time: {club.meeting_time}")
            y -= 12
            c.drawString(90, y, f"Members: {members}, Events: {events}, Posts: {posts}, Polls: {polls}")
            y -= 25

            if y < 100:
                c.showPage()
                y = height - 100

    # Section 2: Upcoming Events
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "2. Upcoming Events")
    y -= 25
    events = Event.objects.filter(date__gte=timezone.now()).order_by("date")[:10]
    if not events:
        c.setFont("Helvetica", 12)
        c.drawString(70, y, "No upcoming events found.")
        y -= 20
    else:
        for event in events:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(70, y, f"- {event.name}")
            y -= 12
            c.setFont("Helvetica", 11)
            c.drawString(90, y, f"Club: {event.club.name} | Date: {event.date.strftime('%Y-%m-%d')} | Attendees: {event.attendees.count()}")
            y -= 20
            if y < 100:
                c.showPage()
                y = height - 100

    # Section 3: Active Polls
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "3. Active Polls")
    y -= 25
    polls = Poll.objects.all().order_by('-created_at')[:10]
    if not polls.exists():
        c.setFont("Helvetica", 12)
        c.drawString(70, y, "No active polls found.")
        y -= 20
    else:
        for poll in polls:
            total_votes = sum(option.votes.count() for option in poll.options.all())
            c.setFont("Helvetica-Bold", 12)
            c.drawString(70, y, f"- {poll.question}")
            y -= 12
            c.setFont("Helvetica", 11)
            c.drawString(90, y, f"Club: {poll.club.name} | Total Votes: {total_votes}")
            y -= 20
            if y < 100:
                c.showPage()
                y = height - 100

    # Section 4: Recent Club Posts
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "4. Recent Club Posts")
    y -= 25
    posts = ClubPost.objects.all().order_by('-created_at')[:10]
    if not posts.exists():
        c.setFont("Helvetica", 12)
        c.drawString(70, y, "No recent posts found.")
        y -= 20
    else:
        for post in posts:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(70, y, f"- {post.title}")
            y -= 12
            c.setFont("Helvetica", 11)
            c.drawString(90, y, f"Club: {post.club.name} | Author: {post.author.username} | {post.created_at.strftime('%Y-%m-%d')}")
            y -= 20
            if y < 100:
                c.showPage()
                y = height - 100

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "End of Report - Generated by School Clubs MS")

    c.save()


@login_required
def generate_report(request):
    """Triggered by admin to generate the School Clubs report asynchronously."""
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'admin':
        messages.error(request, "You are not authorized to generate reports.")
        return redirect('admin_dashboard')

    reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f"clubs_report_{timestamp}.pdf"
    file_path = os.path.join(reports_dir, filename)

    # Run in background thread
    thread = threading.Thread(target=generate_report_file, args=(file_path,))
    thread.start()

    messages.success(request, "Report generation started. Please refresh in a few seconds to download.")
    request.session['latest_report'] = filename
    return redirect('admin_dashboard')


@login_required
def download_report(request):
    """Allow admin to download the generated clubs report."""
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'admin':
        messages.error(request, "You are not authorized to download reports.")
        return redirect('admin_dashboard')

    filename = request.session.get('latest_report', None)
    if not filename:
        messages.error(request, "No recent report found. Please generate one first.")
        return redirect('admin_dashboard')

    file_path = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)

    messages.error(request, "Report file not found.")
    return redirect('admin_dashboard')

@login_required
def system_reports(request):
    return render(request, 'users/system_reports.html')

@login_required
def admin_settings(request):
    """Admin can manage system settings."""
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'admin':
        messages.error(request, "You are not authorized to access system settings.")
        return redirect('admin_dashboard')

    # Example: settings stored in a dictionary (you can use a model for persistent settings)
    system_settings = request.session.get('system_settings', {
        'site_name': 'School Clubs MS',
        'allow_registration': True,
    })

    if request.method == "POST":
        site_name = request.POST.get('site_name')
        allow_registration = request.POST.get('allow_registration') == 'on'

        system_settings['site_name'] = site_name
        system_settings['allow_registration'] = allow_registration

        request.session['system_settings'] = system_settings
        messages.success(request, "System settings updated successfully!")

    context = {
        'system_settings': system_settings
    }
    return render(request, 'users/admin_settings.html', context)

def upload_to_supabase(content: str, filename: str, user_id: int):
    """Minimal helper so tests can patch users.views.upload_to_supabase."""
    supabase_url = getattr(settings, "SUPABASE_URL", None)
    if supabase_url:
        return {"success": True, "url": f"{supabase_url}/fake/{filename}"}
    return {"success": False, "error": "supabase not configured"}

def is_admin(user):
    return hasattr(user, "profile") and getattr(user.profile, "role", "") == "admin"

@login_required
@require_http_methods(["POST"])
def admin_save_report_cloud(request):
    """
    Admin endpoint: builds a small stub report and uploads via upload_to_supabase.
    Returns JSON 200 on success or failure (no 500).
    """
    if not is_admin(request.user):
        return JsonResponse({"success": False, "error": "permission denied"}, status=403)

    report_type = request.POST.get("report_type", "clubs")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"admin_{report_type}_report_{timestamp}.txt"
    content = f"Admin {report_type} report\nGenerated by user {request.user.id} on {timestamp}\n"

    try:
        result = upload_to_supabase(content, filename, request.user.id)
    except Exception as exc:
        result = {"success": False, "error": str(exc)}

    payload = {
        "success": bool(result.get("success")),
        "filename": filename,
        "url": result.get("url") if result.get("success") else None,
        "error": result.get("error") if not result.get("success") else None,
    }
    return JsonResponse(payload, status=200)
