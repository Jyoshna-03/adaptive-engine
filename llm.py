import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

def _build_prompt(
    student_name: str,
    ability_score: float,
    accuracy: float,
    weak_topics: List[dict],
    strong_topics: List[dict],
) -> str:
    weak_str = "\n".join(
        f"  - {t['topic']}: {t['correct']}/{t['total']} correct ({t['accuracy']:.0%})"
        for t in weak_topics
    ) or "  - None identified"

    strong_str = "\n".join(
        f"  - {t['topic']}: {t['correct']}/{t['total']} correct ({t['accuracy']:.0%})"
        for t in strong_topics
    ) or "  - None identified"

    ability_label = (
        "Beginner" if ability_score < 0.35
        else "Intermediate" if ability_score < 0.65
        else "Advanced"
    )

    return f"""You are an expert GRE tutor. A student just completed an adaptive diagnostic test.

Student: {student_name}
Overall ability score: {ability_score:.2f}/1.00 ({ability_label})
Overall accuracy: {accuracy:.0%}

Topics needing improvement:
{weak_str}

Strong topics:
{strong_str}

Create a concise 3-step personalized study plan.
Format your response as:

STEP 1: [Title]
[2-3 sentences of specific guidance]

STEP 2: [Title]
[2-3 sentences of specific guidance]

STEP 3: [Title]
[2-3 sentences of specific guidance]"""


async def generate_study_plan(
    student_name: str,
    ability_score: float,
    accuracy: float,
    weak_topics: List[dict],
    strong_topics: List[dict],
) -> str:
    if not ANTHROPIC_API_KEY:
        return _fallback_study_plan(ability_score, weak_topics)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = _build_prompt(student_name, ability_score, accuracy, weak_topics, strong_topics)
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    except Exception as e:
        print(f"⚠️  LLM call failed: {e}")
        return _fallback_study_plan(ability_score, weak_topics)


def _fallback_study_plan(ability_score: float, weak_topics: List[dict]) -> str:
    topics = [t["topic"] for t in weak_topics[:2]] or ["General GRE Skills"]
    return f"""STEP 1: Review Core Concepts in {topics[0]}
Focus on understanding fundamental principles. Work through 20 practice problems
starting from basic difficulty and gradually increasing.

STEP 2: Timed Practice Sessions
Set a timer for 35 minutes and attempt 20 questions in your weak areas.
Review every mistake carefully and understand why the correct answer is right.

STEP 3: Track Progress with Mini-Tests
Take a 10-question mini-test every 3 days on {', '.join(topics)}.
Aim for at least 70% accuracy before moving to harder difficulty levels.

Your current ability score is {ability_score:.2f}/1.00.
Consistent daily practice of 30-45 minutes will show improvement within 2 weeks."""
