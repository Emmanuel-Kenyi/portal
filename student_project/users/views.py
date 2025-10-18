from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.contrib.auth.models import User
from datetime import timedelta
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
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'lecturer':
        messages.error(request, 'Only lecturers can view reports.')
        return redirect('dashboard')

    clubs = Club.objects.all().annotate(
        member_count=Count('members'),
        event_count=Count('events'),
        post_count=Count('posts'),
        poll_count=Count('polls')
    )
    total_rsvps = Event.objects.aggregate(total=Count('attendees'))['total'] or 0
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
