from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from formulas import calculate_workload
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, TeachingLoad

app = FastAPI(title="System Rozliczania Obciążeń Dydaktycznych")

Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Model danych wejściowych
class WorkloadInput(BaseModel):
    hours: float
    group_type: str  # Typ grupy np. wykład, ćwiczenia
    employee_level: str  # Stanowisko np. profesor, asystent
    discounts: float = 0.0
    practice_supervisor: bool = False
    committee_member: bool = False
    university_function: bool = False

# Model danych wyjściowych
class WorkloadOutput(BaseModel):
    total_workload: float

@app.get("/")
def read_root():
    return {"message": "Witamy w systemie rozliczania obciążeń dydaktycznych!"}

@app.post("/calculate", response_model=WorkloadOutput)
def calculate_endpoint(input_data: WorkloadInput, db: Session = Depends(get_db)):
    try:
        # Fetch additional data from the database
        teaching_loads = db.query(TeachingLoad).all()
        
        # Process each teaching load and add to respective classes
        for load in teaching_loads:
            result = calculate_workload(
                hours=load.hours,
                group_type=load.group_type,
                employee_level=load.employee_level,
                discounts=input_data.discounts,
                practice_supervisor=input_data.practice_supervisor,
                committee_member=input_data.committee_member,
                university_function=input_data.university_function
            )
            load.total_workload = result
            db.add(load)
        
        db.commit()
        
        # Calculate the workload for the input data
        result = calculate_workload(
            hours=input_data.hours,
            group_type=input_data.group_type,
            employee_level=input_data.employee_level,
            discounts=input_data.discounts,
            practice_supervisor=input_data.practice_supervisor,
            committee_member=input_data.committee_member,
            university_function=input_data.university_function
        )
        
        return {"total_workload": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


