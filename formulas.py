from models import Employee, GroupInstructor, ThesisSupervisors, Reviewer, IndividualRates, OrganizationalUnits, CommitteeFunctionPensum, DidacticCycles, Group, Person, Position, Employment, EmployeePensum, Discount, Position, DidacticCycleClasses , Subject, ClassType
from sqlalchemy import and_
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

def calculate_workload_for_employee(employee_id, selected_year, selected_unit):
    db = SessionLocal()
    try:
        # Pobierz zajęcia dydaktyczne dla pracownika z filtrowaniem po roku akademickim i jednostce organizacyjnej
        query = (
            db.query(GroupInstructor, Group, DidacticCycleClasses, Subject, DidacticCycles, ClassType)
            .join(Group, and_(
                GroupInstructor.ZAJ_CYK_ID == Group.ZAJ_CYK_ID,
                GroupInstructor.GR_NR == Group.NR
            ))
            .join(DidacticCycleClasses, Group.ZAJ_CYK_ID == DidacticCycleClasses.ID)
            .join(Subject, DidacticCycleClasses.PRZ_KOD == Subject.KOD)
            .join(DidacticCycles, DidacticCycleClasses.CDYD_KOD == DidacticCycles.KOD)
            .join(ClassType, DidacticCycleClasses.TZAJ_KOD == ClassType.KOD)
            .filter(GroupInstructor.PRAC_ID == employee_id)
            .filter(DidacticCycles.OPIS.like(f"%{selected_year}%"))
        )

        # Dodaj filtrację po jednostce organizacyjnej, jeśli wybrano
        if selected_unit:
            query = query.filter(GroupInstructor.JEDN_KOD == selected_unit)

        results = query.all()
        print(f"Filtr roku akademickiego: {selected_year}")
        total_workload = 0.0
        godziny_dydaktyczne_z = 0.0
        godziny_dydaktyczne_l = 0.0
        pensum = 0.0
        etat = 1.0
        nadgodziny = 0.0
        stawka = 0.0
        kwota_nadgodzin = 0.0

        # Przetwarzanie wyników
        for group_instructor, group, didactic_class, subject, didactic_cycle, class_type in results:
            godziny = didactic_class.LICZBA_GODZ or 0
            total_workload += godziny

            # Rozdzielenie godzin na semestr zimowy i letni
            if "Semestr zimowy" in didactic_cycle.OPIS:
                godziny_dydaktyczne_z += godziny
            elif "Semestr letni" in didactic_cycle.OPIS:
                godziny_dydaktyczne_l += godziny

            # Debugowanie: Wyświetl dodatkowe informacje
            print(f"Przedmiot: {subject.NAZWA}, Typ zajęć: {class_type.OPIS}, Liczba godzin: {godziny}")

        # Obliczenia pensum, nadgodzin i stawki
        pensum_employee = db.query(EmployeePensum).filter_by(PRAC_ID=employee_id).first()
        if pensum_employee:
            pensum = pensum_employee.PENSUM

        stawka = STAWKI_NADGODZIN.get("stanowisko", 0)  # Przykładowe stanowisko
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
                "Symbol grupy": group.GR_NR,
                "Studia": 0,
                "Rok": 0,
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