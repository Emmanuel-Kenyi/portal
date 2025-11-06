from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClubViewSet,
    ClubPostViewSet,
    EventViewSet,
    PollViewSet,
    MyTokenObtainPairView,
    MyTokenRefreshView,
    user_profile,
    student_dashboard_api,
    my_saved_reports_api,
    save_report_cloud_api,
    export_all_data_api,
)

router = DefaultRouter()
router.register(r'clubs', ClubViewSet)
router.register(r'posts', ClubPostViewSet)
router.register(r'events', EventViewSet)
router.register(r'polls', PollViewSet)

urlpatterns = [
    # JWT Authentication
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),

    # Profile and dashboard endpoints
    path('user/profile/', user_profile, name='user_profile'),
    path('student/dashboard/', student_dashboard_api, name='student_dashboard_api'),

    # Reports and exports
    path('reports/', my_saved_reports_api, name='my_saved_reports_api'),
    path('reports/save/', save_report_cloud_api, name='save_report_cloud_api'),
    path('export/', export_all_data_api, name='export_all_data_api'),

    # Router endpoints
    path('', include(router.urls)),
]
