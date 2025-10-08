from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from .models import Profile
from clubs.models import Club, Event, Poll, ClubPost, PollOption


# -------------------------
# Custom Login View
# -------------------------
def login_view(request):
    """
    Handle user login with AuthenticationForm.
    Redirects to role-based dashboard after login.
    """
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
    """
    Redirect user to their dashboard based on role.
    """
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
    """Student-specific dashboard with stats"""
    user = request.user
    
    # Get user's clubs
    user_clubs = user.clubs.all()
    
    # Get upcoming events from user's clubs
    upcoming_events = Event.objects.filter(
        club__in=user_clubs,
        date__gte=timezone.now()
    ).order_by('date')[:5]
    
    # Get recent posts from user's clubs
    recent_posts = ClubPost.objects.filter(
        club__in=user_clubs
    ).order_by('-created_at')[:5]
    
    # Get active polls from user's clubs
    active_polls = Poll.objects.filter(
        club__in=user_clubs
    ).order_by('-created_at')[:3]
    
    # Calculate stats
    total_clubs = user_clubs.count()
    upcoming_events_count = upcoming_events.count()
    
    # Count events user has RSVP'd to
    rsvp_events = Event.objects.filter(
        attendees=user,
        date__gte=timezone.now()
    ).count()
    
    # Count polls user has voted in
    voted_polls = 0
    for poll in Poll.objects.filter(club__in=user_clubs):
        if poll.options.filter(votes=user).exists():
            voted_polls += 1
    
    context = {
        'user_clubs': user_clubs,
        'upcoming_events': upcoming_events,
        'recent_posts': recent_posts,
        'active_polls': active_polls,
        'total_clubs': total_clubs,
        'upcoming_events_count': upcoming_events_count,
        'rsvp_events': rsvp_events,
        'voted_polls': voted_polls,
    }
    
    return render(request, "users/student_dashboard.html", context)


@login_required
def lecturer_dashboard(request):
    """Lecturer-specific dashboard with stats and data"""
    from django.contrib.auth.models import User
    
    # Get all clubs
    clubs = Club.objects.all()
    total_clubs = clubs.count()
    
    # Get total students (users with student role)
    total_students = Profile.objects.filter(role='student').count()
    
    # Get active polls
    active_polls = Poll.objects.all()
    active_polls_count = active_polls.count()
    
    # Get upcoming events
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    upcoming_events_count = upcoming_events.count()
    
    # Get recent posts
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
    """Admin-specific dashboard"""
    return render(request, "users/admin_dashboard.html")


# -------------------------
# NEW NAVIGATION VIEWS
# -------------------------

@login_required
def my_activity(request):
    """Student's activity page - shows their interactions"""
    user = request.user

    user_clubs = (
        user.clubs.all()
        .annotate(post_count=Count('posts', filter=Q(posts__author=user)))
    )

    rsvp_events = Event.objects.filter(attendees=user).order_by('date')

    voted_polls = []
    for poll in Poll.objects.filter(club__in=user_clubs):
        if poll.options.filter(votes=user).exists():
            voted_polls.append(poll)

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
    """List all upcoming events"""
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
    """Send feedback form"""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        category = request.POST.get('category')

        messages.success(request, 'Your feedback has been submitted successfully!')
        return redirect('student_dashboard')

    return render(request, 'users/send_feedback.html')


# -------------------------
# Poll Management (Lecturer)
# -------------------------

@login_required
def create_poll(request):
    """Create a new poll for a club"""
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'lecturer':
        messages.error(request, 'Only lecturers can create polls.')
        return redirect('dashboard')

    if request.method == 'POST':
        club_id = request.POST.get('club')
        question = request.POST.get('question')
        description = request.POST.get('description', '')
        end_date = request.POST.get('end_date')
        allow_multiple = request.POST.get('allow_multiple') == 'on'
        anonymous = request.POST.get('anonymous') == 'on'

        options = []
        for key, value in request.POST.items():
            if key.startswith('option_') and value.strip():
                options.append(value.strip())

        if club_id and question and len(options) >= 2:
            club = get_object_or_404(Club, id=club_id)
            
            poll = Poll.objects.create(
                club=club,
                question=question,
                created_by=request.user
            )

            for option_text in options:
                PollOption.objects.create(poll=poll, text=option_text)

            messages.success(request, f'Poll "{question}" created successfully with {len(options)} options!')
            return redirect('lecturer_dashboard')
        else:
            messages.error(request, 'Please fill in the club, question, and at least 2 options.')

    clubs = Club.objects.all()
    context = {'clubs': clubs}
    return render(request, 'users/create_poll.html', context)


# -------------------------
# Announcements (reuse clubs template)
# -------------------------

@login_required
def announcements(request):
    """Reuse clubs post_announcement template for lecturers"""
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'lecturer':
        messages.error(request, 'Only lecturers can post announcements.')
        return redirect('dashboard')
    
    return render(request, 'clubs/post_announcement.html')


# -------------------------
# Reports & Analytics (Lecturer)
# -------------------------

@login_required
def reports(request):
    """View reports and analytics for lecturers"""
    if not hasattr(request.user, 'profile') or request.user.profile.role.lower() != 'lecturer':
        messages.error(request, 'Only lecturers can view reports.')
        return redirect('dashboard')
    
    # Get all clubs and their stats
    clubs = Club.objects.all().annotate(
        member_count=Count('members'),
        event_count=Count('events'),
        post_count=Count('posts'),
        poll_count=Count('polls')
    )
    
    # Get total statistics
    total_clubs = clubs.count()
    total_students = Profile.objects.filter(role='student').count()
    total_events = Event.objects.count()
    total_polls = Poll.objects.count()
    
    # Get engagement stats
    total_rsvps = Event.objects.aggregate(
        total=Count('attendees')
    )['total'] or 0
    
    # Get recent activity
    recent_events = Event.objects.order_by('-date')[:5]
    recent_polls = Poll.objects.order_by('-created_at')[:5]
    
    context = {
        'clubs': clubs,
        'total_clubs': total_clubs,
        'total_students': total_students,
        'total_events': total_events,
        'total_polls': total_polls,
        'total_rsvps': total_rsvps,
        'recent_events': recent_events,
        'recent_polls': recent_polls,
    }
    
    return render(request, 'users/reports.html', context)


# -------------------------
# Signup view
# -------------------------
def signup(request):
    """
    Allow new users to register using Django's UserCreationForm.
    Automatically creates a Profile with role 'student'.
    """
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
# Custom LogoutView (GET allowed)
# -------------------------

class CustomLogoutView(LogoutView):
    next_page = "login"

    def get(self, request, *args, **kwargs):
        """Allow logout via GET requests"""
        return self.post(request, *args, **kwargs)