from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Unterordner mit den CSV-Dateien
input_dir = Path("03_LueckenloseDaten")

fit_start_times = {
    "GRIPS6_2016012122": "22:28:00",
    "GRIPS7_2016012122": "22:25:00",
    "GRIPS16_2016012122": "22:35:00",
    "GRIPS6_2016012930": "23:35:00",
    "GRIPS7_2016012930": "23:30:00",
    "GRIPS16_2016012930": "23:50:00",
}

station_list = {
    "GRIPS6_2016012122": 'GRIPS6 Oberpfaffenhofen',
    "GRIPS7_2016012122": 'GRIPS7 UFS Schneefernerhaus',
    "GRIPS16_2016012122": 'GRIPS16 Sonnenblick Observatory',
    "GRIPS6_2016012930": 'GRIPS6 Oberpfaffenhofen',
    "GRIPS7_2016012930": 'GRIPS7 UFS Schneefernerhaus',
    "GRIPS16_2016012930": 'GRIPS16 Sonnenblick Observatory',
}

date_list = {
    '2122': '21.01.2016 - 22.01.2016',
    '2930': '29.01.2016-22.01.2016',
}

# Ordner fuer die gespeicherten Plots (wird bei Bedarf angelegt)
output_dir = Path("plots_fft")
output_dir.mkdir(exist_ok=True)

for csv_path in input_dir.glob("*.csv"):
    df = pd.read_csv(csv_path, parse_dates=["Zulu"])
    df = df.set_index("Zulu")

    fit_start_time = fit_start_times.get(csv_path.stem)

    if fit_start_time is None:
        print(f"Keine Startzeit fuer {csv_path.stem} definiert, ueberspringe FFT.")
        continue

    fit_df = df.between_time(fit_start_time, df.index[-1].strftime("%H:%M:%S"))

    y_values = fit_df["Temp"].to_numpy()

    # Abtastintervall in Sekunden aus den Zeitstempeln bestimmen
    dt_seconds = (fit_df.index[1] - fit_df.index[0]).total_seconds()
    n = len(y_values)

    # FFT berechnen
    fft_values = np.fft.rfft(y_values - y_values.mean())
    fft_freqs = np.fft.rfftfreq(n, d=dt_seconds)
    amplitudes = np.abs(fft_values) / n

    # Stationsname und Datum fuer den Titel zusammenstellen
    station_name = station_list.get(csv_path.stem, csv_path.stem)
    date_key = csv_path.stem[-4:]
    date_range = date_list.get(date_key, "")
    suptitle = f"{station_name} ({date_range})" if date_range else station_name

    fig, (ax_full, ax_zoom) = plt.subplots(1, 2, figsize=(14, 5))

    ax_full.plot(fft_freqs, amplitudes)
    ax_full.set_xlabel("Frequenz [Hz]", fontsize=15, fontweight='bold')
    ax_full.set_ylabel("Amplitude [K]", fontsize=15, fontweight='bold')
    ax_full.set_title("gesamter Bereich", fontsize=15, fontweight='bold')
    ax_full.tick_params(axis="both", labelsize=13)

    ax_zoom.plot(fft_freqs, amplitudes)
    ax_zoom.set_xlabel("Frequenz [Hz]", fontsize=15, fontweight='bold')
    ax_zoom.set_ylabel("Amplitude [K]", fontsize=15, fontweight='bold')
    ax_zoom.set_xlim(0, 0.0001)
    ax_zoom.set_title("Bereich 0-0.0001 Hz", fontsize=15, fontweight='bold')
    ax_zoom.tick_params(axis="both", labelsize=13)

    fig.suptitle(suptitle, fontsize=20, fontweight="bold")
    plt.tight_layout()

    output_path = output_dir / f"{csv_path.stem}_fft.png"
    plt.savefig(output_path)
    plt.close()