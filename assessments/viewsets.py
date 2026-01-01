from rest_framework import viewsets
from drf_spectacular.utils import extend_schema_view, extend_schema

from .models import Exam, Question
from .serializers import (
    ExamListSerializer, ExamDetailSerializer,
    ExamCreateUpdateSerializer,
    QuestionSerializer, QuestionCreateUpdateSerializer
)
from .permissions import IsStaff

@extend_schema_view(
    list=extend_schema(tags=["Assessments"], responses=ExamListSerializer(many=True)),
    retrieve=extend_schema(tags=["Assessments"], responses=ExamDetailSerializer),
    create=extend_schema(tags=["Assessments"], request=ExamCreateUpdateSerializer, responses=ExamDetailSerializer),
    update=extend_schema(tags=["Assessments"], request=ExamCreateUpdateSerializer, responses=ExamDetailSerializer),
    partial_update=extend_schema(tags=["Assessments"], request=ExamCreateUpdateSerializer, responses=ExamDetailSerializer),
    destroy=extend_schema(tags=["Assessments"]),
)
class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all().order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return ExamListSerializer
        if self.action == "retrieve":
            return ExamDetailSerializer
        return ExamCreateUpdateSerializer

    def get_permissions(self):
        # students can read exams; only staff can write
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsStaff()]
        return super().get_permissions()


@extend_schema_view(
    list=extend_schema(tags=["Assessments"], responses=QuestionSerializer(many=True)),
    retrieve=extend_schema(tags=["Assessments"], responses=QuestionSerializer),
    create=extend_schema(tags=["Assessments"], request=QuestionCreateUpdateSerializer, responses=QuestionSerializer),
    update=extend_schema(tags=["Assessments"], request=QuestionCreateUpdateSerializer, responses=QuestionSerializer),
    partial_update=extend_schema(tags=["Assessments"], request=QuestionCreateUpdateSerializer, responses=QuestionSerializer),
    destroy=extend_schema(tags=["Assessments"]),
)
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related("exam").all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return QuestionCreateUpdateSerializer
        return QuestionSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsStaff()]
        return super().get_permissions()
