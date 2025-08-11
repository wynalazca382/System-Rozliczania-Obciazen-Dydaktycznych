from models import Employee, GroupInstructor, ThesisSupervisors, Reviewer, IndividualRates, OrganizationalUnits, CommitteeFunctionPensum, DidacticCycles, Group, Person, Position, Employment, EmployeePensum, Discount, Position, DidacticCycleClasses , Subject, ClassType, DiscountType, StanowiskaZatrPensum, PensumSettlement
from sqlalchemy import and_
from database import SessionLocal

def calculate_workload_for_employee(employee_id, selected_year, selected_unit, filtered_groups=None):
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
        
        if filtered_groups:
            allowed_group_keys = {(g["Kod przedmiotu"], g["Nr grupy"]) for g in filtered_groups}
            results = [
                r for r in results
                if (r[3].KOD, r[1].NR) in allowed_group_keys
            ]

        total_workload = 0.0
        godziny_dydaktyczne_z_stacjonarne = 0.0
        godziny_dydaktyczne_z_niestacjonarne = 0.0
        godziny_dydaktyczne_l_stacjonarne = 0.0
        godziny_dydaktyczne_l_niestacjonarne = 0.0
        pensum = 0.0
        etat = 1.0
        nadgodziny = 0.0
        stawka = 0.0
        kwota_nadgodzin = 0.0
        CZY_PODSTAWOWE = None
        stanowisko = None
        pensum_uczelniane = 0.0
        umowa_pocz = None
        umowa_kon = None
        # Przetwarzanie wyników
        for group_instructor, group, didactic_class, subject, didactic_cycle, class_type in results:
            godziny = didactic_class.LICZBA_GODZ or 0
            total_workload += godziny
            parsed_code = parse_subject_code(subject.KOD)
            # Rozdzielenie godzin na semestr zimowy i letni
            if "Semestr zimowy" in didactic_cycle.OPIS:
                if "Stacjonarne" in parsed_code["Tryb"]:
                    godziny_dydaktyczne_z_stacjonarne += godziny
                elif "Niestacjonarne" in parsed_code["Tryb"]:
                    godziny_dydaktyczne_z_niestacjonarne += godziny
                else:
                    godziny_dydaktyczne_z_stacjonarne += godziny
            elif "Semestr letni" in didactic_cycle.OPIS:
                if "Stacjonarne" in parsed_code["Tryb"]:
                    godziny_dydaktyczne_l_stacjonarne += godziny
                elif "Niestacjonarne" in parsed_code["Tryb"]:
                    godziny_dydaktyczne_l_niestacjonarne += godziny
                else:
                    godziny_dydaktyczne_l_stacjonarne += godziny
            

        pensum_employee = (
        db.query(EmployeePensum)
        .join(PensumSettlement, EmployeePensum.RPENS_KOD == PensumSettlement.KOD)
        .filter(EmployeePensum.PRAC_ID == employee_id)
        .filter(PensumSettlement.OPIS.like(f"%{selected_year}%"))
        .first()
        )
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
            CZY_PODSTAWOWE = employment.CZY_PODSTAWOWE
            etat = employment.ETAT
            stanowisko = position.NAZWA
            pensum_uczelniane = position.PENSUM_UCZELNIANE
            pensum = position.PENSUM_UCZELNIANE*etat
            umowa_pocz = employment.UMOWA_POCZ
            umowa_kon = employment.UMOWA_KON
        else:
            position = None
            pensum_uczelniane = 0.0
            stanowisko = None
            CZY_PODSTAWOWE = None
        if pensum_employee:
            pensum = pensum_employee.PENSUM     
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
            if znizka.TYP == "O":
                laczna_znizka += znizka.ZNIZKA  
                typy_znizek.append(znizka.discount_type.NAZWA)
                godziny_znizek.append(znizka.ZNIZKA)
            elif znizka.TYP == "D":
                laczna_znizka += pensum - znizka.ZNIZKA
                typy_znizek.append(znizka.discount_type.NAZWA)
                godziny_znizek.append(laczna_znizka)

        # Aktualizacja pensum
        if laczna_znizka > 0:
            pensum -= laczna_znizka
        stawka = STAWKI_NADGODZIN.get(stanowisko, 0)  # Przykładowe stanowisko
        nadgodziny = total_workload - pensum
        kwota_nadgodzin = nadgodziny * stawka
        return {
            "total_workload": total_workload,
            "godziny_dydaktyczne_z_stacjonarne": godziny_dydaktyczne_z_stacjonarne,
            "godziny_dydaktyczne_z_niestacjonarne": godziny_dydaktyczne_z_niestacjonarne,
            "godziny_dydaktyczne_l_stacjonarne": godziny_dydaktyczne_l_stacjonarne,
            "godziny_dydaktyczne_l_niestacjonarne": godziny_dydaktyczne_l_niestacjonarne,
            "pensum": pensum,
            "etat": etat,
            "nadgodziny": nadgodziny,
            "stawka": stawka,
            "kwota_nadgodzin": kwota_nadgodzin if nadgodziny > 0 else 0,
            "zniżka": laczna_znizka,
            "godziny_znizek": godziny_znizek if godziny_znizek else ["Brak zniżek"],
            "typy_znizek": typy_znizek if typy_znizek else ["Brak zniżek"],
            "CZY_PODSTAWOWE": CZY_PODSTAWOWE if CZY_PODSTAWOWE else "Brak danych",
            "stanowisko": stanowisko if stanowisko else "Brak stanowiska",
            "pensum_uczelniane": pensum_uczelniane if pensum_uczelniane else "Brak pensum uczelnianego",
            "umowa_pocz": umowa_pocz if umowa_pocz else "Brak daty rozpoczęcia umowy",
            "umowa_kon": umowa_kon if umowa_kon else "Brak daty zakończenia umowy"
        }
    finally:
        db.close()

