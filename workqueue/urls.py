from django.urls import path
from .views import dashboard, complete_report, CaseCreateView

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("complete/<int:case_id>/", complete_report, name="complete_report"),
     path("cases/new/", CaseCreateView.as_view(), name="case_create"),
]