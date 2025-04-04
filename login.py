from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from sqlalchemy import create_engine
import os

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logowanie")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        # Username input
        layout.addWidget(QLabel("Nazwa użytkownika:"))
        self.username_input = QLineEdit(self)
        layout.addWidget(self.username_input)

        # Password input
        layout.addWidget(QLabel("Hasło:"))
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Login button
        self.login_button = QPushButton("Zaloguj", self)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
        """Handle login logic."""
        # Pobierz dane logowania od użytkownika
        username = self.username_input.text()
        password = self.password_input.text()
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        database = os.getenv("DB_NAME")

        try:
            # Testuj połączenie z danymi użytkownika
            user_engine = create_engine(f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{database}")
            user_connection = user_engine.connect()
            user_connection.close()

            # Jeśli logowanie się powiedzie, przełącz na użytkownika PENSUM_USR
            pensum_engine = create_engine(os.getenv("DATABASE_URL"))
            pensum_connection = pensum_engine.connect()
            pensum_connection.close()

            # Otwórz główne okno aplikacji
            from app import MainWindow
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Błąd logowania", f"Nie udało się zalogować: {str(e)}")