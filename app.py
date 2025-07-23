from config import load_app_config
load_app_config()
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QComboBox, QListWidget, QTabWidget, QLineEdit, QSpacerItem, QSizePolicy, QListWidgetItem, QFileDialog, QMessageBox, QListWidget, QAbstractItemView, QTableView, QHeaderView, QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox, QLabel, QWidgetAction
)
from PyQt5.QtGui import QFont, QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QSortFilterProxyModel
import pandas as pd
from formulas import calculate_workload_for_employee, get_group_data
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from database import engine
from models import Employee, GroupInstructor, ThesisSupervisors, Reviewer, IndividualRates, OrganizationalUnits, CommitteeFunctionPensum, DidacticCycles, Group, Person, Position, Employment, DidacticCycleClasses, SubjectCycle, Title
from login import LoginWindow
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from datetime import datetime


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MainWindow(QMainWindow):
    def __init__(self, user_right):
        super().__init__()
        self.user_right = user_right
        self.setWindowTitle("System Rozliczania Obciążeń Dydaktycznych")
        self.setGeometry(100, 100, 1000, 700)
        self.showMaximized()
        self.is_dark_mode = False  # Domyślnie jasny tryb

        # Główne okno
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Pasek nagłówka
        header = QLabel("System Rozliczania Obciążeń Dydaktycznych")
        header.setFont(QFont("Verdana", 20, QFont.Bold))  # Czcionka "Verdana", rozmiar 20
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
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

        # Utwórz QTabWidget i dodaj do layoutu
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(self.tab_style())
        main_layout.addWidget(self.tab_widget)
        # Przycisk trybu ciemnego/jasnego z ikonką w prawym górnym rogu zakładek
        self.theme_toggle_btn = QPushButton("🌜")
        self.theme_toggle_btn.setCheckable(True)
        self.theme_toggle_btn.setFixedSize(80, 64)
        self.theme_toggle_btn.setStyleSheet("font-size: 28px; border-radius: 8px; margin-left: 16px; padding: 8px 16px;")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        self.tab_widget.setCornerWidget(self.theme_toggle_btn, Qt.Corner.TopRightCorner)

        # Zakładka grup
        self.groups_tab = QWidget()
        self.groups_layout = QVBoxLayout(self.groups_tab)
        self.group_table = QTableView()
        self.group_model = QStandardItemModel()
        self.group_proxy = QSortFilterProxyModel()
        self.group_proxy.setSourceModel(self.group_model)
        self.group_proxy.setFilterCaseSensitivity(1)
        self.group_proxy.setFilterKeyColumn(-1)  # -1 = wszystkie kolumny
        self.group_table.setModel(self.group_proxy)
        header = self.group_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.group_table.setSortingEnabled(True)
        self.groups_layout.addWidget(self.group_table)
        group_label = QLabel("Grupy:")
        group_label.setStyleSheet("""
            QLabel {
                font-family: 'Verdana';
                font-size: 16px;  /* Zwiększony rozmiar czcionki */
            }
        """)
        self.group_search = QLineEdit()
        self.group_search.setPlaceholderText("Szukaj w grupach...")
        self.group_search.setStyleSheet("""
            QLineEdit {
                font-family: 'Verdana';
                font-size: 16px;
                padding: 5px;
            }
        """)
        self.group_search.textChanged.connect(self.filter_group_list)
        self.group_filter_column_combo = QComboBox()
        self.group_filter_column_combo.setStyleSheet("""
            QComboBox {
                font-family: 'Verdana';
                font-size: 16px;
            }
        """)
        self.group_filter_column_combo.setMinimumHeight(30)
        self.group_filter_column_combo.addItem("Wszystkie kolumny", -1)
        self.group_filter_column_combo.currentIndexChanged.connect(self.on_group_filter_column_changed)
        # Dodaj przycisk Wyczyść filtr
        self.clear_group_filter_button = QPushButton("Wyczyść filtr")
        self.clear_group_filter_button.setStyleSheet(self.button_style())
        self.clear_group_filter_button.clicked.connect(lambda: self.group_search.clear())
        group_search_layout = QHBoxLayout()
        group_search_layout.addWidget(self.group_filter_column_combo)
        group_search_layout.addWidget(self.group_search)
        group_search_layout.addWidget(self.clear_group_filter_button)
        self.groups_layout.addLayout(group_search_layout)
        self.groups_layout.addLayout(group_search_layout)
        self.groups_layout.addWidget(self.group_table)
        self.tab_widget.addTab(self.groups_tab, "Grupy")

        # Zakładka wykładowców
        self.instructors_tab = QWidget()
        self.instructors_layout = QVBoxLayout(self.instructors_tab)
        instructor_label = QLabel("Wykładowcy:")
        instructor_label.setStyleSheet("""
            QLabel {
                font-family: 'Verdana';
                font-size: 16px;
            }
        """)
        self.instructors_layout.addWidget(instructor_label)
        self.instructor_search = QLineEdit()
        self.instructor_search.setPlaceholderText("Szukaj w wykładowcach...")
        self.instructor_search.setStyleSheet("""
            QLineEdit {
                font-family: 'Verdana';
                font-size: 16px;
                padding: 5px;
            }
        """)
        self.instructor_search.textChanged.connect(self.filter_instructor_list)
        # Dodaj przycisk Wyczyść filtr
        self.clear_instructor_filter_button = QPushButton("Wyczyść filtr")
        self.clear_instructor_filter_button.setStyleSheet(self.button_style())
        self.clear_instructor_filter_button.clicked.connect(lambda: self.instructor_search.clear())
        instructor_search_layout = QHBoxLayout()
        instructor_search_layout.addWidget(self.instructor_search)
        instructor_search_layout.addWidget(self.clear_instructor_filter_button)
        self.instructors_layout.addLayout(instructor_search_layout)
        self.instructor_table = QTableView()
        self.instructor_model = QStandardItemModel()
        self.instructor_proxy = QSortFilterProxyModel()
        self.instructor_proxy.setSourceModel(self.instructor_model)
        self.instructor_proxy.setFilterCaseSensitivity(1)
        self.instructor_proxy.setFilterKeyColumn(-1)
        self.instructor_table.setModel(self.instructor_proxy)
        header = self.instructor_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.instructor_table.setSortingEnabled(True)
        self.instructors_layout.addWidget(self.instructor_table)
        details_label = QLabel("Szczegóły wykładowcy:")
        details_label.setStyleSheet("""
            QLabel {
                font-family: 'Verdana';
                font-size: 16px;
            }
        """)
        self.instructor_details_table = QTableView()
        self.instructor_details_model = QStandardItemModel()
        self.instructor_details_table.setModel(self.instructor_details_model)
        header = self.instructor_details_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.instructors_layout.addWidget(self.instructor_details_table)
        self.tab_widget.addTab(self.instructors_tab, "Wykładowcy")
        self.instructor_table.clicked.connect(self.display_instructor_details)
        self.instructor_table.clicked.connect(self.display_instructor_details)

        # Zakładka zestawienie
        self.summary_tab = QWidget()
        self.summary_layout = QVBoxLayout(self.summary_tab)
        self.summary_search = QLineEdit()
        self.summary_search.setPlaceholderText("Szukaj w podsumowaniu...")
        self.summary_search.setStyleSheet("""
            QLineEdit {
                font-family: 'Verdana';
                font-size: 16px;
                padding: 5px;
            }
        """)
        self.summary_search.textChanged.connect(self.filter_summary_list)
        self.summary_layout.addWidget(self.summary_search)
        # Dodaj przycisk Wyczyść filtr
        self.clear_summary_filter_button = QPushButton("Wyczyść filtr")
        self.clear_summary_filter_button.setStyleSheet(self.button_style())
        self.clear_summary_filter_button.clicked.connect(lambda: self.summary_search.clear())
        summary_search_layout = QHBoxLayout()
        summary_search_layout.addWidget(self.summary_search)
        summary_search_layout.addWidget(self.clear_summary_filter_button)
        self.summary_layout.addLayout(summary_search_layout)
        self.summary_table = QTableView()
        self.summary_model = QStandardItemModel()
        self.summary_proxy = QSortFilterProxyModel()
        self.summary_proxy.setSourceModel(self.summary_model)
        self.summary_proxy.setFilterCaseSensitivity(1)
        self.summary_proxy.setFilterKeyColumn(-1)
        self.summary_table.setModel(self.summary_proxy)
        header = self.summary_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.Stretch)
        self.summary_table.setSortingEnabled(True)
        self.summary_layout.addWidget(self.summary_table)
        summary_label = QLabel("Podsumowanie godzin według specjalności:")
        summary_label.setStyleSheet("""
            QLabel {
                font-family: 'Verdana';
                font-size: 16px;
            }
        """)
        self.tab_widget.addTab(self.summary_tab, "Zestawienie")
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
        self.populate_summary()
        self.year_filter.currentIndexChanged.connect(self.filter_instructors)
        self.unit_filter.currentIndexChanged.connect(self.filter_instructors)
        self.year_filter.setToolTip("Wybierz rok akademicki")
        self.unit_filter.setToolTip("Wybierz jednostkę organizacyjną")
        self.employee_filter.setToolTip("Wybierz wykładowcę")
        self.filter_button.setToolTip("Zastosuj wybrane filtry do danych")
        self.refresh_button.setToolTip("Odśwież dane bez zmiany filtrów")
        self.group_search.setToolTip("Wyszukaj grupę po dowolnym polu")
        self.clear_group_filter_button.setToolTip("Wyczyść pole wyszukiwania grup")
        self.instructor_search.setToolTip("Wyszukaj wykładowcę po nazwisku lub imieniu")
        self.clear_instructor_filter_button.setToolTip("Wyczyść pole wyszukiwania wykładowców")
        self.summary_search.setToolTip("Wyszukaj w podsumowaniu po dowolnym polu")
        self.clear_summary_filter_button.setToolTip("Wyczyść pole wyszukiwania w podsumowaniu")
        self.report_button.setToolTip("Wygeneruj raport Excel z aktualnych danych")
        if hasattr(self, 'theme_toggle_btn'):
            self.theme_toggle_btn.setToolTip("Przełącz tryb ciemny/jasny")
        
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
        self.populate_summary()
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
        db = SessionLocal()
        print(f"User right: {self.user_right}")  # Debugging: Log the user right
        try:
            # Pobierz jednostki organizacyjne na podstawie prawa użytkownika
            if self.user_right == 0:  # Dostęp do wszystkich jednostek
                self.unit_filter.addItem("Wszystkie jednostki", None) 
                units = db.query(OrganizationalUnits).filter(OrganizationalUnits.OPIS.like("Instytut %")).all()
            elif self.user_right == 1:  # Dostęp tylko do Instytutu Informatyki Stosowanej
                units = db.query(OrganizationalUnits).filter(OrganizationalUnits.OPIS == "Instytut Informatyki Stosowanej im. Krzysztofa Brzeskiego").all()
            elif self.user_right == 2:  # Dostęp tylko do Instytutu Ekonomicznego
                units = db.query(OrganizationalUnits).filter(OrganizationalUnits.OPIS == "Instytut Ekonomiczny").all()
            elif self.user_right == 3:  # Dostęp tylko do Instytutu Politechnicznego
                units = db.query(OrganizationalUnits).filter(OrganizationalUnits.OPIS == "Instytut Politechniczny").all()
            elif self.user_right == 4:  # Dostęp tylko do Instytutu Pedagogiczno-Językowego
                units = db.query(OrganizationalUnits).filter(OrganizationalUnits.OPIS == "Instytut Pedagogiczno- Językowy").all()
            else:
                units = []  # Brak dostępu do żadnych jednostek
                self.status_label.setText("Błąd: Nieprawidłowa rola użytkownika. Skontaktuj się z administratorem.")
                QMessageBox.critical(self, "Błąd uprawnień", "Nieprawidłowa rola użytkownika. Skontaktuj się z administratorem.")

            # Dodaj jednostki do filtra
            for unit in units:
                self.unit_filter.addItem(str(unit.OPIS), unit.KOD)
        except Exception as e:
            print(f"Błąd podczas ładowania jednostek organizacyjnych: {str(e)}")
        finally:
            db.close()
    
    def apply_filters(self):
        """Apply filters and refresh data in both tabs."""
        self.populate_groups()
        self.filter_instructors() 
        self.populate_employees()
        self.populate_summary()
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
            instructors.sort(key=lambda i: (getattr(i.Person, 'NAZWISKO', ''), getattr(i.Person, 'IMIE', '')) if hasattr(i, 'Person') and i.Person else (getattr(db.query(Person).filter_by(ID=i.OS_ID).first(), 'NAZWISKO', ''), getattr(db.query(Person).filter_by(ID=i.OS_ID).first(), 'IMIE', '')))
            self.employee_filter.clear()
            self.employee_filter.addItem("Wszyscy wykładowcy", None)
            for instructor in instructors:
                person = db.query(Person).filter_by(ID=instructor.OS_ID).first()
                print(f"Adding instructor: {getattr(person, 'NAZWISKO', 'Brak')} {getattr(person, 'IMIE', 'Brak')} {instructor.ID}")  # Debugging: Log the instructor being added
                self.employee_filter.addItem(f"{getattr(person, 'NAZWISKO', 'Brak')} {getattr(person, 'IMIE', 'Brak')}", instructor.ID)
            
            index_to_restore = self.employee_filter.findData(current_instructor)
            if index_to_restore != -1:
                self.employee_filter.setCurrentIndex(index_to_restore)
        except Exception as e:
            print(f"Error: {str(e)}")  # Debugging: Log the error
        finally:
            db.close()
    def display_instructor_details(self, index):
        self.instructor_details_model.clear()
        source_index = self.instructor_proxy.mapToSource(index)
        row = source_index.row()
        item = self.instructor_model.item(row, 1)
        if item is not None:
            nazwisko_imie = item.text()
        else:
            nazwisko_imie = ""
        selected_year = self.year_filter.currentText()
        selected_unit = self.unit_filter.currentData()
        db = SessionLocal()
        try:
            person = db.query(Person).filter(
                (Person.NAZWISKO + " " + Person.IMIE) == nazwisko_imie
            ).first()
            if not person:
                self.instructor_details_model.setHorizontalHeaderLabels(["Informacja"])
                self.instructor_details_model.appendRow([QStandardItem("Nie znaleziono wykładowcy.")])
                return
            employee = db.query(Employee).filter(Employee.OS_ID == person.ID).first()
            if not employee:
                self.instructor_details_model.setHorizontalHeaderLabels(["Informacja"])
                self.instructor_details_model.appendRow([QStandardItem("Nie znaleziono pracownika.")])
                return
            selected_employee_id = employee.ID

            group_data = get_group_data(selected_year, selected_unit, selected_employee_id)
            workload_data = calculate_workload_for_employee(selected_employee_id, selected_year, selected_unit)

            # Dane podstawowe
            headers = [
                "Stanowisko", "Pensum uczelniane", "Umowa od", "Umowa do", "Pensum", "Godziny Z stacjonarne", "Godziny Z niestacjonarne",
                "Godziny L stacjonarne", "Godziny L niestacjonarne", "Nadgodziny/Niedobór", "Łączna zniżka", "Etat", "Czy podstawowe miejsce pracy",
                "Stawka", "Kwota nadgodzin"
            ]
            self.instructor_details_model.setHorizontalHeaderLabels(headers)
            row = [
                QStandardItem(str(workload_data.get('stanowisko', ''))),
                QStandardItem(str(workload_data.get('pensum_uczelniane', ''))),
                QStandardItem(str(workload_data.get('umowa_pocz', ''))),
                QStandardItem(str(workload_data.get('umowa_kon', ''))),
                QStandardItem(str(workload_data.get('pensum', ''))),
                QStandardItem(str(workload_data.get('godziny_dydaktyczne_z_stacjonarne', ''))),
                QStandardItem(str(workload_data.get('godziny_dydaktyczne_z_niestacjonarne', ''))),
                QStandardItem(str(workload_data.get('godziny_dydaktyczne_l_stacjonarne', ''))),
                QStandardItem(str(workload_data.get('godziny_dydaktyczne_l_niestacjonarne', ''))),
                QStandardItem(str(workload_data.get('nadgodziny', ''))),
                QStandardItem(str(workload_data.get('zniżka', ''))),
                QStandardItem(str(workload_data.get('etat', ''))),
                QStandardItem(str(workload_data.get('CZY_PODSTAWOWE', ''))),
                QStandardItem(str(workload_data.get('stawka', ''))),
                QStandardItem(str(workload_data.get('kwota_nadgodzin', '')))
            ]
            self.instructor_details_model.appendRow(row)

            # Zniżki
            self.instructor_details_model.appendRow([QStandardItem("--- Zniżki ---")] + [QStandardItem("") for _ in range(len(headers)-1)])
            if workload_data.get("typy_znizek") and workload_data["typy_znizek"] != ["Brak zniżek"]:
                for znizka, godziny in zip(workload_data["typy_znizek"], workload_data.get("godziny_znizek", [])):
                    self.instructor_details_model.appendRow([QStandardItem(f"{znizka} ({godziny} godz.)")] + [QStandardItem("") for _ in range(len(headers)-1)])
            else:
                self.instructor_details_model.appendRow([QStandardItem("Brak zniżek")] + [QStandardItem("") for _ in range(len(headers)-1)])

            # Przedmioty
            self.instructor_details_model.appendRow([QStandardItem("--- Przedmioty ---")] + [QStandardItem("") for _ in range(len(headers)-1)])
            for group in group_data:
                self.instructor_details_model.appendRow([
                    QStandardItem(group.get('Przedmiot', '')),
                    QStandardItem(group.get('Typ zajęć', '')),
                    QStandardItem(str(group.get('Liczba godzin', ''))),
                    QStandardItem(group.get('Semestr', '')),
                    QStandardItem(group.get('Instytut', '')),
                    QStandardItem(f"{group.get('Kierunek', '')}"),
                    QStandardItem(f"{group.get('Specjalność', '')}"),
                    QStandardItem(group.get('Tryb', '')),
                ] + [QStandardItem("") for _ in range(len(headers)-7)])
        except Exception as e:
            self.instructor_details_model.setHorizontalHeaderLabels(["Błąd"])
            self.instructor_details_model.appendRow([QStandardItem(f"Błąd: {str(e)}")])
        finally:
            db.close()
    def populate_groups(self):
        self.group_model.clear()
        selected_unit = self.unit_filter.currentData()
        selected_year = self.year_filter.currentText()
        selected_employee = self.employee_filter.currentData()

        try:
            # Pobierz dane grup z get_group_data
            group_data = get_group_data(selected_year, selected_unit, selected_employee)
            if not group_data:
                self.group_model.setHorizontalHeaderLabels(["Brak grup do wyświetlenia."])
                return

            # Ustal nagłówki na podstawie kluczy pierwszego rekordu
            headers = list(group_data[0].keys())
            self.group_model.setHorizontalHeaderLabels(headers)
            self.update_group_filter_columns(headers)
            for group in group_data:
                row_items = []
                for col in headers:
                    value = group.get(col, "")
                    item = QStandardItem(str(value))  # <-- Tworzymy nowy obiekt za każdym razem
                    # Jeśli wartość jest liczbą (int lub float), ustaw dane liczbowe
                    try:
                        num = float(value)
                        item.setData(num, 2)
                    except (ValueError, TypeError):
                        pass  # zostaw jako tekst
                    row_items.append(item)
                self.group_model.appendRow(row_items)

        except Exception as e:
            self.group_model.setHorizontalHeaderLabels(["Błąd"])
            self.group_model.appendRow([QStandardItem(f"Błąd: {str(e)}")])
        
    def populate_employees(self):
        self.instructor_model.clear()
        selected_unit = self.unit_filter.currentData()
        selected_year = self.year_filter.currentText()
        selected_employee = self.employee_filter.currentData()
        db = SessionLocal()
        try:
            query = db.query(Employee, Person).join(Person, Employee.OS_ID == Person.ID).filter(GroupInstructor.PRAC_ID == Employee.ID).filter(DidacticCycles.OPIS.like(f"%{selected_year}%"))
            if selected_unit:
                query = query.filter(GroupInstructor.JEDN_KOD == selected_unit)
            if selected_employee:
                query = query.filter(Employee.ID == selected_employee)
            results = query.all()
            results.sort(key=lambda pair: (pair[1].NAZWISKO, pair[1].IMIE))
            headers = [
    "Tytuły", "Nazwisko i imię", "J.O.", "Forma", "Stanowisko", "Umowa od", "Umowa do",
    "Pensum uczelniane", "Zniżka", "Czy podstawowe miejsce pracy", "Godziny dydaktyczne Z stacjonarne",
    "Godziny dydaktyczne Z niestacjonarne", "Godziny dydaktyczne L stacjonarne", "Godziny dydaktyczne L niestacjonarne", "Pensum realne", "Pensum", "Etat", "Nadgodziny", "Stawka", "Kwota nadgodzin"
]
            self.instructor_model.setHorizontalHeaderLabels(headers)
            for employee, person in results:
                workload_data = calculate_workload_for_employee(employee.ID, selected_year, selected_unit)
                if workload_data["total_workload"] > 0:
                    db2 = SessionLocal()
                    tytul = db2.query(Title).filter_by(ID=person.TYTUL_PRZED).first()
                    organizational_unit = db2.query(OrganizationalUnits).filter_by(KOD=person.JED_ORG_KOD).first()
                    db2.close()
                    # Tworzymy QStandardItemy
                    tytul_str = str(tytul.NAZWA) if tytul and hasattr(tytul, 'NAZWA') else "N/A"
                    nazwisko = getattr(person, 'NAZWISKO', 'Brak') if person else 'Brak'
                    imie = getattr(person, 'IMIE', 'Brak') if person else 'Brak'
                    organizational_unit_str = str(organizational_unit.OPIS) if organizational_unit and hasattr(organizational_unit, 'OPIS') else "N/A"
                    row = [
                        QStandardItem(tytul_str),
                        QStandardItem(f"{nazwisko} {imie}"),
                        QStandardItem(organizational_unit_str),
                        QStandardItem("etat" if workload_data["umowa_pocz"] != "Brak daty rozpoczęcia umowy" else "umowa zlecenie"),
                        QStandardItem(str(workload_data['stanowisko'])),
                        QStandardItem(str(workload_data['umowa_pocz'])),
                        QStandardItem(str(workload_data['umowa_kon'])),
                        QStandardItem(str(workload_data['pensum_uczelniane'])),
                        QStandardItem(str(workload_data['zniżka'])),
                        QStandardItem(str(workload_data['CZY_PODSTAWOWE'])),
                        QStandardItem(str(workload_data['godziny_dydaktyczne_z_stacjonarne'])),
                        QStandardItem(str(workload_data['godziny_dydaktyczne_z_niestacjonarne'])),
                        QStandardItem(str(workload_data['godziny_dydaktyczne_l_stacjonarne'])),
                        QStandardItem(str(workload_data['godziny_dydaktyczne_l_niestacjonarne'])),
                        QStandardItem(str(workload_data['total_workload'])),
                        QStandardItem(str(workload_data['pensum'])),
                        QStandardItem(str(workload_data['etat'])),
                        QStandardItem(str(workload_data['nadgodziny'])),
                        QStandardItem(str(workload_data['stawka'])),
                        QStandardItem(str(workload_data['kwota_nadgodzin'])),
                    ]
                    # Ustaw dane liczbowe dla kolumn liczbowych
                    numeric_indices = [7,8,10,11,12,13,14,15,16,17]  # indeksy kolumn liczbowych
                    numeric_keys = [
                        'pensum_uczelniane','zniżka','godziny_dydaktyczne_z_stacjonarne','godziny_dydaktyczne_z_niestacjonarne','godziny_dydaktyczne_l_stacjonarne','godziny_dydaktyczne_l_niestacjonarne',
                        'total_workload','pensum','etat','nadgodziny','stawka','kwota_nadgodzin'
                    ]
                    for idx, key in zip(numeric_indices, numeric_keys):
                        try:
                            value = float(workload_data[key])
                            row[idx].setData(value, 2)
                        except (ValueError, TypeError):
                            pass
                    self.instructor_model.appendRow(row)
            if not results:
                self.instructor_model.setHorizontalHeaderLabels(["Brak wykładowców do wyświetlenia."])
        except Exception as e:
            self.instructor_model.setHorizontalHeaderLabels(["Błąd"])
            self.instructor_model.appendRow([QStandardItem(f"Błąd: {str(e)}")])
        finally:
            db.close()
    def populate_summary(self):
        self.summary_model.clear()
        selected_unit = self.unit_filter.currentData()
        selected_year = self.year_filter.currentText()
        selected_employee = self.employee_filter.currentData()

        try:
            group_data = get_group_data(selected_year, selected_unit, selected_employee)
            kierunek_dict = {}

            for group in group_data:
                kierunek = group.get("Kierunek", "Nieznany kierunek")
                specjalnosc = group.get("Specjalność", "Brak specjalności")
                tryb = group.get("Tryb", "Nieznany tryb").strip().lower()
                hours = group.get("Liczba godzin", 0)
                semester = group.get("Semestr", "Nieznany semestr").lower()

                if kierunek not in kierunek_dict:
                    kierunek_dict[kierunek] = {}
                if specjalnosc not in kierunek_dict[kierunek]:
                    kierunek_dict[kierunek][specjalnosc] = {
                        "Zimowy stacjonarne": 0,
                        "Zimowy niestacjonarne": 0,
                        "Letni stacjonarne": 0,
                        "Letni niestacjonarne": 0,
                        "Suma": 0
                    }
                print(f"tryb: {tryb}, semester: {semester}, hours: {hours}, kierunek: {kierunek}, specjalnosc: {specjalnosc}")
                if "zimowy" in semester and (("niestacjonarne" in tryb) or tryb == "none"):
                    print("Zimowy niestacjonarne:", kierunek, specjalnosc, hours)
                    kierunek_dict[kierunek][specjalnosc]["Zimowy niestacjonarne"] += hours
                elif "zimowy" in semester and "stacjonarne" in tryb:
                    print("Zimowy stacjonarne:", kierunek, specjalnosc, hours)
                    kierunek_dict[kierunek][specjalnosc]["Zimowy stacjonarne"] += hours
                elif "letni" in semester and (("niestacjonarne" in tryb) or tryb == "none"):
                    print("Letni niestacjonarne:", kierunek, specjalnosc, hours)
                    kierunek_dict[kierunek][specjalnosc]["Letni niestacjonarne"] += hours
                elif "letni" in semester and "stacjonarne" in tryb:
                    print("Letni stacjonarne:", kierunek, specjalnosc, hours)
                    kierunek_dict[kierunek][specjalnosc]["Letni stacjonarne"] += hours
                else:
                    # Jeśli tryb nie jest rozpoznany, możesz dodać do osobnej kolumny lub wyświetlić ostrzeżenie
                    print(f"Nieznany tryb/semestr: tryb={tryb}, semester={semester}, hours={hours}, kierunek={kierunek}, specjalnosc={specjalnosc}")

                kierunek_dict[kierunek][specjalnosc]["Suma"] += hours

            headers = [
                "Kierunek", "Specjalność",
                "Zimowy stacjonarne", "Zimowy niestacjonarne",
                "Letni stacjonarne", "Letni niestacjonarne",
                "Suma"
            ]
            self.summary_model.setHorizontalHeaderLabels(headers)

            for kierunek, specjalnosci in kierunek_dict.items():
                # Sumy dla kierunku
                suma_kierunku = {
                    "Zimowy stacjonarne": 0,
                    "Zimowy niestacjonarne": 0,
                    "Letni stacjonarne": 0,
                    "Letni niestacjonarne": 0,
                    "Suma": 0
                }
                for specjalnosc, godziny in specjalnosci.items():
                    row = [
                        QStandardItem(kierunek),
                        QStandardItem(specjalnosc),
                        QStandardItem(str(godziny["Zimowy stacjonarne"])),
                        QStandardItem(str(godziny["Zimowy niestacjonarne"])),
                        QStandardItem(str(godziny["Letni stacjonarne"])),
                        QStandardItem(str(godziny["Letni niestacjonarne"])),
                        QStandardItem(str(godziny["Suma"]))
                    ]
                    self.summary_model.appendRow(row)
                    # Dodaj do sum kierunku
                    suma_kierunku["Zimowy stacjonarne"] += godziny["Zimowy stacjonarne"]
                    suma_kierunku["Zimowy niestacjonarne"] += godziny["Zimowy niestacjonarne"]
                    suma_kierunku["Letni stacjonarne"] += godziny["Letni stacjonarne"]
                    suma_kierunku["Letni niestacjonarne"] += godziny["Letni niestacjonarne"]
                    suma_kierunku["Suma"] += godziny["Suma"]
                # Dodaj wiersz sumujący dla kierunku
                row = [
                    QStandardItem(kierunek),
                    QStandardItem("SUMA kierunku"),
                    QStandardItem(str(suma_kierunku["Zimowy stacjonarne"])),
                    QStandardItem(str(suma_kierunku["Zimowy niestacjonarne"])),
                    QStandardItem(str(suma_kierunku["Letni stacjonarne"])),
                    QStandardItem(str(suma_kierunku["Letni niestacjonarne"])),
                    QStandardItem(str(suma_kierunku["Suma"]))
                ]
                self.summary_model.appendRow(row)

            if not kierunek_dict:
                self.summary_model.setHorizontalHeaderLabels(["Brak danych do wyświetlenia."])
        except Exception as e:
            self.summary_model.setHorizontalHeaderLabels(["Błąd"])
            self.summary_model.appendRow([QStandardItem(f"Błąd: {str(e)}")])
    def display_employee_workload(self, item):
        """Display workload data for the selected employee."""
        self.instructor_details.clear()
        self.instructor_details.setStyleSheet("""
            QListWidget {
                font-family: 'Verdana';
                font-size: 16px;
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
            group_data = get_group_data(selected_year, selected_unit, selected_employee_id)

            workload_data = calculate_workload_for_employee(selected_employee_id, selected_year, selected_unit)

            # Wyświetl szczegóły obciążenia dydaktycznego
            self.instructor_details.addItem(f"Stanowisko: {workload_data['stanowisko']}")
            self.instructor_details.addItem(f"Pensum uczelniane: {workload_data['pensum_uczelniane']}")
            self.instructor_details.addItem(f"Umowa od: {workload_data['umowa_pocz']} do: {workload_data['umowa_kon']}")
            self.instructor_details.addItem(f"Pensum: {workload_data['pensum']}")
            self.instructor_details.addItem(f"Godziny dydaktyczne Z stacjonarne: {workload_data['godziny_dydaktyczne_z_stacjonarne']}")
            self.instructor_details.addItem(f"Godziny dydaktyczne Z niestacjonarne: {workload_data['godziny_dydaktyczne_z_niestacjonarne']}")
            self.instructor_details.addItem(f"Godziny dydaktyczne L stacjonarne: {workload_data['godziny_dydaktyczne_l_stacjonarne']}")
            self.instructor_details.addItem(f"Godziny dydaktyczne L niestacjonarne: {workload_data['godziny_dydaktyczne_l_niestacjonarne']}")
            self.instructor_details.addItem(f"Nadgodziny/Niedobór: {workload_data['nadgodziny']}")
            self.instructor_details.addItem(f"Łączna zniżka: {workload_data['zniżka']} godzin")
            self.instructor_details.addItem(f"Etat: {workload_data['etat']}")
            self.instructor_details.addItem(f"Czy podstawowe miejsce pracy: {workload_data['CZY_PODSTAWOWE']}")
            # Wyświetl szczegóły zniżek
            self.instructor_details.addItem("Zniżki:")
            if workload_data.get("typy_znizek"):
                for znizka, godziny in zip(workload_data["typy_znizek"], workload_data.get("godziny_znizek", [])):
                    self.instructor_details.addItem(f"  - Typ: {znizka}, Liczba godzin: {godziny}")
            else:
                self.instructor_details.addItem("  Brak zniżek")

            # Wyświetl szczegóły przedmiotów
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

    def select_columns_dialog(self, columns, title):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Wybierz kolumny do eksportu - {title}")
        layout = QVBoxLayout(dialog)
        label = QLabel("Zaznacz kolumny do eksportu:")
        layout.addWidget(label)
        checkboxes = []
        for col in columns:
            cb = QCheckBox(col)
            cb.setChecked(True)
            layout.addWidget(cb)
            checkboxes.append(cb)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec_() == QDialog.Accepted:
            selected = [cb.text() for cb in checkboxes if cb.isChecked()]
            return selected
        else:
            return None

    def generate_report_from_db(self):
        """Generate an Excel report with improved formatting, nagłówek i stopka, wybór kolumn."""
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
            if selected_employee:
                query = query.filter(Employee.ID == selected_employee)
            employees = query.all()
            lp = 1
            data = []
            for employee, person in employees:
                person = db.query(Person).filter_by(ID=person.ID).first()
                organizational_unit = db.query(OrganizationalUnits).filter_by(KOD=person.JED_ORG_KOD).first()
                workload_data = calculate_workload_for_employee(employee.ID, selected_year, selected_unit)
                tytul = db.query(Title).filter_by(ID=person.TYTUL_PRZED).first()
                data.append({
                    "Lp.": lp,
                    "Tytuły": tytul.NAZWA if tytul else "N/A",
                    "Nazwisko i imię": f"{person.NAZWISKO} {person.IMIE}",
                    "J.O.": organizational_unit.OPIS if organizational_unit else "N/A",
                    "Forma": "etat" if workload_data["umowa_pocz"] != "Brak daty rozpoczęcia umowy" else "umowa zlecenie",
                    "Stanowisko": workload_data["stanowisko"],
                    "Umowa od": workload_data["umowa_pocz"],
                    "Umowa do": workload_data["umowa_kon"],
                    "Pensum uczelniane": workload_data["pensum_uczelniane"],
                    "Zniżka": workload_data["zniżka"],
                    "Czy podstawowe miejsce pracy": workload_data["CZY_PODSTAWOWE"],
                    "Godziny dydaktyczne Z stacjonarne": workload_data["godziny_dydaktyczne_z_stacjonarne"],
                    "Godziny dydaktyczne Z niestacjonarne": workload_data["godziny_dydaktyczne_z_niestacjonarne"],
                    "Godziny dydaktyczne L stacjonarne": workload_data["godziny_dydaktyczne_l_stacjonarne"],
                    "Godziny dydaktyczne L niestacjonarne": workload_data["godziny_dydaktyczne_l_niestacjonarne"],
                    "Pensum realne": workload_data["total_workload"],
                    "Pensum": workload_data["pensum"],
                    "Etat": workload_data["etat"],
                    "Nadgodziny": workload_data["nadgodziny"],
                    "Stawka": workload_data["stawka"],
                    "Kwota nadgodzin": workload_data["kwota_nadgodzin"],
                })
                lp += 1
            # Wybór kolumn dla Wykładowców
            if data:
                all_columns = list(data[0].keys())
                selected_columns = self.select_columns_dialog(all_columns, "Wykładowcy")
                if not selected_columns:
                    self.status_label.setText("Status: Anulowano eksport.")
                    db.close()
                    return
                df1 = pd.DataFrame(data)[selected_columns]
            else:
                df1 = pd.DataFrame()
            # Grupy
            data2 = get_group_data(selected_year, selected_unit, selected_employee)
            if data2:
                all_columns2 = list(data2[0].keys())
                selected_columns2 = self.select_columns_dialog(all_columns2, "Grupy")
                if not selected_columns2:
                    self.status_label.setText("Status: Anulowano eksport.")
                    db.close()
                    return
                df2 = pd.DataFrame(data2)[selected_columns2]
            else:
                df2 = pd.DataFrame()
            # Podsumowanie (z sumą kierunku)
            summary_data = []
            group_data = get_group_data(selected_year, selected_unit, selected_employee)
            kierunek_dict = {}
            for group in group_data:
                kierunek = group.get("Kierunek", "Nieznany kierunek")
                specjalnosc = group.get("Specjalność", "Brak specjalności")
                tryb = group.get("Tryb", "Nieznany tryb").strip().lower()
                hours = group.get("Liczba godzin", 0)
                semester = group.get("Semestr", "Nieznany semestr").lower()
                if kierunek not in kierunek_dict:
                    kierunek_dict[kierunek] = {}
                if specjalnosc not in kierunek_dict[kierunek]:
                    kierunek_dict[kierunek][specjalnosc] = {
                        "Zimowy stacjonarne": 0,
                        "Zimowy niestacjonarne": 0,
                        "Letni stacjonarne": 0,
                        "Letni niestacjonarne": 0,
                        "Suma": 0
                    }
                if "zimowy" in semester and (("niestacjonarne" in tryb) or tryb == "none"):
                    kierunek_dict[kierunek][specjalnosc]["Zimowy niestacjonarne"] += hours
                elif "zimowy" in semester and "stacjonarne" in tryb:
                    kierunek_dict[kierunek][specjalnosc]["Zimowy stacjonarne"] += hours
                elif "letni" in semester and (("niestacjonarne" in tryb) or tryb == "none"):
                    kierunek_dict[kierunek][specjalnosc]["Letni niestacjonarne"] += hours
                elif "letni" in semester and "stacjonarne" in tryb:
                    kierunek_dict[kierunek][specjalnosc]["Letni stacjonarne"] += hours
                kierunek_dict[kierunek][specjalnosc]["Suma"] += hours
            for kierunek, specjalnosci in kierunek_dict.items():
                suma_kierunku = {
                    "Zimowy stacjonarne": 0,
                    "Zimowy niestacjonarne": 0,
                    "Letni stacjonarne": 0,
                    "Letni niestacjonarne": 0,
                    "Suma": 0
                }
                for specjalnosc, godziny in specjalnosci.items():
                    summary_data.append({
                        "Kierunek": kierunek,
                        "Specjalność": specjalnosc,
                        "Zimowy stacjonarne": godziny["Zimowy stacjonarne"],
                        "Zimowy niestacjonarne": godziny["Zimowy niestacjonarne"],
                        "Letni stacjonarne": godziny["Letni stacjonarne"],
                        "Letni niestacjonarne": godziny["Letni niestacjonarne"],
                        "Suma": godziny["Suma"]
                    })
                    suma_kierunku["Zimowy stacjonarne"] += godziny["Zimowy stacjonarne"]
                    suma_kierunku["Zimowy niestacjonarne"] += godziny["Zimowy niestacjonarne"]
                    suma_kierunku["Letni stacjonarne"] += godziny["Letni stacjonarne"]
                    suma_kierunku["Letni niestacjonarne"] += godziny["Letni niestacjonarne"]
                    suma_kierunku["Suma"] += godziny["Suma"]
                summary_data.append({
                    "Kierunek": kierunek,
                    "Specjalność": "SUMA kierunku",
                    "Zimowy stacjonarne": suma_kierunku["Zimowy stacjonarne"],
                    "Zimowy niestacjonarne": suma_kierunku["Zimowy niestacjonarne"],
                    "Letni stacjonarne": suma_kierunku["Letni stacjonarne"],
                    "Letni niestacjonarne": suma_kierunku["Letni niestacjonarne"],
                    "Suma": suma_kierunku["Suma"]
                })
            df3 = pd.DataFrame(summary_data)
            now = datetime.now().strftime("%Y-%m-%d_%H-%M")
            default_name = f"raport_{now}.xlsx"
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", default_name, "Excel Files (*.xlsx)")
            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Eksport bez nagłówków tekstowych i bez nagłówków kolumn
                    if not df1.empty:
                        df1.to_excel(writer, sheet_name='Wykładowcy', index=False, header=True)
                    if not df2.empty:
                        df2.to_excel(writer, sheet_name='Grupy', index=False, header=True)
                    if not df3.empty:
                        df3.to_excel(writer, sheet_name='Podsumowanie', index=False, header=True)
                # Dodaj stopkę z datą do arkuszy
                self.add_footer_to_excel(file_path)
                self.format_excel(file_path)
                self.status_label.setText(f"Status: Raport zapisany do {file_path}")
            else:
                self.status_label.setText("Status: Anulowano zapis raportu")
        except Exception as e:
            self.status_label.setText(f"Status: Błąd podczas generowania raportu: {str(e)}")
        finally:
            db.close()

    def add_footer_to_excel(self, file_path):
        from openpyxl import load_workbook
        wb = load_workbook(file_path)
        date_str = datetime.now().strftime("Data wygenerowania raportu: %Y-%m-%d %H:%M")
        for sheet_name in ["Wykładowcy", "Grupy"]:
            if sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                last_row = ws.max_row + 2
                ws.cell(row=last_row, column=1, value=date_str)
        wb.save(file_path)

    def format_excel(self, file_path):
        """Apply formatting to the Excel file, adjust column widths, and add Excel tables with filtering."""
        from openpyxl import load_workbook
        from openpyxl.worksheet.table import Table, TableStyleInfo

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
                from openpyxl.utils import get_column_letter
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = max_length + 2
                sheet.column_dimensions[column_letter].width = adjusted_width

            # Dodaj tabelę Excela z filtrowaniem
            if sheet.max_row > 1 and sheet.max_column > 0:
                table_ref = f"A1:{sheet.cell(row=sheet.max_row, column=sheet.max_column).coordinate}"
                table = Table(displayName=f"Table_{sheet.title.replace(' ', '_')}", ref=table_ref)
                style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                                    showLastColumn=False, showRowStripes=True, showColumnStripes=False)
                table.tableStyleInfo = style
                # Usuń istniejące tabele o tej samej nazwie (jeśli są)
                if table.displayName in sheet.tables:
                    del sheet.tables[table.displayName]
                sheet.add_table(table)

        wb.save(file_path)
    def filter_group_list(self, text):
        self.group_proxy.setFilterFixedString(text)


    def filter_instructor_list(self, text):
        self.instructor_proxy.setFilterFixedString(text)

    def filter_summary_list(self, text):
        self.summary_proxy.setFilterFixedString(text)
    
    def on_group_filter_column_changed(self, index):
        column = self.group_filter_column_combo.currentData()
        self.group_proxy.setFilterKeyColumn(column)

    def update_group_filter_columns(self, headers):
        self.group_filter_column_combo.blockSignals(True)
        self.group_filter_column_combo.clear()
        self.group_filter_column_combo.addItem("Wszystkie kolumny", -1)
        for i, header in enumerate(headers):
            self.group_filter_column_combo.addItem(header, i)
        self.group_filter_column_combo.blockSignals(False)

    from PyQt5.QtWidgets import QMessageBox

    def generate_report_from_view(self):
        try:
            group_headers = [self.group_model.headerData(i, Qt.Orientation.Horizontal) for i in range(self.group_model.columnCount())]
            instructor_headers = [self.instructor_model.headerData(i, Qt.Orientation.Horizontal) for i in range(self.instructor_model.columnCount())]
            summary_headers = [self.summary_model.headerData(i, Qt.Orientation.Horizontal) for i in range(self.summary_model.columnCount())]

            group_data = self.get_visible_table_data(self.group_proxy, group_headers)
            instructor_data = self.get_visible_table_data(self.instructor_proxy, instructor_headers)
            summary_data = self.get_visible_table_data(self.summary_proxy, summary_headers)

            import pandas as pd
            df1 = pd.DataFrame(instructor_data)
            df2 = pd.DataFrame(group_data)
            df3 = pd.DataFrame(summary_data)

            now = datetime.now().strftime("%Y-%m-%d_%H-%M")
            default_name = f"raport_{now}.xlsx"
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", default_name, "Excel Files (*.xlsx)")
            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # Eksport bez nagłówków tekstowych
                    if not df1.empty:
                        df1.to_excel(writer, sheet_name='Wykładowcy', index=False)
                    if not df2.empty:
                        df2.to_excel(writer, sheet_name='Grupy', index=False)
                    if not df3.empty:
                        df3.to_excel(writer, sheet_name='Podsumowanie', index=False)
                self.format_excel(file_path)
                self.status_label.setText(f"Status: Raport zapisany do {file_path}")
            else:
                self.status_label.setText("Status: Anulowano zapis raportu")
        except Exception as e:
            self.status_label.setText(f"Status: Błąd podczas generowania raportu: {str(e)}")

    def get_visible_table_data(self, proxy_model, headers):
        data = []
        for row in range(proxy_model.rowCount()):
            row_data = {}
            for col, header in enumerate(headers):
                index = proxy_model.index(row, col)
                row_data[header] = proxy_model.data(index)
            data.append(row_data)
        return data
    
    def generate_report(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Wybierz tryb raportu")
        msg.setText("Z jakiego źródła wygenerować raport?")
        widok_btn = msg.addButton("Z widoku (to co w tabelach)", QMessageBox.AcceptRole)
        baza_btn = msg.addButton("Z bazy (pełne dane)", QMessageBox.DestructiveRole)
        msg.setDefaultButton(widok_btn)
        msg.exec_()

        if msg.clickedButton() == widok_btn:
            self.generate_report_from_view()
        else:
            self.generate_report_from_db()

    def toggle_theme(self):
        if self.is_dark_mode:
            # Jasny motyw
            light_stylesheet = """
                QWidget { background-color: #fff; color: #232629; }
                QLineEdit, QComboBox, QTableView, QTabWidget, QHeaderView::section {
                    background-color: #ecf0f1; color: #232629; border: 1px solid #bdc3c7;
                }
                QPushButton { background-color: #1abc9c; color: white; border-radius: 5px; }
                QPushButton:hover { background-color: #16a085; }
                QMenuBar { background-color: #fff; color: #232629; }
                QMenu { background-color: #fff; color: #232629; }
                QTableView QHeaderView::section { background-color: #ecf0f1; color: #232629; }
                QTabBar::tab { background: #ecf0f1; color: #232629; border: 1px solid #bdc3c7; min-width: 120px; }
                QTabBar::tab:selected { background: #1abc9c; color: white; }
                QTabBar::tab:!selected { background: #ecf0f1; color: #232629; }
                QTabWidget::pane { border: 1px solid #bdc3c7; }
                QTableCornerButton::section { background-color: #ecf0f1; border: 1px solid #bdc3c7; }
            """
            self.setStyleSheet(light_stylesheet)
            self.is_dark_mode = False
            self.theme_toggle_btn.setText(" 🌜 ")
            self.theme_toggle_btn.setStyleSheet("font-size: 28px; border-radius: 8px; margin-left: 16px; padding: 8px 16px; background-color: #ecf0f1; color: #232629;")
        else:
            dark_stylesheet = """
                QWidget { background-color: #232629; color: #f0f0f0; }
                QLineEdit, QComboBox, QTableView, QTabWidget, QHeaderView::section {
                    background-color: #31363b; color: #f0f0f0; border: 1px solid #444;
                }
                QPushButton { background-color: #444; color: #f0f0f0; border-radius: 5px; }
                QPushButton:hover { background-color: #666; }
                QMenuBar { background-color: #232629; color: #f0f0f0; }
                QMenu { background-color: #232629; color: #f0f0f0; }
                QTableView QHeaderView::section { background-color: #31363b; color: #f0f0f0; }
                QTabBar::tab { background: #31363b; color: #f0f0f0; border: 1px solid #444; min-width: 120px; }
                QTabBar::tab:selected { background: #444; color: #fff; border-bottom: 2px solid #1abc9c; }
                QTabBar::tab:!selected { background: #31363b; color: #bbb; }
                QTabWidget::pane { border: 1px solid #444; }
                QTableCornerButton::section { background-color: #31363b; border: 1px solid #444; }
            """
            self.setStyleSheet(dark_stylesheet)
            self.is_dark_mode = True
            self.theme_toggle_btn.setText("☀️")
            self.theme_toggle_btn.setStyleSheet("font-size: 28px; border-radius: 8px; margin-left: 16px; padding: 8px 16px; background-color: #444; color: #f0f0f0;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())