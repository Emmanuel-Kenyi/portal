from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path("dashboard/student/", views.student_dashboard, name="student_dashboard"),
    path("dashboard/lecturer/", views.lecturer_dashboard, name="lecturer_dashboard"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("my-activity/", views.my_activity, name="my_activity"),
    path("events/", views.events_list, name="events_list"),
    path("feedback/", views.send_feedback, name="send_feedback"),
    path('create-poll/', views.create_poll, name='create_poll'),
    path('announcements/', views.announcements, name='announcements'),
    path('reports/', views.reports, name='reports'),
    path('award-points/<int:club_id>/', views.award_points, name='award_points'),
    path('my-points/', views.student_points_summary, name='student_points'),
]