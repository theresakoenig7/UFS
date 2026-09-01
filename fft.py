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

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(fft_freqs, amplitudes)

    ax.set_xlabel("Frequenz [Hz]")
    ax.set_ylabel("Amplitude")
    ax.set_xlim(0, 0.00006)
    ax.set_title(csv_path.stem)
    plt.tight_layout()

    output_path = output_dir / f"{csv_path.stem}_fft.png"
    plt.savefig(output_path)
    plt.close()