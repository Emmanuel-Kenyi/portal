from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Count, Q, Avg  
from django.contrib import messages
from datetime import timedelta
from .models import Club, ClubPost, Poll, PollOption, Event
from .forms import ClubPostForm
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from clubs.reports import (
    generate_my_clubs_report,
    generate_my_events_report,
    generate_my_grades_report,
    upload_to_supabase,
    get_my_reports
)

# Import for PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import csv
from django.views.decorators.http import require_http_methods
import os
from django.http import FileResponse
from django.conf import settings
from django.contrib.auth.models import User

# -------------------------
# ROLE CHECKS
# -------------------------
def is_admin(user):
    return hasattr(user, "profile") and user.profile.role == "admin"


def is_lecturer(user):
    return hasattr(user, "profile") and user.profile.role == "lecturer"


def is_student(user):
    return hasattr(user, "profile") and user.profile.role == "student"

# new helper: allow admin OR lecturer
def is_admin_or_lecturer(user):
    return hasattr(user, "profile") and getattr(user.profile, "role", "") in ("admin", "lecturer")


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
        'role': getattr(user, 'profile', None).role if hasattr(user, 'profile') else '',
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
    
    event_label = getattr(event, 'title', None) or getattr(event, 'name', 'Event')
    
    if request.user in event.attendees.all():
        event.attendees.remove(request.user)
        messages.success(request, f'You have cancelled your RSVP to {event_label}.')
    else:
        event.attendees.add(request.user)
        messages.success(request, f'You have RSVP\'d to {event_label}!')
    
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


# ============================================
# STUDENT REPORTS - CSV DOWNLOADS
# ============================================

@login_required
def download_my_clubs(request):
    """Download my clubs as CSV"""
    csv_data = generate_my_clubs_report(request.user)
    
    response = HttpResponse(csv_data, content_type='text/csv')
    filename = f"my_clubs_{datetime.now().strftime('%Y%m%d')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def download_my_events(request):
    """Download my events as CSV"""
    csv_data = generate_my_events_report(request.user)
    
    response = HttpResponse(csv_data, content_type='text/csv')
    filename = f"my_events_{datetime.now().strftime('%Y%m%d')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def download_my_grades(request):
    """Download my grades as CSV"""
    csv_data = generate_my_grades_report(request.user)
    
    response = HttpResponse(csv_data, content_type='text/csv')
    filename = f"my_grades_{datetime.now().strftime('%Y%m%d')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
@require_http_methods(["POST"])
def save_report_cloud(request):
    """Save student report to Supabase"""
    report_type = request.POST.get('report_type', 'clubs')
    
    # Generate report
    if report_type == 'clubs':
        csv_data = generate_my_clubs_report(request.user)
    elif report_type == 'events':
        csv_data = generate_my_events_report(request.user)
    elif report_type == 'grades':
        csv_data = generate_my_grades_report(request.user)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid report type'}, status=400)
    
    # Upload to Supabase
    filename = f"student_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    result = upload_to_supabase(csv_data, filename, request.user.id)
    
    return JsonResponse(result)


@login_required
def my_saved_reports(request):
    """View all saved reports for student"""
    reports = get_my_reports(request.user.id)
    
    return render(request, 'clubs/my_reports.html', {
        'reports': reports
    })


# ============================================
# LECTURER REPORTS - PDF DOWNLOADS
# ============================================

