import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QComboBox, QFileDialog, QListWidget, QListWidgetItem, QTabWidget, QCheckBox, QSpacerItem, QSizePolicy
import pandas as pd
from formulas import calculate_workload_for_employee, get_group_data
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from database import engine
from models import Employee, GroupInstructor, ThesisSupervisors, Reviewer, IndividualRates, OrganizationalUnits, CommitteeFunctionPensum, DidacticCycles, Group, Person, Position, Employment, DidacticCycleClasses
from login import LoginWindow

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Rozliczania Obciążeń Dydaktycznych")
        self.setGeometry(100, 100, 800, 600)
        
        main_layout = QVBoxLayout()
        self.status_label = QLabel("Status: Oczekiwanie na akcję", self)
        main_layout.addWidget(self.status_label)
        # Filters layout
        filters_layout = QHBoxLayout()
        
        # Year filter
        self.year_filter = QComboBox(self)
        self.populate_years()
        self.year_filter.currentIndexChanged.connect(self.populate_groups)
        filters_layout.addWidget(QLabel("Rok akademicki:"))
        filters_layout.addWidget(self.year_filter)
        
        # Unit filter
        self.unit_filter = QComboBox(self)
        self.unit_filter.addItem("Wszystkie jednostki")
        self.populate_units()
        self.unit_filter.currentIndexChanged.connect(self.populate_groups)
        filters_layout.addWidget(QLabel("Jednostka organizacyjna:"))
        filters_layout.addWidget(self.unit_filter)
        
        main_layout.addLayout(filters_layout)
        
        # Edit mode checkbox
        self.edit_mode_checkbox = QCheckBox("Tryb edycji", self)
        self.edit_mode_checkbox.stateChanged.connect(self.toggle_edit_mode)
        main_layout.addWidget(self.edit_mode_checkbox)
        
        # Tab widget
        self.tab_widget = QTabWidget(self)
        self.groups_tab = QWidget()
        self.instructors_tab = QWidget()
        
        self.tab_widget.addTab(self.groups_tab, "Grupy")
        self.tab_widget.addTab(self.instructors_tab, "Wykładowcy")
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tab_widget)
        
        # Groups layout
        self.groups_layout = QVBoxLayout()
        self.groups_tab.setLayout(self.groups_layout)
        
        self.group_list = QListWidget(self)
        self.group_list.setDragEnabled(False)
        self.groups_layout.addWidget(QLabel("Grupy:"))
        self.groups_layout.addWidget(self.group_list)
        
        self.employee_list = QListWidget(self)
        self.employee_list.setAcceptDrops(False)
        self.employee_list.setDragDropMode(QListWidget.InternalMove)
        self.groups_layout.addWidget(QLabel("Wykładowcy:"))
        self.groups_layout.addWidget(self.employee_list)
        
        # Instructors layout
        self.instructors_layout = QVBoxLayout()
        self.instructors_tab.setLayout(self.instructors_layout)
        
        self.instructor_list = QListWidget(self)
        self.instructors_layout.addWidget(QLabel("Wykładowcy:"))
        self.instructors_layout.addWidget(self.instructor_list)
        
        # Populate initial data
        self.populate_groups()
        self.populate_employees()
        
        # Generate report button
        self.generate_report_button = QPushButton("Generuj raport Excel", self)
        self.generate_report_button.clicked.connect(self.generate_report)
        main_layout.addWidget(self.generate_report_button)
        
        # Status label
        self.status_label = QLabel("Status: Oczekiwanie na akcję", self)
        main_layout.addWidget(self.status_label)
        
        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
    def on_tab_changed(self, index):
        """Handle tab change events."""
        if self.tab_widget.tabText(index) == "Wykładowcy":
            self.populate_employees()
    def populate_years(self):
        """Populate the year filter with distinct academic years from DidacticCycles."""
        self.year_filter.clear()
        db = SessionLocal()
        try:
            # Explicitly cast to string to avoid any implicit conversions
            years = db.query(DidacticCycles.OPIS).filter(
                DidacticCycles.OPIS.like("Rok akademicki%")
            ).distinct().all()

            # Extract unique academic years
            unique_years = sorted(set(str(year[0]) for year in years if year[0] is not None))

            # Add each academic year to the year filter
            for year in unique_years:
                self.year_filter.addItem(year)
        except Exception as e:
            self.status_label.setText(f"Status: Błąd podczas pobierania lat: {str(e)}")
            print(f"Database error details: {str(e)}")  # Add this for debugging
        finally:
            db.close()
    
    def populate_units(self):
        """Populate the unit filter with only institutes."""
        self.unit_filter.clear()
        self.unit_filter.addItem("Wszystkie jednostki", None)  # Opcja dla wszystkich jednostek
        db = SessionLocal()
        # Pobieranie jednostek, których nazwa zawiera "Instytut"
        units = db.query(OrganizationalUnits).filter(OrganizationalUnits.OPIS.like("Instytut %")).all()
        for unit in units:
            self.unit_filter.addItem(unit.OPIS, unit.KOD)
        db.close()
    
    def populate_groups(self):
        """Populate the group list based on the selected academic year and unit, and filter instructors."""
        self.group_list.clear()
        self.employee_list.clear()  # Clear the instructor list as well
        selected_unit = self.unit_filter.currentData()
        selected_year = self.year_filter.currentText()
        db = SessionLocal()

        try:
            # Query groups based on the selected academic year and unit
            query = db.query(Group).join(DidacticCycleClasses, Group.ZAJ_CYK_ID == DidacticCycleClasses.ID)

            # Debugging: Log selected filters
            print(f"Selected Year: {selected_year}, Selected Unit: {selected_unit}")

            # Filter by the selected academic year
            if selected_year and selected_year != "Wszystkie lata":
                query = query.join(DidacticCycles, DidacticCycleClasses.CDYD_KOD == DidacticCycles.KOD)
                query = query.filter(DidacticCycles.OPIS.like(f"%{selected_year.split()[-1]}%"))

            if selected_unit:  # If a specific unit is selected
                query = query.join(
                    GroupInstructor,
                    and_(
                        GroupInstructor.ZAJ_CYK_ID == Group.ZAJ_CYK_ID,
                        GroupInstructor.GR_NR == Group.NR
                    )
                ).filter(GroupInstructor.JEDN_KOD == selected_unit)

            # Fetch groups
            groups = query.all()

            # Debugging: Log query results
            print(f"Groups Found: {len(groups)}")

            for group in groups:
                item = QListWidgetItem(f"{group.GR_NR} - {group.OPIS}")
                item.setData(1, group.ZAJ_CYK_ID)
                self.group_list.addItem(item)

            if not groups:  # If no groups are found, display a message
                self.group_list.addItem("Brak grup do wyświetlenia.")

            # Query instructors based on the selected unit
            instructor_query = db.query(Employee).join(Person, Employee.OS_ID == Person.ID)
            if selected_unit:
                instructor_query = instructor_query.filter(Person.JED_ORG_KOD == selected_unit)

            instructors = instructor_query.all()
            for instructor in instructors:
                person = db.query(Person).filter_by(ID=instructor.OS_ID).first()
                item = QListWidgetItem(f"{person.NAZWISKO} {person.IMIE}")
                item.setData(1, instructor.ID)
                self.employee_list.addItem(item)

            if not instructors:  # If no instructors are found, display a message
                self.employee_list.addItem("Brak wykładowców do wyświetlenia.")
        except Exception as e:
            self.group_list.addItem(f"Błąd: {str(e)}")
            self.employee_list.addItem(f"Błąd: {str(e)}")
            print(f"Error: {str(e)}")  # Debugging: Log the error
        finally:
            db.close()
        
    def populate_employees(self):
        """Populate the employee list and display workload data for the selected employee."""
        self.instructor_list.clear()
        selected_unit = self.unit_filter.currentData()
        db = SessionLocal()

        try:
            # Pobierz dane wykładowców
            query = db.query(Employee, Person).join(Person, Employee.OS_ID == Person.ID)
            if selected_unit:  # Filtruj według wybranej jednostki
                query = query.filter(Person.JED_ORG_KOD == selected_unit)

            results = query.all()
            for employee, person in results:
                # Wyświetl dane wykładowcy w widżecie
                item = QListWidgetItem(f"{person.NAZWISKO} {person.IMIE}")
                item.setData(1, employee.ID)  # Przechowuj ID wykładowcy w elemencie listy
                self.employee_list.addItem(item)

            if not results:  # Jeśli brak wyników
                self.employee_list.addItem("Brak wykładowców do wyświetlenia.")
        except Exception as e:
            print(f"Błąd podczas pobierania danych wykładowców: {str(e)}")
            self.employee_list.addItem("Błąd podczas ładowania wykładowców.")
        finally:
            db.close()

        # Po wybraniu wykładowcy wyświetl jego obciążenie dydaktyczne
        self.employee_list.itemClicked.connect(self.display_employee_workload)
    
    def display_employee_workload(self, item):
        """Display workload data for the selected employee."""
        selected_employee_id = item.data(1)  # Pobierz ID wykładowcy
        db = SessionLocal()
        try:
            # Oblicz obciążenie dydaktyczne
            workload_data = calculate_workload_for_employee(selected_employee_id)
            # Wyświetl dane w konsoli (lub w innym widżecie, jeśli jest dostępny)
            print("Obciążenie dydaktyczne:")
            for key, value in workload_data.items():
                print(f"{key}: {value}")
        except Exception as e:
            print(f"Błąd podczas obliczania obciążenia dydaktycznego: {str(e)}")
        finally:
            db.close()
    
    def toggle_edit_mode(self, state):
        """Toggle edit mode to enable or disable drag-and-drop functionality."""
        if state == 2:  # Checked
            self.group_list.setDragEnabled(True)
            self.employee_list.setAcceptDrops(True)
        else:
            self.group_list.setDragEnabled(False)
            self.employee_list.setAcceptDrops(False)
    
    from formulas import calculate_workload_for_employee, get_group_data

    def generate_report(self):
        """Generate an Excel report based on the current data."""
        db = SessionLocal()
        selected_unit = self.unit_filter.currentData()
        selected_year = self.year_filter.currentText()
        
        try:
            # Query employees and filter by the selected unit
            query = db.query(Employee).join(Person, Employee.OS_ID == Person.ID)
            
            if selected_unit:
                query = query.filter(Person.JED_ORG_KOD == selected_unit)
            
            employees = query.all()
            lp = 1
            data = []
            for employee in employees:
                # Get related data for the employee
                person = db.query(Person).filter_by(ID=employee.OS_ID).first()
                organizational_unit = db.query(OrganizationalUnits).filter_by(KOD=person.JED_ORG_KOD).first()
                prac_zatr = db.query(Employment).filter_by(PRAC_ID=employee.ID).first()
                position = db.query(Position).filter_by(ID=prac_zatr.STAN_ID).first() if prac_zatr else None
                stanowisko = position.NAZWA if position else "N/A"
                workload_data = calculate_workload_for_employee(employee.ID, selected_year)
                
                # Append data for the report
                data.append({
                    "Lp.": lp,
                    "Tytuły": person.TYTUL_PO,
                    "Nazwisko i imię": f"{person.NAZWISKO} {person.IMIE}",
                    "J.O.": organizational_unit.OPIS if organizational_unit else "N/A",
                    "Stanowisko": stanowisko,
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
            
            # Data for the second sheet
            data2 = get_group_data()
            
            # Create DataFrame for the second sheet
            df2 = pd.DataFrame(data2)
            
            # Save to an Excel file with two sheets
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx)")
            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df1.to_excel(writer, sheet_name='Raport 1', index=False)
                    df2.to_excel(writer, sheet_name='Raport 2', index=False)
                self.status_label.setText(f"Status: Raport zapisany do {file_path}")
            else:
                self.status_label.setText("Status: Anulowano zapis raportu")
        except Exception as e:
            self.status_label.setText(f"Status: Błąd podczas generowania raportu: {str(e)}")
        finally:
            db.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())