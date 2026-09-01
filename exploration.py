from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import argrelextrema

# Unterordner mit den CSV-Dateien
input_dir = Path("03_LueckenloseDaten")

# Ordner fuer die gespeicherten Plots (wird bei Bedarf angelegt)
output_dir = Path("plots")
output_dir.mkdir(exist_ok=True)

fit_start_times = {
    "GRIPS6_2016012122": "22:28:00",
    "GRIPS7_2016012122": "22:25:00",
    "GRIPS16_2016012122": "22:35:00",
    "GRIPS6_2016012930": "23:35:00",
    "GRIPS7_2016012930": "23:30:00",
    "GRIPS16_2016012930": "23:50:00",
}
frequency_guesses = {
    "GRIPS6_2016012122": 1 / 16200,
    "GRIPS7_2016012122": 1 / 16200,
    "GRIPS16_2016012122": 1 / 16200,
    "GRIPS6_2016012930": 1 / 16200,
    "GRIPS7_2016012930": 1 / 16200,
    "GRIPS16_2016012930": 1 / 16200,
}
station_list={
    "GRIPS6_2016012122": 'GRIPS6 Oberpfaffenhofen',
    "GRIPS7_2016012122": 'GRIPS7 UFS Schneefernerhaus',
    "GRIPS16_2016012122": 'GRIPS16 Sonnenblick Observatory',
    "GRIPS6_2016012930": 'GRIPS6 Oberpfaffenhofen',
    "GRIPS7_2016012930": 'GRIPS7 UFS Schneefernerhaus',
    "GRIPS16_2016012930": 'GRIPS16 Sonnenblick Observatory', 
}
date_list={
    '2122': '21.01.2016 - 22.01.2016',
    '2930': '29.01.2016-22.01.2016',
}
def sine_func(t, amplitude, frequency, phase, offset):
    """Return a sine curve evaluated at t with the given parameters."""
    return amplitude * np.sin(2 * np.pi * frequency * t + phase) + offset

for csv_path in input_dir.glob("*.csv"):
    df = pd.read_csv(csv_path, parse_dates=["Zulu"])
    df = df.set_index("Zulu")

    fig, ax = plt.subplots(figsize=(20, 5))
    ax.plot(df.index, df["Temp"], alpha=0.5)

    fit_start_time = fit_start_times.get(csv_path.stem)

    if fit_start_time is not None:
        fit_df = df.between_time(fit_start_time, df.index[-1].strftime("%H:%M:%S"))

        if len(fit_df) > 3:
            t_seconds = (fit_df.index - fit_df.index[0]).total_seconds().to_numpy()
            y_values = fit_df["Temp"].to_numpy()

            amplitude_guess = (y_values.max() - y_values.min()) / 2
            offset_guess = y_values.mean()
            frequency_guess = frequency_guesses.get(csv_path.stem, 1 / 16200)
            initial_guess = [amplitude_guess, frequency_guess, 0, offset_guess]

            params, _ = curve_fit(sine_func, t_seconds, y_values, p0=initial_guess, maxfev=10000)

            fit_values = sine_func(t_seconds, *params)
            ax.plot(fit_df.index, fit_values, label="Sinus-Fit", linestyle="--")
    else:
        print(f"Keine Fit-Startzeit fuer {csv_path.stem} definiert, ueberspringe Fit.")

    # Tick fuer jede Minute
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=90, fontsize=7)

    ax.set_xlabel("Datum")
    ax.set_ylabel("Wert")
    ax.set_title(csv_path.stem)
    plt.tight_layout()

    output_path = output_dir / f"{csv_path.stem}.png"
    plt.savefig(output_path)
    plt.close()


groups = ["2122", "2930"]

