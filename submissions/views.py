from django.db import transaction
from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from .models import Submission
from .serializers import SubmissionCreateSerializer, SubmissionDetailSerializer
from .permissions import IsOwnerOrStaff

from grading.services import MockGradingService

class SubmissionCreateView(generics.CreateAPIView):
    serializer_class = SubmissionCreateSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        submission = serializer.save()

        # Prefetch answers + questions for grading efficiency
        submission = (
            Submission.objects
            .select_related("exam", "student")
            .prefetch_related("answers__question")
            .get(id=submission.id)
        )

        grader = MockGradingService()
        result = grader.grade(submission)

        # Persist grading to answers + submission
        per_q = {g.question_id: g for g in result.per_question}

        answers = list(submission.answers.all())
        for ans in answers:
            g = per_q.get(ans.question_id)
            if g:
                ans.awarded_score = g.awarded_score
                ans.feedback = g.feedback

        from .models import SubmissionAnswer
        SubmissionAnswer.objects.bulk_update(answers, ["awarded_score", "feedback"])

        submission.score = result.total_score
        submission.graded_at = timezone.now()
        submission.status = Submission.Status.GRADED
        submission.grade_letter = letter_grade(submission.score)
        submission.save(update_fields=["score", "graded_at", "status", "grade_letter"])


class SubmissionListView(generics.ListAPIView):
    serializer_class = SubmissionDetailSerializer

    def get_queryset(self):
        qs = (
            Submission.objects
            .select_related("exam", "student")
            .prefetch_related("answers__question")
            .order_by("-submitted_at")
        )
        if self.request.user.is_staff:
            return qs
        return qs.filter(student=self.request.user)


class SubmissionDetailView(generics.RetrieveAPIView):
    serializer_class = SubmissionDetailSerializer
    permission_classes = [IsOwnerOrStaff]

    def get_queryset(self):
        return (
            Submission.objects
            .select_related("exam", "student")
            .prefetch_related("answers__question")
        )

    def get_object(self):
        obj = super().get_object()
        if not self.request.user.is_staff and obj.student_id != self.request.user.id:
            raise PermissionDenied("You can only view your own submissions.")
        self.check_object_permissions(self.request, obj)
        return obj


def letter_grade(score: float) -> str:
    # Simple scale; adjust if needed
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"
