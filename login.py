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
        self.setGeometry(100, 100, 400, 200)

        # Główne okno
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Nagłówek
        header_label = QLabel("System Rozliczania Obciążeń Dydaktycznych")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # Username input
        username_layout = QHBoxLayout()
        username_label = QLabel("Nazwa użytkownika:")
        username_label.setFont(QFont("Arial", 10))
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Wprowadź nazwę użytkownika")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # Password input
        password_layout = QHBoxLayout()
        password_label = QLabel("Hasło:")
        password_label.setFont(QFont("Arial", 10))
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Wprowadź hasło")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # Login button
        button_layout = QHBoxLayout()
        spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.login_button = QPushButton("Zaloguj", self)
        self.login_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.login_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 15px; border-radius: 5px;")
        self.login_button.clicked.connect(self.handle_login)
        button_layout.addSpacerItem(spacer)
        button_layout.addWidget(self.login_button)
        button_layout.addSpacerItem(spacer)
        layout.addLayout(button_layout)

        # Ustawienia layoutu
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
        """)

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