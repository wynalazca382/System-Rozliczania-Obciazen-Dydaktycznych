# Aplikacja wspierająca planowanie obciążeń dydaktycznych w systemie USOS

## Opis Projektu

Niniejszy projekt inżynierski stanowi implementację aplikacji desktopowej, której głównym celem jest **usprawnienie i automatyzacja procesu planowania oraz rozliczania obciążeń dydaktycznych (pensum) dla pracowników naukowych w środowisku akademickim**, w oparciu o dane z systemu **USOS (Uniwersytecki System Obsługi Studiów)**.

Aplikacja ma za zadanie zminimalizować czas i ryzyko błędów związane z manualnym przeliczaniem pensum, oferując intuicyjny interfejs do przeglądania danych o pracownikach i zajęciach, automatycznego obliczania obciążeń dydaktycznych oraz generowania szczegółowych raportów. Projekt koncentruje się na efektywnym dostępie do danych z bazy USOS oraz ich przetwarzaniu w celu wsparcia procesów administracyjnych na uczelni.

## Funkcjonalności

Aplikacja oferuje następujące kluczowe funkcjonalności:

* **Logowanie użytkownika:** Bezpieczne uwierzytelnianie dostępu do aplikacji.
* **Przeglądanie i filtrowanie danych o pracownikach:** Szybki dostęp do listy pracowników z możliwością wyszukiwania i filtrowania według różnych kryteriów (np. nazwisko, jednostka organizacyjna).
* **Wyświetlanie szczegółów zajęć:** Prezentacja zajęć dydaktycznych przypisanych do poszczególnych pracowników, pobieranych z systemu USOS.
* **Automatyczne obliczanie pensum dydaktycznego:** Kalkulacja obciążeń dydaktycznych na podstawie danych o zajęciach i zdefiniowanej logiki przeliczania godzin na punkty pensum.
* **Generowanie raportów:** Tworzenie szczegółowych raportów z obciążeń dydaktycznych w formacie [NP. XLSX (Microsoft Excel)], ułatwiających rozliczanie i archiwizację.
* **Mechanizmy filtrowania i sortowania danych:** Umożliwienie dynamicznego przeglądania danych w tabelach.
* **Intuicyjny interfejs użytkownika:** Zaprojektowany z myślą o prostocie i efektywności obsługi.

## Wymagania Systemowe

Aby uruchomić aplikację, wymagane są następujące komponenty:

* **System Operacyjny:** Windows 10/11 (aplikacja desktopowa)
* **Python:** Wersja 3.x (zalecana 3.8+)
* **Dostęp do bazy danych Oracle:** Aplikacja łączy się z bazą danych USOS (Oracle Database). Wymagane są odpowiednie uprawnienia dostępu do danych oraz dostęp sieciowy.

## Instalacja i Uruchomienie

Poniższe kroki opisują proces instalacji i uruchomienia aplikacji.

### Klonowanie Repozytorium

```bash
git clone https://github.com/wynalazca382/System-Rozliczania-Obciazen-Dydaktycznych
cd System-Rozliczania-Obciazen-Dydaktycznych
```
Tworzenie Wirtualnego Środowiska i Instalacja Zależności
Zaleca się użycie wirtualnego środowiska, aby uniknąć konfliktów zależności.


```bash
python -m venv venv
# Aktywacja wirtualnego środowiska
# Na Windows:
.\venv\Scripts\activate
# Na macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

```
Konfiguracja Połączenia z Bazą Danych USOS
Aplikacja wymaga dostępu do bazy danych Oracle, w której przechowywane są dane USOS. Szczegóły konfiguracji połączenia powinny być umieszczone w pliku config.py (lub podobnym) zgodnie z dokumentacją Oracle.

Uruchomienie Aplikacji
Po zainstalowaniu zależności i skonfigurowaniu połączenia z bazą danych, aplikację można uruchomić za pomocą pliku main.py:
```bash
python main.py
```
Zastosowane Technologie
Projekt został zrealizowany z wykorzystaniem następujących technologii:

## Zastosowane Technologie

Projekt został zrealizowany z wykorzystaniem następujących technologii:

* **Język Programowania:** Python 3.x
* **Framework GUI:** PyQt5
* **Object-Relational Mapper (ORM):** SQLAlchemy
* **Baza Danych:** Oracle Database (USOS)
* **Sterownik Bazy Danych:** cx_Oracle (lub `python-oracledb`, w zależności od tego, którego używasz)
* **Generowanie raportów:** xlsxwriter

## Wspierana Baza Danych

Aplikacja jest zaprojektowana do współpracy z bazą danych **Oracle Database**, na której pracuje system USOS. Wszystkie operacje odczytu danych odbywają się z tej bazy, zapewniając spójność z oficjalnymi danymi uczelni.

## Autor

* **Imię i Nazwisko:** Łukasz Gajewski
* **Kierunek Studiów:** Informatyka, Akademia Nauk Stosowanych w Elblągu
* **Opiekun Pracy:** dr inż. Jerzy Buriak
