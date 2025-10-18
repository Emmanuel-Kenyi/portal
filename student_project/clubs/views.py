from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Count, Q  # Added Q import here
from django.contrib import messages
from datetime import timedelta
from .models import Club, ClubPost, Poll, PollOption, Event
from .forms import ClubPostForm

# -------------------------
# ROLE CHECKS
# -------------------------
def is_admin(user):
    return hasattr(user, "profile") and user.profile.role == "admin"


def is_lecturer(user):
    return hasattr(user, "profile") and user.profile.role == "lecturer"


def is_student(user):
    return hasattr(user, "profile") and user.profile.role == "student"


# -------------------------
# STUDENT DASHBOARD
# -------------------------

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    """Student dashboard with clubs, events, and stats."""
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
        for option in poll.options.all():
            if user in option.votes.all():
                voted_polls += 1
                break
    
    context = {
        'user': user,
        'user_clubs': user_clubs,
        'upcoming_events': upcoming_events,
        'recent_posts': recent_posts,
        'active_polls': active_polls,
        'total_clubs': total_clubs,
        'upcoming_events_count': upcoming_events_count,
        'rsvp_events': rsvp_events,
        'voted_polls': voted_polls,
    }
    
    return render(request, 'users/student_dashboard.html', context)


# -------------------------
# LECTURER DASHBOARD
# -------------------------

@login_required
@user_passes_test(is_lecturer)
def lecturer_dashboard(request):
    """Lecturer dashboard with clubs and statistics."""
    user = request.user
    
    # Get all clubs
    clubs = Club.objects.all()
    
    # Get upcoming events
    upcoming_events = Event.objects.filter(
        date__gte=timezone.now()
    ).order_by('date')[:5]
    
    # Get recent posts
    recent_posts = ClubPost.objects.all().order_by('-created_at')[:5]
    
    # Get active polls
    active_polls = Poll.objects.all().order_by('-created_at')[:4]
    
    # Calculate stats
    total_clubs = clubs.count()
    total_students = sum(club.members.count() for club in clubs)
    active_polls_count = active_polls.count()
    upcoming_events_count = upcoming_events.count()
    
    context = {
        'user': user,
        'clubs': clubs,
        'upcoming_events': upcoming_events,
        'recent_posts': recent_posts,
        'active_polls': active_polls,
        'total_clubs': total_clubs,
        'total_students': total_students,
        'active_polls_count': active_polls_count,
        'upcoming_events_count': upcoming_events_count,
    }
    
    return render(request, 'users/lecturer_dashboard.html', context)


# -------------------------
# NEW NAVIGATION VIEWS
# -------------------------

@login_required
def my_activity(request):
    """Student's activity page - shows their interactions"""
    user = request.user
    
    # Get user's joined clubs
    user_clubs = user.clubs.all()
    
    # Get events user RSVP'd to
    rsvp_events = Event.objects.filter(attendees=user).order_by('date')
    
    # Get polls user voted in
    voted_polls = []
    for poll in Poll.objects.filter(club__in=user_clubs):
        for option in poll.options.all():
            if user in option.votes.all():
                voted_polls.append(poll)
                break
    
    # Get user's posts
    user_posts = ClubPost.objects.filter(author=user).order_by('-created_at')
    
    context = {
        'user_clubs': user_clubs,
        'rsvp_events': rsvp_events,
        'voted_polls': voted_polls,
        'user_posts': user_posts,
        'feedback_count': 0,  # Add feedback model later if needed
    }
    return render(request, 'users/my_activity.html', context)


@login_required
def events_list(request):
    """List all upcoming events"""
    user = request.user
    
    # All events
    events = Event.objects.all().order_by('date')
    
    # Upcoming events
    upcoming_count = events.filter(date__gte=timezone.now()).count()
    
    # Events this month
    today = timezone.now()
    this_month_count = events.filter(
        date__year=today.year,
        date__month=today.month
    ).count()
    
    # Total attendees across all events
    total_attendees = sum(event.attendees.count() for event in events)
    
    # RSVP count for current user
    rsvp_count = events.filter(attendees=user).count()
    
    context = {
        'events': events,
        'upcoming_count': upcoming_count,
        'this_month_count': this_month_count,
        'total_attendees': total_attendees,
        'rsvp_count': rsvp_count,
        'today': timezone.now().date(),
    }
    return render(request, 'users/events_list.html', context)


