from models import Employee, GroupInstructor, ThesisSupervisors, Reviewer, IndividualRates, OrganizationalUnits, CommitteeFunctionPensum, DidacticCycles, Group, Person, Position, Employment, EmployeePensum, Discount, Position, DidacticCycleClasses , Subject, ClassType, DiscountType, StanowiskaZatrPensum, PensumSettlement
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
        CZY_PODSTAWOWE = None
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
        #if pensum_employee:
            #print(f"Pobrano pensum dla pracownika {employee_id}: {pensum_employee.PENSUM}")
            #pensum = pensum_employee.PENSUM
        #else:
            # Dodaj pobieranie zakresu dat roku akademickiego
        start_date, end_date = get_academic_year_dates(selected_year)
        employment_qs = (
                db.query(Employment, Position)
                .join(Position, Employment.STAN_ID == Position.ID)
                .filter(Employment.PRAC_ID == employee_id)
                .filter(Employment.UMOWA_POCZ <= end_date)
                .filter((Employment.UMOWA_KON == None) | (Employment.UMOWA_KON == '') | (Employment.UMOWA_KON >= start_date))
                .order_by(Employment.UMOWA_POCZ.desc())
                .all()
            )

        if employment_qs:
            employment, position = employment_qs[0]
            print(employee_id, employment.PRAC_ID)
            print(f"Wybrane pensum: {position.PENSUM_UCZELNIANE} dla umowy od {employment.UMOWA_POCZ} do {employment.UMOWA_KON}")
            pensum = position.PENSUM_UCZELNIANE
            CZY_PODSTAWOWE = employment.CZY_PODSTAWOWE
            etat = employment.ETAT
        # Pobierz wszystkie zniżki dla pracownika
        znizki = (
            db.query(Discount)
            .join(DiscountType, Discount.RODZ_ZNIZ_ID == DiscountType.ID)
            .join(PensumSettlement, Discount.RPENS_KOD == PensumSettlement.KOD)
            .filter(Discount.PRAC_ID == employee_id)
            .filter(DiscountType.CZY_AKTUALNE == 'T')
            .filter(PensumSettlement.OPIS.like(f"%{selected_year}%"))
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
        print(f"Total workload: {total_workload}, Pensum: {pensum}, Nadgodziny: {nadgodziny}, Kwota nadgodzin: {kwota_nadgodzin}")
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
            "CZY_PODSTAWOWE": CZY_PODSTAWOWE if CZY_PODSTAWOWE else "Brak danych"
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

from datetime import date

def get_academic_year_dates(selected_year):
    try:
        start_year = int(selected_year.split("/")[0])
        end_year = start_year + 1
        start_date = date(start_year, 10, 1)
        end_date = date(end_year, 9, 30)
        return start_date, end_date
    except Exception as e:
        print(f"Błąd parsowania roku akademickiego: {e}")
        return None, None