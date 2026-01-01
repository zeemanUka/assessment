from django.contrib import admin
from .models import Submission, SubmissionAnswer

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "exam", "status", "score", "submitted_at", "graded_at")
    list_filter = ("status", "exam")
    search_fields = ("student__username",)

@admin.register(SubmissionAnswer)
class SubmissionAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "submission", "question", "awarded_score")
    list_filter = ("question__question_type",)
