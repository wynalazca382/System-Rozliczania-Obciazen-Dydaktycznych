from models import Employee, GroupInstructor, ThesisSupervisors, Reviewer, IndividualRates, OrganizationalUnits, CommitteeFunctionPensum, DidacticCycles

def calculate_workload_for_employee(db, employee):
    teaching_loads = db.query(GroupInstructor).filter_by(PRAC_ID=employee.ID).all()
    thesis_supervisions = db.query(ThesisSupervisors).filter_by(OS_ID=employee.ID).all()
    reviews = db.query(Reviewer).filter_by(OS_ID=employee.ID).all()
    individual_rates = db.query(IndividualRates).filter_by(PRAC_ID=employee.ID).all()
    
    total_workload = 0.0
    godziny_dydaktyczne_z = 0.0
    godziny_dydaktyczne_l = 0.0
    pensum = 0.0
    etat = 1.0  # Assuming full-time by default
    nadgodziny = 0.0
    stawka = 0.0
    kwota_nadgodzin = 0.0
    zw_godz_z = 0.0
    zw_godz_l = 0.0
    zw_kwota_z = 0.0
    zw_kwota_l = 0.0
    
    for load in teaching_loads:
        if load.SEMESTER == 'Z':
            godziny_dydaktyczne_z += load.LICZBA_GODZ_DO_PENSUM
        elif load.SEMESTER == 'L':
            godziny_dydaktyczne_l += load.LICZBA_GODZ_DO_PENSUM
        total_workload += load.LICZBA_GODZ_DO_PENSUM
        teaching_cycle = db.query(DidacticCycles).filter_by(ID=load.ZAJ_CYK_ID).first()
        if teaching_cycle:
            pensum_record = db.query(CommitteeFunctionPensum).filter_by(CDYD_KON=teaching_cycle.KOD).first()
            if pensum_record:
                pensum += pensum_record.PENSUM
    
    for supervision in thesis_supervisions:
        total_workload += supervision.LICZBA_GODZ_DO_PENSUM
    
    for review in reviews:
        total_workload += review.LICZBA_GODZ_DO_PENSUM
    
    for rate in individual_rates:
        stawka = rate.STAWKA
        total_workload *= rate.STAWKA
    
    nadgodziny = total_workload - pensum if total_workload > pensum else 0
    kwota_nadgodzin = nadgodziny * stawka
    
    return {
        "total_workload": total_workload,
        "godziny_dydaktyczne_z": godziny_dydaktyczne_z,
        "godziny_dydaktyczne_l": godziny_dydaktyczne_l,
        "pensum": pensum,
        "etat": etat,
        "nadgodziny": nadgodziny,
        "stawka": stawka,
        "kwota_nadgodzin": kwota_nadgodzin,
        "zw_godz_z": zw_godz_z,
        "zw_godz_l": zw_godz_l,
        "zw_kwota_z": zw_kwota_z,
        "zw_kwota_l": zw_kwota_l
    }