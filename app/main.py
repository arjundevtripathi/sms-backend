from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from .database import engine, Base, get_db
from .models import Student
from .schemas import StudentCreate

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="Student Management System API",
    description="API for managing students",
    version="1.0.0"
)

# ============ CORS CONFIGURATION ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ============================================

@app.get("/")
def home():
    return {
        "message": "Student Management System API is running!"
    }

@app.get("/health")
def database_test():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "message": "Database connection successful."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/students")
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    # Check whether email already exists
    existing_student = (
        db.query(Student)
        .filter(Student.email == student.email)
        .first()
    )

    if existing_student:
        raise HTTPException(
            status_code=400,
            detail="Student with this email already exists."
        )

    # Create new student
    new_student = Student(
        name=student.name,
        email=student.email,
        age=student.age
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {
        "message": "Student created successfully.",
        "id": new_student.id,
        "name": new_student.name,
        "email": new_student.email,
        "age": new_student.age
    }

@app.get("/students")
def get_all_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return students

@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = (
        db.query(Student).filter(Student.id == student_id).first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )

    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted successfully."
    }