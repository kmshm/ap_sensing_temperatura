# AP Sensing - Procesor Danych Temperatury

Aplikacja GUI do przetwarzania danych z czujników temperatury AP Sensing. Umożliwia łączenie plików CSV, definiowanie czujników i eksport danych.

## Wymagania

- Python 3.6 lub nowszy
- Tkinter (zazwyczaj dołączony do Pythona)

## Instalacja i uruchomienie

### 1. Utwórz środowisko wirtualne (opcjonalne, ale zalecane)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate  # Windows
```

### 2. Uruchom aplikację

```bash
python3 sensor_data_processor.py
```

## Instrukcja użytkowania

### Krok 1: Wczytaj Pliki CSV

1. Kliknij **"📁 Wybierz Pliki CSV"** aby wybrać pojedyncze pliki
   - lub -
2. Kliknij **"📂 Wybierz Folder"** aby wczytać wszystkie pliki CSV z folderu

3. Kliknij **"🔄 Scal Pliki"** aby połączyć wszystkie wybrane pliki

**Wynik:** Pliki zostaną scalone chronologicznie według dat i godzin pomiarów.

### Krok 1b: Wczytaj Dane Referencyjne (Opcjonalne)

1. Przejdź do zakładki **"1b. Dane Referencyjne"**

2. Kliknij **"📁 Wybierz Plik Referencyjny"** i wybierz plik `svws_measurements.csv`

**Informacja:** Plik referencyjny zawiera pomiary z czujników punktowych (CH001, CH002, ...), które służą do kalibracji czujników światłowodowych. Czujniki światłowodowe dobrze pokazują rozkład temperatury, ale mogą mieć błędy w wartościach bezwzględnych. Czujniki punktowe poprawiają dokładność pomiarów.

### Krok 2: Zdefiniuj Czujniki

1. Wprowadź **Nazwę czujnika** (np. "Czujnik_A", "Sonda_1")

2. Podaj **Metr początkowy** (np. 5.0)

3. Podaj **Metr końcowy** (np. 25.0)

4. Zaznacz **Odwróć** jeśli chcesz odwrócić dane tego czujnika

5. **(Opcjonalne)** Wybierz **Kanał referencyjny** (np. CH001) i podaj **Metr czujnika ref.** (pozycja na czujniku światłowodowym, gdzie znajduje się czujnik punktowy)

6. Kliknij **"➕ Dodaj czujnik"**

**Uwaga:** Jeśli podasz wartość, która nie istnieje dokładnie w danych (np. 5.13), aplikacja automatycznie wybierze najbliższą dostępną pozycję (np. 5.00 lub 5.25) i poinformuje Cię o korekcie.

**Powtórz kroki 1-6 dla każdego czujnika, który chcesz zdefiniować.**

### Krok 3: Eksportuj Dane

#### Opcja A: Eksport scalonego pliku

1. Kliknij **"💾 Zapisz scalony plik"**
2. Wybierz lokalizację i nazwę pliku
3. Plik zostanie zapisany **bez wierszy X Units i Y Units**

#### Opcja B: Eksport poszczególnych czujników

1. Wybierz **Folder zapisu** (przycisk "Przeglądaj...")
2. Kliknij **"📊 Eksportuj wszystkie czujniki"**
3. Każdy zdefiniowany czujnik zostanie zapisany jako osobny plik CSV

**Nazwy plików:** Automatycznie generowane na podstawie nazw czujników (np. "Czujnik_A.csv")

## Format plików wyjściowych

### Scalony plik (merged):
```
Date:;01.10.2025;01.10.2025;01.10.2025;...
Time:;08:38:02;08:40:04;08:42:04;...
0.00;14.48;14.64;14.89;...
0.25;13.82;13.89;14.21;...
...
```

### Pliki czujników:
```
Date:;01.10.2025;01.10.2025;01.10.2025;...
Time:;08:38:02;08:40:04;08:42:04;...
Ref_Temp(CH001@5.00m):;14.254;14.250;14.251;...    ← (jeśli dodano dane referencyjne)
Ref_DateTime:;2025-10-01 08:38:00;2025-10-01 08:40:00;...    ← (jeśli dodano dane referencyjne)
5.00;14.48;14.64;14.89;...
5.25;13.82;13.89;14.21;...
...
```
- Tylko wybrany zakres metrów (od metr początkowy do metr końcowy)
- Jeśli zaznaczono "Odwróć", dane są w odwróconej kolejności
- Jeśli wybrano kanał referencyjny, dodawane są 2 dodatkowe wiersze z temperaturą referencyjną i datą/godziną pomiaru

## Funkcje aplikacji

✅ **Automatyczne sortowanie** - Pomiary są sortowane chronologicznie
✅ **Zamiana separatorów** - Przecinki zamieniane na kropki dziesiętne
✅ **Inteligentne dopasowanie** - Automatyczne znajdowanie najbliższych pozycji
✅ **Odwracanie czujników** - Możliwość odwrócenia danych dla wybranych czujników
✅ **Kalibracja referencyjna** - Dodawanie pomiarów z czujników punktowych do weryfikacji temperatury
✅ **Dopasowanie czasowe** - Automatyczne dopasowanie pomiarów referencyjnych do pomiarów światłowodowych
✅ **Batch export** - Eksport wszystkich czujników jednym kliknięciem
✅ **Log eksportu** - Szczegółowy log wszystkich operacji eksportu
✅ **Intuicyjny interfejs** - Prosty 3-krokowy proces

## Przykładowe zastosowanie

### Scenariusz: 3 czujniki w pętli

Masz 3 czujniki o długościach 20m każdy, połączone w pętlę:

1. **Czujnik A**: 0m - 20m (normalny)
2. **Czujnik B**: 20m - 40m (odwrócony - kablem powrotnym)
3. **Czujnik C**: 40m - 60m (normalny)

**Konfiguracja w aplikacji:**

| Nazwa | Metr początkowy | Metr końcowy | Odwróć |
|-------|----------------|--------------|--------|
| Czujnik_A | 0 | 20 | NIE |
| Czujnik_B | 20 | 40 | TAK |
| Czujnik_C | 40 | 60 | NIE |

Po eksporcie otrzymasz 3 pliki:
- `Czujnik_A.csv` - dane od 0m do 20m
- `Czujnik_B.csv` - dane od 40m do 20m (odwrócone)
- `Czujnik_C.csv` - dane od 40m do 60m

## Rozwiązywanie problemów

### Aplikacja się nie uruchamia

**Problem:** `ModuleNotFoundError: No module named 'tkinter'`

**Rozwiązanie:** Zainstaluj Tkinter:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (zazwyczaj już zainstalowany)
brew install python-tk
```

### Błąd kodowania

**Problem:** `UnicodeDecodeError`

**Rozwiązanie:** Aplikacja automatycznie używa kodowania `latin-1` dla plików CSV. Jeśli problem występuje, sprawdź czy pliki są prawidłowymi plikami CSV.

### Nie ma mojej dokładnej pozycji

**To normalne!** Aplikacja automatycznie wybiera najbliższą dostępną pozycję. Dane są zapisywane co 0.25m, więc jeśli podasz np. 5.13m, aplikacja użyje 5.00m lub 5.25m (w zależności która jest bliżej).

## Autor

Aplikacja stworzona do przetwarzania danych z reflektometru AP Sensing.

## Licencja

Do użytku wewnętrznego.
