from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Student Dashboard
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    
    # Club views
    path('clubs/', views.club_list, name='club_list'),
    path('clubs/<int:club_id>/', views.club_detail, name='club_detail'),
    path('clubs/<int:club_id>/toggle-membership/', views.toggle_membership, name='toggle_membership'),
    path('clubs/<int:club_id>/new-post/', views.new_post, name='new_post'),
    
    # Poll & Event views
    path('polls/<int:poll_id>/vote/', views.vote_poll, name='vote_poll'),
    path('events/<int:event_id>/rsvp/', views.rsvp_event, name='rsvp_event'),
    
    # Logout
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Admin views
    path('admin/manage-clubs/', views.manage_clubs, name='manage_clubs'),
    path('admin/posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
]