from django.urls import path
from .views import HomeView, PushTimecard, AttendanceRecords


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('push', PushTimecard.as_view(), name='push'),
    path('records', AttendanceRecords.as_view(), name='records'),
]