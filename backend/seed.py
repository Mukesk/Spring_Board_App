from app.db.database import SessionLocal, engine, Base
from app.models.quiz import Question

# Ensure tables are created
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Initial Questions
seed_data = [
    {
        "question": "What is the capital of India?",
        "option_a": "Delhi",
        "option_b": "Mumbai",
        "option_c": "Chennai",
        "option_d": "Kolkata",
        "correct_answer": "Delhi",
        "difficulty": "easy"
    },
    {
        "question": "Which array method is used to add elements to the end of an array in JS?",
        "option_a": "push()",
        "option_b": "pop()",
        "option_c": "shift()",
        "option_d": "unshift()",
        "correct_answer": "push()",
        "difficulty": "medium"
    },
    {
        "question": "In Python, which keyword is used to handle exceptions?",
        "option_a": "catch",
        "option_b": "except",
        "option_c": "error",
        "option_d": "try-catch",
        "correct_answer": "except",
        "difficulty": "medium"
    },
    {
        "question": "What is the Big O complexity of accessing an array element by index?",
        "option_a": "O(1)",
        "option_b": "O(log n)",
        "option_c": "O(n)",
        "option_d": "O(n^2)",
        "correct_answer": "O(1)",
        "difficulty": "hard"
    },
    {
        "question": "What does CSS stand for?",
        "option_a": "Cascading Style Sheets",
        "option_b": "Creative Style System",
        "option_c": "Computer Style Sheets",
        "option_d": "Colorful Style Sheets",
        "correct_answer": "Cascading Style Sheets",
        "difficulty": "easy"
    }
]

def seed_db():
    # Only seed if no questions exist
    if db.query(Question).count() == 0:
        for data in seed_data:
            q = Question(**data)
            db.add(q)
        db.commit()
        print("Database seeded with sample questions!")
    else:
        print("Database already contains questions. Skipping seed.")

if __name__ == "__main__":
    seed_db()
