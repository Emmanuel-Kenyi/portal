from django.urls import path
from . import views
from clubs import views as clubs_views

urlpatterns = [
    # Authentication
    path("login/", views.login_view, name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),

    # Dashboard redirects
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path("dashboard/student/", views.student_dashboard, name="student_dashboard"),
    path("dashboard/lecturer/", views.lecturer_dashboard, name="lecturer_dashboard"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    # Admin settings page
    path("dashboard/admin/settings/", views.admin_settings, name="admin_settings"),

    # General actions
    path("my-activity/", views.my_activity, name="my_activity"),
    path("events/", views.events_list, name="events_list"),
    path("feedback/", views.send_feedback, name="send_feedback"),

    # Lecturer actions
    path('create-poll/', views.create_poll, name='create_poll'),
    path('announcements/', views.announcements, name='announcements'),
    path('reports/', views.reports, name='reports'),

    # Award points
    path('award-points/<int:club_id>/', views.award_points, name='award_points'),
    path('my-points/', views.student_points_summary, name='student_points'),

    # User management
    path('manage-users/', views.manage_users, name='manage_users'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),

    # Post management
    path('manage-posts/', views.manage_posts, name='manage_posts'),

    # Lecturer Add Student Marks
    path('dashboard/lecturer/add-marks/', views.lecturer_add_mark, name='lecturer_add_mark'),
    path('dashboard/lecturer/edit-mark/<int:mark_id>/', views.edit_mark, name='edit_mark'),
    path('dashboard/lecturer/delete-mark/<int:mark_id>/', views.delete_mark, name='delete_mark'),
    path('dashboard/student/grades/', views.grade_panel, name='grade_panel'),

    # Admin Reports
    path('generate-report/', views.generate_report, name='generate_report'),
    path('download-report/', views.download_report, name='download_report'),
    path('system-reports/', views.system_reports, name='system_reports'),

    # Individual report downloads for admin
    path('reports/download-users/', clubs_views.download_students_report, name='download_users_report'),
    path('reports/download-clubs/', clubs_views.download_clubs_report, name='download_clubs_report'),
    path('reports/download-posts/', clubs_views.download_polls_report, name='download_posts_report'),
    path('reports/download-events/', clubs_views.download_events_report, name='download_events_report'),

    # student/lecturer/admin reports
    path('reports/clubs/download/', clubs_views.download_clubs_report, name='download_clubs_report'),
    path('reports/students/download/', clubs_views.download_students_report, name='download_students_report'),
    path('reports/events/download/', clubs_views.download_events_report, name='download_events_report'),
    path('reports/polls/download/', clubs_views.download_polls_report, name='download_polls_report'),
    path('reports/engagement/download/', clubs_views.download_engagement_report, name='download_engagement_report'),

    # saved reports / cloud endpoints (these are POST-only)
    path('reports/lecturer-save/', clubs_views.lecturer_save_report_cloud, name='lecturer_save_report_cloud'),
    path('reports/admin-save/', views.admin_save_report_cloud, name="admin_save_report_cloud"),

    # saved-reports listing
    path('reports/lecturer-saved/', clubs_views.lecturer_saved_reports, name='lecturer_saved_reports'),
    path('reports/admin-saved/', clubs_views.admin_saved_reports, name='admin_saved_reports'),
]
