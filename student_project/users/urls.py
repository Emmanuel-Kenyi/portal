from django.urls import path
from . import views

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

    # -------------------------
# Lecturer Add Student Marks
# -------------------------
    path('dashboard/lecturer/add-marks/', views.lecturer_add_mark, name='lecturer_add_mark'),
    path('dashboard/lecturer/edit-mark/<int:mark_id>/', views.edit_mark, name='edit_mark'),
    path('dashboard/lecturer/delete-mark/<int:mark_id>/', views.delete_mark, name='delete_mark'),
    path('dashboard/student/grades/', views.grade_panel, name='grade_panel'),

]
