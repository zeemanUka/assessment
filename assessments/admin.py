from django.contrib import admin
from .models import Exam, Question

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "title", "duration_minutes", "created_at")
    search_fields = ("title", "course")
    list_filter = ("course",)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "exam", "question_type", "max_score")
    list_filter = ("question_type", "exam")
    search_fields = ("prompt",)
