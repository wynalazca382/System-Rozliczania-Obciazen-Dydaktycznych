from config import load_app_config
load_app_config()
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from sqlalchemy import create_engine, func
from sqlalchemy.engine import Connection, URL
import os
from models import PensumRight
from database import SessionLocal
from cryptography.fernet import Fernet
from typing import Optional, Any

class LoginWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Logowanie")
        self.setGeometry(100, 100, 400, 300)

        # Główne okno
        layout: QVBoxLayout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Nagłówek
        header_label: QLabel = QLabel("System Rozliczania Obciążeń Dydaktycznych")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(header_label)

        # Username input
        username_layout: QVBoxLayout = QVBoxLayout()
        username_label: QLabel = QLabel("Nazwa użytkownika:")
        username_label.setFont(QFont("Arial", 10))
        username_label.setStyleSheet("color: #34495e;")
        self.username_input: QLineEdit = QLineEdit(self)
        self.username_input.setPlaceholderText("Wprowadź nazwę użytkownika")
        self.username_input.setStyleSheet(self.input_style())
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # Password input
        password_layout: QVBoxLayout = QVBoxLayout()
        password_label: QLabel = QLabel("Hasło:")
        password_label.setFont(QFont("Arial", 10))
        password_label.setStyleSheet("color: #34495e;")
        self.password_input: QLineEdit = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Wprowadź hasło")
        self.password_input.setStyleSheet(self.input_style())
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # Login button
        button_layout: QHBoxLayout = QHBoxLayout()
        spacer: QSpacerItem = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.login_button: QPushButton = QPushButton("Zaloguj", self)
        self.login_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.login_button.setStyleSheet(self.button_style())
        self.login_button.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login) # Dodanie obsługi logowania enterem
        button_layout.addSpacerItem(spacer)
        button_layout.addWidget(self.login_button)
        button_layout.addSpacerItem(spacer)
        layout.addLayout(button_layout)

        # Ustawienia layoutu
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 10px;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
        self.main_window: Optional[Any] = None # Initialize main_window

    def input_style(self) -> str:
        """Styl dla pól tekstowych."""
        return """
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 1px solid #1abc9c;
            }
        """

    def button_style(self) -> str:
        """Styl dla przycisków."""
        return """
            QPushButton {
                background-color: #1abc9c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
        """

    def handle_login(self) -> None:
        """Handle login logic."""
        username_input: str = self.username_input.text()
        password_input: str = self.password_input.text()
        host: Optional[str] = os.getenv("DB_HOST")
        port: Optional[str] = os.getenv("DB_PORT")
        database: Optional[str] = os.getenv("DB_NAME")

        if not all([host, port, database]):
            QMessageBox.critical(self, "Błąd konfiguracji", "Brak pełnych danych konfiguracyjnych bazy danych (DB_HOST, DB_PORT, DB_NAME).")
            return

        try:
            user_url = URL.create(
                "oracle+cx_oracle",
                username=username_input,
                password=password_input,
                host=host,
                port=int(port),
                database=database,
            )
            user_engine = create_engine(user_url)
            user_connection: Connection = user_engine.connect()
            user_connection.close()

            normalized_username: str = username_input.strip()
            username_variants = {
                normalized_username,
                normalized_username.split("\\")[-1],
                normalized_username.split("@")[0],
                normalized_username.replace(".", ""),
            }
            username_variants = {value for value in username_variants if value}

            db = SessionLocal()
            user_right: Optional[PensumRight] = (
                db.query(PensumRight)
                .filter(func.upper(func.trim(PensumRight.LOGIN)).in_([value.upper() for value in username_variants]))
                .first()
            )
            print(user_right)
            db.close()
            if not user_right:
                QMessageBox.warning(self, "Brak uprawnień", "Nie znaleziono prawa dla tego użytkownika.")
                return
            
            db_user: Optional[str] = os.getenv("DB_USER")
            db_password_encrypted: Optional[str] = os.getenv("DB_PASSWORD")
            db_key: Optional[str] = os.getenv("DB_KEY")

            if not all([db_user, db_password_encrypted, db_key]):
                QMessageBox.critical(self, "Błąd konfiguracji", "Brak pełnych danych uwierzytelniających dla połączenia z bazą danych (DB_USER, DB_PASSWORD, DB_KEY).")
                return

            f_decrypt: Fernet = Fernet(db_key)
            db_password: str = f_decrypt.decrypt(db_password_encrypted.encode()).decode()
            pensum_url = URL.create(
                "oracle+cx_oracle",
                username=db_user,
                password=db_password,
                host=host,
                port=int(port),
                database=database,
            )
            pensum_engine = create_engine(pensum_url)
            pensum_connection: Connection = pensum_engine.connect()
            pensum_connection.close()

            from app import MainWindow
            self.main_window = MainWindow(user_right.PRAWO)
            self.main_window.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Błąd logowania", f"Nie udało się zalogować: {str(e)}")

