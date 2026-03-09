import math
from typing import List, Optional

TOTAL_QUESTIONS = 10
STARTING_ABILITY = 0.5
LEARNING_RATE = 0.3

def irt_probability(ability: float, difficulty: float, discrimination: float = 1.0) -> float:
    exponent = -discrimination * (ability - difficulty)
    return 1.0 / (1.0 + math.exp(exponent))

def update_ability(
    ability: float,
    difficulty: float,
    correct: bool,
    discrimination: float = 1.0,
    lr: float = LEARNING_RATE,
) -> float:
    p = irt_probability(ability, difficulty, discrimination)
    response = 1.0 if correct else 0.0
    new_ability = ability + lr * (response - p)
    return round(max(0.0, min(1.0, new_ability)), 4)

def select_next_question(
    current_ability: float,
    answered_ids: List[str],
    all_questions: List[dict],
) -> Optional[dict]:
    candidates = [q for q in all_questions if str(q["_id"]) not in answered_ids]
    if not candidates:
        return None
    best = min(candidates, key=lambda q: abs(q["difficulty"] - current_ability))
    return best

def is_session_complete(questions_answered: int) -> bool:
    return questions_answered >= TOTAL_QUESTIONS
