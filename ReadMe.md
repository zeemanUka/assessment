# Acad AI Mini Assessment Engine (Backend)

## What this project is

This is a backend API for running simple exams and collecting student submissions. It also grades submissions using a mock grading service built from scratch.

It supports:

* Exams and Questions
* Student Submissions
* Auto grading after submission
* Token login (Django auth)
* Swagger (OpenAPI) documentation for frontend use
* Students can only view their own submissions

---

## Built with

* Python 3.x
* Django
* Django REST Framework (DRF)
* DRF Token Authentication
* drf-spectacular (Swagger / OpenAPI docs)
* SQLite (default for local dev)

No paid services are used.

---

## How to run locally

### 1) Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

Or

```bash
pip install Django djangorestframework django-filter drf-spectacular python-dotenv
pip freeze > requirements.txt
```

### 3) Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4) Create admin user

```bash
python manage.py createsuperuser
```

### 5) Start the server

```bash
python manage.py runserver
```

Server runs at:

* [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Useful links

* Swagger UI: `GET /api/docs/`
* OpenAPI schema JSON: `GET /api/schema/`
* Django Admin: `/admin/`

---

## Project structure (folders and what they do)

```
config/
  settings.py          # Django settings, DRF config, Swagger config
  urls.py              # Main URL routes
  wsgi.py / asgi.py

accounts/
  urls.py              # /api/auth routes
  views.py             # login/logout endpoints
  serializers.py       # login request/response serializers

assessments/
  models.py            # Exam, Question
  serializers.py       # exam/question serializers
  views.py             # read-only exam endpoints (student)
  viewsets.py          # admin CRUD endpoints (staff)
  permissions.py       # staff permission for admin endpoints
  urls.py              # routes for exams + admin router

submissions/
  models.py            # Submission, SubmissionAnswer
  serializers.py       # submission create + detail serializers
  views.py             # create submission, list submissions, detail
  permissions.py       # owner-only permission
  urls.py              # submissions routes

grading/
  services.py          # mock grading logic (keyword overlap, MCQ match)

common/
  renderers.py         # response format wrapper (status/message/data)
```

---

## Authentication (Login)

This API uses Token Authentication.

### How to login

Endpoint:

* `POST /api/auth/login/`

Body:

```json
{
  "username": "myuser",
  "password": "mypassword"
}
```

Response:

```json
{
  "status": true,
  "message": "Success",
  "data": {
    "token": "abc123...",
    "user_id": 1,
    "username": "myuser"
  }
}
```

### How to use the token

Send this header on protected endpoints:

```
Authorization: Token abc123...
```

### Logout

* `POST /api/auth/logout/`

Response:

```json
{
  "status": true,
  "message": "Success",
  "data": {
    "detail": "Logged out"
  }
}
```

---

## Response format (same for all endpoints)

All endpoints return:

```json
{
  "status": true/false,
  "message": "text",
  "data": {}
}
```

### Example success

```json
{
  "status": true,
  "message": "Success",
  "data": {
    "id": 1
  }
}
```

### Example error

```json
{
  "status": false,
  "message": "Validation error",
  "data": {
    "field_name": ["This field is required."]
  }
}
```

---

## Core models (database tables)

### Exam

* title
* course
* duration_minutes
* metadata (JSON)
* created_at

### Question

* exam (FK)
* question_type: MCQ, SHORT, ESSAY
* prompt
* expected_answer
* options (JSON) for MCQ
* max_score

### Submission

* student (FK)
* exam (FK)
* status
* submitted_at
* graded_at
* score
* grade_letter

### SubmissionAnswer

* submission (FK)
* question (FK)
* answer_text or selected_option
* awarded_score
* feedback

Important rule:

* A student can submit **only once** per exam (unique constraint). If they try again, the API returns a clean validation error.

---

## Endpoints

### 1) Exams (students can read)

#### List exams

* `GET /api/exams/`

Response:

```json
{
  "status": true,
  "message": "Success",
  "data": [
    {
      "id": 1,
      "title": "Coding",
      "course": "CDC301",
      "duration_minutes": 60,
      "metadata": {},
      "created_at": "..."
    }
  ]
}
```

#### Exam detail (includes questions)

* `GET /api/exams/<id>/`

Response:

```json
{
  "status": true,
  "message": "Success",
  "data": {
    "id": 1,
    "title": "Coding",
    "course": "CDC301",
    "duration_minutes": 60,
    "metadata": {},
    "created_at": "...",
    "questions": [
      {
        "id": 10,
        "question_type": "MCQ",
        "prompt": "What is 2 + 2?",
        "options": ["2", "3", "4"],
        "max_score": 1
      }
    ]
  }
}
```

---

### 2) Admin Assessments (staff only)

These endpoints are for creating exams and questions using API (instead of only Django admin).

#### Create exam

* `POST /api/admin/exams/`

Body:

```json
{
  "title": "Coding",
  "course": "CDC301",
  "duration_minutes": 60,
  "metadata": {}
}
```

#### Create question

* `POST /api/admin/questions/`

Body:

```json
{
  "exam": 1,
  "question_type": "MCQ",
  "prompt": "What is 2 + 2?",
  "expected_answer": "4",
  "options": ["2", "3", "4"],
  "max_score": 1
}
```

Note:

* These require a staff user token.

---

### 3) Submissions (students)

#### Create submission (auto grades)

* `POST /api/submissions/create/`

Body example:

```json
{
  "exam_id": 1,
  "answers": [
    { "question_id": 10, "selected_option": "4" },
    { "question_id": 11, "answer_text": "My short answer" }
  ]
}
```

Response includes grading:

```json
{
  "status": true,
  "message": "Success",
  "data": {
    "id": 5,
    "exam_id": 1,
    "exam_title": "Coding",
    "course": "CDC301",
    "status": "GRADED",
    "submitted_at": "...",
    "graded_at": "...",
    "score": 2.0,
    "grade_letter": "F",
    "answers": [
      {
        "id": 20,
        "question_id": 10,
        "question_prompt": "What is 2 + 2?",
        "question_type": "MCQ",
        "max_score": 1,
        "answer_text": "",
        "selected_option": "4",
        "awarded_score": 1.0,
        "feedback": "Correct"
      }
    ]
  }
}
```

If student tries to submit the same exam again:

```json
{
  "status": false,
  "message": "Validation error",
  "data": {
    "exam_id": ["You have already submitted for this exam."]
  }
}
```

#### List my submissions

* `GET /api/submissions/`

Response:

```json
{
  "status": true,
  "message": "Success",
  "data": [
    {
      "id": 5,
      "exam_id": 1,
      "status": "GRADED",
      "score": 2.0,
      "graded_at": "...",
      "answers": [...]
    }
  ]
}
```

#### Get one submission

* `GET /api/submissions/<id>/`

Rules:

* A student can only view their own submission.
* Staff can view all submissions.

---

## Grading

Grading runs automatically when a student submits.

Rules:

* MCQ: checks if `selected_option` matches `expected_answer`
* SHORT/ESSAY: uses keyword overlap between student answer and expected answer

Grading output:

* `Submission.score`
* `Submission.graded_at`
* `SubmissionAnswer.awarded_score`
* `SubmissionAnswer.feedback`

---

## Frontend collaboration notes

* Swagger UI shows all endpoints and request bodies.
* Token auth is required for protected endpoints.
* Students only see their own submissions.
* Responses always come in the same wrapper format.

---

## Common problems

### “Authentication credentials were not provided.”

You forgot the token header format.

Use:

```
Authorization: Token <token>
```

### “Forbidden”

You are calling a staff-only endpoint with a student token.

Make sure `is_staff=True` for admin endpoints.
