from django.urls import path

from .views import VisitRequestView

app_name = 'visits'

urlpatterns = [
    path('request/', VisitRequestView.as_view(), name='visit_request'),
]