@login_required
@user_passes_test(is_admin_or_lecturer)   # was is_lecturer
def download_clubs_report(request):
    """Generate and download all clubs report as PDF"""
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="clubs_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Title
    elements.append(Paragraph("All Clubs Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Get clubs data
    clubs = Club.objects.annotate(
        member_count=Count('members'),
        event_count=Count('events')
    ).order_by('name')
    
    # Create table data
    data = [['Club Name', 'Members', 'Events', 'Description']]
    for club in clubs:
        desc = club.description[:50] + '...' if len(club.description) > 50 else club.description
        data.append([
            club.name,
            str(club.member_count),
            str(club.event_count),
            desc
        ])
    
    # Create table
    table = Table(data, colWidths=[2*inch, 1*inch, 1*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(f"<b>Total Clubs:</b> {clubs.count()}", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


@login_required
@user_passes_test(is_admin_or_lecturer)   # was is_lecturer
def download_students_report(request):
    """Generate and download students report as PDF"""
    from django.contrib.auth.models import User
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="students_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph("Students Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Get students data
    students = User.objects.filter(profile__role='student').annotate(
        club_count=Count('clubs')
    ).order_by('profile__name')
    
    # Create table data
    data = [['Student Name', 'Email', 'Clubs Joined', 'Reg. Number']]
    for student in students:
        reg_num = getattr(student.profile, 'registration_number', 'N/A')
        data.append([
            student.profile.name,
            student.email,
            str(student.club_count),
            reg_num
        ])
    
    table = Table(data, colWidths=[2*inch, 2*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(f"<b>Total Students:</b> {students.count()}", styles['Normal']))
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


@login_required
@user_passes_test(is_admin_or_lecturer)   # was is_lecturer
def download_events_report(request):
    """Generate and download events report as PDF"""
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="events_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph("Events Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Get events data
    events = Event.objects.annotate(
        attendee_count=Count('attendees')
    ).order_by('-date')
    
    # Create table data
    data = [['Event Title', 'Club', 'Date', 'Location', 'Attendees']]
    for event in events:
        data.append([
            event.title,
            event.club.name,
            event.date.strftime('%Y-%m-%d'),
            event.location[:30],
            str(event.attendee_count)
        ])
    
    table = Table(data, colWidths=[2*inch, 1.5*inch, 1*inch, 2*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(f"<b>Total Events:</b> {events.count()}", styles['Normal']))
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


@login_required
@user_passes_test(is_admin_or_lecturer)   # was is_lecturer
def download_polls_report(request):
    """Generate and download polls report as PDF"""
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="polls_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph("Polls Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Get polls data
    polls = Poll.objects.annotate(
        vote_count=Count('options__votes')
    ).order_by('-created_at')
    
    # Create table data
    data = [['Question', 'Club', 'Total Votes', 'Status', 'Created']]
    for poll in polls:
        status = 'Active' if getattr(poll, 'is_active', True) else 'Closed'
        question = poll.question[:40] + '...' if len(poll.question) > 40 else poll.question
        data.append([
            question,
            poll.club.name,
            str(poll.vote_count),
            status,
            poll.created_at.strftime('%Y-%m-%d')
        ])
    
    table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(f"<b>Total Polls:</b> {polls.count()}", styles['Normal']))
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


@login_required
@user_passes_test(is_admin_or_lecturer)   # was is_lecturer
def download_grades_report(request):
    """Generate and download grades report as PDF"""
    from django.contrib.auth.models import User

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="grades_report_{datetime.now().strftime("%Y%m%d")}.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    elements.append(Paragraph("Student Grades Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # Try to find StudentMark model
    StudentMark = None
    try:
        from .models import StudentMark
        StudentMark = StudentMark
    except Exception:
        StudentMark = None

    if StudentMark is None:
        try:
            from users.models import StudentMark as UM
            StudentMark = UM
        except Exception:
            StudentMark = None

    # If no StudentMark model found, show message
    if StudentMark is None:
        elements.append(Paragraph(
            "<b>Grades Module Not Available</b>",
            styles['Heading2']
        ))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(
            "The student grades functionality has not been configured yet. Please set up the StudentMark model to enable grades reporting.",
            styles['Normal']
        ))
    else:
        # Get students with grades
        students = User.objects.filter(profile__role='student')
        has_data = False

        for student in students[:20]:
            marks = StudentMark.objects.filter(student=student)
            if marks.exists():
                has_data = True
                elements.append(Paragraph(f"<b>{getattr(student.profile, 'name', student.username)}</b>", styles['Heading3']))

                data = [['Course', 'Marks', 'Grade', 'Grade Point']]
                for mark in marks:
                    data.append([
                        getattr(getattr(mark, 'course', None), 'name', 'N/A'),
                        str(getattr(mark, 'marks', 'N/A')),
                        getattr(mark, 'grade_letter', 'N/A'),
                        str(getattr(mark, 'grade_point', 'N/A'))
                    ])

                # Calculate GPA
                try:
                    avg_gpa = marks.aggregate(Avg('grade_point'))['grade_point__avg']
                    data.append(['', '', 'GPA:', f"{avg_gpa:.2f}" if avg_gpa else 'N/A'])
                except Exception:
                    data.append(['', '', 'GPA:', 'N/A'])

                table = Table(data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightyellow),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
                ]))

                elements.append(table)
                elements.append(Spacer(1, 0.2*inch))

        if not has_data:
            elements.append(Paragraph(
                "<b>No grades data available yet.</b>",
                styles['Heading2']
            ))
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(
                "Grades will appear here once lecturers have entered student marks.",
                styles['Normal']
            ))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response


@login_required
@user_passes_test(is_admin_or_lecturer)   # was is_lecturer
def download_engagement_report(request):
    """Generate and download student engagement analytics report as PDF"""
    from django.contrib.auth.models import User
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="engagement_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph("Student Engagement Analytics", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary statistics
    total_students = User.objects.filter(profile__role='student').count()
    total_clubs = Club.objects.count()
    total_events = Event.objects.count()
    total_polls = Poll.objects.count()
    total_posts = ClubPost.objects.count()
    
    # Calculate average clubs per student
    clubs_with_members = Club.objects.annotate(mc=Count('members'))
    avg_members = clubs_with_members.aggregate(Avg('mc'))['mc__avg'] or 0
    
    # Calculate average attendance
    events_with_attendees = Event.objects.annotate(ac=Count('attendees'))
    avg_attendance = events_with_attendees.aggregate(Avg('ac'))['ac__avg'] or 0
    
    summary_data = [
        ['Metric', 'Count'],
        ['Total Students', str(total_students)],
        ['Total Clubs', str(total_clubs)],
        ['Total Events', str(total_events)],
        ['Total Polls', str(total_polls)],
        ['Total Posts', str(total_posts)],
        ['Avg Members/Club', f"{avg_members:.1f}"],
        ['Avg Event Attendance', f"{avg_attendance:.1f}"],
    ]
    
    table = Table(summary_data, colWidths=[4*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 0), (-1, -1), 11)
    ]))
    
    elements.append(Paragraph("<b>System Overview</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Most active clubs
    elements.append(Paragraph("<b>Most Active Clubs (by posts)</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    
    active_clubs = Club.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:10]
    
    club_data = [['Club Name', 'Posts', 'Members', 'Events']]
    for club in active_clubs:
        club_data.append([
            club.name,
            str(club.post_count),
            str(club.members.count()),
            str(club.events.count())
        ])
    
    club_table = Table(club_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
    club_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige)
    ]))
    
    elements.append(club_table)
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


