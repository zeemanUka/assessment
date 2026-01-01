from django.db import transaction
from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from .models import Submission, SubmissionAnswer
from .serializers import SubmissionCreateSerializer, SubmissionDetailSerializer
from .permissions import IsOwnerOrStaff

from grading.services import MockGradingService
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample



@extend_schema_view(
    post=extend_schema(
        tags=["Submissions"],
        request=SubmissionCreateSerializer,
        responses={201: SubmissionDetailSerializer},
        examples=[
            OpenApiExample(
                "Create submission example",
                value={
                    "exam_id": 1,
                    "answers": [
                        {"question_id": 10, "selected_option": "B"},
                        {"question_id": 11, "answer_text": "My short answer"}
                    ],
                },
                request_only=True,
            ),
        ],
    ),
)

class SubmissionCreateView(generics.GenericAPIView):
    serializer_class = SubmissionCreateSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        input_serializer = self.get_serializer(data=request.data, context={"request": request})
        input_serializer.is_valid(raise_exception=True)

        try:
            submission = input_serializer.save()
        except IntegrityError:
            # handles UNIQUE constraint failed: (student, exam)
            raise ValidationError({"exam_id": "You have already submitted for this exam."})

        # Re-fetch with optimal prefetch for grading
        submission = (
            Submission.objects
            .select_related("exam", "student")
            .prefetch_related("answers__question")
            .get(id=submission.id)
        )

        grader = MockGradingService()
        result = grader.grade(submission)

        per_q = {g.question_id: g for g in result.per_question}

        answers = list(submission.answers.all())
        for ans in answers:
            g = per_q.get(ans.question_id)
            if g:
                ans.awarded_score = g.awarded_score
                ans.feedback = g.feedback

        SubmissionAnswer.objects.bulk_update(answers, ["awarded_score", "feedback"])

        submission.score = result.total_score
        submission.graded_at = timezone.now()
        submission.status = Submission.Status.GRADED
        submission.grade_letter = letter_grade(submission.score)
        submission.save(update_fields=["score", "graded_at", "status", "grade_letter"])

        output = SubmissionDetailSerializer(submission).data
        return Response(output, status=status.HTTP_201_CREATED)


class SubmissionListView(generics.ListAPIView):
    serializer_class = SubmissionDetailSerializer

    @extend_schema(tags=["Submissions"], responses=SubmissionDetailSerializer(many=True))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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

    @extend_schema(tags=["Submissions"], responses=SubmissionDetailSerializer)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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
