# VStudy World Plus — Backend API

**Learn Smarter. Understand Better.**

Production-ready REST API for the VStudy World Plus AI-powered smart learning platform (Grades 6–13 / O/L and A/L).

Built with **Flask**, **SQLAlchemy**, **MySQL**, **JWT**, **Marshmallow**, **OpenAI**, and **Blueprint architecture**.

---

## Features

- JWT authentication with bcrypt password hashing
- Role-based access: Student, Teacher, Admin
- Subjects and Lessons CRUD
- AI Study Helper (summarize, explain, generate video) with OpenAI + mock fallback
- AI Quiz Generation and submission scoring
- Progress tracking per student
- Interactive Geography map activities
- Mathematics solve, practice, and answer checking
- AI-generated exam study plans
- AI Chatbot with conversation history
- Standardized API response format
- Flask-Migrate database migrations
- Application logging
- CORS enabled

---

## Project Structure

```
flask-student-api/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── run.py
├── postman/
│   └── VStudy_World_Plus_API.postman_collection.json
├── migrations/
└── app/
    ├── __init__.py          # App factory, JWT handlers, error handlers
    ├── config.py            # Environment configuration
    ├── extensions.py        # db, jwt, migrate instances
    ├── models/
    │   ├── user.py
    │   ├── subject.py
    │   ├── lesson.py
    │   ├── lesson_video.py
    │   ├── lesson_summary.py
    │   ├── quiz.py
    │   ├── progress.py
    │   ├── study_plan.py
    │   ├── chat_history.py
    │   ├── geography.py
    │   └── math.py
    ├── schemas/
    │   ├── user_schema.py
    │   ├── subject_schema.py
    │   ├── lesson_schema.py
    │   ├── ai_schema.py
    │   ├── quiz_schema.py
    │   ├── progress_schema.py
    │   ├── geography_schema.py
    │   ├── math_schema.py
    │   ├── study_plan_schema.py
    │   └── chat_schema.py
    ├── services/
    │   ├── auth_service.py
    │   ├── subject_service.py
    │   ├── lesson_service.py
    │   ├── ai_service.py
    │   ├── quiz_service.py
    │   ├── progress_service.py
    │   ├── geography_service.py
    │   ├── math_service.py
    │   ├── study_plan_service.py
    │   └── chat_service.py
    ├── routes/
    │   ├── auth_routes.py
    │   ├── subject_routes.py
    │   ├── lesson_routes.py
    │   ├── ai_routes.py
    │   ├── quiz_routes.py
    │   ├── progress_routes.py
    │   ├── geography_routes.py
    │   ├── math_routes.py
    │   ├── study_plan_routes.py
    │   └── chat_routes.py
    └── utils/
        ├── response.py
        ├── decorators.py
        ├── time_utils.py
        ├── logger.py
        └── openai_client.py
```

---

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your MySQL credentials and OpenAI API key

# 4. Create the database
mysql -u root -p -e "CREATE DATABASE vstudy_world_plus;"

# 5. Run migrations
export FLASK_APP=run.py
flask db upgrade

# 6. Seed default admin (admin@gmail.com / admin123)
python seed.py

# 7. Start the server
python run.py
```

Base URL: `http://localhost:5001`

Default admin: `admin@gmail.com` / `admin123`  
MySQL database: `vstudy_world_plus`

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Flask secret key | `change-me-in-production` |
| `JWT_SECRET_KEY` | JWT signing key | `change-me-jwt-secret` |
| `MYSQL_HOST` | MySQL host | `localhost` |
| `MYSQL_PORT` | MySQL port | `3306` |
| `MYSQL_USER` | MySQL username | `root` |
| `MYSQL_PASSWORD` | MySQL password | `root123` |
| `MYSQL_DATABASE` | Database name | `vstudy_world_plus` |
| `FLASK_DEBUG` | Debug mode | `False` |
| `JWT_ACCESS_TOKEN_EXPIRES_HOURS` | Token expiry | `24` |
| `OPENAI_API_KEY` | OpenAI API key (optional) | *(empty — uses mock)* |
| `OPENAI_MODEL` | OpenAI model | `gpt-4o-mini` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_DIR` | Log file directory | `logs` |

---

## API Response Format

All endpoints return:

```json
{
  "success": true,
  "message": "Description of the result",
  "data": {}
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description",
  "data": {}
}
```

---

## Authentication APIs

| Method | Endpoint | Access |
|---|---|---|
| POST | `/api/auth/register` | Public |
| POST | `/api/auth/login` | Public |
| GET | `/api/auth/me` | JWT required |
| PUT | `/api/auth/profile` | JWT required |
| PUT | `/api/auth/email` | JWT required (needs current password) |
| PUT | `/api/auth/password` | JWT required (needs current password) |
| POST | `/api/auth/logout` | JWT required |

### POST `/api/auth/register`

```json
{
  "full_name": "Kamal Perera",
  "email": "kamal@school.lk",
  "password": "secure123",
  "school": "Colombo Central College",
  "grade": "11"
}
```

### POST `/api/auth/login`

```json
{
  "email": "kamal@school.lk",
  "password": "secure123"
}
```

Returns `access_token` in `data`. Use header: `Authorization: Bearer <token>`

---

## Subject APIs (JWT required)

| Method | Endpoint | Access |
|---|---|---|
| GET | `/api/subjects` | All authenticated users |
| GET | `/api/subjects/<id>` | All authenticated users |
| POST | `/api/subjects` | Teacher, Admin |
| PUT | `/api/subjects/<id>` | Teacher, Admin |
| DELETE | `/api/subjects/<id>` | Teacher, Admin |

---

## Lesson APIs (JWT required)

| Method | Endpoint | Access |
|---|---|---|
| GET | `/api/lessons` | All authenticated users |
| GET | `/api/lessons?subject_id=1` | Filter by subject |
| GET | `/api/lessons/<id>` | All authenticated users |
| POST | `/api/lessons` | Teacher, Admin |
| PUT | `/api/lessons/<id>` | Teacher, Admin |
| DELETE | `/api/lessons/<id>` | Teacher, Admin |

---

## AI Study Helper APIs (JWT required)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/ai/summarize` | Summarize lesson content |
| POST | `/api/ai/explain` | Explain a topic simply |
| POST | `/api/ai/generate-video` | Generate history story video |

