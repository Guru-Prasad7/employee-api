from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./employees.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DB Model
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    department = Column(String)
    salary = Column(Float)

Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class EmployeeCreate(BaseModel):
    name: str
    email: str
    department: str
    salary: float

class EmployeeResponse(EmployeeCreate):
    id: int
    class Config:
        orm_mode = True

# FastAPI app
app = FastAPI(title="Employee Management API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Employee Management API is running"}

@app.post("/employees", response_model=EmployeeResponse)
def create_employee(employee: EmployeeCreate):
    db = SessionLocal()
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    db.close()
    return db_employee

@app.get("/employees", response_model=List[EmployeeResponse])
def get_employees():
    db = SessionLocal()
    employees = db.query(Employee).all()
    db.close()
    return employees

@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int):
    db = SessionLocal()
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    db.close()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@app.put("/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, updated: EmployeeCreate):
    db = SessionLocal()
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        db.close()
        raise HTTPException(status_code=404, detail="Employee not found")
    employee.name = updated.name
    employee.email = updated.email
    employee.department = updated.department
    employee.salary = updated.salary
    db.commit()
    db.refresh(employee)
    db.close()
    return employee

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    db = SessionLocal()
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        db.close()
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    db.close()
    return {"message": "Employee deleted successfully"}
