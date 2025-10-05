from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Count
from django.contrib import messages
from .models import Club, ClubPost, Poll, PollOption, Event
from .forms import ClubPostForm

# -------------------------
# ROLE CHECKS
# -------------------------
def is_admin(user):
    return hasattr(user, "profile") and user.profile.role == "admin"


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
    }
    return render(request, 'users/my_activity.html', context)


@login_required
def events_list(request):
    """List all upcoming events"""
    user = request.user
    user_clubs = user.clubs.all()
    
    # All upcoming events
    all_events = Event.objects.filter(
        date__gte=timezone.now()
    ).order_by('date')
    
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

# -------------------------
# STUDENT VIEWS
# -------------------------

@login_required
def club_list(request):
    clubs = Club.objects.all()
    return render(request, "clubs/club_list.html", {"clubs": clubs})


@login_required
def club_detail(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    posts = club.posts.all()
    polls = club.polls.all()
    events = club.events.order_by("date")
    return render(request, "clubs/club_detail.html", {
        "club": club,
        "posts": posts,
        "polls": polls,
        "events": events
    })


@login_required
def toggle_membership(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.user in club.members.all():
        club.members.remove(request.user)
    else:
        club.members.add(request.user)
    
    # Redirect to dashboard if coming from there, otherwise to club detail
    next_url = request.GET.get('next', 'club_detail')
    if next_url == 'student_dashboard':
        return redirect('student_dashboard')
    return redirect("club_detail", club_id=club.id)


@login_required
def new_post(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.method == "POST":
        form = ClubPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.club = club
            post.author = request.user
            post.save()
            return redirect("club_detail", club_id=club.id)
    else:
        form = ClubPostForm()
    return render(request, "clubs/new_post.html", {"form": form, "club": club})


@login_required
def vote_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if request.method == "POST":
        option_id = request.POST.get("option")
        option = get_object_or_404(PollOption, id=option_id)

        # Prevent multiple votes per student
        for opt in poll.options.all():
            if request.user in opt.votes.all():
                raise PermissionDenied("You have already voted in this poll.")

        option.votes.add(request.user)
        return redirect("club_detail", club_id=poll.club.id)

    return render(request, "clubs/poll_vote.html", {"poll": poll})


@login_required
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user in event.attendees.all():
        event.attendees.remove(request.user)
    else:
        event.attendees.add(request.user)
    
    # Redirect to dashboard if coming from there
    next_url = request.GET.get('next', 'club_detail')
    if next_url == 'student_dashboard':
        return redirect('student_dashboard')
    return redirect("club_detail", club_id=event.club.id)


# -------------------------
# ADMIN VIEWS
# -------------------------

@user_passes_test(is_admin)
def manage_clubs(request):
    """Admin: view all clubs for management."""
    clubs = Club.objects.all()
    return render(request, "clubs/manage_clubs.html", {"clubs": clubs})


@user_passes_test(is_admin)
def delete_post(request, post_id):
    """Admin: delete a specific club post."""
    post = get_object_or_404(ClubPost, id=post_id)
    club_id = post.club.id
    post.delete()
    return redirect("club_detail", club_id=club_id)