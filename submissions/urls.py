from django.urls import path
from .views import SubmissionCreateView, SubmissionListView, SubmissionDetailView

urlpatterns = [
    path("submissions/", SubmissionListView.as_view(), name="submission-list"),
    path("submissions/create/", SubmissionCreateView.as_view(), name="submission-create"),
    path("submissions/<int:pk>/", SubmissionDetailView.as_view(), name="submission-detail"),
]
