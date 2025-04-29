import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QComboBox, QListWidget, QTabWidget, QLineEdit, QSpacerItem, QSizePolicy, QListWidgetItem, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import pandas as pd
from formulas import calculate_workload_for_employee, get_group_data
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from database import engine
from models import Employee, GroupInstructor, ThesisSupervisors, Reviewer, IndividualRates, OrganizationalUnits, CommitteeFunctionPensum, DidacticCycles, Group, Person, Position, Employment, DidacticCycleClasses, SubjectCycle, Title
from login import LoginWindow
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MainWindow(QMainWindow):
    def __init__(self, user_right):
        super().__init__()
        self.user_right = user_right
        self.setWindowTitle("System Rozliczania Obciążeń Dydaktycznych")
        self.setGeometry(100, 100, 1000, 700)
        self.showMaximized()
        # Główne okno
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Pasek nagłówka
        header = QLabel("System Rozliczania Obciążeń Dydaktycznych")
        header.setFont(QFont("Verdana", 20, QFont.Bold))  # Czcionka "Verdana", rozmiar 20
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("background-color: #2c3e50; color: white; padding: 10px;")
        main_layout.addWidget(header)

        # Filtry
        filters_layout = QVBoxLayout()
        filters_layout.setSpacing(10)

        # Filtry: Rok akademicki
        year_layout = QHBoxLayout()
        year_label = QLabel("Rok akademicki:")
        year_label.setStyleSheet("""
            QLabel {
                font-family: 'Verdana';
                font-size: 16px;  /* Zwiększony rozmiar czcionki */
            }
        """)
        self.year_filter = QComboBox(self)
        self.year_filter.setStyleSheet("""
            QComboBox {
                font-family: 'Verdana';
                font-size: 16px;  /* Zwiększony rozmiar czcionki */
            }
        """)
        self.year_filter.setMinimumHeight(30)
        self.populate_years()
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_filter)
        filters_layout.addLayout(year_layout)

        # Filtry: Jednostka organizacyjna
        unit_layout = QHBoxLayout()
        unit_label = QLabel("Jednostka organizacyjna:")
        unit_label.setStyleSheet("""
            QLabel {
                font-family: 'Verdana';
                font-size: 16px;  /* Zwiększony rozmiar czcionki */
            }
        """)
        self.unit_filter = QComboBox(self)
        self.unit_filter.setStyleSheet("""
            QComboBox {
                font-family: 'Verdana';
                font-size: 16px;  /* Zwiększony rozmiar czcionki */
            }
        """)
        self.unit_filter.setMinimumHeight(30)
        self.unit_filter.addItem("Wszystkie jednostki")
        self.populate_units()
        unit_layout.addWidget(unit_label)
        unit_layout.addWidget(self.unit_filter)
        filters_layout.addLayout(unit_layout)

        # Filtry: Wykładowca
        employee_layout = QHBoxLayout()
        employee_label = QLabel("Wykładowca:")
        employee_label.setStyleSheet("""
            QLabel {
                font-family: 'Verdana';
                font-size: 16px;  /* Zwiększony rozmiar czcionki */
            }
        """)
        self.employee_filter = QComboBox(self)
        self.employee_filter.setStyleSheet("""
            QComboBox {
                font-family: 'Verdana';
                font-size: 16px;  /* Zwiększony rozmiar czcionki */
            }
        """)
        self.employee_filter.setMinimumHeight(30)
        self.employee_filter.addItem("Wszyscy wykładowcy")
        self.filter_instructors()
        employee_layout.addWidget(employee_label)
        employee_layout.addWidget(self.employee_filter)
        filters_layout.addLayout(employee_layout)

        # Przyciski "Filtruj" i "Odśwież"
        buttons_layout = QHBoxLayout()
        self.filter_button = QPushButton("Filtruj")
        self.filter_button.setStyleSheet(self.button_style())
        self.filter_button.clicked.connect(self.apply_filters)
        buttons_layout.addWidget(self.filter_button)

        self.refresh_button = QPushButton("Odśwież")
        self.refresh_button.setStyleSheet(self.button_style())
        self.refresh_button.clicked.connect(self.refresh_data)
        buttons_layout.addWidget(self.refresh_button)

        filters_layout.addLayout(buttons_layout)
        main_layout.addLayout(filters_layout)

        # Zakładki
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(self.tab_style())
        main_layout.addWidget(self.tab_widget)

        # Zakładka grup
        self.groups_tab = QWidget()
        self.groups_layout = QVBoxLayout(self.groups_tab)
        self.group_list = QListWidget()
        group_label = QLabel("Grupy:")
        group_label.setStyleSheet("""
            QLabel {
                font-family: 'Verdana';
                font-size: 16px;  /* Zwiększony rozmiar czcionki */
            }
        """)
        self.groups_layout.addWidget(group_label)
        self.groups_layout.addWidget(self.group_list)
        self.tab_widget.addTab(self.groups_tab, "Grupy")

        # Zakładka wykładowców
        self.instructors_tab = QWidget()
        self.instructors_layout = QVBoxLayout(self.instructors_tab)
        self.instructor_list = QListWidget()
        instructor_label = QLabel("Wykładowcy:")
        instructor_label.setStyleSheet("""
            QLabel {
                font-family: 'Verdana';
                font-size: 16px;  /* Zwiększony rozmiar czcionki */
            }
        """)
        self.instructors_layout.addWidget(instructor_label)
        self.instructors_layout.addWidget(self.instructor_list)
        self.instructor_details = QListWidget(self)
        details_label = QLabel("Szczegóły wykładowcy:")
        details_label.setStyleSheet("""
            QLabel {
                font-family: 'Verdana';
                font-size: 16px;  /* Zwiększony rozmiar czcionki */
            }
        """)
        self.instructors_layout.addWidget(details_label)
        self.instructors_layout.addWidget(self.instructor_details)
        self.instructor_details.setStyleSheet("""
            QListWidget {
                font-family: 'Verdana';
                font-size: 16px;  /* Zwiększony rozmiar czcionki */
            }
        """)
        self.tab_widget.addTab(self.instructors_tab, "Wykładowcy")
        self.instructor_list.itemClicked.connect(self.display_employee_workload)

        # Przycisk "Generuj raport" na samym dole
        self.report_button = QPushButton("Generuj raport")
        self.report_button.setStyleSheet(self.button_style())
        self.report_button.clicked.connect(self.generate_report)
        main_layout.addWidget(self.report_button)

        # Status bar
        self.status_label = QLabel("Status: Oczekiwanie na akcję")
        self.status_label.setStyleSheet("background-color: #2c3e50; color: white; padding: 5px;")
        main_layout.addWidget(self.status_label)

        self.setCentralWidget(main_widget)

        # Populate initial data
        self.populate_groups()
        self.populate_employees()

    def button_style(self):
        return """
            QPushButton {
                background-color: #1abc9c;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-family: 'Verdana';
                font-size: 14px;  /* Zwiększony rozmiar czcionki */
            }
            QPushButton:hover {
                background-color: #16a085;
            }
        """

    def tab_style(self):
        return """
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 10px;  /* Zwiększony padding: góra-dół 10px, lewo-prawo 15px */
                margin: 15px 15px;  /* Zwiększony padding: góra-dół 25px, lewo-prawo 15px */
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-family: 'Verdana';
                font-size: 15px;  /* Zwiększony rozmiar czcionki */
                min-width: 150px;  /* Minimalna szerokość zakładki */
            }
            QTabBar::tab:selected {
                background: #1abc9c;
                color: white;
            }
        """
    def refresh_data(self):
        """Refresh data in both tabs without changing filters."""
        self.populate_groups()
        self.populate_employees()
        self.status_label.setText("Status: Dane zostały odświeżone.")
    def on_tab_changed(self, index):
        """Handle tab change events."""
        if self.tab_widget.tabText(index) == "Wykładowcy":
            self.populate_employees()
    def populate_years(self):
        """Populate the year filter with distinct academic years from DidacticCycles."""
        self.year_filter.clear()
        db = SessionLocal()
        try:
            # Pobierz unikalne lata akademickie
            years = db.query(DidacticCycles.OPIS).filter(
                DidacticCycles.OPIS.like("Rok akademicki%")
            ).distinct().all()

            # Wyodrębnij fragment "2024/25" z "Rok akademicki 2024/25"
            unique_years = sorted(set(year[0].split()[-1] for year in years if year[0] is not None),
                                reverse=True)  # Sortuj malejąco

            # Dodaj każdy rok akademicki do filtra
            for year in unique_years:
                self.year_filter.addItem(year)
        except Exception as e:
            self.status_label.setText(f"Status: Błąd podczas pobierania lat: {str(e)}")
            print(f"Database error details: {str(e)}")
        finally:
            db.close()
    
    def populate_units(self):
        """Populate the unit filter with only allowed institutes based on user rights."""
        self.unit_filter.clear()
        self.unit_filter.addItem("Wszystkie jednostki", None)  # Opcja dla wszystkich jednostek, jeśli prawo = 0
        db = SessionLocal()

        try:
            # Pobierz jednostki organizacyjne na podstawie prawa użytkownika
            if self.user_right == 0:  # Dostęp do wszystkich jednostek
                units = db.query(OrganizationalUnits).filter(OrganizationalUnits.OPIS.like("Instytut %")).all()
            elif self.user_right == 1:  # Dostęp tylko do Instytutu Informatyki Stosowanej
                units = db.query(OrganizationalUnits).filter(OrganizationalUnits.OPIS == "Instytut Informatyki Stosowanej%").all()
            elif self.user_right == 2:  # Dostęp tylko do Instytutu Ekonomicznego
                units = db.query(OrganizationalUnits).filter(OrganizationalUnits.OPIS == "Instytut Ekonomiczny%").all()
            elif self.user_right == 3:  # Dostęp tylko do Instytutu Politechnicznego
                units = db.query(OrganizationalUnits).filter(OrganizationalUnits.OPIS == "Instytut Politechniczny%").all()
            elif self.user_right == 4:  # Dostęp tylko do Instytutu Pedagogiczno-Językowego
                units = db.query(OrganizationalUnits).filter(OrganizationalUnits.OPIS == "Instytut Pedagogiczno-Językowy%").all()
            else:
                units = []  # Brak dostępu do żadnych jednostek

            # Dodaj jednostki do filtra
            for unit in units:
                self.unit_filter.addItem(unit.OPIS, unit.KOD)
        except Exception as e:
            print(f"Błąd podczas ładowania jednostek organizacyjnych: {str(e)}")
        finally:
            db.close()
    
    def apply_filters(self):
        """Apply filters and refresh data in both tabs."""
        self.populate_groups()
        self.filter_instructors() 
        self.populate_employees()
        self.status_label.setText("Status: Filtry zostały zastosowane.")

    def filter_instructors(self):
        """Filter and populate the instructor list based on the selected unit."""
        db = SessionLocal()
        selected_unit = self.unit_filter.currentData()
        selected_year = self.year_filter.currentText()

        current_instructor = self.employee_filter.currentData()

        try:
            # Query instructors based on the selected unit
            instructor_query = (
                db.query(Employee)
                .join(Person, Employee.OS_ID == Person.ID)
                .join(GroupInstructor, Employee.ID == GroupInstructor.PRAC_ID)
                .join(OrganizationalUnits, GroupInstructor.JEDN_KOD == OrganizationalUnits.KOD)
                .join(Group, GroupInstructor.ZAJ_CYK_ID == Group.ZAJ_CYK_ID)
                .join(DidacticCycleClasses, Group.ZAJ_CYK_ID == DidacticCycleClasses.ID)
                .join(DidacticCycles, DidacticCycleClasses.CDYD_KOD == DidacticCycles.KOD)
            )
            if selected_unit:
                print(f"Selected unit: {selected_unit}")  # Debugging: Log the selected unit
                instructor_query = instructor_query.filter(GroupInstructor.JEDN_KOD == selected_unit)
            if selected_year:
                print(f"Selected year: {selected_year}")  # Debugging: Log the selected year
                instructor_query = instructor_query.filter(DidacticCycles.OPIS.like(f"%{selected_year}%"))
            instructors = instructor_query.all()
            self.employee_filter.clear()
            self.employee_filter.addItem("Wszyscy wykładowcy", None)
            for instructor in instructors:
                person = db.query(Person).filter_by(ID=instructor.OS_ID).first()
                print(f"Adding instructor: {person.NAZWISKO} {person.IMIE} {instructor.ID}")  # Debugging: Log the instructor being added
                self.employee_filter.addItem(f"{person.NAZWISKO} {person.IMIE}", instructor.ID)
            
            index_to_restore = self.employee_filter.findData(current_instructor)
            if index_to_restore != -1:
                self.employee_filter.setCurrentIndex(index_to_restore)
        except Exception as e:
            print(f"Error: {str(e)}")  # Debugging: Log the error
        finally:
            db.close()
    def display_instructor_details(self):
        """Display details for the selected instructor."""
        self.instructor_details.clear()  # Wyczyść szczegóły
        selected_employee = self.employee_filter.currentData()
        selected_year = self.year_filter.currentText()
        selected_unit = self.unit_filter.currentData()

        if not selected_employee:
            self.instructor_details.addItem("Wybierz wykładowcę, aby zobaczyć szczegóły.")
            return

        db = SessionLocal()
        try:
            # Pobierz dane grup dla wybranego wykładowcy
            group_data = get_group_data(selected_year, selected_unit, selected_employee)

            # Pobierz pensum i zniżki
            workload_data = calculate_workload_for_employee(selected_employee, selected_year, selected_unit)

            # Wyświetl szczegóły
            self.instructor_details.addItem(f"Pensum: {workload_data['pensum']}")
            self.instructor_details.addItem(f"Zniżka: {workload_data['zniżka']}")
            self.instructor_details.addItem(f"Godziny dydaktyczne Z: {workload_data['godziny_dydaktyczne_z']}")
            self.instructor_details.addItem(f"Godziny dydaktyczne L: {workload_data['godziny_dydaktyczne_l']}")
            self.instructor_details.addItem(f"Nadgodziny/Niedobór: {workload_data['nadgodziny']}")
            self.instructor_details.addItem(f"Czy podstawowe miejsce pracy w rozumieniu ustawy: {workload_data['CZY_PODSTAWOWE']}")

            self.instructor_details.addItem("Przedmioty:")
            for group in group_data:
                self.instructor_details.addItem(
                    f"  - {group['Przedmiot']} ({group['Typ zajęć']}): {group['Liczba godzin']} godz. w {group['Semestr']} semestrze"
                )
        except Exception as e:
            self.instructor_details.addItem(f"Błąd: {str(e)}")
            print(f"Error: {str(e)}")
        finally:
            db.close()
    def populate_groups(self):
        """Populate the group list based on the selected academic year and unit."""
        self.group_list.clear()
        self.group_list.setStyleSheet("""
            QListWidget {
                font-family: 'Verdana';
                font-size: 16px;
            }
        """)
        selected_unit = self.unit_filter.currentData()
        print(selected_unit)
        selected_year = self.year_filter.currentText()
        print(selected_year)
        selected_employee = self.employee_filter.currentData()
        print(selected_employee)

        try:
            # Pobierz dane grup z get_group_data
            group_data = get_group_data(selected_year, selected_unit, selected_employee)

            # Wyświetl dane grup w group_list
            for group in group_data:
                item_text = (
                    f"{group['Prowadzący']} | "
                    f"Przedmiot: {group['Przedmiot']}, Typ zajęć: {group['Typ zajęć']}, "
                    f"Liczba godzin: {group['Liczba godzin']}, Semestr: {group['Semestr']}, "
                    f"Jednostka: {group['Jednostka']}"
                )
                self.group_list.addItem(item_text)

            if not group_data:  # Jeśli brak wyników
                self.group_list.addItem("Brak grup do wyświetlenia.")
        except Exception as e:
            self.group_list.addItem(f"Błąd: {str(e)}")
            print(f"Error: {str(e)}")
        
    def populate_employees(self):
        """Populate the employee list and display workload data for each employee."""
        self.instructor_list.clear()
        self.instructor_list.setStyleSheet("""
            QListWidget {
                font-family: 'Verdana';
                font-size: 16px;  /* Zwiększony rozmiar czcionki */
            }
        """)
        selected_unit = self.unit_filter.currentData()
        print(selected_unit)
        selected_year = self.year_filter.currentText()
        print(selected_year)
        selected_employee = self.employee_filter.currentData()
        print(selected_employee)
        db = SessionLocal()

        try:
            # Pobierz dane wykładowców
            query = db.query(Employee, Person).join(Person, Employee.OS_ID == Person.ID).filter(GroupInstructor.PRAC_ID == Employee.ID).filter(DidacticCycles.OPIS.like(f"%{selected_year}%"))
            if selected_unit:  # Filtruj według wybranej jednostki
                query = query.filter(GroupInstructor.JEDN_KOD== selected_unit)
            if selected_employee:  # Filtruj według wybranego wykładowcy
                query = query.filter(Employee.ID == selected_employee)
            results = query.all()
            for employee, person in results:
                # Oblicz obciążenie dydaktyczne dla każdego wykładowcy
                workload_data = calculate_workload_for_employee(employee.ID, selected_year, selected_unit)

                if workload_data["total_workload"] > 0:
                    item_text = (
                        f"{person.NAZWISKO} {person.IMIE} | "
                        f"Pensum: {workload_data['pensum']} | "
                        f"Godziny Z: {workload_data['godziny_dydaktyczne_z']} | "
                        f"Godziny L: {workload_data['godziny_dydaktyczne_l']} | "
                        f"Nadgodziny: {workload_data['nadgodziny']}"
                    )
                    item = QListWidgetItem(item_text)
                    item.setData(1, employee.ID)  # Przechowuj ID wykładowcy w elemencie listy
                    self.instructor_list.addItem(item)

            if not results:  # Jeśli brak wyników
                self.instructor_list.addItem("Brak wykładowców do wyświetlenia.")
        except Exception as e:
            print(f"Błąd podczas pobierania danych wykładowców: {str(e)}")
            self.instructor_list.addItem("Błąd podczas ładowania wykładowców.")
        finally:
            db.close()
    
    def display_employee_workload(self, item):
        """Display workload data for the selected employee."""
        self.instructor_details.clear()
        self.instructor_details.setStyleSheet("""
            QListWidget {
                font-family: 'Verdana';
                font-size: 16px;  /* Zwiększony rozmiar czcionki */
            }
        """)
        selected_employee_id = item.data(1)
        selected_year = self.year_filter.currentText()
        selected_unit = self.unit_filter.currentData()

        if not selected_employee_id:
            self.instructor_details.addItem("Nie wybrano wykładowcy.")
            return

        db = SessionLocal()
        try:
            # Pobierz dane grup dla wybranego wykładowcy
            group_data = get_group_data(selected_year, selected_unit, selected_employee_id)

            # Pobierz pensum i zniżki
            workload_data = calculate_workload_for_employee(selected_employee_id, selected_year, selected_unit)

            # Wyświetl szczegóły
            self.instructor_details.addItem(f"Pensum: {workload_data['pensum']}")
            self.instructor_details.addItem(f"Zniżka: {workload_data['zniżka']} Rodzaj: {workload_data['typ_zniżki']}")
            self.instructor_details.addItem(f"Godziny dydaktyczne Z: {workload_data['godziny_dydaktyczne_z']}")
            self.instructor_details.addItem(f"Godziny dydaktyczne L: {workload_data['godziny_dydaktyczne_l']}")
            self.instructor_details.addItem(f"Nadgodziny: {workload_data['nadgodziny']}")

            self.instructor_details.addItem("Przedmioty:")
            for group in group_data:
                self.instructor_details.addItem(
                    f"  - {group['Przedmiot']} ({group['Typ zajęć']}): {group['Liczba godzin']} godz. w {group['Semestr']} semestrze"
                )
        except Exception as e:
            self.instructor_details.addItem(f"Błąd: {str(e)}")
            print(f"Error: {str(e)}")
        finally:
            db.close()
    
    from formulas import calculate_workload_for_employee, get_group_data

    def generate_report(self):
        """Generate an Excel report with improved formatting."""
        db = SessionLocal()
        selected_unit = self.unit_filter.currentData()
        selected_year = self.year_filter.currentText()
        selected_employee = self.employee_filter.currentData()
        
        try:
            # Query employees and filter by the selected unit
            query = (
                db.query(Employee, Person)
                .join(Person, Employee.OS_ID == Person.ID)
                .join(GroupInstructor, GroupInstructor.PRAC_ID == Employee.ID)
                .join(Group, GroupInstructor.ZAJ_CYK_ID == Group.ZAJ_CYK_ID)
                .join(DidacticCycleClasses, Group.ZAJ_CYK_ID == DidacticCycleClasses.ID)
                .join(DidacticCycles, DidacticCycleClasses.CDYD_KOD == DidacticCycles.KOD)
                .filter(DidacticCycles.OPIS.like(f"%{selected_year}%"))
            )
            
            if selected_unit:
                query = query.filter(GroupInstructor.JEDN_KOD == selected_unit)
            
            employees = query.all()
            lp = 1
            data = []
            for employee, person in employees:
                # Get related data for the employee
                person = db.query(Person).filter_by(ID=person.ID).first()
                organizational_unit = db.query(OrganizationalUnits).filter_by(KOD=person.JED_ORG_KOD).first()
                workload_data = calculate_workload_for_employee(employee.ID, selected_year, selected_unit)
                tytul = db.query(Title).filter_by(ID=person.TYTUL_PO).first()
                
                # Append data for the report
                data.append({
                    "Lp.": lp,
                    "Tytuły": tytul.NAZWA if tytul else "N/A",
                    "Nazwisko i imię": f"{person.NAZWISKO} {person.IMIE}",
                    "J.O.": organizational_unit.OPIS if organizational_unit else "N/A",
                    "Forma": "etat",
                    "Godziny dydaktyczne Z": workload_data["godziny_dydaktyczne_z"],
                    "Godziny dydaktyczne L": workload_data["godziny_dydaktyczne_l"],
                    "Pensum realne": workload_data["total_workload"],
                    "Pensum": workload_data["pensum"],
                    "Etat": workload_data["etat"],
                    "Nadgodziny": workload_data["nadgodziny"],
                    "Stawka": workload_data["stawka"],
                    "Kwota nadgodzin": workload_data["kwota_nadgodzin"],
                })
                lp += 1

            # Create DataFrame for the first sheet
            df1 = pd.DataFrame(data)
            print(f"Wywołanie get_group_data z parametrami: year={selected_year}, unit={selected_unit}, employee={selected_employee}")
            data2 = get_group_data(selected_year, selected_unit, selected_employee)
            print(f"Dane zwrócone przez get_group_data: {data2}")
            
            if not data2:
                print("Brak danych dla drugiej karty raportu.")
                self.status_label.setText("Status: Brak danych dla drugiej karty raportu.")
                data2 = [{"Informacja": "Brak danych"}]
            
            # Create DataFrame for the second sheet
            df2 = pd.DataFrame(data2)
            
            # Save to an Excel file with two sheets
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx)")
            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Write the first sheet
                    df1.to_excel(writer, sheet_name='Raport 1', index=False)
                    df2.to_excel(writer, sheet_name='Raport 2', index=False)
                
                # Apply formatting
                self.format_excel(file_path)
                self.status_label.setText(f"Status: Raport zapisany do {file_path}")
            else:
                self.status_label.setText("Status: Anulowano zapis raportu")
        except Exception as e:
            self.status_label.setText(f"Status: Błąd podczas generowania raportu: {str(e)}")
        finally:
            db.close()

    def format_excel(self, file_path):
        """Apply formatting to the Excel file and adjust column widths."""
        from openpyxl import load_workbook

        wb = load_workbook(file_path)
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]

            # Apply formatting to the header row
            for cell in sheet[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = thin_border

            # Apply formatting to the rest of the cells
            for row in sheet.iter_rows(min_row=2):
                for cell in row:
                    cell.alignment = Alignment(horizontal='left', vertical='center')
                    cell.border = thin_border

            # Adjust column widths
            for column in sheet.columns:
                max_length = 0
                column_letter = column[0].column_letter  # Get the column letter (e.g., 'A', 'B', etc.)
                for cell in column:
                    try:
                        if cell.value:  # Check if the cell has a value
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = max_length + 2  # Add some padding
                sheet.column_dimensions[column_letter].width = adjusted_width

        wb.save(file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())