light_stylesheet = """
        QWidget {
            background-color: #fff;
            color: #232629;
            font-family: 'Verdana';
            font-size: 16px;
        }
        QLabel {
            font-family: 'Verdana';
            font-size: 16px;
            color: #232629;
        }
        QComboBox {
            font-family: 'Verdana';
            font-size: 16px;
            min-height: 30px;
            background-color: #ecf0f1;
            color: #232629;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
        }
        QLineEdit {
            font-family: 'Verdana';
            font-size: 16px;
            padding: 5px;
            background-color: #ecf0f1;
            color: #232629;
            border: 1px solid #bdc3c7;
            border-radius: 5px;
        }
        QPushButton {
            background-color: #1abc9c;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Verdana';
            font-size: 14px;
            font-weight: bold;
            transition: background 0.2s;
        }
        QPushButton:hover {
            background-color: #16a085;
        }
        QTabWidget::pane {
            border: 1px solid #bdc3c7;
            border-radius: 5px;
        }
        QTabBar::tab {
            background: #ecf0f1;
            border: 1px solid #bdc3c7;
            padding: 10px 15px;
            margin: 15px 15px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            font-family: 'Verdana';
            font-size: 15px;
            min-width: 150px;
            color: #232629;
        }
        QTabBar::tab:selected {
            background: #1abc9c;
            color: white;
        }
        QTabBar::tab:!selected {
            background: #ecf0f1;
            color: #232629;
        }
        QTableView {
            background-color: #ecf0f1;
            color: #232629;
            gridline-color: #bdc3c7;
            selection-background-color: #1abc9c;
            selection-color: #fff;
            border-radius: 5px;
            font-family: 'Verdana';
            font-size: 16px;
        }
        QHeaderView::section {
            background-color: #ecf0f1;
            color: #232629;
            font-family: 'Verdana';
            font-size: 16px;
            border: 1px solid #bdc3c7;
            padding: 5px;
        }
        QTableCornerButton::section {
            background-color: #ecf0f1;
            border: 1px solid #bdc3c7;
        }
        QToolTip {
            background-color: #1abc9c;
            color: #fff;
            font-family: 'Verdana';
            font-size: 14px;
            border-radius: 5px;
            padding: 5px;
        }
        QListWidget {
            font-family: 'Verdana';
            font-size: 16px;
        }
        QLabel#StatusLabel {
            background-color: #2c3e50;
            color: white;
            padding: 5px;
        }
        QPushButton#ThemeToggle {
    font-size: 28px;
    border-radius: 8px;
    margin: 0;
    padding: 8px 16px;
    min-width: 64px;
    min-height: 48px;
    max-width: 80px;
    max-height: 64px;
}
        QPushButton#FilterRemove {
    background-color: #e74c3c;
    color: #fff;
    border: none;
    font-weight: bold;
    font-size: 16px;
    border-radius: 10px;
    min-width: 24px;
    min-height: 24px;
    max-width: 24px;
    max-height: 24px;
    padding: 0;
}
QPushButton#FilterRemove:hover {
    background-color: #c0392b;
}
        """
dark_stylesheet = """
        QWidget {
            background-color: #232629;
            color: #f0f0f0;
            font-family: 'Verdana';
            font-size: 16px;
        }
        QLabel {
            font-family: 'Verdana';
            font-size: 16px;
            color: #f0f0f0;
        }
        QComboBox {
            font-family: 'Verdana';
            font-size: 16px;
            min-height: 30px;
            background-color: #31363b;
            color: #f0f0f0;
            border: 1px solid #444;
            border-radius: 5px;
        }
        QLineEdit {
            font-family: 'Verdana';
            font-size: 16px;
            padding: 5px;
            background-color: #31363b;
            color: #f0f0f0;
            border: 1px solid #444;
            border-radius: 5px;
        }
        QPushButton {
            background-color: #1abc9c;
            color: #fff;
            border: none;
            padding: 10px;
            border-radius: 5px;
            font-family: 'Verdana';
            font-size: 14px;
            font-weight: bold;
            transition: background 0.2s;
        }
        QPushButton:hover {
            background-color: #16a085;
        }
        QTabWidget::pane {
            border: 1px solid #444;
            border-radius: 5px;
        }
        QTabBar::tab {
            background: #31363b;
            border: 1px solid #444;
            padding: 10px 15px;
            margin: 15px 15px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            font-family: 'Verdana';
            font-size: 15px;
            min-width: 150px;
            color: #f0f0f0;
        }
        QTabBar::tab:selected {
            background: #1abc9c;
            color: #fff;
        }
        QTabBar::tab:!selected {
            background: #31363b;
            color: #bbb;
        }
        QTableView {
            background-color: #31363b;
            color: #f0f0f0;
            gridline-color: #444;
            selection-background-color: #1abc9c;
            selection-color: #fff;
            border-radius: 5px;
            font-family: 'Verdana';
            font-size: 16px;
        }
        QHeaderView::section {
            background-color: #31363b;
            color: #f0f0f0;
            font-family: 'Verdana';
            font-size: 16px;
            border: 1px solid #444;
            padding: 5px;
        }
        QTableCornerButton::section {
            background-color: #31363b;
            border: 1px solid #444;
        }
        QToolTip {
            background-color: #1abc9c;
            color: #fff;
            font-family: 'Verdana';
            font-size: 14px;
            border-radius: 5px;
            padding: 5px;
        }
        QListWidget {
            font-family: 'Verdana';
            font-size: 16px;
        }
        QLabel#StatusLabel {
            background-color: #2c3e50;
            color: white;
            padding: 5px;
        }
        QPushButton#FilterRemove {
    background-color: #e74c3c;
    color: #fff;
    border: none;
    font-weight: bold;
    font-size: 16px;
    border-radius: 10px;
    min-width: 24px;
    min-height: 24px;
    max-width: 24px;
    max-height: 24px;
    padding: 0;
}
QPushButton#FilterRemove:hover {
    background-color: #c0392b;
}
QPushButton#ThemeToggle {
    font-size: 28px;
    border-radius: 8px;
    margin: 0;
    padding: 8px 16px;
    min-width: 64px;
    min-height: 48px;
    max-width: 80px;
    max-height: 64px;
}
        """