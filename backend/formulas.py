from models import Employee, GroupInstructor, ThesisSupervisors, Reviewer, IndividualRates, OrganizationalUnits, CommitteeFunctionPensum, DidacticCycles

def calculate_workload_for_employee(db, employee):
    teaching_loads = db.query(GroupInstructor).filter_by(PRAC_ID=employee.ID).all()
    thesis_supervisions = db.query(ThesisSupervisors).filter_by(OS_ID=employee.ID).all()
    reviews = db.query(Reviewer).filter_by(OS_ID=employee.ID).all()
    individual_rates = db.query(IndividualRates).filter_by(PRAC_ID=employee.ID).all()
    
    total_workload = 0.0
    
    for load in teaching_loads:
        total_workload += load.LICZBA_GODZ_DO_PENSUM
        teaching_cycle = db.query(DidacticCycles).filter_by(ID=load.ZAJ_CYK_ID).first()
        if teaching_cycle:
            pensum = db.query(CommitteeFunctionPensum).filter_by(CDYD_KON=teaching_cycle.KOD).first()
            if pensum:
                total_workload += pensum.PENSUM
    
    for supervision in thesis_supervisions:
        total_workload += supervision.LICZBA_GODZ_DO_PENSUM
    
    for review in reviews:
        total_workload += review.LICZBA_GODZ_DO_PENSUM
    
    for rate in individual_rates:
        total_workload *= rate.STAWKA
    
    return total_workload