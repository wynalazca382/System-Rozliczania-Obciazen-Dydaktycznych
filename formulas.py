from models import Employee, GroupInstructor, ThesisSupervisors, Reviewer, IndividualRates, OrganizationalUnits, CommitteeFunctionPensum, DidacticCycles, Group, Person, Position, Employment, EmployeePensum, Discount, Position, DidacticCycleClasses , Subject, ClassType, DiscountType
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
            .filter(ClassType.OPIS != "Praktyka zawodowa").filter(~Subject.NAZWA.like("Praktyka zawodowa%"))
        )

        # Dodaj filtrację po jednostce organizacyjnej, jeśli wybrano
        if selected_unit:
            query = query.filter(GroupInstructor.JEDN_KOD == selected_unit)

        results = query.all()
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

        pensum_employee = db.query(EmployeePensum).filter_by(PRAC_ID=employee_id).first()
        if pensum_employee:
            pensum = pensum_employee.PENSUM
        # Pobierz wszystkie zniżki dla pracownika
        znizki = (
            db.query(Discount)
            .join(DiscountType, Discount.RODZ_ZNIZ_ID == DiscountType.ID)
            .filter(Discount.PRAC_ID == employee_id)
            .filter(DiscountType.CZY_AKTUALNE == 'T')
            .all()
        )

        # Inicjalizacja zmiennych dla zniżek
        laczna_znizka = 0
        typy_znizek = []
        godziny_znizek = []

        # Przetwarzanie wszystkich zniżek
        for znizka in znizki:
            laczna_znizka += znizka.ZNIZKA
            typy_znizek.append(znizka.discount_type.NAZWA)
            godziny_znizek.append(znizka.ZNIZKA)

        # Aktualizacja pensum
        if laczna_znizka > 0:
            pensum -= laczna_znizka
        stawka = STAWKI_NADGODZIN.get("stanowisko", 0)  # Przykładowe stanowisko
        nadgodziny = total_workload - pensum
        kwota_nadgodzin = nadgodziny * stawka
        CZY_PODSTAWOWE = db.query(Employment).filter_by(PRAC_ID=employee_id).first()
        return {
            "total_workload": total_workload,
            "godziny_dydaktyczne_z": godziny_dydaktyczne_z,
            "godziny_dydaktyczne_l": godziny_dydaktyczne_l,
            "pensum": pensum,
            "etat": etat,
            "nadgodziny": nadgodziny,
            "stawka": stawka,
            "kwota_nadgodzin": kwota_nadgodzin,
            "zniżka": laczna_znizka,
            "godziny_znizek": godziny_znizek if godziny_znizek else ["Brak zniżek"],
            "typy_znizek": typy_znizek if typy_znizek else ["Brak zniżek"],
            "CZY_PODSTAWOWE": CZY_PODSTAWOWE.CZY_PODSTAWOWE if CZY_PODSTAWOWE else "Brak danych"
        }
    finally:
        db.close()

def get_group_data(selected_year=None, selected_unit=None, selected_employee=None):
    db = SessionLocal()
    try:
        # Pobierz dane grup z powiązanymi informacjami
        query = (
            db.query(GroupInstructor, Group, DidacticCycleClasses, Subject, DidacticCycles, ClassType, OrganizationalUnits, Person)
            .join(Group, and_(
                GroupInstructor.ZAJ_CYK_ID == Group.ZAJ_CYK_ID,
                GroupInstructor.GR_NR == Group.NR
            ))
            .join(DidacticCycleClasses, Group.ZAJ_CYK_ID == DidacticCycleClasses.ID)
            .join(Subject, DidacticCycleClasses.PRZ_KOD == Subject.KOD)
            .join(DidacticCycles, DidacticCycleClasses.CDYD_KOD == DidacticCycles.KOD)
            .join(ClassType, DidacticCycleClasses.TZAJ_KOD == ClassType.KOD)
            .join(OrganizationalUnits, GroupInstructor.JEDN_KOD == OrganizationalUnits.KOD, isouter=True)
            .join(Employee, GroupInstructor.PRAC_ID == Employee.ID)  # Połączenie z Employee
            .join(Person, Employee.OS_ID == Person.ID)  # Połączenie z Person
            .filter(ClassType.OPIS != "Praktyka zawodowa").filter(~Subject.NAZWA.like("Praktyka zawodowa%"))
        )

        # Filtruj po roku akademickim
        if selected_year:
            query = query.filter(DidacticCycles.OPIS.like(f"%{selected_year}%"))

        # Filtruj po jednostce organizacyjnej
        if selected_unit:
            query = query.filter(GroupInstructor.JEDN_KOD == selected_unit)

        if selected_employee:
            query = query.filter(GroupInstructor.PRAC_ID == selected_employee)

        results = query.all()
        data = []
        institute_mapping = {
            "1": "IIS",
            "2": "IE",
            "3": "IP",
            "4": "IPJ"
        }
        # Przetwarzanie wyników
        for group_instructor, group, didactic_class, subject, didactic_cycle, class_type, organizational_unit, person in results:
            if person is None:
                print("Błąd: Brak danych dla osoby!")
            else:
                print(f"Prowadzący: {person.IMIE} {person.NAZWISKO}")
            godziny = didactic_class.LICZBA_GODZ or 0
            subject_code = subject.KOD if subject else "N/A"
            parsed_code = parse_subject_code(subject_code)
            if parsed_code and "Kod instytutu" in parsed_code:
                institute_code = parsed_code.pop("Kod instytutu")
                parsed_code["Instytut"] = institute_mapping.get(institute_code, "Nieznany instytut")
            group_data = {
                "Przedmiot": subject.NAZWA,
                "Typ zajęć": class_type.OPIS,
                "Liczba godzin": godziny,
                "Semestr": didactic_cycle.OPIS,
                "Prowadzący": f"{person.IMIE} {person.NAZWISKO}" if person else "Nieznany prowadzący"
            }
            if parsed_code:
                group_data = {**parsed_code, **group_data}
            data.append(group_data)

        return data
    finally:
        db.close()

def parse_subject_code(subject_code):
    try:
        # Podziel kod przedmiotu na części
        parts = subject_code.split("-")
        if len(parts) < 3:
            raise ValueError("Nieprawidłowy format kodu przedmiotu.")

        # Wyciągnij informacje
        institute_code = parts[0]
        kierunek_specjalnosc = parts[1]
        tryb_stopien_rok_semestr = parts[2]
        if len(tryb_stopien_rok_semestr) != 4:
            raise ValueError("Nieprawidłowy format sekcji trybu, stopnia, roku i semestru.")

        tryb = "Stacjonarne" if tryb_stopien_rok_semestr[0] == "N" else "Niestacjonarne"
        stopien = "I stopień" if tryb_stopien_rok_semestr[1] == "1" else "II stopień"
        rok = f"{tryb_stopien_rok_semestr[2]} rok"
        semestr = f"{tryb_stopien_rok_semestr[3]} semestr"

        # Zwróć wyniki w formie słownika
        return {
            "Kod instytutu": institute_code,
            "Kierunek i specjalność": kierunek_specjalnosc,
            "Tryb": tryb,
            "Stopień": stopien,
            "Rok": rok,
            "Semestr": semestr
        }

    except Exception as e:
        print(f"Błąd podczas parsowania kodu przedmiotu: {e}")
        return None