from app.db.database import SessionLocal, engine, Base
from app.models.quiz import Question, Course

# Ensure tables are created
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Initial Questions
seed_data = [
    {
        "question": "What is the capital of India?",
        "course": "General Knowledge",
        "option_a": "Delhi",
        "option_b": "Mumbai",
        "option_c": "Chennai",
        "option_d": "Kolkata",
        "correct_answer": "Delhi",
        "difficulty": "easy"
    },
    {
        "question": "Which array method is used to add elements to the end of an array in JS?",
        "course": "JavaScript Basics",
        "option_a": "push()",
        "option_b": "pop()",
        "option_c": "shift()",
        "option_d": "unshift()",
        "correct_answer": "push()",
        "difficulty": "medium"
    },
    {
        "question": "In Python, which keyword is used to handle exceptions?",
        "course": "Python Basics",
        "option_a": "catch",
        "option_b": "except",
        "option_c": "error",
        "option_d": "try-catch",
        "correct_answer": "except",
        "difficulty": "medium"
    },
    {
        "question": "What is the Big O complexity of accessing an array element by index?",
        "course": "Data Structures and Algorithms",
        "option_a": "O(1)",
        "option_b": "O(log n)",
        "option_c": "O(n)",
        "option_d": "O(n^2)",
        "correct_answer": "O(1)",
        "difficulty": "hard"
    },
    {
        "question": "What does CSS stand for?",
        "course": "Web Development Basics",
        "option_a": "Cascading Style Sheets",
        "option_b": "Creative Style System",
        "option_c": "Computer Style Sheets",
        "option_d": "Colorful Style Sheets",
        "correct_answer": "Cascading Style Sheets",
        "difficulty": "easy"
    }
]

def seed_db():
    if db.query(Course).count() == 0:
        print("Seeding Courses and Questions...")
        
        # 1. Gather all unique courses
        course_names = list(set(item["course"] for item in seed_data))
        course_map = {}
        
        for name in course_names:
            c = Course(course_name=name)
            db.add(c)
            db.flush() # flush to get c.id
            course_map[name] = c.id
            
        # 2. Add Questions
        for data in seed_data:
            c_name = data.pop("course")
            data["course_id"] = course_map[c_name]
            q = Question(**data)
            db.add(q)
            
        db.commit()
        print("Database seeded with sample courses and questions!")
    else:
        print("Database already contains Data. Skipping seed.")

if __name__ == "__main__":
    seed_db()