@login_required
def send_feedback(request):
    """Send feedback page"""
    user = request.user
    user_clubs = user.clubs.all()
    
    if request.method == 'POST':
        # Handle feedback submission
        feedback_type = request.POST.get('feedback_type')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        club_id = request.POST.get('club')
        anonymous = request.POST.get('anonymous')
        
        # Here you would save to a Feedback model
        # For now, just show a success message
        messages.success(request, 'Your feedback has been submitted successfully!')
        return redirect('send_feedback')
    
    context = {
        'user_clubs': user_clubs,
        'previous_feedback': [],  # Add feedback model later
    }
    return render(request, 'users/send_feedback.html', context)


# -------------------------
# STUDENT VIEWS
# -------------------------

@login_required
def club_list(request):
    """List all clubs with role-based context"""
    clubs = Club.objects.all()
    user_clubs_count = request.user.clubs.count() if hasattr(request.user, 'clubs') else 0
    
    context = {
        'clubs': clubs,
        'user_clubs_count': user_clubs_count,
    }
    return render(request, "clubs/club_list.html", context)


@login_required
def club_detail(request, club_id):
    """Club detail page with all information"""
    club = get_object_or_404(Club, id=club_id)
    posts = club.posts.all().order_by('-created_at')
    polls = club.polls.all()
    events = club.events.filter(date__gte=timezone.now()).order_by("date")
    upcoming_events = events
    active_polls = polls
    
    context = {
        "club": club,
        "posts": posts,
        "polls": polls,
        "events": events,
        "upcoming_events": upcoming_events,
        "active_polls": active_polls,
    }
    return render(request, "clubs/club_detail.html", context)


@login_required
def toggle_membership(request, club_id):
    """Toggle club membership for students"""
    if request.user.profile.role != 'student':
        messages.error(request, 'Only students can join clubs.')
        return redirect('club_detail', club_id=club_id)
    
    club = get_object_or_404(Club, id=club_id)
    if request.user in club.members.all():
        club.members.remove(request.user)
        messages.success(request, f'You have left {club.name}.')
    else:
        club.members.add(request.user)
        messages.success(request, f'You have joined {club.name}!')
    
    # Redirect based on 'next' parameter
    next_url = request.GET.get('next', 'club_detail')
    if next_url == 'student_dashboard':
        return redirect('student_dashboard')
    elif next_url == 'club_list':
        return redirect('club_list')
    elif next_url == 'my_activity':
        return redirect('my_activity')
    elif next_url == 'club_detail':
        return redirect('club_detail', club_id=club.id)
    else:
        return redirect("club_detail", club_id=club.id)


@login_required
def new_post(request, club_id):
    """Create new post in club"""
    club = get_object_or_404(Club, id=club_id)
    
    # Check if user is a member
    if request.user not in club.members.all():
        messages.error(request, 'You must be a member to post.')
        return redirect('club_detail', club_id=club.id)
    
    if request.method == "POST":
        form = ClubPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.club = club
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect("club_detail", club_id=club.id)
    else:
        form = ClubPostForm()
    
    return render(request, "clubs/new_post.html", {"form": form, "club": club})


@login_required
def vote_poll(request, poll_id):
    """Vote on a poll"""
    poll = get_object_or_404(Poll, id=poll_id)

    if request.method == "POST":
        option_id = request.POST.get("option")
        option = get_object_or_404(PollOption, id=option_id)

        # Prevent multiple votes per student
        for opt in poll.options.all():
            if request.user in opt.votes.all():
                messages.error(request, "You have already voted in this poll.")
                return redirect("club_detail", club_id=poll.club.id)

        option.votes.add(request.user)
        messages.success(request, 'Your vote has been recorded!')
        return redirect("club_detail", club_id=poll.club.id)

    return render(request, "clubs/poll_vote.html", {"poll": poll})


