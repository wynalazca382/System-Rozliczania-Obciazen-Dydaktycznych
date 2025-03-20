from models import Employee, GroupInstructor, ThesisSupervisors, Reviewer, IndividualRates, OrganizationalUnits, CommitteeFunctionPensum, DidacticCycles, Group, Person, StanowiskaZatr, Employment
from database import SessionLocal
from database import SessionLocal

STAWKI_NADGODZIN = {
    "asystent": 65,
    "asystent n-d": 65,
    "adiunkt": 94,
    "instruktor": 65,
    "lektor": 65,
    "prof. ndzw.": 107,
    "profesor": 129,
    "profesor uczelni": 107,
    "st. wykł.": 80,
    "st. wykł. spec.": 98,
    "wykładowca": 65,
    "st. wykł. doktor": 94,
    "st. wykł. dr spec.": 103,
    "wykł. spec.": 71
}

def calculate_workload_for_employee(employee_id):
    db = SessionLocal()
    try:
        teaching_loads = db.query(GroupInstructor).filter_by(PRAC_ID=employee_id).all()
        thesis_supervisions = db.query(ThesisSupervisors).filter_by(OS_ID=employee_id).all()
        reviews = db.query(Reviewer).filter_by(OS_ID=employee_id).all()
        individual_rates = db.query(IndividualRates).filter_by(PRAC_ID=employee_id).all()
        
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
        
        # Pobieranie stanowiska pracownika
        employee = db.query(Employee).filter_by(ID=employee_id).first()
        prac_zatr = db.query(Employment).filter_by(PRAC_ID=employee_id).first()
        position = db.query(StanowiskaZatr).filter_by(ID=prac_zatr.STAN_ID).first() if prac_zatr else None
        stanowisko = position.NAZWA if position else "N/A"
        
        # Ustalanie stawki na podstawie stanowiska
        stawka = STAWKI_NADGODZIN.get(stanowisko, 0)
        
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
    finally:
        db.close()

def get_group_data():
    db = SessionLocal()
    try:
        groups = db.query(Group).all()
        data = []
        for group in groups:
            # Pobieranie powiązanych danych
            cycle = db.query(DidacticCycles).filter_by(KOD=group.ZAJ_CYK_ID).first()
            instructors = db.query(GroupInstructor).filter_by(ZAJ_CYK_ID=group.ZAJ_CYK_ID, GR_NR=group.NR).all()
            instructor_names = ", ".join([f"{instr.pracownik.osoba.NAZWISKO} {instr.pracownik.osoba.IMIE}" for instr in instructors])
            organizational_unit = db.query(OrganizationalUnits).filter_by(KOD=group.ZAJ_CYK_ID).first()

            group_data = {
                "Symbol grupy": group.OPIS,
                "Studia": cycle.OPIS if cycle else "",
                "Rok": group.NR,
                "Instytut": organizational_unit.OPIS if organizational_unit else "",
                "Specjalność": "",  # Brak odpowiednika w modelach
                "p.d.": group.WAGA_PENSUM,
                "Semestr": cycle.DATA_OD.year if cycle else "",
                "Lstud": group.LIMIT_MIEJSC,
                "Wykonanie": group.ZAKRES_TEMATOW,
                "Przedmiot": "",  # Brak odpowiednika w modelach
                "Nazwisko i imię": instructor_names,
                "stan.": ", ".join([instr.pracownik.stanowisko.NAZWA for instr in instructors]),
                "Inst.": organizational_unit.OPIS if organizational_unit else "",
                "Do Inst.": organizational_unit.OPIS if organizational_unit else "",
                "Zespół": group.ZESPOL,
                "Z/E": group.ZE,
                "Godz.wg siatki W": group.GODZ_WG_SIATKI_W,
                "Godz.wg siatki C": group.GODZ_WG_SIATKI_C,
                "Godz.wg siatki L": group.GODZ_WG_SIATKI_L,
                "Godz.wg siatki P": group.GODZ_WG_SIATKI_P,
                "Godz.wg siatki S": group.GODZ_WG_SIATKI_S,
                "Liczba grup W": group.LICZBA_GRUP_W,
                "Liczba grup C": group.LICZBA_GRUP_C,
                "Liczba grup L": group.LICZBA_GRUP_L,
                "Liczba grup P": group.LICZBA_GRUP_P,
                "Liczba grup S": group.LICZBA_GRUP_S,
                "Łącznie liczba godz. W": group.LACZNIE_LICZBA_GODZ_W,
                "Łącznie liczba godz. C": group.LACZNIE_LICZBA_GODZ_C,
                "Łącznie liczba godz. L": group.LACZNIE_LICZBA_GODZ_L,
                "Łącznie liczba godz. P": group.LACZNIE_LICZBA_GODZ_P,
                "Łącznie liczba godz. S": group.LACZNIE_LICZBA_GODZ_S,
                "Łącznie liczba godz. SUMA": group.LACZNIE_LICZBA_GODZ_SUMA
            }
            data.append(group_data)
        return data
    finally:
        db.close()