def calculate_workload(hours: float, group_type: str, employee_level: str, discounts: float = 0.0, practice_supervisor: bool = False, committee_member: bool = False, university_function: bool = False) -> float:
    """
    Funkcja obliczająca obciążenie dydaktyczne.
    - hours: liczba godzin zajęć
    - group_type: typ grupy (np. wykład, ćwiczenia)
    - employee_level: stanowisko pracownika
    - discounts: zniżki w obciążeniu
    - practice_supervisor: czy jest opiekunem praktyk
    - committee_member: czy jest członkiem komisji
    - university_function: czy pełni funkcję na uczelni
    """
    # Przykładowa logika (do zastąpienia prawdziwą formułą)
    group_multiplier = {
        "wykład": 1.5,
        "ćwiczenia": 1.2,
        "laboratorium": 1.3
    }
    level_multiplier = {
        "profesor": 1.0,
        "adiunkt": 0.9,
        "asystent": 0.8
    }
    
    group_factor = group_multiplier.get(group_type, 1.0)
    level_factor = level_multiplier.get(employee_level, 1.0)

    workload = hours * group_factor * level_factor

    # Apply discounts
    workload -= discounts

    # Apply additional factors
    if practice_supervisor:
        workload *= 0.9  # Example factor
    if committee_member:
        workload *= 0.95  # Example factor
    if university_function:
        workload *= 0.85  # Example factor

    return workload
