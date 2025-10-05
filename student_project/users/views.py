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
            return redirect('dashboard')  # role-based redirect
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
    """Student-specific dashboard"""
    return render(request, "users/student_dashboard.html")


@login_required
def lecturer_dashboard(request):
    """Lecturer-specific dashboard"""
    return render(request, "users/lecturer_dashboard.html")


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

    # Get user's joined clubs and annotate post count
    user_clubs = (
        user.clubs.all()
        .annotate(post_count=Count('posts', filter=Q(posts__author=user)))
    )

    # Get events user RSVP'd to
    rsvp_events = Event.objects.filter(attendees=user).order_by('date')

    # Get polls user voted in
    voted_polls = []
    for poll in Poll.objects.filter(club__in=user_clubs):
        if poll.options.filter(votes=user).exists():
            voted_polls.append(poll)

    # Get user's posts
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

    # All upcoming events
    all_events = Event.objects.filter(date__gte=timezone.now()).order_by('date')

    # Events from user's clubs
    my_clubs_events = all_events.filter(club__in=user_clubs)

    # Events user RSVP'd to
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
    next_page = "login"  # redirect after logout

    def get(self, request, *args, **kwargs):
        """Allow logout via GET requests"""
        return self.post(request, *args, **kwargs)



