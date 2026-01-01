from django.conf import settings
from django.db import models

class Submission(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        SUBMITTED = "SUBMITTED", "Submitted"
        GRADED = "GRADED", "Graded"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions", db_index=True)
    exam = models.ForeignKey("assessments.Exam", on_delete=models.CASCADE, related_name="submissions", db_index=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED, db_index=True)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    graded_at = models.DateTimeField(null=True, blank=True)

    score = models.FloatField(default=0.0)
    grade_letter = models.CharField(max_length=5, blank=True, default="")

    class Meta:
        constraints = [
            # one submission per student per exam (simple policy).
            models.UniqueConstraint(fields=["student", "exam"], name="uniq_student_exam_submission"),
        ]
        indexes = [
            models.Index(fields=["student", "submitted_at"]),
            models.Index(fields=["student", "exam"]),
            models.Index(fields=["exam", "graded_at"]),
        ]

    def __str__(self):
        return f"Submission({self.id}) student={self.student_id} exam={self.exam_id}"


class SubmissionAnswer(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="answers", db_index=True)
    question = models.ForeignKey("assessments.Question", on_delete=models.CASCADE, related_name="submission_answers", db_index=True)

    answer_text = models.TextField(blank=True, default="")
    selected_option = models.CharField(max_length=255, blank=True, default="")

    awarded_score = models.FloatField(default=0.0)
    feedback = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["submission", "question"], name="uniq_submission_question_answer"),
        ]

    def __str__(self):
        return f"Answer({self.id}) sub={self.submission_id} q={self.question_id}"