def get_group_data(selected_year=None, selected_unit=None, selected_employee=None, current_filtered_groups=None, filtered_employee_ids=None):
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
            if selected_employee:
                query = query.filter(GroupInstructor.PRAC_ID==selected_employee)
        
        if filtered_employee_ids is not None and len(filtered_employee_ids) > 0:
            query = query.filter(GroupInstructor.PRAC_ID.in_(filtered_employee_ids))
        elif filtered_employee_ids is not None and len(filtered_employee_ids) == 0:
            query = query.filter(False)


        results = query.all()

        if current_filtered_groups:
            allowed_group_keys = {(g["Kod przedmiotu"], g["Nr grupy"]) for g in current_filtered_groups}
            results = [
                r for r in results
                if (r[3].KOD, r[1].NR) in allowed_group_keys
            ]
        data = []
        institute_mapping = {
            "1": "IIS",
            "4": "IE",
            "3": "IP",
            "2": "IPJ"
        }
        # Przetwarzanie wyników
        for group_instructor, group, didactic_class, subject, didactic_cycle, class_type, organizational_unit, person in results:
            godziny = didactic_class.LICZBA_GODZ or 0
            subject_code = subject.KOD if subject else "N/A"
            parsed_code = parse_subject_code(subject_code)
            if parsed_code and "Instytut dla którego jest prowadzony przedmiot" in parsed_code:
                institute_code = parsed_code.pop("Instytut dla którego jest prowadzony przedmiot")
                parsed_code["Instytut dla którego jest prowadzony przedmiot"] = institute_mapping.get(institute_code, "Nieznany instytut")
            group_data = {
                "Przedmiot": subject.NAZWA,
                "Typ zajęć": class_type.OPIS,
                "Liczba godzin": godziny,
                "Semestr": didactic_cycle.OPIS,
                "Prowadzący": f"{person.IMIE} {person.NAZWISKO}" if person else "Nieznany prowadzący",
                "Nr grupy": group_instructor.GR_NR,
                "Kod przedmiotu": subject_code,
                "Instytut w którym jest rozliczany przedmiot": organizational_unit.OPIS if organizational_unit else "Brak jednostki",
            }
            if parsed_code:
                group_data = {**parsed_code, **group_data}
            data.append(group_data)

        return data
    finally:
        db.close()

def parse_subject_code(subject_code):
    try:
        parts = subject_code.split("-")
        if len(parts) < 4:
            #raise ValueError("Nieprawidłowy format kodu przedmiotu.")
            institute_code = parts[0]
            kierunek = "None"
            specjalnosc = "Ogólny"
            tryb = "None"
            stopien = "Nieznany stopień"
            rok = "Nieznany rok"
            semestr = "Nieznany semestr"
            extra = "Brak dodatkowego kodu"
        else:
            institute_code = parts[0]
            kierunek = parts[1]
            # Jeśli jest specjalność, to parts[2], jeśli nie, to None
            if len(parts) == 5:
                specjalnosc = parts[2]
                tryb_stopien_rok_semestr = parts[3]
                extra = parts[4]
            elif len(parts) == 4:
                specjalnosc = "Ogólny"
                tryb_stopien_rok_semestr = parts[2]
                extra = parts[3]
            else:
                raise ValueError("Nieprawidłowa liczba części kodu przedmiotu.")

            if len(tryb_stopien_rok_semestr) != 4:
                raise ValueError("Nieprawidłowy format sekcji trybu, stopnia, roku i semestru.")

            tryb = "Stacjonarne" if tryb_stopien_rok_semestr[0] == "S" else "Niestacjonarne"
            stopien_map = {"1": "I stopień", "2": "II stopień", "M": "Magisterskie"}
            stopien = stopien_map.get(tryb_stopien_rok_semestr[1], "Nieznany stopień")
            rok = f"{tryb_stopien_rok_semestr[2]} rok"
            semestr = f"{tryb_stopien_rok_semestr[3]} semestr"

        result = {
            "Instytut dla którego jest prowadzony przedmiot": institute_code,
            "Kierunek": kierunek,
            "Specjalność": specjalnosc,
            "Tryb": tryb,
            "Stopień": stopien,
            "Rok": rok,
            "Semestr": semestr
        }
        # Dodaj dodatkowy kod jeśli jest
        if extra:
            result["Dodatkowy kod"] = extra

        return result

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
    
import pandas as pd
import os

def load_stawki_nadgodzin(filepath="stawki_nadgodzin.xlsx"):
    stawki = {}
    if not os.path.exists(filepath):
        print(f"Plik {filepath} nie istnieje! Używam pustego słownika stawek.")
        return stawki
    df = pd.read_excel(filepath)
    for _, row in df.iterrows():
        stawki[str(row["stanowisko"]).strip()] = float(row["stawka"])
    return stawki

STAWKI_NADGODZIN = load_stawki_nadgodzin()