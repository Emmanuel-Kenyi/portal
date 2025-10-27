from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ============================================
    # DASHBOARDS
    # ============================================
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
    
    # ============================================
    # NAVIGATION VIEWS
    # ============================================
    path('my-activity/', views.my_activity, name='my_activity'),
    path('events/', views.events_list, name='events_list'),
    path('send-feedback/', views.send_feedback, name='send_feedback'),
    
    # ============================================
    # CLUB VIEWS
    # ============================================
    path('clubs/', views.club_list, name='club_list'),
    path('clubs/<int:club_id>/', views.club_detail, name='club_detail'),
    path('clubs/<int:club_id>/toggle-membership/', views.toggle_membership, name='toggle_membership'),
    path('clubs/<int:club_id>/new-post/', views.new_post, name='new_post'),
    path('clubs/create/', views.create_club, name='create_club'),
    
    # ============================================
    # POLL & EVENT VIEWS
    # ============================================
    path('polls/<int:poll_id>/vote/', views.vote_poll, name='vote_poll'),
    path('polls/create/', views.create_poll, name='create_poll'),
    path('events/<int:event_id>/rsvp/', views.rsvp_event, name='rsvp_event'),
    
    # ============================================
    # AUTHENTICATION
    # ============================================
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # ============================================
    # ADMIN VIEWS
    # ============================================
    path('admin/manage-clubs/', views.manage_clubs, name='manage_clubs'),
    path('admin/posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),

    # ============================================
    # STUDENT REPORTS - CSV DOWNLOADS & CLOUD SAVE
    # ============================================
    path('student/reports/download/clubs/', views.download_my_clubs, name='download_my_clubs'),
    path('student/reports/download/events/', views.download_my_events, name='download_my_events'),
    path('student/reports/download/grades/', views.download_my_grades, name='download_my_grades'),
    path('student/reports/save-cloud/', views.save_report_cloud, name='save_report_cloud'),
    path('student/reports/saved/', views.my_saved_reports, name='my_saved_reports'),
    
    # ============================================
    # LECTURER REPORTS - PDF DOWNLOADS
    # ============================================
    path('lecturer/reports/download/clubs/', 
         views.download_clubs_report, 
         name='download_clubs_report'),
    
    path('lecturer/reports/download/students/', 
         views.download_students_report, 
         name='download_students_report'),
    
    path('lecturer/reports/download/events/', 
         views.download_events_report, 
         name='download_events_report'),
    
    path('lecturer/reports/download/polls/', 
         views.download_polls_report, 
         name='download_polls_report'),
    
    path('lecturer/reports/download/grades/', 
         views.download_grades_report, 
         name='download_grades_report'),
    
    path('lecturer/reports/download/engagement/', 
         views.download_engagement_report, 
         name='download_engagement_report'),
    
    # ============================================
    # LECTURER CLOUD SAVE & MANAGEMENT
    # ============================================
    path('lecturer/reports/save-cloud/', 
         views.lecturer_save_report_cloud, 
         name='lecturer_save_report_cloud'),
    
    path('lecturer/reports/saved/', 
         views.lecturer_saved_reports, 
         name='lecturer_saved_reports'),
    
    # ============================================
    # LECTURER DATA EXPORT
    # ============================================
    path('lecturer/reports/export-all/', 
         views.export_all_data, 
         name='export_all_data'),
]