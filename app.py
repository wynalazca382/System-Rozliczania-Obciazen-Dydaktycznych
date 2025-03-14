import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QComboBox, QFileDialog, QListWidget, QListWidgetItem, QHBoxLayout, QTabWidget, QCheckBox
import pandas as pd
from formulas import calculate_workload_for_employee
from sqlalchemy.orm import sessionmaker
from database import engine
from models import Employee, GroupInstructor, ThesisSupervisors, Reviewer, IndividualRates, OrganizationalUnits, CommitteeFunctionPensum, DidacticCycles, Group, Person, Position

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Rozliczania Obciążeń Dydaktycznych")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        self.year_filter = QComboBox(self)
        self.year_filter.addItem("2023/2024")
        self.year_filter.addItem("2024/2025")
        self.year_filter.currentIndexChanged.connect(self.populate_semesters)
        layout.addWidget(self.year_filter)
        
        self.unit_filter = QComboBox(self)
        self.unit_filter.addItem("Wszystkie jednostki")
        self.populate_units()
        self.unit_filter.currentIndexChanged.connect(self.populate_groups)
        layout.addWidget(self.unit_filter)
        
        self.semester_filter = QComboBox(self)
        self.semester_filter.addItem("Wszystkie semestry")
        self.populate_semesters()
        layout.addWidget(self.semester_filter)
        
        self.edit_mode_checkbox = QCheckBox("Tryb edycji", self)
        self.edit_mode_checkbox.stateChanged.connect(self.toggle_edit_mode)
        layout.addWidget(self.edit_mode_checkbox)
        
        self.tab_widget = QTabWidget(self)
        self.groups_tab = QWidget()
        self.instructors_tab = QWidget()
        
        self.tab_widget.addTab(self.groups_tab, "Grupy")
        self.tab_widget.addTab(self.instructors_tab, "Wykładowcy")
        
        layout.addWidget(self.tab_widget)
        
        self.groups_layout = QVBoxLayout()
        self.groups_tab.setLayout(self.groups_layout)
        
        self.group_list = QListWidget(self)
        self.group_list.setDragEnabled(False)
        self.groups_layout.addWidget(self.group_list)
        
        self.employee_list = QListWidget(self)
        self.employee_list.setAcceptDrops(False)
        self.employee_list.setDragDropMode(QListWidget.InternalMove)
        self.groups_layout.addWidget(self.employee_list)
        
        self.instructors_layout = QVBoxLayout()
        self.instructors_tab.setLayout(self.instructors_layout)
        
        self.instructor_list = QListWidget(self)
        self.instructors_layout.addWidget(self.instructor_list)
        
        self.populate_groups()
        self.populate_employees()
        
        self.generate_report_button = QPushButton("Generuj raport Excel", self)
        self.generate_report_button.clicked.connect(self.generate_report)
        layout.addWidget(self.generate_report_button)
        
        self.status_label = QLabel("Status: Oczekiwanie na akcję", self)
        layout.addWidget(self.status_label)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def populate_units(self):
        db = SessionLocal()
        units = db.query(OrganizationalUnits).all()
        for unit in units:
            self.unit_filter.addItem(unit.OPIS, unit.KOD)
        db.close()
    
    def populate_semesters(self):
        self.semester_filter.clear()
        self.semester_filter.addItem("Wszystkie semestry")
        selected_year = self.year_filter.currentText()
        db = SessionLocal()
        semesters = db.query(DidacticCycles).filter(DidacticCycles.OPIS.like(f"%{selected_year}%")).all()
        for semester in semesters:
            self.semester_filter.addItem(semester.KOD)
        db.close()
    
    def populate_groups(self):
        self.group_list.clear()
        selected_unit = self.unit_filter.currentData()
        selected_semester = self.semester_filter.currentData()
        db = SessionLocal()
        query = db.query(Group)
        if selected_unit:
            query = query.filter_by(JEDN_KOD=selected_unit)
        if selected_semester:
            query = query.filter_by(CYKL_ID=selected_semester)
        groups = query.all()
        for group in groups:
            item = QListWidgetItem(f"{group.OPIS} - {group.ZAJ_CYK_ID}")
            item.setData(1, group.ZAJ_CYK_ID)
            self.group_list.addItem(item)
        db.close()
    
    def populate_employees(self):
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
        if state == 2:  # Checked
            self.group_list.setDragEnabled(True)
            self.employee_list.setAcceptDrops(True)
        else:
            self.group_list.setDragEnabled(False)
            self.employee_list.setAcceptDrops(False)
    
    def generate_report(self):
        db = SessionLocal()
        selected_unit = self.unit_filter.currentData()
        
        query = db.query(Employee)
        
        if selected_unit:
            query = query.join(Employee.organizational_unit).filter(OrganizationalUnits.KOD == selected_unit)
        
        employees = query.all()
        
        data = []
        for employee in employees:
            person = db.query(Person).filter_by(ID=employee.OS_ID).first()
            position = db.query(Position).filter_by(ID=employee.position_id).first()
            workload_data = calculate_workload_for_employee(db, employee)
            
            data.append({
                "Tytuły": person.TYTUL_PO,
                "Nazwisko i imię": f"{person.NAZWISKO} {person.IMIE}",
                "J.O.": employee.organizational_unit.OPIS,
                "Stanowisko": position.NAZWA if position else "N/A",
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
        
        df = pd.DataFrame(data)
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx)")
        if file_path:
            df.to_excel(file_path, index=False)
            self.status_label.setText(f"Status: Raport zapisany do {file_path}")
        else:
            self.status_label.setText("Status: Anulowano zapis raportu")
        
        db.close()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()