@login_required
def rsvp_event(request, event_id):
    """RSVP to an event"""
    event = get_object_or_404(Event, id=event_id)
    
    if request.user in event.attendees.all():
        event.attendees.remove(request.user)
        messages.success(request, f'You have cancelled your RSVP to {event.title}.')
    else:
        event.attendees.add(request.user)
        messages.success(request, f'You have RSVP\'d to {event.title}!')
    
    # Redirect based on 'next' parameter
    next_url = request.GET.get('next', 'club_detail')
    if next_url == 'student_dashboard':
        return redirect('student_dashboard')
    elif next_url == 'my_activity':
        return redirect('my_activity')
    elif next_url == 'events_list':
        return redirect('events_list')
    elif next_url == 'club_detail':
        return redirect('club_detail', club_id=event.club.id)
    else:
        return redirect("club_detail", club_id=event.club.id)


# -------------------------
# LECTURER VIEWS
# -------------------------

@login_required
@user_passes_test(is_lecturer)
def create_poll(request):
    """Lecturer: Create a new poll"""
    clubs = Club.objects.all()
    
    if request.method == 'POST':
        club_id = request.POST.get('club')
        question = request.POST.get('question')
        description = request.POST.get('description', '')
        
        club = get_object_or_404(Club, id=club_id)
        
        # Create poll
        poll = Poll.objects.create(
            club=club,
            question=question,
            description=description,
            created_by=request.user
        )
        
        # Create poll options
        option_count = 1
        while f'option_{option_count}' in request.POST:
            option_text = request.POST.get(f'option_{option_count}')
            if option_text:
                PollOption.objects.create(poll=poll, text=option_text)
            option_count += 1
        
        messages.success(request, 'Poll created successfully!')
        return redirect('lecturer_dashboard')
    
    context = {
        'clubs': clubs,
    }
    return render(request, 'clubs/create_poll.html', context)


# -------------------------
# ADMIN VIEWS
# -------------------------

@user_passes_test(is_admin)
def manage_clubs(request):
    """Admin: view all clubs for management."""
    
    # Get all clubs with statistics
    clubs = Club.objects.all().annotate(
        member_count=Count('members'),
        event_count=Count('events'),
        post_count=Count('posts'),
        poll_count=Count('polls')
    )
    
    # Calculate totals
    total_members = sum(club.members.count() for club in clubs)
    total_events = Event.objects.count()
    total_posts = ClubPost.objects.count()
    total_activity = total_events + total_posts + Poll.objects.count()
    
    # Most popular clubs (by member count)
    popular_clubs = clubs.order_by('-member_count')[:5]
    
    # Most active clubs (by post count)
    active_clubs = clubs.order_by('-post_count')[:5]
    
    # Active clubs (with activity in last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    active_club_count = Club.objects.filter(
        Q(posts__created_at__gte=thirty_days_ago) |
        Q(events__date__gte=thirty_days_ago)
    ).distinct().count()
    
    context = {
        'clubs': clubs,
        'total_members': total_members,
        'total_events': total_events,
        'total_posts': total_posts,
        'total_activity': total_activity,
        'popular_clubs': popular_clubs,
        'active_clubs': active_clubs,
        'active_club_count': active_club_count,
    }
    
    return render(request, "clubs/manage_clubs.html", context)


@user_passes_test(is_admin)
def delete_post(request, post_id):
    """Admin: delete a specific club post."""
    post = get_object_or_404(ClubPost, id=post_id)
    club_id = post.club.id
    post.delete()
    messages.success(request, 'Post deleted successfully.')
    return redirect("club_detail", club_id=club_id)


# Club Creation (Lecturer)
# -------------------------
@login_required
def create_club(request):
    profile = getattr(request.user, "profile", None)
    if not profile or profile.role.lower() != "lecturer":
        messages.error(request, "Only lecturers can create clubs.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ClubForm(request.POST)
        if form.is_valid():
            club = form.save(commit=False)
            club.created_by = request.user 
            club.save()
            messages.success(request, f'Club "{club.name}" created successfully!')
            return redirect("club_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ClubForm()

    return render(request, "clubs/create_club.html", {"form": form})

