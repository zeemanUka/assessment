from django.db import models

class Exam(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    course = models.CharField(max_length=255, db_index=True)
    duration_minutes = models.PositiveIntegerField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course}: {self.title}"


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MCQ = "MCQ", "Multiple Choice"
        SHORT = "SHORT", "Short Answer"
        ESSAY = "ESSAY", "Essay"

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions", db_index=True)
    question_type = models.CharField(max_length=10, choices=QuestionType.choices, db_index=True)
    prompt = models.TextField()
    expected_answer = models.TextField(blank=True, default="")
    options = models.JSONField(default=list, blank=True)  # for MCQ
    max_score = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["exam", "question_type"]),
        ]

    def __str__(self):
        return f"{self.exam_id} - {self.question_type}"
