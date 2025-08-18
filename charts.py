import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

# Ustawienia matplotlib dla lepszej jakości
plt.style.use('default')
plt.rcParams.update({
    'font.size': 10,
    'figure.dpi': 100,
    'savefig.dpi': 150,
    'font.family': 'sans-serif'
})

class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Utwórz matplotlib figure
        self.figure = Figure(figsize=(12, 6))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        # Panel przycisków do wyboru typu wykresu
        buttons_layout = QHBoxLayout()
        
        self.chart_buttons = {
            "kierunek_pie": QPushButton("📊 Kierunki (kołowy)"),
            "semestr_bar": QPushButton("📊 Semestry"),
            "tryb_bar": QPushButton("📊 Tryby studiów"),
            "specjalnosc_bar": QPushButton("📊 Specjalności"),
            "combined_stacked": QPushButton("📊 Kierunki/Tryby")
        }
        
        for button_name, button in self.chart_buttons.items():
            button.clicked.connect(lambda checked, name=button_name: self.update_chart(name))
            button.setStyleSheet("QPushButton { padding: 5px 10px; margin: 2px; }")
            buttons_layout.addWidget(button)
        
        self.layout.insertLayout(0, buttons_layout)
        
        # Dane wykresu
        self.chart_data = []
        
    def set_data(self, data):
        """Ustaw dane dla wykresów"""
        self.chart_data = data
        # Domyślnie pokaż wykres kołowy kierunków
        if data:
            self.update_chart("kierunek_pie")
    
    def update_chart(self, chart_type):
        """Aktualizuj wykres na podstawie wybranego typu"""
        if not self.chart_data:
            # Pokaż pusty wykres z komunikatem
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Brak danych do wyświetlenia', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14, alpha=0.5)
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()
            return
            
        # Podświetl aktywny przycisk
        for name, button in self.chart_buttons.items():
            if name == chart_type:
                button.setStyleSheet("QPushButton { background-color: #3498db; color: white; padding: 5px 10px; margin: 2px; }")
            else:
                button.setStyleSheet("QPushButton { padding: 5px 10px; margin: 2px; }")
        
        self.figure.clear()
        
        try:
            if chart_type == "kierunek_pie":
                self.create_kierunek_pie_chart()
            elif chart_type == "semestr_bar":
                self.create_semestr_bar_chart()
            elif chart_type == "tryb_bar":
                self.create_tryb_bar_chart()
            elif chart_type == "specjalnosc_bar":
                self.create_specjalnosc_bar_chart()
            elif chart_type == "combined_stacked":
                self.create_combined_stacked_chart()
        except Exception as e:
            # W przypadku błędu pokaż komunikat
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Błąd generowania wykresu:\n{str(e)}', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, alpha=0.7)
            ax.set_xticks([])
            ax.set_yticks([])
            
        self.canvas.draw()
    
    def create_kierunek_pie_chart(self):
        """Wykres kołowy - rozkład godzin według kierunków (obwarzanek z białymi przerwami)"""
        kierunek_sum = {}
        
        for row in self.chart_data:
            kierunek = row.get("Kierunek", "Nieznany")
            suma = row.get("Suma", 0)
            
            if "SUMA kierunku" in str(row.get("Specjalność", "")):
                continue
            
            try:
                suma = float(suma) if suma else 0
            except (ValueError, TypeError):
                suma = 0
                
            if kierunek not in kierunek_sum:
                kierunek_sum[kierunek] = 0
            kierunek_sum[kierunek] += suma
        
        if not kierunek_sum or all(v == 0 for v in kierunek_sum.values()):
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Brak danych do wyświetlenia w wykresie kołowym', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
            return
            
        ax = self.figure.add_subplot(111)
        
        # Usuń kierunki z zerowymi wartościami
        kierunek_sum = {k: v for k, v in kierunek_sum.items() if v > 0}
        
        labels = list(kierunek_sum.keys())
        sizes = list(kierunek_sum.values())
        total = sum(sizes)
        
        # Generuj kolory
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        # Najpierw rysujemy biały pasek (tworzący efekt obwarzanka)
        wedges, _ = ax.pie([1], radius=0.8, colors=['white'], 
                        wedgeprops=dict(width=0.2, edgecolor='w'))
        
        # Następnie rysujemy właściwy wykres z białymi przerwami
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            autopct=lambda p: f'{p:.1f}%\n({int(p/100*total)}h)' if p > 5 else '',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 10, 'fontweight': 'bold'},
            wedgeprops={'linewidth': 1.5, 'edgecolor': 'white', 'width': 0.6},
            pctdistance=0.85  # Odległość procentów od środka
        )
        
        ax.set_title('Rozkład godzin według kierunków', fontsize=16, fontweight='bold', pad=20)
        
        legend_labels = []
        for label, size in zip(labels, sizes):
            legend_labels.append(f"{label}: {int(size)}h ({size/total*100:.1f}%)")
        
        ax.legend(
            [w for i,w in enumerate(wedges)],
            legend_labels,
            title="Kierunki (godziny)",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=10,
            title_fontsize=12
        )
        
        plt.tight_layout(rect=[0, 0, 0.85, 1])

    
    def create_semestr_bar_chart(self):
        """Wykres słupkowy - porównanie semestrów zimowego i letniego"""
        zimowy_sum = {"stacjonarne": 0, "niestacjonarne": 0}
        letni_sum = {"stacjonarne": 0, "niestacjonarne": 0}
        
        for row in self.chart_data:
            # Pomiń wiersze z sumą kierunku
            if "SUMA kierunku" in str(row.get("Specjalność", "")):
                continue
            
            try:
                zimowy_sum["stacjonarne"] += float(row.get("Zimowy stacjonarne", 0) or 0)
                zimowy_sum["niestacjonarne"] += float(row.get("Zimowy niestacjonarne", 0) or 0)
                letni_sum["stacjonarne"] += float(row.get("Letni stacjonarne", 0) or 0)
                letni_sum["niestacjonarne"] += float(row.get("Letni niestacjonarne", 0) or 0)
            except (ValueError, TypeError):
                continue
        
        ax = self.figure.add_subplot(111)
        
        categories = ['Stacjonarne', 'Niestacjonarne']
        zimowy_values = [zimowy_sum["stacjonarne"], zimowy_sum["niestacjonarne"]]
        letni_values = [letni_sum["stacjonarne"], letni_sum["niestacjonarne"]]
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, zimowy_values, width, label='Semestr zimowy', 
                      color='#3498db', alpha=0.8)
        bars2 = ax.bar(x + width/2, letni_values, width, label='Semestr letni', 
                      color='#e74c3c', alpha=0.8)
        
        ax.set_xlabel('Tryb studiów', fontsize=12)
        ax.set_ylabel('Liczba godzin', fontsize=12)
        ax.set_title('Porównanie godzin według semestrów i trybów', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=10)
        ax.tick_params(axis='y', labelsize=10)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Dodaj etykiety na słupkach
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f'{int(height)}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3),
                               textcoords="offset points",
                               ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
    
    def create_tryb_bar_chart(self):
        """Wykres słupkowy - porównanie trybów stacjonarnych i niestacjonarnych"""
        tryb_sum = {"stacjonarne": 0, "niestacjonarne": 0}
        
        for row in self.chart_data:
            if "SUMA kierunku" in str(row.get("Specjalność", "")):
                continue
            
            try:
                tryb_sum["stacjonarne"] += float(row.get("Zimowy stacjonarne", 0) or 0) + float(row.get("Letni stacjonarne", 0) or 0)
                tryb_sum["niestacjonarne"] += float(row.get("Zimowy niestacjonarne", 0) or 0) + float(row.get("Letni niestacjonarne", 0) or 0)
            except (ValueError, TypeError):
                continue
        
        ax = self.figure.add_subplot(111)
        
        labels = ['Stacjonarne', 'Niestacjonarne']
        values = [tryb_sum["stacjonarne"], tryb_sum["niestacjonarne"]]
        colors = ['#3498db', '#e74c3c']
        
        bars = ax.bar(labels, values, color=colors, alpha=0.8)
        
        ax.set_ylabel('Liczba godzin', fontsize=12) # Zwiększona czcionka
        ax.set_title('Porównanie godzin według trybów studiów', fontsize=16, fontweight='bold') # Zwiększona czcionka nagłówka
        ax.tick_params(axis='x', labelsize=10) # Zwiększona czcionka
        ax.tick_params(axis='y', labelsize=10) # Zwiększona czcionka
        ax.grid(True, alpha=0.3, axis='y')
        
        # Dodaj etykiety na słupkach
        for bar, value in zip(bars, values):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(values)*0.01,
                       f'{int(value)}h', ha='center', va='bottom', fontweight='bold', fontsize=10) # Zwiększona czcionka
        
        plt.tight_layout()
    
    def create_specjalnosc_bar_chart(self):
        """Wykres słupkowy - godziny według specjalności"""
        spec_sum = {}
        
        for row in self.chart_data:
            if "SUMA kierunku" in str(row.get("Specjalność", "")):
                continue
                
            spec = row.get("Specjalność", "Nieznana")
            kierunek = row.get("Kierunek", "Nieznany")
            
            try:
                suma = float(row.get("Suma", 0) or 0)
            except (ValueError, TypeError):
                suma = 0
            
            key = f"{kierunek} - {spec}"  # Zmiana formatu, aby uniknąć nowej linii
            if key not in spec_sum:
                spec_sum[key] = 0
            spec_sum[key] += suma
        
        if not spec_sum or all(v == 0 for v in spec_sum.values()):
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Brak danych do wyświetlenia', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)  # Zwiększona czcionka
            return
            
        ax = self.figure.add_subplot(111)
        
        # Usuń specjalności z zerowymi wartościami i sortuj według wartości
        spec_sum = {k: v for k, v in spec_sum.items() if v > 0}
        sorted_items = sorted(spec_sum.items(), key=lambda x: x[1], reverse=True)
        labels, values = zip(*sorted_items) if sorted_items else ([], [])
        
        # Zwiększenie odstępu między słupkami
        bar_width = 0.4  # Szerokość słupków
        bars = ax.barh(range(len(labels)), values, color=plt.cm.viridis(np.linspace(0, 1, len(labels))), height=bar_width)
        
        ax.set_xlabel('Liczba godzin', fontsize=12)
        ax.set_ylabel('Kierunek / Specjalność', fontsize=12)
        ax.set_title('Godziny według specjalności', fontsize=16, fontweight='bold')
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=9)
        ax.tick_params(axis='x', labelsize=10)
        ax.grid(True, alpha=0.3, axis='x')
        
        for bar, value in zip(bars, values):
            if value > 0:
                ax.text(bar.get_width() + max(values) * 0.01, bar.get_y() + bar.get_height() / 2.,
                    f'{int(value)}', ha='left', va='center', fontsize=9, fontweight='bold')
        
        plt.tight_layout()

    
    def create_combined_stacked_chart(self):
        """Wykres skumulowany - kierunki z podziałem na tryby"""
        kierunek_data = {}
        
        for row in self.chart_data:
            if "SUMA kierunku" in str(row.get("Specjalność", "")):
                continue
                
            kierunek = row.get("Kierunek", "Nieznany")
            if kierunek not in kierunek_data:
                kierunek_data[kierunek] = {
                    "stacjonarne": 0,
                    "niestacjonarne": 0
                }
            
            try:
                kierunek_data[kierunek]["stacjonarne"] += (
                    float(row.get("Zimowy stacjonarne", 0) or 0) + float(row.get("Letni stacjonarne", 0) or 0)
                )
                kierunek_data[kierunek]["niestacjonarne"] += (
                    float(row.get("Zimowy niestacjonarne", 0) or 0) + float(row.get("Letni niestacjonarne", 0) or 0)
                )
            except (ValueError, TypeError):
                continue
        
        if not kierunek_data:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Brak danych do wyświetlenia', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            return
            
        ax = self.figure.add_subplot(111)
        
        kierunki = list(kierunek_data.keys())
        stacjonarne = [kierunek_data[k]["stacjonarne"] for k in kierunki]
        niestacjonarne = [kierunek_data[k]["niestacjonarne"] for k in kierunki]
        
        bars1 = ax.bar(kierunki, stacjonarne, label='Stacjonarne', color='#3498db', alpha=0.8)
        bars2 = ax.bar(kierunki, niestacjonarne, bottom=stacjonarne, 
                      label='Niestacjonarne', color='#e74c3c', alpha=0.8)
        
        ax.set_xlabel('Kierunki', fontsize=12)
        ax.set_ylabel('Liczba godzin', fontsize=12)
        ax.set_title('Rozkład godzin według kierunków i trybów (skumulowany)', fontsize=16, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
        ax.tick_params(axis='y', labelsize=10)
        
        # Dodaj etykiety z sumą
        for i, kierunek in enumerate(kierunki):
            total = stacjonarne[i] + niestacjonarne[i]
            if total > 0:
                ax.text(i, total + max([sum(x) for x in zip(stacjonarne, niestacjonarne)])*0.01,
                       f'{int(total)}', ha='center', va='bottom', fontweight='bold', fontsize=10) # Zwiększona czcionka
        
        plt.tight_layout()