import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QComboBox, QFileDialog, QListWidget, QListWidgetItem, QTabWidget, QCheckBox, QSpacerItem, QSizePolicy
import pandas as pd
from formulas import calculate_workload_for_employee, get_group_data
from sqlalchemy.orm import sessionmaker
from database import engine
from models import Employee, GroupInstructor, ThesisSupervisors, Reviewer, IndividualRates, OrganizationalUnits, CommitteeFunctionPensum, DidacticCycles, Group, Person, StanowiskaZatr, Employment

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Rozliczania Obciążeń Dydaktycznych")
        self.setGeometry(100, 100, 800, 600)
        
        main_layout = QVBoxLayout()
        
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
    
    def populate_years(self):
        """Populate the year filter with distinct years from DidacticCycles."""
        db = SessionLocal()
        years = db.query(DidacticCycles.OPIS).distinct().all()
        for year in years:
            self.year_filter.addItem(year[0])
        db.close()
    
    def populate_units(self):
        """Populate the unit filter with all organizational units."""
        db = SessionLocal()
        units = db.query(OrganizationalUnits).all()
        for unit in units:
            self.unit_filter.addItem(unit.OPIS, unit.KOD)
        db.close()
    
    def populate_groups(self):
        """Populate the group list based on the selected year and unit."""
        self.group_list.clear()
        selected_unit = self.unit_filter.currentData()
        selected_year = self.year_filter.currentText()
        db = SessionLocal()
        
        query = db.query(Group).join(DidacticCycles).filter(DidacticCycles.OPIS.like(f"%{selected_year}%"))
        
        if selected_unit:
            query = query.join(GroupInstructor).filter(GroupInstructor.JEDN_KOD == selected_unit)
        
        groups = query.all()
        for group in groups:
            item = QListWidgetItem(f"{group.OPIS} - {group.ZAJ_CYK_ID}")
            item.setData(1, group.ZAJ_CYK_ID)
            self.group_list.addItem(item)   
        db.close()
        
    def populate_employees(self):
        """Populate the employee list with all employees."""
        self.employee_list.clear()
        db = SessionLocal()
        employees = db.query(Employee).all()
        for employee in employees:
            person = db.query(Person).filter_by(ID=employee.OS_ID).first()
            item = QListWidgetItem(f"{person.NAZWISKO} {person.IMIE}")
            item.setData(1, employee.ID)
            self.employee_list.addItem(item)
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
        
        query = db.query(Employee)
        
        if selected_unit:
            query = query.join(Employee.organizational_unit).filter(OrganizationalUnits.KOD == selected_unit)
        
        employees = query.all()
        lp = 1
        data = []
        for employee in employees:
            organizational_unit = db.query(OrganizationalUnits).filter_by(KOD=employee.organizational_unit).first()
            person = db.query(Person).filter_by(ID=employee.OS_ID).first()
            prac_zatr = db.query(Employment).filter_by(PRAC_ID=employee.ID).first()
            position = db.query(StanowiskaZatr).filter_by(ID=prac_zatr.STAN_ID).first() if prac_zatr else None
            stanowisko = position.NAZWA if position else "N/A"
            workload_data = calculate_workload_for_employee(employee.ID)
            
            data.append({
                "Lp.": lp,
                "Tytuły": person.TYTUL_PO,
                "Nazwisko i imię": f"{person.NAZWISKO} {person.IMIE}",
                "J.O.": organizational_unit.OPIS,
                "Stanowisko": stanowisko,
                "Forma": "etat",
                "Godziny dydaktyczne Z": workload_data["godziny_dydaktyczne_z"],
                "Godziny dydaktyczne L": workload_data["godziny_dydaktyczne_l"],
                "SUMA": workload_data["total_workload"],
                "Pensum": workload_data["pensum"],
                "Etat": workload_data["etat"],
                "Nadgodziny": workload_data["nadgodziny"],
                "Stawka": workload_data["stawka"],
                "Kwota nadgodzin": workload_data["kwota_nadgodzin"],
                "Zw. Godz. Z": workload_data["zw_godz_z"],
                "Zw. Godz. L": workload_data["zw_godz_l"],
                "Zw. kwota Z": workload_data["zw_kwota_z"],
                "Zw. kwota L": workload_data["zw_kwota_l"]
            })
            lp += 1

        # Tworzenie DataFrame z danych dla pierwszej karty
        df1 = pd.DataFrame(data)
        
        # Dane dla drugiej karty
        data2 = get_group_data()
        
        # Tworzenie DataFrame z danych dla drugiej karty
        df2 = pd.DataFrame(data2)
        
        # Zapis do pliku Excel z dwiema kartami
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx)")
        if file_path:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df1.to_excel(writer, sheet_name='Raport 1', index=False)
                df2.to_excel(writer, sheet_name='Raport 2', index=False)
            self.status_label.setText(f"Status: Raport zapisany do {file_path}")
        else:
            self.status_label.setText("Status: Anulowano zapis raportu")
        
        db.close()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()