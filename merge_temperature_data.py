#!/usr/bin/env python3
"""
Program do łączenia plików CSV z pomiarów temperatury AP Sensing.
Łączy wszystkie pliki CSV z folderu w jeden plik posortowany chronologicznie.
"""

import os
import csv
from datetime import datetime
from pathlib import Path


def parse_datetime(date_str, time_str):
    """
    Parsuje datę i czas z formatu DD.MM.YYYY i HH:MM:SS.

    Args:
        date_str: Data w formacie DD.MM.YYYY
        time_str: Czas w formacie HH:MM:SS

    Returns:
        datetime: Obiekt datetime
    """
    datetime_str = f"{date_str} {time_str}"
    return datetime.strptime(datetime_str, "%d.%m.%Y %H:%M:%S")


def read_csv_file(filepath):
    """
    Wczytuje pojedynczy plik CSV z pomiarami.

    Args:
        filepath: Ścieżka do pliku CSV

    Returns:
        dict: Słownik zawierający:
            - dates: lista dat dla każdej kolumny pomiarów
            - times: lista czasów dla każdej kolumny pomiarów
            - datetimes: lista obiektów datetime dla sortowania
            - positions: lista pozycji (długości) czujnika
            - measurements: lista kolumn z pomiarami
    """
    with open(filepath, 'r', encoding='latin-1') as f:
        reader = csv.reader(f, delimiter=';')

        # Wczytaj pierwsze 4 wiersze nagłówkowe
        date_row = next(reader)
        time_row = next(reader)
        x_units_row = next(reader)
        y_units_row = next(reader)

        # Wyciągnij daty i czasy (pomijając pierwszą kolumnę z etykietami)
        dates = date_row[1:]
        times = time_row[1:]

        # Parsuj datetime dla każdej kolumny
        datetimes = []
        for date, time in zip(dates, times):
            try:
                dt = parse_datetime(date, time)
                datetimes.append(dt)
            except Exception as e:
                print(f"Błąd parsowania daty/czasu w pliku {filepath}: {date} {time}")
                raise e

        # Wczytaj dane pomiarowe
        positions = []
        measurements = [[] for _ in range(len(dates))]

        for row in reader:
            if not row or not row[0]:  # Pomiń puste wiersze
                continue

            # Pierwsza kolumna to pozycja (zamień przecinek na kropkę)
            position = row[0].replace(',', '.')
            positions.append(position)

            # Kolejne kolumny to pomiary (zamień przecinki na kropki, usuń cudzysłowy)
            for i, value in enumerate(row[1:]):
                cleaned_value = value.replace('"', '').replace(',', '.')
                measurements[i].append(cleaned_value)

        return {
            'dates': dates,
            'times': times,
            'datetimes': datetimes,
            'positions': positions,
            'measurements': measurements
        }


def merge_csv_files(input_folder, output_file):
    """
    Łączy wszystkie pliki CSV z folderu w jeden plik posortowany chronologicznie.

    Args:
        input_folder: Ścieżka do folderu z plikami CSV
        output_file: Ścieżka do wyjściowego pliku CSV
    """
    # Znajdź wszystkie pliki CSV
    csv_files = list(Path(input_folder).glob('*.csv'))

    if not csv_files:
        print(f"Nie znaleziono plików CSV w folderze: {input_folder}")
        return

    print(f"Znaleziono {len(csv_files)} plików CSV")

    # Wczytaj wszystkie pliki i zbierz wszystkie pomiary
    all_measurements = []
    reference_positions = None

    for csv_file in csv_files:
        print(f"Przetwarzam: {csv_file.name}")
        data = read_csv_file(csv_file)

        # Sprawdź czy pozycje są takie same we wszystkich plikach
        if reference_positions is None:
            reference_positions = data['positions']
        elif reference_positions != data['positions']:
            print(f"UWAGA: Pozycje w pliku {csv_file.name} różnią się od referencyjnych!")

        # Dodaj każdą kolumnę pomiarów z datą i czasem
        for i, dt in enumerate(data['datetimes']):
            all_measurements.append({
                'datetime': dt,
                'date': data['dates'][i],
                'time': data['times'][i],
                'measurements': data['measurements'][i]
            })

    # Posortuj pomiary chronologicznie
    all_measurements.sort(key=lambda x: x['datetime'])

    print(f"\nŁącznie pomiarów: {len(all_measurements)}")
    print(f"Zakres dat: od {all_measurements[0]['datetime']} do {all_measurements[-1]['datetime']}")

    # Zapisz do pliku wyjściowego
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')

        # Wiersz 1: Daty
        date_row = ['Date:'] + [m['date'] for m in all_measurements]
        writer.writerow(date_row)

        # Wiersz 2: Czasy
        time_row = ['Time:'] + [m['time'] for m in all_measurements]
        writer.writerow(time_row)

        # Wiersz 3: Jednostki X
        x_units_row = ['X Units:'] + ['[m]'] * len(all_measurements)
        writer.writerow(x_units_row)

        # Wiersz 4: Jednostki Y
        y_units_row = ['Y Units:'] + ['[°C]'] * len(all_measurements)
        writer.writerow(y_units_row)

        # Wiersze z danymi pomiarowymi
        for i, position in enumerate(reference_positions):
            row = [position] + [m['measurements'][i] for m in all_measurements]
            writer.writerow(row)

    print(f"\nPlik wyjściowy zapisany: {output_file}")
    print(f"Liczba pozycji pomiarowych: {len(reference_positions)}")
    print(f"Liczba kolumn pomiarowych: {len(all_measurements)}")


def main():
    """Główna funkcja programu."""
    # Ustaw ścieżki
    script_dir = Path(__file__).parent
    input_folder = script_dir / 'csv_data'
    output_file = script_dir / 'merged_temperature_data.csv'

    print("=" * 60)
    print("Program łączenia pomiarów temperatury AP Sensing")
    print("=" * 60)
    print(f"\nFolder wejściowy: {input_folder}")
    print(f"Plik wyjściowy: {output_file}")
    print()

    # Sprawdź czy folder istnieje
    if not input_folder.exists():
        print(f"BŁĄD: Folder {input_folder} nie istnieje!")
        return

    # Połącz pliki
    merge_csv_files(input_folder, output_file)

    print("\nGotowe!")


if __name__ == '__main__':
    main()
