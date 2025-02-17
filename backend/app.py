import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QComboBox, QFileDialog
import pandas as pd
from formulas import calculate_workload_for_employee
from sqlalchemy.orm import sessionmaker
from database import engine
from models import Employee, GroupInstructor, ThesisSupervisors, Reviewer, IndividualRates, OrganizationalUnits, CommitteeFunctionPensum, DidacticCycles

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Rozliczania Obciążeń Dydaktycznych")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        self.unit_filter = QComboBox(self)
        self.unit_filter.addItem("Wszystkie jednostki")
        self.populate_units()
        layout.addWidget(self.unit_filter)
        
        self.semester_filter = QComboBox(self)
        self.semester_filter.addItem("Wszystkie semestry")
        self.populate_semesters()
        layout.addWidget(self.semester_filter)
        
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
    
    def generate_report(self):
        db = SessionLocal()
        selected_unit = self.unit_filter.currentData()
        
        query = db.query(Employee)
        
        if selected_unit:
            query = query.join(Employee.organizational_unit).filter(OrganizationalUnits.KOD == selected_unit)
        
        employees = query.all()
        
        data = []
        for employee in employees:
            total_workload = calculate_workload_for_employee(db, employee)
            data.append({
                "Employee ID": employee.ID,
                "Total Workload": total_workload
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