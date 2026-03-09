import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "adaptive_engine")

QUESTIONS = [
    {
        "text": "What is 15% of 200?",
        "difficulty": 0.1,
        "discrimination": 0.8,
        "topic": "Arithmetic",
        "tags": ["percentages", "basic-math"],
        "options": ["A) 20", "B) 25", "C) 30", "D) 35"],
        "correct_answer": "C",
    },
    {
        "text": "If a train travels 60 miles in 1.5 hours, what is its average speed?",
        "difficulty": 0.2,
        "discrimination": 1.0,
        "topic": "Arithmetic",
        "tags": ["rates", "speed"],
        "options": ["A) 30", "B) 40", "C) 45", "D) 50"],
        "correct_answer": "B",
    },
    {
        "text": "What is the value of 3³ + 4²?",
        "difficulty": 0.25,
        "discrimination": 0.9,
        "topic": "Arithmetic",
        "tags": ["exponents", "basic-math"],
        "options": ["A) 37", "B) 41", "C) 43", "D) 49"],
        "correct_answer": "C",
    },
    {
        "text": "If 2x + 5 = 17, what is the value of x?",
        "difficulty": 0.2,
        "discrimination": 1.0,
        "topic": "Algebra",
        "tags": ["linear-equations", "solving"],
        "options": ["A) 4", "B) 6", "C) 8", "D) 10"],
        "correct_answer": "B",
    },
    {
        "text": "Which value of x satisfies x² - 5x + 6 = 0?",
        "difficulty": 0.4,
        "discrimination": 1.2,
        "topic": "Algebra",
        "tags": ["quadratic", "factoring"],
        "options": ["A) x=1 or x=6", "B) x=2 or x=3", "C) x=-2 or x=-3", "D) x=3 or x=5"],
        "correct_answer": "B",
    },
    {
        "text": "If f(x) = 3x² - 2x + 1, what is f(-2)?",
        "difficulty": 0.5,
        "discrimination": 1.2,
        "topic": "Algebra",
        "tags": ["functions", "substitution"],
        "options": ["A) 7", "B) 9", "C) 17", "D) 21"],
        "correct_answer": "C",
    },
    {
        "text": "A store marks up a $40 item by 25% then discounts by 20%. What is the final price?",
        "difficulty": 0.55,
        "discrimination": 1.3,
        "topic": "Algebra",
        "tags": ["word-problems", "percent-change"],
        "options": ["A) $38", "B) $39", "C) $40", "D) $42"],
        "correct_answer": "C",
    },
    {
        "text": "If |2x - 3| = 7, which is a possible value of x?",
        "difficulty": 0.65,
        "discrimination": 1.4,
        "topic": "Algebra",
        "tags": ["absolute-value", "equations"],
        "options": ["A) -2", "B) -1", "C) 2", "D) 5"],
        "correct_answer": "D",
    },
    {
        "text": "For what value of k does 2x + ky = 8, 4x + 6y = 16 have infinitely many solutions?",
        "difficulty": 0.8,
        "discrimination": 1.5,
        "topic": "Algebra",
        "tags": ["systems-of-equations"],
        "options": ["A) 2", "B) 3", "C) 4", "D) 6"],
        "correct_answer": "B",
    },
    {
        "text": "A circle has radius 7. What is its area? (π ≈ 3.14)",
        "difficulty": 0.3,
        "discrimination": 1.0,
        "topic": "Geometry",
        "tags": ["circles", "area"],
        "options": ["A) 44.0", "B) 153.86", "C) 169.0", "D) 196.0"],
        "correct_answer": "B",
    },
    {
        "text": "Two angles of a triangle are 55° and 75°. What is the third angle?",
        "difficulty": 0.2,
        "discrimination": 0.9,
        "topic": "Geometry",
        "tags": ["triangles", "angles"],
        "options": ["A) 40°", "B) 45°", "C) 50°", "D) 60°"],
        "correct_answer": "C",
    },
    {
        "text": "A rectangle has perimeter 48 cm. Length is twice the width. What is the area?",
        "difficulty": 0.45,
        "discrimination": 1.2,
        "topic": "Geometry",
        "tags": ["rectangles", "area"],
        "options": ["A) 96 cm²", "B) 112 cm²", "C) 128 cm²", "D) 144 cm²"],
        "correct_answer": "C",
    },
    {
        "text": "In a right triangle, legs are 9 and 12. What is the hypotenuse?",
        "difficulty": 0.35,
        "discrimination": 1.1,
        "topic": "Geometry",
        "tags": ["pythagorean-theorem"],
        "options": ["A) 13", "B) 14", "C) 15", "D) 16"],
        "correct_answer": "C",
    },
    {
        "text": "A cone has base radius 3 and height 4. What is its volume? (V=⅓πr²h, π≈3.14)",
        "difficulty": 0.7,
        "discrimination": 1.4,
        "topic": "Geometry",
        "tags": ["3D-shapes", "volume"],
        "options": ["A) 28.26", "B) 37.68", "C) 50.24", "D) 75.36"],
        "correct_answer": "B",
    },
    {
        "text": "The word EPHEMERAL most nearly means:",
        "difficulty": 0.45,
        "discrimination": 1.2,
        "topic": "Vocabulary",
        "tags": ["gre-words", "adjectives"],
        "options": ["A) Permanent", "B) Short-lived", "C) Mysterious", "D) Abundant"],
        "correct_answer": "B",
    },
    {
        "text": "The word PERFIDIOUS most nearly means:",
        "difficulty": 0.6,
        "discrimination": 1.3,
        "topic": "Vocabulary",
        "tags": ["gre-words", "adjectives"],
        "options": ["A) Loyal", "B) Treacherous", "C) Talented", "D) Stubborn"],
        "correct_answer": "B",
    },
    {
        "text": "Choose the word most OPPOSITE in meaning to LACONIC:",
        "difficulty": 0.7,
        "discrimination": 1.4,
        "topic": "Vocabulary",
        "tags": ["antonyms", "gre-words"],
        "options": ["A) Quiet", "B) Brief", "C) Verbose", "D) Timid"],
        "correct_answer": "C",
    },
    {
        "text": "ENERVATE : WEAKEN :: OBFUSCATE : ___",
        "difficulty": 0.85,
        "discrimination": 1.6,
        "topic": "Vocabulary",
        "tags": ["analogies", "gre-words"],
        "options": ["A) Clarify", "B) Confuse", "C) Strengthen", "D) Expand"],
        "correct_answer": "B",
    },
    {
        "text": "Passage: 'The placebo effect shows belief alone can trigger physiological changes. Patients given sugar pills report significant symptom relief.' The passage supports which conclusion?",
        "difficulty": 0.5,
        "discrimination": 1.2,
        "topic": "Reading Comprehension",
        "tags": ["inference", "main-idea"],
        "options": ["A) Sugar pills are medicine", "B) Doctors should prescribe placebos", "C) Mental states influence physical health", "D) Symptom relief needs chemicals"],
        "correct_answer": "C",
    },
    {
        "text": "Passage: 'Critics argue social media erodes attention spans while proponents say it fosters global connectivity.' The author's attitude is best described as:",
        "difficulty": 0.6,
        "discrimination": 1.3,
        "topic": "Reading Comprehension",
        "tags": ["author-tone", "inference"],
        "options": ["A) Strongly positive", "B) Strongly negative", "C) Balanced", "D) Indifferent"],
        "correct_answer": "C",
    },
    {
        "text": "The mean of five numbers is 12. Four numbers are 10, 11, 13, 14. What is the fifth?",
        "difficulty": 0.4,
        "discrimination": 1.1,
        "topic": "Statistics",
        "tags": ["mean", "averages"],
        "options": ["A) 10", "B) 11", "C) 12", "D) 13"],
        "correct_answer": "C",
    },
    {
        "text": "In data set {3, 7, 7, 9, 10, 12}, what is the median?",
        "difficulty": 0.35,
        "discrimination": 1.0,
        "topic": "Statistics",
        "tags": ["median", "descriptive-stats"],
        "options": ["A) 7", "B) 8", "C) 9", "D) 9.5"],
        "correct_answer": "B",
    },
    {
        "text": "If P(A)=0.4 and P(B)=0.3 and A,B are independent, what is P(A and B)?",
        "difficulty": 0.65,
        "discrimination": 1.4,
        "topic": "Statistics",
        "tags": ["probability", "independence"],
        "options": ["A) 0.07", "B) 0.10", "C) 0.12", "D) 0.70"],
        "correct_answer": "C",
    },
    {
        "text": "A box has 4 red and 6 blue balls. Two drawn WITHOUT replacement. P(both red)?",
        "difficulty": 0.75,
        "discrimination": 1.5,
        "topic": "Statistics",
        "tags": ["probability", "without-replacement"],
        "options": ["A) 2/15", "B) 4/25", "C) 1/5", "D) 8/25"],
        "correct_answer": "A",
    },
    {
        "text": "Column A: std dev of {2,2,2,2}. Column B: std dev of {1,2,3,4}. Which is greater?",
        "difficulty": 0.9,
        "discrimination": 1.7,
        "topic": "Statistics",
        "tags": ["standard-deviation"],
        "options": ["A) Column A", "B) Column B", "C) Equal", "D) Cannot determine"],
        "correct_answer": "B",
    },
]


async def seed():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    deleted = await db.questions.delete_many({})
    print(f"🗑️  Cleared {deleted.deleted_count} existing questions.")
    result = await db.questions.insert_many(QUESTIONS)
    print(f"✅ Seeded {len(result.inserted_ids)} questions into '{DB_NAME}.questions'")
    await db.questions.create_index("difficulty")
    await db.questions.create_index("topic")
    await db.user_sessions.create_index("created_at")
    print("📇 Indexes created.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())