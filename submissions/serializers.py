from django.utils import timezone
from rest_framework import serializers
from assessments.models import Exam, Question
from .models import Submission, SubmissionAnswer

class SubmissionAnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_text = serializers.CharField(required=False, allow_blank=True)
    selected_option = serializers.CharField(required=False, allow_blank=True)

class SubmissionCreateSerializer(serializers.Serializer):
    exam_id = serializers.IntegerField()
    answers = SubmissionAnswerInputSerializer(many=True)

    def validate(self, attrs):
        exam_id = attrs["exam_id"]
        answers = attrs["answers"]

        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            raise serializers.ValidationError({"exam_id": "Exam not found"})

        if not answers:
            raise serializers.ValidationError({"answers": "At least one answer is required"})

        question_ids = [a["question_id"] for a in answers]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError({"answers": "Duplicate question_id in answers payload"})

        # Ensure questions belong to this exam
        valid_questions = Question.objects.filter(exam=exam, id__in=question_ids).values_list("id", flat=True)
        valid_questions_set = set(valid_questions)
        missing = [qid for qid in question_ids if qid not in valid_questions_set]
        if missing:
            raise serializers.ValidationError({"answers": f"Questions not in this exam: {missing}"})

        attrs["exam"] = exam
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        exam = validated_data["exam"]
        answers = validated_data["answers"]

        submission = Submission.objects.create(
            student=request.user,
            exam=exam,
            status=Submission.Status.SUBMITTED,
            submitted_at=timezone.now(),
        )

        # Create answers
        questions = {q.id: q for q in Question.objects.filter(exam=exam, id__in=[a["question_id"] for a in answers])}

        answer_objs = []
        for a in answers:
            q = questions[a["question_id"]]
            answer_text = a.get("answer_text", "") or ""
            selected_option = a.get("selected_option", "") or ""

            # Basic per-type validation
            if q.question_type == "MCQ" and not selected_option:
                raise serializers.ValidationError({"answers": f"MCQ question {q.id} requires selected_option"})
            if q.question_type in ("SHORT", "ESSAY") and not answer_text:
                raise serializers.ValidationError({"answers": f"Question {q.id} requires answer_text"})

            answer_objs.append(SubmissionAnswer(
                submission=submission,
                question=q,
                answer_text=answer_text,
                selected_option=selected_option,
            ))

        SubmissionAnswer.objects.bulk_create(answer_objs)
        return submission


class SubmissionAnswerDetailSerializer(serializers.ModelSerializer):
    question_prompt = serializers.CharField(source="question.prompt", read_only=True)
    question_type = serializers.CharField(source="question.question_type", read_only=True)
    max_score = serializers.IntegerField(source="question.max_score", read_only=True)

    class Meta:
        model = SubmissionAnswer
        fields = [
            "id",
            "question_id",
            "question_prompt",
            "question_type",
            "max_score",
            "answer_text",
            "selected_option",
            "awarded_score",
            "feedback",
        ]


class SubmissionDetailSerializer(serializers.ModelSerializer):
    exam_title = serializers.CharField(source="exam.title", read_only=True)
    course = serializers.CharField(source="exam.course", read_only=True)
    answers = SubmissionAnswerDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "exam_id",
            "exam_title",
            "course",
            "status",
            "submitted_at",
            "graded_at",
            "score",
            "grade_letter",
            "answers",
        ]
