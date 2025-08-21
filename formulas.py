from models import Employee, GroupInstructor, ThesisSupervisors, Reviewer, IndividualRates, OrganizationalUnits, CommitteeFunctionPensum, DidacticCycles, Group, Person, Position, Employment, EmployeePensum, Discount, Position, DidacticCycleClasses , Subject, ClassType, DiscountType, StanowiskaZatrPensum, PensumSettlement
from sqlalchemy import and_
from database import SessionLocal
from typing import Dict, Any, List, Optional, Tuple
from datetime import date
import pandas as pd
import os

def calculate_workload_for_employee(employee_id: int, selected_year: str, selected_unit: Optional[str], filtered_groups: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        # Pobierz dane pracownika, aby uzyskać imię i nazwisko
        employee = db.query(Employee).join(Person, Employee.OS_ID == Person.ID).filter(Employee.ID == employee_id).first()
        if not employee:
            return {
                "total_workload": 0.0,
                "godziny_dydaktyczne_z_stacjonarne": 0.0,
                "godziny_dydaktyczne_z_niestacjonarne": 0.0,
                "godziny_dydaktyczne_l_stacjonarne": 0.0,
                "godziny_dydaktyczne_l_niestacjonarne": 0.0,
                "pensum": 0.0,
                "etat": 1.0,
                "nadgodziny": 0.0,
                "stawka": 0.0,
                "kwota_nadgodzin": 0.0,
                "zniżka": 0.0,
                "godziny_znizek": ["Brak zniżek"],
                "typy_znizek": ["Brak zniżek"],
                "CZY_PODSTAWOWE": "Brak danych",
                "stanowisko": "Brak stanowiska",
                "pensum_uczelniane": "Brak pensum uczelnianego",
                "umowa_pocz": "Brak daty rozpoczęcia umowy",
                "umowa_kon": "Brak daty zakończenia umowy"
            }
        
        employee_name: str = f"{employee.person.IMIE} {employee.person.NAZWISKO}"
        
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

        results: List[Tuple[GroupInstructor, Any, DidacticCycleClasses, Subject, DidacticCycles, ClassType]] = query.all()
        
        if filtered_groups:
            # Filtruj filtered_groups po pracowniku
            employee_filtered_groups: List[Dict[str, Any]] = [g for g in filtered_groups if g.get("Prowadzący") == employee_name]
            allowed_group_keys: set[Tuple[str, Any, str]] = {(g["Kod przedmiotu"], g["Nr grupy"], g["Typ zajęć"]) for g in employee_filtered_groups}
            results = [
                r for r in results
                if (r[3].KOD, r[1].NR, r[5].OPIS) in allowed_group_keys
            ]

        total_workload: float = 0.0
        godziny_dydaktyczne_z_stacjonarne: float = 0.0
        godziny_dydaktyczne_z_niestacjonarne: float = 0.0
        godziny_dydaktyczne_l_stacjonarne: float = 0.0
        godziny_dydaktyczne_l_niestacjonarne: float = 0.0
        pensum: float = 0.0
        etat: float = 1.0
        nadgodziny: float = 0.0
        stawka: float = 0.0
        kwota_nadgodzin: float = 0.0
        CZY_PODSTAWOWE: Optional[str] = None
        stanowisko: Optional[str] = None
        pensum_uczelniane: float = 0.0
        umowa_pocz: Optional[date] = None
        umowa_kon: Optional[date] = None
        # Przetwarzanie wyników
        for group_instructor, group, didactic_class, subject, didactic_cycle, class_type in results:
            godziny: float = float(didactic_class.LICZBA_GODZ or 0)
            total_workload += godziny
            parsed_code: Optional[Dict[str, str]] = parse_subject_code(subject.KOD)
            if parsed_code:
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
        start_date_acad: Optional[date]
        end_date_acad: Optional[date]
        start_date_acad, end_date_acad = get_academic_year_dates(selected_year)
        
        employment_qs: List[Tuple[Employment, Position]] = []
        if start_date_acad and end_date_acad:
            employment_qs = (
                        db.query(Employment, Position)
                        .join(Position, Employment.STAN_ID == Position.ID)
                        .filter(Employment.PRAC_ID == employee_id)
                        .filter(Employment.UMOWA_POCZ <= end_date_acad)
                        .filter((Employment.UMOWA_KON == None) | (Employment.UMOWA_KON == '') | (Employment.UMOWA_KON >= start_date_acad))
                        .order_by(Employment.UMOWA_POCZ.desc())
                        .all()
                    )

        if employment_qs:
            employment, position = employment_qs[0]
            CZY_PODSTAWOWE = employment.CZY_PODSTAWOWE
            etat = float(employment.ETAT)
            stanowisko = position.NAZWA
            pensum_uczelniane = float(position.PENSUM_UCZELNIANE)
            pensum = pensum_uczelniane * etat
            umowa_pocz = employment.UMOWA_POCZ
            umowa_kon = employment.UMOWA_KON
        else:
            pensum_uczelniane = 0.0
            stanowisko = None
            CZY_PODSTAWOWE = None
        if pensum_employee:
            pensum = float(pensum_employee.PENSUM)     
        # Pobierz wszystkie zniżki dla pracownika
        znizki: List[Discount] = (
            db.query(Discount)
            .join(DiscountType, Discount.RODZ_ZNIZ_ID == DiscountType.ID)
            .join(PensumSettlement, Discount.RPENS_KOD == PensumSettlement.KOD)
            .filter(Discount.PRAC_ID == employee_id)
            .filter(DiscountType.CZY_AKTUALNE == 'T')
            .filter(PensumSettlement.OPIS.like(f"%{selected_year}%"))
            .all()
        )

        # Inicjalizacja zmiennych dla zniżek
        laczna_znizka: float = 0.0
        typy_znizek: List[str] = []
        godziny_znizek: List[float] = []

        # Przetwarzanie wszystkich zniżek
        for znizka in znizki:
            if znizka.TYP == "O":
                laczna_znizka += float(znizka.ZNIZKA)  
                typy_znizek.append(znizka.discount_type.NAZWA)
                godziny_znizek.append(float(znizka.ZNIZKA))
            elif znizka.TYP == "D":
                laczna_znizka += pensum - float(znizka.ZNIZKA)
                typy_znizek.append(znizka.discount_type.NAZWA)
                godziny_znizek.append(laczna_znizka)

        # Aktualizacja pensum
        if laczna_znizka > 0:
            pensum -= laczna_znizka
        stawka = STAWKI_NADGODZIN.get(stanowisko, 0.0)  # Przykładowe stanowisko
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
            "kwota_nadgodzin": kwota_nadgodzin if nadgodziny > 0 else 0.0,
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

def get_group_data(selected_year: Optional[str] = None, selected_unit: Optional[str] = None, selected_employee: Optional[int] = None, current_filtered_groups: Optional[List[Dict[str, Any]]] = None, filtered_employee_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
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

        if filtered_employee_ids is not None and len(filtered_employee_ids) > 0:
            query = query.filter(GroupInstructor.PRAC_ID.in_(filtered_employee_ids))
        elif filtered_employee_ids is not None and len(filtered_employee_ids) == 0:
            query = query.filter(False)

        results: List[Tuple[GroupInstructor, Any, DidacticCycleClasses, Subject, DidacticCycles, ClassType, Optional[OrganizationalUnits], Person]] = query.all()

        if current_filtered_groups:
            allowed_group_keys: set[Tuple[str, Any, str]] = {(g["Kod przedmiotu"], g["Typ zajęć"]) for g in current_filtered_groups}
            results = [
                r for r in results
                if (r[3].KOD, r[5].OPIS) in allowed_group_keys
            ]

        data: List[Dict[str, Any]] = []
        institute_mapping: Dict[str, str] = {
            "1": "Instytut Informatyki Stosowanej im. Krzysztofa Brzeskiego",
            "4": "Instytut Ekonomiczny",
            "3": "Instytut Politechniczny",
            "2": "Instytut Pedagogiczno-Językowy"
        }

        # Słownik do grupowania danych
        grouped_data = {}
        
        for group_instructor, group, didactic_class, subject, didactic_cycle, class_type, organizational_unit, person in results:
            godziny: float = float(didactic_class.LICZBA_GODZ or 0)
            subject_code: str = subject.KOD if subject else "N/A"
            parsed_code: Optional[Dict[str, str]] = parse_subject_code(subject_code)
            
            # Klucz do grupowania: semestr, prowadzący, typ zajęć, liczba godzin, kod przedmiotu
            group_key = (
                didactic_cycle.OPIS,
                f"{person.IMIE} {person.NAZWISKO}" if person else "Nieznany prowadzący",
                class_type.OPIS,
                godziny,
                subject_code,
                organizational_unit.OPIS if organizational_unit else "Brak jednostki",
                subject.NAZWA
            )
            
            if group_key not in grouped_data:
                grouped_data[group_key] = {
                    "count": 0,
                    "parsed_code": parsed_code
                }
            grouped_data[group_key]["count"] += 1

        # Przetwórz zgrupowane dane do finalnego formatu
        for key, value in grouped_data.items():
            semestr, prowadzacy, typ_zajec, godziny, kod_przedmiotu, instytut, przedmiot = key
            group_data = {
                "Przedmiot": przedmiot,
                "Prowadzący": prowadzacy,
                "Typ zajęć": typ_zajec,
                "Liczba godzin": godziny,
                "Semestr": semestr,
                "Liczba grup": value["count"],
                "Łączne godziny": godziny * value["count"],
                "Kod przedmiotu": kod_przedmiotu,
                "Instytut w którym jest rozliczany przedmiot": instytut,
            }
            
            # Dodaj dane z parsowanego kodu jeśli istnieją
            if value["parsed_code"]:
                if "Instytut dla którego jest prowadzony przedmiot" in value["parsed_code"]:
                    institute_code = value["parsed_code"].pop("Instytut dla którego jest prowadzony przedmiot")
                    value["parsed_code"]["Instytut dla którego jest prowadzony przedmiot"] = institute_mapping.get(institute_code, "Nieznany instytut")
                group_data = {**value["parsed_code"], **group_data}
            
            data.append(group_data)

        return data
    finally:
        db.close()



def parse_subject_code(subject_code: str) -> Optional[Dict[str, str]]:
    try:
        parts: List[str] = subject_code.split("-")
        institute_code: str
        kierunek: str
        specjalnosc: str
        tryb: str
        stopien: str
        rok: str
        semestr: str
        extra: str = "Brak dodatkowego kodu"

        if len(parts) < 4:
            institute_code = parts[0]
            kierunek = "None"
            specjalnosc = "Ogólny"
            tryb = "None"
            stopien = "Nieznany stopień"
            rok = "Nieznany rok"
            semestr = "Nieznany semestr"
        else:
            institute_code = parts[0]
            kierunek = parts[1]
            if len(parts) == 5:
                specjalnosc = parts[2]
                tryb_stopien_rok_semestr: str = parts[3]
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
            stopien_map: Dict[str, str] = {"1": "I stopień", "2": "II stopień", "M": "Magisterskie"}
            stopien = stopien_map.get(tryb_stopien_rok_semestr[1], "Nieznany stopień")
            rok = f"{tryb_stopien_rok_semestr[2]} rok"
            semestr = f"{tryb_stopien_rok_semestr[3]} semestr"

        result: Dict[str, str] = {
            "Instytut dla którego jest prowadzony przedmiot": institute_code,
            "Kierunek": kierunek,
            "Specjalność": specjalnosc,
            "Tryb": tryb,
            "Stopień": stopien,
            "Rok": rok,
            "Semestr": semestr
        }
        if extra != "Brak dodatkowego kodu":
            result["Dodatkowy kod"] = extra

        return result

    except Exception as e:
        print(f"Błąd podczas parsowania kodu przedmiotu: {e}")
        return None

def get_academic_year_dates(selected_year: str) -> Tuple[Optional[date], Optional[date]]:
    try:
        start_year: int = int(selected_year.split("/")[0])
        end_year: int = start_year + 1
        start_date_obj: date = date(start_year, 10, 1)
        end_date_obj: date = date(end_year, 9, 30)
        return start_date_obj, end_date_obj
    except Exception as e:
        print(f"Błąd parsowania roku akademickiego: {e}")
        return None, None
    
def load_stawki_nadgodzin(filepath: str = "stawki_nadgodzin.xlsx") -> Dict[Optional[str], float]:
    stawki: Dict[Optional[str], float] = {}
    if not os.path.exists(filepath):
        print(f"Plik {filepath} nie istnieje! Używam pustego słownika stawek.")
        return stawki
    df = pd.read_excel(filepath)
    for _, row in df.iterrows():
        stanowisko_str: Optional[str] = str(row["stanowisko"]).strip() if pd.notna(row["stanowisko"]) else None
        stawki[stanowisko_str] = float(row["stawka"])
    return stawki

STAWKI_NADGODZIN: Dict[Optional[str], float] = load_stawki_nadgodzin()
