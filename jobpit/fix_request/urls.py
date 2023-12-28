from django.urls import path
from .views import (
    FixAttendanceRequestView,
    AttendanceAcceptionView,
    AcceptionDetailView,
    PushAcceptionView,
)

urlpatterns = [
    path('request', FixAttendanceRequestView.as_view(), name='fix_request'),
    path('request', FixAttendanceRequestView.as_view(), name='fix_request'),
    path('acception/', AttendanceAcceptionView.as_view(), name='fix_acception'),
    path('acception/detail/<int:request_id>', AcceptionDetailView.as_view(), name='acception_detail'),
    path('acception/push', PushAcceptionView.as_view(), name='push_acception')
]
