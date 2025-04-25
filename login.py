from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from sqlalchemy import create_engine
import os
from models import PensumRight
from database import SessionLocal


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logowanie")
        self.setGeometry(100, 100, 400, 300)

        # Główne okno
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Nagłówek
        header_label = QLabel("System Rozliczania Obciążeń Dydaktycznych")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(header_label)

        # Username input
        username_layout = QVBoxLayout()
        username_label = QLabel("Nazwa użytkownika:")
        username_label.setFont(QFont("Arial", 10))
        username_label.setStyleSheet("color: #34495e;")
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Wprowadź nazwę użytkownika")
        self.username_input.setStyleSheet(self.input_style())
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # Password input
        password_layout = QVBoxLayout()
        password_label = QLabel("Hasło:")
        password_label.setFont(QFont("Arial", 10))
        password_label.setStyleSheet("color: #34495e;")
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Wprowadź hasło")
        self.password_input.setStyleSheet(self.input_style())
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # Login button
        button_layout = QHBoxLayout()
        spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.login_button = QPushButton("Zaloguj", self)
        self.login_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.login_button.setStyleSheet(self.button_style())
        self.login_button.clicked.connect(self.handle_login)
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

    def input_style(self):
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

    def button_style(self):
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

    def handle_login(self):
        """Handle login logic."""
        username = self.username_input.text()
        password = self.password_input.text()
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        database = os.getenv("DB_NAME")

        try:
            user_engine = create_engine(f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{database}")
            user_connection = user_engine.connect()
            user_connection.close()

            db = SessionLocal()
            user_right = db.query(PensumRight).filter_by(LOGIN=username).first()
            print(user_right)
            db.close()
            if not user_right:
                QMessageBox.warning(self, "Brak uprawnień", "Nie znaleziono prawa dla tego użytkownika.")
                return

            pensum_engine = create_engine(os.getenv("DATABASE_URL"))
            pensum_connection = pensum_engine.connect()
            pensum_connection.close()

            from app import MainWindow
            self.main_window = MainWindow(user_right.PRAWO)
            self.main_window.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Błąd logowania", f"Nie udało się zalogować: {str(e)}")