for group in groups:
    fig, ax = plt.subplots(figsize=(20, 5))
    linestyles = ["--", "-.", ":"]
    colors = ["#6495ED", "#FA8072", "mediumseagreen"]

    for i, csv_path in enumerate(sorted(input_dir.glob(f"*{group}*.csv"))):
        station_name = station_list.get(csv_path.stem, csv_path.stem)
        date_name= date_list.get(group, group)

        df = pd.read_csv(csv_path, parse_dates=["Zulu"])
        df = df.set_index("Zulu")

        fit_start_time = fit_start_times.get(csv_path.stem)

        if fit_start_time is None:
            print(f"Keine Fit-Startzeit fuer {csv_path.stem} definiert, ueberspringe Fit.")
            continue

        fit_df = df.between_time(fit_start_time, df.index[-1].strftime("%H:%M:%S"))

        if len(fit_df) <= 3:
            continue

        t_seconds = (fit_df.index - fit_df.index[0]).total_seconds().to_numpy()
        y_values = fit_df["Temp"].to_numpy()

        amplitude_guess = (y_values.max() - y_values.min()) / 2
        offset_guess = y_values.mean()
        frequency_guess = frequency_guesses.get(csv_path.stem, 1 / 16200)
        initial_guess = [amplitude_guess, frequency_guess, 0, offset_guess]

        params, _ = curve_fit(sine_func, t_seconds, y_values, p0=initial_guess, maxfev=10000)

        fit_values = sine_func(t_seconds, *params)
        ax.plot(fit_df.index, fit_values, label=station_name, linewidth=4, linestyle=linestyles[i % len(linestyles)], color=colors[i % len(colors)])

    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45, fontsize=13)
    ax.tick_params(axis="y", labelsize=13)

    ax.set_xlabel("Zeit", fontsize=20, fontweight='bold')
    ax.set_ylabel("Temperatur in K", fontsize=20, fontweight='bold')
    ax.set_title(f"Sinus-Fits {date_name}", fontsize=20, fontweight='bold')
    ax.legend(fontsize=13)
    plt.tight_layout()

    output_path = output_dir / f"sinus_fits_{group}.png"
    plt.savefig(output_path)
    plt.close()

stations = ["GRIPS6", "GRIPS7", "GRIPS16"]
groups = ["2122", "2930"]

for group in groups:
    date_name= date_list.get(group, group)
    fig, axes = plt.subplots(len(stations), 1, figsize=(20, 12), sharex=True)
    fig.suptitle(f"Sinus-Fits {date_name}", fontsize=20, fontweight='bold')

    for row, station in enumerate(stations):
        ax = axes[row]

        matches = list(input_dir.glob(f"*{station}*{group}*.csv"))
        if not matches:
            continue

        csv_path = matches[0]
        station_name = station_list.get(csv_path.stem, csv_path.stem)
        
        df = pd.read_csv(csv_path, parse_dates=["Zulu"])
        df = df.set_index("Zulu")

        ax.plot(df.index, df["Temp"], alpha=0.5)

        fit_start_time = fit_start_times.get(csv_path.stem)

        if fit_start_time is not None:
            fit_df = df.between_time(fit_start_time, df.index[-1].strftime("%H:%M:%S"))

            if len(fit_df) > 3:
                t_seconds = (fit_df.index - fit_df.index[0]).total_seconds().to_numpy()
                y_values = fit_df["Temp"].to_numpy()

                amplitude_guess = (y_values.max() - y_values.min()) / 2
                offset_guess = y_values.mean()
                frequency_guess = frequency_guesses.get(csv_path.stem, 1 / 16200)
                initial_guess = [amplitude_guess, frequency_guess, 0, offset_guess]

                params, _ = curve_fit(sine_func, t_seconds, y_values, p0=initial_guess, maxfev=10000)

                amplitude, frequency, phase, offset = params
                print(f"{csv_path.stem}: berechnete Frequenz = {frequency:.6f} Hz")

                fit_values = sine_func(t_seconds, *params)
                maxima_idx = argrelextrema(fit_values, np.greater)[0]
                minima_idx = argrelextrema(fit_values, np.less)[0]

                print(f"{csv_path.stem}:")
                print(f"  Maxima bei: {fit_df.index[maxima_idx].strftime('%H:%M:%S').tolist()}")
                print(f"  Minima bei: {fit_df.index[minima_idx].strftime('%H:%M:%S').tolist()}")
                ax.plot(fit_df.index, fit_values, label="Sinus-Fit", linewidth=4, linestyle="--", color='salmon')

        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.tick_params(axis="x", rotation=45, labelsize=13)
        ax.tick_params(axis="y", labelsize=13)

        ax.set_title(station_name, fontsize=20, fontweight='bold')
        ax.set_ylabel("Temperatur in K", fontsize=20, fontweight='bold')

    plt.tight_layout()

    output_path = output_dir / f"grid_sinus_fits_{group}.png"
    plt.savefig(output_path)
    plt.close()