🧠 AI-Driven Adaptive Diagnostic Engine

A 1-Dimension Adaptive Testing system that determines student proficiency by dynamically selecting GRE-style questions using Item Response Theory (IRT) and generates personalized AI study plans via Anthropic Claude API.

---

🚀 How to Run the Project

 Prerequisites
- Python 3.10+
- MongoDB (local or Atlas)
- Anthropic API key

 1. Clone the Repository
```
git clone https://github.com/Jyoshna-03/adaptive-engine.git
cd adaptive-engine
```

2. Install Dependencies
```
pip install -r requirements.txt
```

3. Configure Environment
Create a `.env` file:
```
MONGODB_URI=mongodb://localhost:27017
DB_NAME=adaptive_engine
ANTHROPIC_API_KEY=your_key_here
```

4. Seed the Database
```
python seed.py
```

5. Run the Server
```
python -m uvicorn app.main:app --reload
```

6. Open Swagger UI
```
http://127.0.0.1:8000/docs
```

---

📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/session/start` | Start a new test session |
| GET | `/session/{id}/next-question` | Get next adaptive question |
| POST | `/session/{id}/submit-answer` | Submit an answer |
| GET | `/session/{id}/report` | Get final report + AI study plan |
| GET | `/session/{id}/status` | Check session progress |
| GET | `/questions/` | List all questions |
| GET | `/questions/count` | Get question count |

---

🧮 Adaptive Algorithm Explanation

The system uses Item Response Theory (IRT) 2PL model:
```
P(correct | θ, b, a) = 1 / (1 + e^(-a * (θ - b)))
```

Where:
- **θ (theta)** — student ability score [0.0 to 1.0]
- **b** — question difficulty [0.1 to 1.0]
- **a** — discrimination parameter

Ability Update Rule
After each response, ability is updated:
```
θ_new = θ_old + lr × (response - P)
```
- If **correct** → ability goes UP
- If **incorrect** → ability goes DOWN
- Learning rate = 0.3

Question Selection
Next question is chosen by finding the unanswered question whose difficulty is closest to current ability:
```
best = min(candidates, key=lambda q: abs(q["difficulty"] - current_ability))
```

 Starting Conditions
- Baseline ability: 0.5
- Session length: 10 questions
- Ability range: 0.0 to 1.0

---

🤖 AI Log - How I Used AI Tools

### What AI accelerated:
- **Claude** generated all 25 GRE-style questions with difficulty scores, tags and answer options instantly
- **Claude** helped implement the IRT probability formula and gradient update logic
- **Cursor** autocompleted repetitive FastAPI route boilerplate and Pydantic models
- **Claude** suggested using Motor async MongoDB driver for non-blocking FastAPI compatibility

 What AI could not solve:
- **MongoDB ObjectId serialization** — FastAPI could not serialize ObjectId to JSON by default. Had to manually convert `_id` to string at the right layer
- **IRT clamping edge cases** — AI's initial formula did not clamp values to [0,1] causing runaway scores on answer streaks. Added `max(0.0, min(1.0, ...))` manually
- **Session completion logic** — checking `is_complete` needed to happen after counting new answer not before. AI had logic inverted, caught during manual testing

---
 📁 Project Structure
```
adaptive-engine/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # MongoDB connection
│   ├── models.py            # Pydantic schemas
│   ├── routes/
│   │   ├── sessions.py      # Core test endpoints
│   │   └── questions.py     # Question bank endpoints
│   └── services/
│       ├── adaptive.py      # IRT algorithm
│       └── llm.py           # AI study plan generator
├── seed.py                  # Database seeder
├── requirements.txt
├── .env
└── README.md
```

---

🗄️ MongoDB Schema

questions collection
```json
{
  "_id": "ObjectId",
  "text": "Question text",
  "difficulty": 0.6,
  "discrimination": 1.2,
  "topic": "Algebra",
  "tags": ["quadratic", "factoring"],
  "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
  "correct_answer": "B"
}
```

user_sessions collection
```json
{
  "_id": "ObjectId",
  "student_name": "Alex",
  "ability_score": 0.72,
  "questions_answered": ["id1", "id2"],
  "answers": [
    {
      "question_id": "id1",
      "selected": "C",
      "correct": true,
      "difficulty": 0.4,
      "topic": "Algebra"
    }
  ],
  "is_complete": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```
