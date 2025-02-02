from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from formulas import calculate_workload
from sqlalchemy.orm import Session
from database import SessionLocal, engine, get_db, Base
from models import Base, Employee, TeachingLoad, ThesisSupervisors, Reviewer, IndividualRates

app = FastAPI(title="System Rozliczania Obciążeń Dydaktycznych")

Base.metadata.create_all(bind=engine)

class WorkloadInput(BaseModel):
    hours: float
    group_type: str  # Typ grupy np. wykład, ćwiczenia
    employee_level: str  # Stanowisko np. profesor, asystent
    discounts: float = 0.0
    practice_supervisor: bool = False
    committee_member: bool = False
    university_function: bool = False

class WorkloadOutput(BaseModel):
    total_workload: float

@app.get("/")
def read_root():
    return {"message": "Witamy w systemie rozliczania obciążeń dydaktycznych!"}

@app.post("/calculate", response_model=WorkloadOutput)
def calculate_endpoint(input_data: WorkloadInput, db: Session = Depends(get_db)):
    try:
        # Fetch all relevant data for each employee
        employees = db.query(Employee).all()
        
        for employee in employees:
            teaching_loads = db.query(TeachingLoad).filter_by(employee_id=employee.ID).all()
            thesis_supervisions = db.query(ThesisSupervisors).filter_by(OS_ID=employee.ID).all()
            reviews = db.query(Reviewer).filter_by(OS_ID=employee.ID).all()
            individual_rates = db.query(IndividualRates).filter_by(PRAC_ID=employee.ID).all()
            
            total_workload = 0.0
            
            # Calculate workload for teaching loads
            for load in teaching_loads:
                result = calculate_workload(
                    hours=load.hours,
                    group_type=load.group_type,
                    employee_level=employee.level,
                    discounts=input_data.discounts,
                    practice_supervisor=input_data.practice_supervisor,
                    committee_member=input_data.committee_member,
                    university_function=input_data.university_function
                )
                total_workload += result
            
            # Calculate workload for thesis supervisions
            for supervision in thesis_supervisions:
                total_workload += supervision.LICZBA_GODZ_DO_PENSUM  # Adjust as needed
            
            # Calculate workload for reviews
            for review in reviews:
                total_workload += review.LICZBA_GODZ_DO_PENSUM  # Adjust as needed
            
            # Apply individual rates
            for rate in individual_rates:
                total_workload *= rate.STAWKA  # Adjust as needed
            
            employee.total_workload = total_workload
            db.add(employee)
        
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