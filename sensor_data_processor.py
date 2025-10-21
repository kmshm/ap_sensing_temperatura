#!/usr/bin/env python3
"""
Aplikacja GUI do przetwarzania danych z czujników temperatury AP Sensing.
Umożliwia wczytywanie plików CSV, łączenie ich, definiowanie czujników i eksport danych.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import csv
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path


class SensorDataProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("AP Sensing - Procesor Danych Temperatury")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)

        # Dane aplikacji
        self.input_files = []
        self.merged_data = None
        self.positions = []
        self.sensors = []
        self.reference_data = None  # Dane z pliku svws_measurements.csv
        self.reference_channels = []  # Lista dostępnych kanałów (CH001, CH002, ...)

        # Konfiguracja stylów
        self.setup_styles()

        # Tworzenie interfejsu
        self.create_widgets()

    def setup_styles(self):
        """Konfiguracja stylów wizualnych."""
        style = ttk.Style()
        style.theme_use('clam')

        # Kolory
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'),
                       foreground='#2c3e50', padding=10)
        style.configure('Title.TLabel', font=('Arial', 11, 'bold'),
                       foreground='#34495e')
        style.configure('Info.TLabel', font=('Arial', 9),
                       foreground='#7f8c8d')
        style.configure('Success.TLabel', font=('Arial', 9),
                       foreground='#27ae60')
        style.configure('Action.TButton', font=('Arial', 10),
                       padding=8)

    def create_widgets(self):
        """Tworzy wszystkie elementy interfejsu."""
        # Główny kontener
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(2, weight=1)

        # Nagłówek
        header = ttk.Label(main_container,
                          text="🌡️ AP Sensing - Procesor Danych Temperatury",
                          style='Header.TLabel')
        header.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # Notebook (zakładki)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Zakładka 1: Wczytywanie plików
        self.tab1 = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab1, text="1. Wczytaj Pliki")
        self.create_tab1()

        # Zakładka 1b: Wczytywanie danych referencyjnych
        self.tab1b = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab1b, text="1b. Dane Referencyjne")
        self.create_tab1b()

        # Zakładka 2: Definicja czujników
        self.tab2 = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab2, text="2. Zdefiniuj Czujniki")
        self.create_tab2()

        # Zakładka 3: Eksport
        self.tab3 = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab3, text="3. Eksportuj Dane")
        self.create_tab3()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Gotowy do pracy")
        status_bar = ttk.Label(main_container, textvariable=self.status_var,
                              style='Info.TLabel', relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

    def create_tab1(self):
        """Zakładka wczytywania plików."""
        # Instrukcja
        instruction = ttk.Label(self.tab1,
                               text="Krok 1: Wybierz pliki CSV z pomiarami",
                               style='Title.TLabel')
        instruction.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Przyciski
        btn_frame = ttk.Frame(self.tab1)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)

        self.btn_select = ttk.Button(btn_frame, text="📁 Wybierz Pliki CSV",
                                     command=self.select_files, style='Action.TButton')
        self.btn_select.grid(row=0, column=0, padx=(0, 10))

        self.btn_select_folder = ttk.Button(btn_frame, text="📂 Wybierz Folder",
                                           command=self.select_folder, style='Action.TButton')
        self.btn_select_folder.grid(row=0, column=1, padx=(0, 10))

        self.btn_merge = ttk.Button(btn_frame, text="🔄 Scal Pliki",
                                   command=self.merge_files, style='Action.TButton',
                                   state=tk.DISABLED)
        self.btn_merge.grid(row=0, column=2)

        # Lista plików
        list_label = ttk.Label(self.tab1, text="Wybrane pliki:", style='Title.TLabel')
        list_label.grid(row=2, column=0, sticky=tk.W, pady=(15, 5))

        # Frame dla listy z scrollbarem
        list_frame = ttk.Frame(self.tab1)
        list_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.file_listbox = tk.Listbox(list_frame, height=10, font=('Arial', 9))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                 command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)

        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Informacje o scaleniu
        self.merge_info = ttk.Label(self.tab1, text="", style='Success.TLabel')
        self.merge_info.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        # Konfiguracja rozciągania
        self.tab1.columnconfigure(0, weight=1)
        self.tab1.rowconfigure(3, weight=1)

    def create_tab1b(self):
        """Zakładka wczytywania danych referencyjnych."""
        # Instrukcja
        instruction = ttk.Label(self.tab1b,
                               text="Krok 1b: Wczytaj plik z pomiarami referencyjnymi (svws_measurements.csv)",
                               style='Title.TLabel')
        instruction.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Opis
        description = ttk.Label(self.tab1b,
                               text="Plik zawiera pomiary z czujników punktowych, które służą do kalibracji czujników światłowodowych.",
                               style='Info.TLabel')
        description.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))

        # Przyciski
        btn_frame = ttk.Frame(self.tab1b)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

        self.btn_select_reference = ttk.Button(btn_frame, text="📁 Wybierz Plik Referencyjny",
                                              command=self.select_reference_file,
                                              style='Action.TButton')
        self.btn_select_reference.grid(row=0, column=0, padx=(0, 10))

        # Informacja o wczytanym pliku
        self.reference_info = ttk.Label(self.tab1b, text="Nie wczytano pliku referencyjnego",
                                       style='Info.TLabel')
        self.reference_info.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(15, 5))

        # Lista dostępnych kanałów
        channels_label = ttk.Label(self.tab1b, text="Dostępne kanały:", style='Title.TLabel')
        channels_label.grid(row=4, column=0, sticky=tk.W, pady=(15, 5))

        # Frame dla listy kanałów
        channels_frame = ttk.Frame(self.tab1b)
        channels_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        channels_frame.columnconfigure(0, weight=1)
        channels_frame.rowconfigure(0, weight=1)

        self.channels_listbox = tk.Listbox(channels_frame, height=10, font=('Arial', 9))
        scrollbar = ttk.Scrollbar(channels_frame, orient=tk.VERTICAL,
                                 command=self.channels_listbox.yview)
        self.channels_listbox.configure(yscrollcommand=scrollbar.set)

        self.channels_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Konfiguracja rozciągania
        self.tab1b.columnconfigure(0, weight=1)
        self.tab1b.rowconfigure(5, weight=1)

    def create_tab2(self):
        """Zakładka definiowania czujników."""
        # Instrukcja
        instruction = ttk.Label(self.tab2,
                               text="Krok 2: Zdefiniuj czujniki (nazwa, metr początkowy, metr końcowy)",
                               style='Title.TLabel')
        instruction.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))

        # Formularz dodawania czujnika
        form_frame = ttk.LabelFrame(self.tab2, text="Dodaj nowy czujnik", padding="10")
        form_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(form_frame, text="Nazwa czujnika:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.sensor_name = ttk.Entry(form_frame, width=20)
        self.sensor_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Metr początkowy:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.sensor_start = ttk.Entry(form_frame, width=10)
        self.sensor_start.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form_frame, text="Metr końcowy:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.sensor_end = ttk.Entry(form_frame, width=10)
        self.sensor_end.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(form_frame, text="Odwróć:").grid(row=0, column=6, sticky=tk.W, padx=5)
        self.sensor_reverse = tk.BooleanVar()
        ttk.Checkbutton(form_frame, variable=self.sensor_reverse).grid(row=0, column=7, padx=5)

        # Drugi wiersz - dane referencyjne (opcjonalne)
        ttk.Label(form_frame, text="Kanał referencyjny (opcjonalnie):").grid(row=1, column=0,
                                                                              sticky=tk.W, padx=5, pady=5)
        self.sensor_ref_channel = ttk.Combobox(form_frame, width=18, state='readonly')
        self.sensor_ref_channel.grid(row=1, column=1, padx=5, pady=5)
        self.sensor_ref_channel['values'] = ['Brak']
        self.sensor_ref_channel.current(0)

        ttk.Label(form_frame, text="Metr czujnika ref.:").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.sensor_ref_position = ttk.Entry(form_frame, width=10)
        self.sensor_ref_position.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(form_frame, text="➕ Dodaj czujnik",
                  command=self.add_sensor, style='Action.TButton').grid(row=1, column=4, columnspan=2, padx=10, pady=5)

        # Lista czujników
        list_label = ttk.Label(self.tab2, text="Zdefiniowane czujniki:", style='Title.TLabel')
        list_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 5))

        # Treeview dla listy czujników
        tree_frame = ttk.Frame(self.tab2)
        tree_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = ('name', 'start', 'end', 'reversed', 'ref_channel', 'ref_position')
        self.sensor_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)

        self.sensor_tree.heading('name', text='Nazwa')
        self.sensor_tree.heading('start', text='Metr początkowy')
        self.sensor_tree.heading('end', text='Metr końcowy')
        self.sensor_tree.heading('reversed', text='Odwrócony')
        self.sensor_tree.heading('ref_channel', text='Kanał ref.')
        self.sensor_tree.heading('ref_position', text='Pozycja ref.')

        self.sensor_tree.column('name', width=150)
        self.sensor_tree.column('start', width=100)
        self.sensor_tree.column('end', width=100)
        self.sensor_tree.column('reversed', width=80)
        self.sensor_tree.column('ref_channel', width=80)
        self.sensor_tree.column('ref_position', width=90)

        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                                       command=self.sensor_tree.yview)
        self.sensor_tree.configure(yscrollcommand=tree_scrollbar.set)

        self.sensor_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Przycisk usuwania
        ttk.Button(self.tab2, text="🗑️ Usuń wybrany czujnik",
                  command=self.remove_sensor, style='Action.TButton').grid(row=4, column=0,
                                                                           sticky=tk.W, pady=10)

        # Informacja o zakresie danych
        self.range_info = ttk.Label(self.tab2, text="", style='Info.TLabel')
        self.range_info.grid(row=5, column=0, columnspan=4, sticky=tk.W)

        # Konfiguracja rozciągania
        self.tab2.columnconfigure(0, weight=1)
        self.tab2.rowconfigure(3, weight=1)

    def create_tab3(self):
        """Zakładka eksportu danych."""
        # Instrukcja
        instruction = ttk.Label(self.tab3,
                               text="Krok 3: Eksportuj dane do plików CSV",
                               style='Title.TLabel')
        instruction.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # Opcje eksportu
        export_frame = ttk.LabelFrame(self.tab3, text="Opcje eksportu", padding="10")
        export_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(export_frame, text="Folder zapisu:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.export_path = tk.StringVar()
        self.export_path.set(str(Path.cwd()))

        ttk.Entry(export_frame, textvariable=self.export_path, width=50).grid(row=0, column=1,
                                                                              padx=5, pady=5)
        ttk.Button(export_frame, text="Przeglądaj...",
                  command=self.select_export_folder).grid(row=0, column=2, padx=5)

        # Przyciski eksportu
        btn_frame = ttk.Frame(self.tab3)
        btn_frame.grid(row=2, column=0, sticky=tk.W, pady=10)

        self.btn_export_merged = ttk.Button(btn_frame,
                                           text="💾 Zapisz scalony plik",
                                           command=self.export_merged,
                                           style='Action.TButton',
                                           state=tk.DISABLED)
        self.btn_export_merged.grid(row=0, column=0, padx=(0, 10))

        self.btn_export_sensors = ttk.Button(btn_frame,
                                            text="📊 Eksportuj wszystkie czujniki",
                                            command=self.export_all_sensors,
                                            style='Action.TButton',
                                            state=tk.DISABLED)
        self.btn_export_sensors.grid(row=0, column=1)

        # Log eksportu
        log_label = ttk.Label(self.tab3, text="Log eksportu:", style='Title.TLabel')
        log_label.grid(row=3, column=0, sticky=tk.W, pady=(15, 5))

        self.export_log = scrolledtext.ScrolledText(self.tab3, height=15, width=80,
                                                    font=('Courier', 9))
        self.export_log.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Konfiguracja rozciągania
        self.tab3.columnconfigure(0, weight=1)
        self.tab3.rowconfigure(4, weight=1)

    def select_reference_file(self):
        """Wybór pliku referencyjnego."""
        file = filedialog.askopenfilename(
            title="Wybierz plik referencyjny (svws_measurements.csv)",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file:
            try:
                self.load_reference_data(file)
            except Exception as e:
                messagebox.showerror("Błąd", f"Błąd podczas wczytywania pliku referencyjnego:\n{str(e)}")

    def load_reference_data(self, filepath):
        """Wczytuje dane referencyjne z pliku CSV."""
        with open(filepath, 'r', encoding='latin-1') as f:
            reader = csv.reader(f, delimiter=';')
            header = next(reader)

            # Znajdź kolumny z kanałami (CHxxx_temp_val_c)
            channels = {}
            channel_names = []

            for idx, col_name in enumerate(header):
                if '_temp_val_c' in col_name:
                    channel = col_name.split('_')[0]  # np. CH001
                    channels[channel] = idx
                    channel_names.append(channel)

            # Wczytaj wszystkie wiersze
            measurements = []
            for row in reader:
                if not row or not row[0]:
                    continue

                # Parsuj timestamp (UTC) i konwertuj na czas lokalny
                timestamp_str = row[0]
                try:
                    # Timestamp w pliku jest w UTC
                    timestamp_utc = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    # Dodaj informację o UTC
                    timestamp_utc = timestamp_utc.replace(tzinfo=timezone.utc)
                    # Konwertuj na czas lokalny
                    timestamp_local = timestamp_utc.astimezone()
                    # Format dla wyświetlania (bez strefy czasowej)
                    timestamp_local_str = timestamp_local.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    continue

                # Zbierz wartości temperatur dla każdego kanału
                temps = {}
                for channel, idx in channels.items():
                    try:
                        temp_val = float(row[idx].replace('"', ''))
                        temps[channel] = temp_val
                    except:
                        temps[channel] = None

                measurements.append({
                    'timestamp': timestamp_local.replace(tzinfo=None),  # Dla porównania bez tzinfo
                    'timestamp_str': timestamp_local_str,  # Już w czasie lokalnym
                    'temperatures': temps
                })

            # Sortuj chronologicznie (powinny być już posortowane, ale dla pewności)
            measurements.sort(key=lambda x: x['timestamp'])

            self.reference_data = {
                'channels': channel_names,
                'measurements': measurements
            }
            self.reference_channels = channel_names

            # Aktualizuj UI
            self.reference_info.config(text=f"✓ Wczytano {len(measurements)} pomiarów referencyjnych | "
                                           f"Kanały: {', '.join(channel_names)}")

            self.channels_listbox.delete(0, tk.END)
            for channel in channel_names:
                self.channels_listbox.insert(tk.END, channel)

            # Aktualizuj combobox w formularzu czujnika
            self.sensor_ref_channel['values'] = ['Brak'] + channel_names

            self.status_var.set("Dane referencyjne wczytane pomyślnie!")

    def select_files(self):
        """Wybór pojedynczych plików CSV."""
        files = filedialog.askopenfilenames(
            title="Wybierz pliki CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if files:
            self.input_files = list(files)
            self.update_file_list()

    def select_folder(self):
        """Wybór folderu z plikami CSV."""
        folder = filedialog.askdirectory(title="Wybierz folder z plikami CSV")
        if folder:
            csv_files = list(Path(folder).glob("*.csv"))
            self.input_files = [str(f) for f in csv_files]
            self.update_file_list()

    def update_file_list(self):
        """Aktualizuje listę wybranych plików."""
        self.file_listbox.delete(0, tk.END)
        for file in self.input_files:
            self.file_listbox.insert(tk.END, Path(file).name)

        if self.input_files:
            self.btn_merge.config(state=tk.NORMAL)
            self.status_var.set(f"Wybrano {len(self.input_files)} plików")
        else:
            self.btn_merge.config(state=tk.DISABLED)

    def parse_datetime(self, date_str, time_str):
        """Parsuje datę i czas."""
        datetime_str = f"{date_str} {time_str}"
        return datetime.strptime(datetime_str, "%d.%m.%Y %H:%M:%S")

    def read_csv_file(self, filepath):
        """Wczytuje pojedynczy plik CSV."""
        with open(filepath, 'r', encoding='latin-1') as f:
            reader = csv.reader(f, delimiter=';')

            date_row = next(reader)
            time_row = next(reader)
            x_units_row = next(reader)  # Pomijamy
            y_units_row = next(reader)  # Pomijamy

            dates = date_row[1:]
            times = time_row[1:]

            datetimes = []
            for date, time in zip(dates, times):
                dt = self.parse_datetime(date, time)
                datetimes.append(dt)

            positions = []
            measurements = [[] for _ in range(len(dates))]

            for row in reader:
                if not row or not row[0]:
                    continue

                position = row[0].replace(',', '.')
                positions.append(float(position))

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

    def merge_files(self):
        """Scala wszystkie wybrane pliki."""
        if not self.input_files:
            messagebox.showwarning("Ostrzeżenie", "Nie wybrano żadnych plików!")
            return

        self.status_var.set("Scalanie plików...")
        self.root.update()

        try:
            all_measurements = []
            reference_positions = None

            for csv_file in self.input_files:
                data = self.read_csv_file(csv_file)

                if reference_positions is None:
                    reference_positions = data['positions']
                    self.positions = reference_positions

                for i, dt in enumerate(data['datetimes']):
                    all_measurements.append({
                        'datetime': dt,
                        'date': data['dates'][i],
                        'time': data['times'][i],
                        'measurements': data['measurements'][i]
                    })

            # Sortuj chronologicznie
            all_measurements.sort(key=lambda x: x['datetime'])

            self.merged_data = {
                'positions': reference_positions,
                'measurements': all_measurements
            }

            # Aktualizuj interfejs
            info_text = (f"✓ Scalono pomyślnie!\n"
                        f"Plików: {len(self.input_files)} | "
                        f"Pomiarów: {len(all_measurements)} | "
                        f"Pozycji: {len(reference_positions)} | "
                        f"Zakres: {reference_positions[0]:.2f}m - {reference_positions[-1]:.2f}m")
            self.merge_info.config(text=info_text)

            self.range_info.config(text=f"Dostępny zakres danych: {reference_positions[0]:.2f}m - {reference_positions[-1]:.2f}m (co 0.25m)")

            self.btn_export_merged.config(state=tk.NORMAL)
            self.status_var.set("Pliki scalone pomyślnie!")

            # Przejdź do następnej zakładki
            self.notebook.select(1)

        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas scalania plików:\n{str(e)}")
            self.status_var.set("Błąd podczas scalania")

    def find_nearest_position(self, target):
        """Znajduje najbliższą dostępną pozycję."""
        if not self.positions:
            return None

        target_float = float(target)
        nearest = min(self.positions, key=lambda x: abs(x - target_float))
        return nearest

    def add_sensor(self):
        """Dodaje nowy czujnik do listy."""
        if not self.merged_data:
            messagebox.showwarning("Ostrzeżenie", "Najpierw scal pliki!")
            return

        name = self.sensor_name.get().strip()
        start = self.sensor_start.get().strip()
        end = self.sensor_end.get().strip()
        reverse = self.sensor_reverse.get()
        ref_channel = self.sensor_ref_channel.get()
        ref_position = self.sensor_ref_position.get().strip()

        if not name or not start or not end:
            messagebox.showwarning("Ostrzeżenie", "Wypełnij wszystkie pola podstawowe!")
            return

        # Sprawdź czy podano dane referencyjne
        if ref_channel != 'Brak' and not ref_position:
            messagebox.showwarning("Ostrzeżenie", "Podaj metr czujnika referencyjnego!")
            return

        if ref_channel != 'Brak' and not self.reference_data:
            messagebox.showwarning("Ostrzeżenie", "Najpierw wczytaj plik referencyjny!")
            return

        try:
            # Znajdź najbliższe pozycje
            start_nearest = self.find_nearest_position(start)
            end_nearest = self.find_nearest_position(end)

            if start_nearest is None or end_nearest is None:
                messagebox.showerror("Błąd", "Nie można znaleźć pozycji!")
                return

            # Przygotuj dane czujnika
            sensor = {
                'name': name,
                'start': start_nearest,
                'end': end_nearest,
                'reversed': reverse,
                'ref_channel': None if ref_channel == 'Brak' else ref_channel,
                'ref_position': None
            }

            # Jeśli podano dane referencyjne, znajdź najbliższą pozycję
            if ref_channel != 'Brak':
                ref_position_nearest = self.find_nearest_position(ref_position)
                sensor['ref_position'] = ref_position_nearest

            self.sensors.append(sensor)

            # Dodaj do treeview
            reverse_text = "TAK" if reverse else "NIE"
            ref_channel_text = ref_channel if ref_channel != 'Brak' else '-'
            ref_position_text = f"{sensor['ref_position']:.2f}m" if sensor['ref_position'] is not None else '-'

            self.sensor_tree.insert('', tk.END, values=(name, f"{start_nearest:.2f}m",
                                                       f"{end_nearest:.2f}m", reverse_text,
                                                       ref_channel_text, ref_position_text))

            # Wyczyść pola
            self.sensor_name.delete(0, tk.END)
            self.sensor_start.delete(0, tk.END)
            self.sensor_end.delete(0, tk.END)
            self.sensor_reverse.set(False)
            self.sensor_ref_channel.current(0)
            self.sensor_ref_position.delete(0, tk.END)

            self.btn_export_sensors.config(state=tk.NORMAL)
            self.status_var.set(f"Dodano czujnik: {name}")

            # Pokaż info jeśli wartości zostały skorygowane
            corrections = []
            if float(start) != start_nearest:
                corrections.append(f"Start: {start} → {start_nearest:.2f}m")
            if float(end) != end_nearest:
                corrections.append(f"Koniec: {end} → {end_nearest:.2f}m")
            if ref_position and float(ref_position) != sensor['ref_position']:
                corrections.append(f"Pozycja ref.: {ref_position} → {sensor['ref_position']:.2f}m")

            if corrections:
                messagebox.showinfo("Informacja",
                                  f"Skorygowano pozycje do najbliższych dostępnych:\n" +
                                  "\n".join(corrections))

        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawne wartości liczbowe dla metrów!")

    def remove_sensor(self):
        """Usuwa wybrany czujnik."""
        selected = self.sensor_tree.selection()
        if not selected:
            messagebox.showwarning("Ostrzeżenie", "Wybierz czujnik do usunięcia!")
            return

        index = self.sensor_tree.index(selected[0])
        self.sensor_tree.delete(selected[0])
        del self.sensors[index]

        self.status_var.set("Usunięto czujnik")

    def select_export_folder(self):
        """Wybór folderu do eksportu."""
        folder = filedialog.askdirectory(title="Wybierz folder zapisu")
        if folder:
            self.export_path.set(folder)

    def export_merged(self):
        """Eksportuje scalony plik."""
        if not self.merged_data:
            messagebox.showwarning("Ostrzeżenie", "Brak danych do eksportu!")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="merged_temperature_data.csv"
        )

        if not filepath:
            return

        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';')

                # Wiersz dat
                date_row = ['Date:'] + [m['date'] for m in self.merged_data['measurements']]
                writer.writerow(date_row)

                # Wiersz czasów
                time_row = ['Time:'] + [m['time'] for m in self.merged_data['measurements']]
                writer.writerow(time_row)

                # Dane pomiarowe
                for i, position in enumerate(self.merged_data['positions']):
                    row = [f"{position:.2f}"] + [m['measurements'][i]
                                                 for m in self.merged_data['measurements']]
                    writer.writerow(row)

            self.log_export(f"✓ Zapisano scalony plik: {Path(filepath).name}")
            messagebox.showinfo("Sukces", f"Plik zapisany:\n{filepath}")
            self.status_var.set("Eksport zakończony pomyślnie")

        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas eksportu:\n{str(e)}")

    def export_all_sensors(self):
        """Eksportuje wszystkie zdefiniowane czujniki."""
        if not self.sensors:
            messagebox.showwarning("Ostrzeżenie", "Brak zdefiniowanych czujników!")
            return

        export_dir = self.export_path.get()
        if not os.path.exists(export_dir):
            messagebox.showerror("Błąd", "Wybrany folder nie istnieje!")
            return

        try:
            for sensor in self.sensors:
                self.export_single_sensor(sensor, export_dir)

            self.log_export(f"\n{'='*60}")
            self.log_export(f"✓ Wyeksportowano wszystkie czujniki ({len(self.sensors)} sztuk)")
            self.log_export(f"Lokalizacja: {export_dir}")

            messagebox.showinfo("Sukces",
                              f"Wyeksportowano {len(self.sensors)} czujników\n"
                              f"do folderu:\n{export_dir}")
            self.status_var.set(f"Wyeksportowano {len(self.sensors)} czujników")

            # Przejdź do zakładki eksportu
            self.notebook.select(2)

        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas eksportu czujników:\n{str(e)}")

    def find_reference_temperature(self, measurement_datetime, channel):
        """
        Znajduje najbliższy pomiar referencyjny dla danej daty/godziny i kanału.
        Zwraca (temperature, ref_datetime_str) lub (None, None) jeśli nie znaleziono.
        """
        if not self.reference_data or channel not in self.reference_data['channels']:
            return None, None

        # Znajdź najbliższy pomiar w czasie
        min_diff = None
        best_measurement = None

        for ref_measurement in self.reference_data['measurements']:
            time_diff = abs((ref_measurement['timestamp'] - measurement_datetime).total_seconds())
            if min_diff is None or time_diff < min_diff:
                min_diff = time_diff
                best_measurement = ref_measurement

        if best_measurement and best_measurement['temperatures'][channel] is not None:
            return best_measurement['temperatures'][channel], best_measurement['timestamp_str']
        else:
            return None, None

    def export_single_sensor(self, sensor, export_dir):
        """Eksportuje dane pojedynczego czujnika."""
        # Znajdź indeksy pozycji
        positions = self.merged_data['positions']

        start_idx = positions.index(sensor['start'])
        end_idx = positions.index(sensor['end'])

        # Upewnij się że start < end
        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx

        # Wyciągnij fragment
        sensor_positions = positions[start_idx:end_idx+1]

        # Jeśli odwrócony, odwróć pozycje
        if sensor['reversed']:
            sensor_positions = sensor_positions[::-1]

        # Nazwa pliku
        filename = f"{sensor['name'].replace(' ', '_')}.csv"
        filepath = os.path.join(export_dir, filename)

        # Jeśli czujnik ma dane referencyjne, przygotuj je
        ref_temps = []
        ref_datetimes = []
        offsets = []  # Offset dla każdego pomiaru
        has_reference = sensor['ref_channel'] is not None and sensor['ref_position'] is not None

        if has_reference:
            # Znajdź indeks pozycji czujnika referencyjnego
            ref_position_idx = positions.index(sensor['ref_position'])

            # Dla każdego pomiaru światłowodowego znajdź odpowiedni pomiar referencyjny
            for measurement in self.merged_data['measurements']:
                ref_temp, ref_datetime = self.find_reference_temperature(
                    measurement['datetime'],
                    sensor['ref_channel']
                )
                ref_temps.append(ref_temp if ref_temp is not None else '')
                ref_datetimes.append(ref_datetime if ref_datetime is not None else '')

                # Oblicz offset (różnica między temperaturą referencyjną a światłowodową)
                if ref_temp is not None:
                    try:
                        fiber_temp_at_ref_position = float(measurement['measurements'][ref_position_idx])
                        offset = ref_temp - fiber_temp_at_ref_position
                        offsets.append(offset)
                    except:
                        offsets.append(0.0)
                else:
                    offsets.append(0.0)

        # Zapisz do pliku
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=';')

            # Wiersz dat
            date_row = ['Date:'] + [m['date'] for m in self.merged_data['measurements']]
            writer.writerow(date_row)

            # Wiersz czasów
            time_row = ['Time:'] + [m['time'] for m in self.merged_data['measurements']]
            writer.writerow(time_row)

            # Jeśli są dane referencyjne, dodaj wiersze
            if has_reference:
                # Wiersz z temperaturą referencyjną
                ref_temp_row = [f'Ref_Temp({sensor["ref_channel"]}@{sensor["ref_position"]:.2f}m):'] + ref_temps
                writer.writerow(ref_temp_row)

                # Wiersz z datą/godziną referencyjną
                ref_datetime_row = ['Ref_DateTime:'] + ref_datetimes
                writer.writerow(ref_datetime_row)

            # Dane pomiarowe
            if sensor['reversed']:
                # Odwrócone dane
                for i in range(len(sensor_positions)):
                    original_idx = end_idx - i
                    position = sensor_positions[i]

                    # Zastosuj offset jeśli są dane referencyjne
                    if has_reference:
                        row = [f"{position:.2f}"]
                        for j, m in enumerate(self.merged_data['measurements']):
                            try:
                                calibrated_value = float(m['measurements'][original_idx]) + offsets[j]
                                row.append(f"{calibrated_value:.2f}")
                            except:
                                row.append(m['measurements'][original_idx])
                        writer.writerow(row)
                    else:
                        row = [f"{position:.2f}"] + [m['measurements'][original_idx]
                                                     for m in self.merged_data['measurements']]
                        writer.writerow(row)
            else:
                # Normalne dane
                for i in range(len(sensor_positions)):
                    original_idx = start_idx + i
                    position = sensor_positions[i]

                    # Zastosuj offset jeśli są dane referencyjne
                    if has_reference:
                        row = [f"{position:.2f}"]
                        for j, m in enumerate(self.merged_data['measurements']):
                            try:
                                calibrated_value = float(m['measurements'][original_idx]) + offsets[j]
                                row.append(f"{calibrated_value:.2f}")
                            except:
                                row.append(m['measurements'][original_idx])
                        writer.writerow(row)
                    else:
                        row = [f"{position:.2f}"] + [m['measurements'][original_idx]
                                                     for m in self.merged_data['measurements']]
                        writer.writerow(row)

        ref_info = ""
        if has_reference:
            ref_info = f" | Ref: {sensor['ref_channel']}@{sensor['ref_position']:.2f}m"

        self.log_export(f"✓ {sensor['name']}: {sensor['start']:.2f}m - {sensor['end']:.2f}m "
                       f"({'odwrócony' if sensor['reversed'] else 'normalny'}){ref_info} → {filename}")

    def log_export(self, message):
        """Dodaje wpis do logu eksportu."""
        self.export_log.insert(tk.END, message + "\n")
        self.export_log.see(tk.END)
        self.root.update()


def main():
    """Główna funkcja aplikacji."""
    root = tk.Tk()
    app = SensorDataProcessor(root)
    root.mainloop()


if __name__ == '__main__':
    main()
