import re
from dataclasses import dataclass
from typing import List, Dict

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "is", "are", "was", "were",
    "with", "as", "by", "at", "from", "that", "this", "it"
}

def tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    words = re.findall(r"[a-z0-9]+", text)
    return [w for w in words if w not in STOPWORDS]

@dataclass
class QuestionGrade:
    question_id: int
    awarded_score: float
    feedback: str

@dataclass
class GradeResult:
    total_score: float
    per_question: List[QuestionGrade]

class MockGradingService:
    """
    Rules:
    - MCQ: selected_option must match expected_answer exactly (case-insensitive)
    - SHORT/ESSAY: keyword overlap ratio * max_score (0..max_score)
    """

    def grade(self, submission) -> GradeResult:
        # expects submission.answers prefetched and answers.question select_related
        per_q: List[QuestionGrade] = []
        total = 0.0

        for ans in submission.answers.all():
            q = ans.question
            max_score = float(q.max_score or 1)

            if q.question_type == "MCQ":
                expected = (q.expected_answer or "").strip().lower()
                chosen = (ans.selected_option or "").strip().lower()
                awarded = max_score if expected and chosen and expected == chosen else 0.0
                feedback = "Correct" if awarded > 0 else "Incorrect"

            else:
                expected_tokens = set(tokenize(q.expected_answer))
                answer_tokens = set(tokenize(ans.answer_text))

                if not expected_tokens:
                    # If there is no expected answer, give 0 (or you could default to max_score)
                    awarded = 0.0
                    feedback = "No expected answer configured"
                else:
                    overlap = len(expected_tokens.intersection(answer_tokens))
                    ratio = overlap / max(1, len(expected_tokens))
                    awarded = round(max_score * ratio, 2)
                    feedback = f"Keyword overlap: {overlap}/{len(expected_tokens)}"

            total += awarded
            per_q.append(QuestionGrade(question_id=q.id, awarded_score=awarded, feedback=feedback))

        total = round(total, 2)
        return GradeResult(total_score=total, per_question=per_q)
