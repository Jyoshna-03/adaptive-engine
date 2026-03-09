from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from typing import List

from app.database import get_db
from app.models import SessionStart, SessionOut, AnswerSubmit, AnswerResult, StudyPlan, WeakTopic
from app.services.adaptive import (
    update_ability,
    select_next_question,
    is_session_complete,
    STARTING_ABILITY,
)
from app.services.llm import generate_study_plan

router = APIRouter(prefix="/session", tags=["Session"])

async def _get_session(session_id: str):
    db = get_db()
    try:
        session = await db.user_sessions.find_one({"_id": ObjectId(session_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid session_id format")
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/start", response_model=SessionOut)
async def start_session(body: SessionStart):
    db = get_db()
    session_doc = {
        "student_name": body.student_name,
        "ability_score": STARTING_ABILITY,
        "questions_answered": [],
        "answers": [],
        "is_complete": False,
        "created_at": datetime.utcnow(),
    }
    result = await db.user_sessions.insert_one(session_doc)
    return SessionOut(
        session_id=str(result.inserted_id),
        student_name=body.student_name,
        ability_score=STARTING_ABILITY,
        questions_answered=0,
        message="Session started! Call GET /session/{session_id}/next-question to begin.",
    )

@router.get("/{session_id}/next-question")
async def next_question(session_id: str):
    session = await _get_session(session_id)
    if session["is_complete"]:
        raise HTTPException(status_code=400, detail="Session complete. Fetch /report instead.")
    db = get_db()
    all_questions = await db.questions.find().to_list(length=200)
    question = select_next_question(
        current_ability=session["ability_score"],
        answered_ids=session["questions_answered"],
        all_questions=all_questions,
    )
    if not question:
        raise HTTPException(status_code=404, detail="No more questions available.")
    return {
        "question_id": str(question["_id"]),
        "text": question["text"],
        "options": question["options"],
        "topic": question["topic"],
        "difficulty": question["difficulty"],
        "question_number": len(session["questions_answered"]) + 1,
        "total_questions": 10,
        "current_ability": round(session["ability_score"], 4),
    }

@router.post("/{session_id}/submit-answer", response_model=AnswerResult)
async def submit_answer(session_id: str, body: AnswerSubmit):
    session = await _get_session(session_id)
    if session["is_complete"]:
        raise HTTPException(status_code=400, detail="Session already complete.")
    db = get_db()
    try:
        question = await db.questions.find_one({"_id": ObjectId(body.question_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid question_id")
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if body.question_id in session["questions_answered"]:
        raise HTTPException(status_code=400, detail="Question already answered.")
    is_correct = body.selected_answer.upper() == question["correct_answer"].upper()
    new_ability = update_ability(
        ability=session["ability_score"],
        difficulty=question["difficulty"],
        correct=is_correct,
        discrimination=question.get("discrimination", 1.0),
    )
    updated_answered = session["questions_answered"] + [body.question_id]
    updated_answers = session["answers"] + [{
        "question_id": body.question_id,
        "selected": body.selected_answer.upper(),
        "correct": is_correct,
        "difficulty": question["difficulty"],
        "topic": question["topic"],
    }]
    complete = is_session_complete(len(updated_answered))
    await db.user_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {
            "ability_score": new_ability,
            "questions_answered": updated_answered,
            "answers": updated_answers,
            "is_complete": complete,
        }},
    )
    return AnswerResult(
        correct=is_correct,
        correct_answer=question["correct_answer"],
        explanation=f"{'✅ Correct!' if is_correct else '❌ Incorrect.'} The answer is {question['correct_answer']}.",
        new_ability_score=new_ability,
        questions_answered=len(updated_answered),
        session_complete=complete,
    )

@router.get("/{session_id}/report", response_model=StudyPlan)
async def get_report(session_id: str):
    session = await _get_session(session_id)
    if not session["is_complete"]:
        raise HTTPException(
            status_code=400,
            detail=f"Answer {10 - len(session['questions_answered'])} more questions.",
        )
    answers: List[dict] = session["answers"]
    total = len(answers)
    correct_count = sum(1 for a in answers if a["correct"])
    accuracy = correct_count / total if total else 0
    topic_stats: dict = {}
    for a in answers:
        t = a["topic"]
        if t not in topic_stats:
            topic_stats[t] = {"topic": t, "correct": 0, "total": 0}
        topic_stats[t]["total"] += 1
        if a["correct"]:
            topic_stats[t]["correct"] += 1
    for v in topic_stats.values():
        v["accuracy"] = v["correct"] / v["total"]
    sorted_topics = sorted(topic_stats.values(), key=lambda x: x["accuracy"])
    weak_topics = [WeakTopic(**t) for t in sorted_topics if t["accuracy"] < 0.6]
    strong_topics = [WeakTopic(**t) for t in sorted_topics if t["accuracy"] >= 0.6]
    study_plan_text = await generate_study_plan(
        student_name=session["student_name"],
        ability_score=session["ability_score"],
        accuracy=accuracy,
        weak_topics=[t.model_dump() for t in weak_topics],
        strong_topics=[t.model_dump() for t in strong_topics],
    )
    return StudyPlan(
        student_name=session["student_name"],
        final_ability_score=session["ability_score"],
        total_questions=total,
        accuracy_percent=round(accuracy * 100, 1),
        weak_topics=weak_topics,
        study_plan=study_plan_text,
    )

@router.get("/{session_id}/status")
async def session_status(session_id: str):
    session = await _get_session(session_id)
    return {
        "session_id": session_id,
        "student_name": session["student_name"],
        "ability_score": round(session["ability_score"], 4),
        "questions_answered": len(session["questions_answered"]),
        "is_complete": session["is_complete"],
    }