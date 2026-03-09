from fastapi import APIRouter
from app.database import get_db

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.get("/", summary="List all questions")
async def list_questions(topic: str = None, min_diff: float = None, max_diff: float = None):
    db = get_db()
    query = {}
    if topic:
        query["topic"] = {"$regex": topic, "$options": "i"}
    if min_diff is not None:
        query.setdefault("difficulty", {})["$gte"] = min_diff
    if max_diff is not None:
        query.setdefault("difficulty", {})["$lte"] = max_diff
    questions = await db.questions.find(query).to_list(length=200)
    for q in questions:
        q["_id"] = str(q["_id"])
    return {"count": len(questions), "questions": questions}

@router.get("/count", summary="Get total question count")
async def question_count():
    db = get_db()
    count = await db.questions.count_documents({})
    return {"total_questions": count}