# ============================================
# LECTURER CLOUD SAVE & MANAGEMENT
# ============================================

@login_required
@user_passes_test(is_lecturer)
@require_http_methods(["POST"])
def lecturer_save_report_cloud(request):
    """Save lecturer report to cloud storage (Supabase)"""
    
    report_type = request.POST.get('report_type')
    
    if not report_type:
        return JsonResponse({'success': False, 'error': 'Report type is required'}, status=400)
    
    try:
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"lecturer_{report_type}_report_{timestamp}.pdf"
        
        # Generate the appropriate report content
        # In a real implementation, you would generate the actual PDF here
        # For now, we'll simulate with metadata
        
        # Upload to Supabase (you already have this function)
        result = upload_to_supabase(
            f"Lecturer {report_type} report data",  # Replace with actual PDF data
            filename, 
            request.user.id
        )
        
        if result.get('success'):
            return JsonResponse({
                'success': True,
                'url': result.get('url', f'https://cloud-storage.example.com/reports/{filename}'),
                'filename': filename,
                'report_type': report_type,
                'timestamp': timestamp
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Failed to upload to cloud')
            }, status=500)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@user_passes_test(is_lecturer)
def lecturer_saved_reports(request):
    """View all saved reports for lecturer"""
    
    # Fetch saved reports from Supabase or database
    reports = get_my_reports(request.user.id)
    
    # Add mock data if no reports exist
    if not reports:
        reports = [
            {
                'name': 'Clubs Report',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'size': '2.4 MB',
                'type': 'clubs',
                'url': '#'
            },
            {
                'name': 'Students Report',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'size': '1.8 MB',
                'type': 'students',
                'url': '#'
            },
        ]
    
    context = {
        'saved_reports': reports,
        'total_reports': len(reports),
    }
    
    return render(request, 'clubs/lecturer_saved_reports.html', context)


