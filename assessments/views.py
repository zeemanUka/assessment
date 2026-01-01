from rest_framework import generics
from .models import Exam
from .serializers import ExamListSerializer, ExamDetailSerializer

class ExamListView(generics.ListAPIView):
    queryset = Exam.objects.all().order_by("-created_at")
    serializer_class = ExamListSerializer

class ExamDetailView(generics.RetrieveAPIView):
    queryset = Exam.objects.prefetch_related("questions").all()
    serializer_class = ExamDetailSerializer