Uses OpenAI when `OPENAI_API_KEY` is configured; otherwise returns intelligent mock responses.

---

## Quiz APIs (JWT required)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/quiz/generate` | Generate AI quiz from lesson or topic |
| GET | `/api/quiz/<id>` | Get quiz with questions |
| POST | `/api/quiz/submit` | Submit answers and get score |

### POST `/api/quiz/generate`

```json
{
  "lesson_id": 1,
  "topic": "Water Cycle",
  "num_questions": 5
}
```

### POST `/api/quiz/submit`

```json
{
  "quiz_id": 1,
  "answers": {
    "1": "A",
    "2": "B",
    "3": "C"
  }
}
```

---

## Progress APIs (JWT required)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/progress/<userId>` | Get student progress |
| POST | `/api/progress/update` | Update learning progress |

### POST `/api/progress/update`

```json
{
  "lesson_id": 1,
  "status": "in_progress",
  "completion_percentage": 75,
  "time_spent_minutes": 45
}
```

---

## Geography APIs (JWT required)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/geo/maps` | List available maps |
| GET | `/api/geo/activities` | List geography activities |
| POST | `/api/geo/marking` | Submit map markings |

---

## Mathematics APIs (JWT required)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/math/solve` | Solve a math problem with steps |
| GET | `/api/math/practice` | Get practice problems |
| GET | `/api/math/practice?topic=algebra&difficulty=easy` | Filter practice |
| POST | `/api/math/check` | Check student answer |

---

## Study Plan APIs (JWT required)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/study-plan/generate` | Generate exam study plan |
| GET | `/api/study-plan/<userId>` | Get user's study plans |

### POST `/api/study-plan/generate`

```json
{
  "title": "O/L Science Exam Plan",
  "exam_date": "2026-08-15",
  "subjects": ["Science", "Mathematics"],
  "hours_per_day": 3,
  "focus_areas": ["Physics", "Chemistry"]
}
```

---

## Chat APIs (JWT required)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat/ask` | Ask the AI chatbot |
| GET | `/api/chat/history` | Get conversation history |

### POST `/api/chat/ask`

```json
{
  "question": "What is photosynthesis in simple words?"
}
```

---

## Database Tables

| Table | Description |
|---|---|
| `users` | Student, Teacher, Admin accounts |
| `subjects` | Academic subjects |
| `lessons` | Lesson content per subject |
| `lesson_videos` | AI-generated history videos |
| `lesson_summaries` | AI-generated summaries |
| `quizzes` | Generated quizzes |
| `quiz_questions` | Quiz questions with options |
| `quiz_results` | Student quiz submissions |
| `progress` | Learning progress tracking |
| `study_plans` | AI-generated study plans |
| `chat_history` | AI chatbot conversations |
| `geography_activities` | Map activities |
| `map_submissions` | Student map marking submissions |
| `math_practice` | Practice math problems |
| `math_solutions` | Student math solution attempts |

---

## Roles

| Role | Permissions |
|---|---|
| **Student** | View content, use AI helpers, quizzes, progress, chat |
| **Teacher** | All Student permissions + create/edit/delete subjects & lessons |
| **Admin** | Full access (same as Teacher for content management) |

---

## Postman Collection

Import `postman/VStudy_World_Plus_API.postman_collection.json` into Postman.

The Login request automatically saves the `access_token` to collection variables.

---

## Production Deployment

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

Use a Redis-backed JWT blocklist for logout in multi-instance deployments.

---

## License

Final Year Project — VStudy World Plus API





<!-- POST

http://localhost:5000/api/auth/register

Headers:

Content-Type: application/json

{
  "full_name": "Vathumy",
  "email": "vathumy@gmail.com",
  "password": "123456"
} -->



<!-- POST

URL:

http://localhost:5000/api/auth/login

Body:

{
  "email": "vathumy@gmail.com",
  "password": "123456"
} -->


<!-- POST

URL:

http://localhost:5000/api/ai/explain

Body:

{
  "question": "Explain photosynthesis in simple words"
} -->



<!-- GET

URL:

http://localhost:5000/api/subjects

Body தேவையில்லை. -->



<!-- POST

URL:

http://localhost:5000/api/chat/ask

Body:

{
  "message": "Explain Newton's law"
} -->