@login_required
@user_passes_test(is_admin)
def admin_saved_reports(request):
    """Admin: view saved reports (reuses lecturer template)."""
    reports = get_my_reports(request.user.id)

    # fallback/mock data
    if not reports:
        reports = [
            {'name': 'Clubs Report', 'date': datetime.now().strftime('%Y-%m-%d'), 'size': '2.4 MB', 'type': 'clubs', 'url': '#'},
            {'name': 'Students Report', 'date': datetime.now().strftime('%Y-%m-%d'), 'size': '1.8 MB', 'type': 'students', 'url': '#'},
        ]

    context = {
        'saved_reports': reports,
        'total_reports': len(reports),
    }
    return render(request, 'clubs/lecturer_saved_reports.html', context)


@login_required
@user_passes_test(is_admin_or_lecturer)
def export_all_data(request):
     """Export all system data as CSV"""
     from django.contrib.auth.models import User
     
     response = HttpResponse(content_type='text/csv')
     response['Content-Disposition'] = f'attachment; filename="system_export_{datetime.now().strftime("%Y%m%d")}.csv"'
     
     writer = csv.writer(response)
     
     # Header
     writer.writerow(['CLUB MANAGEMENT SYSTEM - COMPLETE DATA EXPORT'])
     writer.writerow([f'Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}'])
     writer.writerow([])
     
     # Export Clubs
     writer.writerow(['=== CLUBS ==='])
     writer.writerow(['Club Name', 'Description', 'Members Count', 'Events Count', 'Posts Count'])
     clubs = Club.objects.annotate(
         member_count=Count('members'),
         event_count=Count('events'),
         post_count=Count('posts')
     )
     for club in clubs:
         writer.writerow([
             club.name, 
             club.description, 
             club.member_count, 
             club.event_count,
             club.post_count
         ])
     
     writer.writerow([])
     
     # Export Students
     writer.writerow(['=== STUDENTS ==='])
     writer.writerow(['Name', 'Email', 'Registration Number', 'Clubs Joined'])
     students = User.objects.filter(profile__role='student').annotate(club_count=Count('clubs'))
     for student in students:
         reg_num = getattr(student.profile, 'registration_number', 'N/A')
         writer.writerow([
             student.profile.name,
             student.email,
             reg_num,
             student.club_count
         ])
     
     writer.writerow([])
     
     # Export Events
     writer.writerow(['=== EVENTS ==='])
     writer.writerow(['Title', 'Club', 'Date', 'Location', 'Attendees', 'Description'])
     events = Event.objects.annotate(attendee_count=Count('attendees'))
     for event in events:
         title = getattr(event, 'title', None) or getattr(event, 'name', '')
         location = getattr(event, 'location', '')
         desc = getattr(event, 'description', '')
         writer.writerow([
             title,
             event.club.name,
             event.date.strftime('%Y-%m-%d'),
             location,
             event.attendee_count,
             desc[:100] if desc else ''
         ])
     
     writer.writerow([])
     
     # Export Polls
     writer.writerow(['=== POLLS ==='])
     writer.writerow(['Question', 'Club', 'Total Votes', 'Created Date'])
     polls = Poll.objects.annotate(vote_count=Count('options__votes'))
     for poll in polls:
         writer.writerow([
             poll.question,
             poll.club.name,
             poll.vote_count,
             poll.created_at.strftime('%Y-%m-%d')
         ])
     
     writer.writerow([])
     
     # Export Posts
     writer.writerow(['=== POSTS ==='])
     writer.writerow(['Title', 'Club', 'Author', 'Created Date', 'Content Preview'])
     posts = ClubPost.objects.all().order_by('-created_at')
     for post in posts:
         content_preview = post.content[:100] + '...' if len(post.content) > 100 else post.content
         writer.writerow([
             post.title,
             post.club.name,
             post.author.profile.name,
             post.created_at.strftime('%Y-%m-%d'),
             content_preview
         ])
     
     writer.writerow([])
     writer.writerow(['=== END OF REPORT ==='])
     
     return response


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_save_report_cloud(request):
    """Admin: save a report stub to cloud (uses upload_to_supabase)."""
    report_type = request.POST.get('report_type', 'clubs')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"admin_{report_type}_report_{timestamp}.txt"

    # Minimal report content (replace with real export data if available)
    content = f"Admin {report_type} report\nGenerated by user {request.user.id} on {timestamp}\n\n"
    content += "For full exports, call the dedicated export endpoints.\n"

    result = upload_to_supabase(content, filename, request.user.id)

    # Ensure consistent JSON response
    if result.get('success'):
        return JsonResponse({'success': True, 'url': result.get('url'), 'filename': filename})
    else:
        return JsonResponse({'success': False, 'error': result.get('error', 'upload failed')}, status=500)