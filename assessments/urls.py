from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamListView, ExamDetailView
from .viewsets import ExamViewSet, QuestionViewSet

router = DefaultRouter()
router.register(r"admin/exams", ExamViewSet, basename="admin-exams")
router.register(r"admin/questions", QuestionViewSet, basename="admin-questions")

urlpatterns = [
    # student/read-only endpoints
    path("exams/", ExamListView.as_view(), name="exam-list"),
    path("exams/<int:pk>/", ExamDetailView.as_view(), name="exam-detail"),
    path("", include(router.urls)),
]
