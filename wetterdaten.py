"""
Wetterdaten für Standortanalyse (Übungsprojekt)
================================================
Holt Wetter- und Einstrahlungsdaten von der offenen Open-Meteo-API,
speichert sie als CSV und berechnet einfache Kennzahlen je Standort.

Fachlicher Bezug: Sonneneinstrahlung und Windgeschwindigkeit sind die
Grundgrössen für die Bewertung von PV- und Windstandorten.

Setup in VS Code:
    python -m venv .venv
    .venv\\Scripts\\activate          (Windows)
    pip install requests pandas
    python wetterdaten.py

Geübte Themen: requests, JSON, Fehlerbehandlung, Dateien schreiben,
Dictionaries, List Comprehensions, Funktionen, pandas groupby.
"""

import csv
import requests
import pandas as pd
from datetime import datetime


# Standorte als Dictionary: Name -> Koordinaten
# (Dictionary statt Liste, weil wir per Name zugreifen wollen)
STANDORTE = {
    "Oberstdorf":   (47.41, 10.28),
    "Reussenköge": (54.62, 8.90),
    "Osnabrück":   (52.28, 8.05),
    "Kempten":      (47.75, 10.31),
    "München":      (48.14, 11.58),
    "Buttenwiesen":   (48.10, 10.90),
    "Stuttgart":     (48.78, 9.18),
    "Husum":         (54.48, 9.05),
    "Augsburg":       (48.37, 10.90),
    "Hamburg":       (53.55, 9.99) 
}

API_URL = "https://api.open-meteo.com/v1/forecast"


def hole_wetterdaten(name: str, lat: float, lon: float) -> list[dict]:
    """Fragt Stundenwerte fuer einen Standort ab und gibt sie als Liste von Dicts zurueck."""
    parameter = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,wind_speed_10m,shortwave_radiation",
        "forecast_days": 3,
        "timezone": "Europe/Berlin",
    }

    try:
        antwort = requests.get(API_URL, params=parameter, timeout=10)
        antwort.raise_for_status()          # wirft Fehler bei Status 4xx/5xx
        daten = antwort.json()
    except requests.exceptions.Timeout:
        print(f"  {name}: Zeitüberschreitung – Standort wird übersprungen.")
        return []
    except requests.exceptions.RequestException as fehler:
        print(f"  {name}: Abfrage fehlgeschlagen ({fehler}).")
        return []

    # Prüfen, ob die erwarteten Schlüssel vorhanden sind,
    # bevor wir sie verwenden (nie blind auf JSON-Struktur vertrauen)
    if "hourly" not in daten:
        print(f"  {name}: unerwartete Antwortstruktur.")
        return []

    stunden = daten["hourly"]

    # List Comprehension mit zip: baut je Zeitstempel eine Zeile
    zeilen = [
        {
            "standort": name,
            "zeitpunkt": zeit,
            "temperatur_c": temp,
            "wind_ms": wind,
            "strahlung_wm2": strahlung,
        }
        for zeit, temp, wind, strahlung in zip(
            stunden["time"],
            stunden["temperature_2m"],
            stunden["wind_speed_10m"],
            stunden["shortwave_radiation"],
        )
    ]

    print(f"  {name}: {len(zeilen)} Stundenwerte geladen.")
    return zeilen


def schreibe_csv(zeilen: list[dict], pfad: str) -> None:
    """Schreibt die Zeilen als CSV. 'with' schliesst die Datei auch bei Fehlern."""
    if not zeilen:
        print("Keine Daten zum Schreiben.")
        return

    with open(pfad, "w", newline="", encoding="utf-8") as datei:
        writer = csv.DictWriter(datei, fieldnames=list(zeilen[0].keys()))
        writer.writeheader()
        writer.writerows(zeilen)

    print(f"CSV geschrieben: {pfad}")


def auswerten(pfad: str) -> pd.DataFrame:
    """Berechnet Kennzahlen je Standort – das ist die Data-Analyst-Seite."""
    df = pd.read_csv(pfad, parse_dates=["zeitpunkt"])

    kennzahlen = df.groupby("standort").agg(
        temperatur_mittel=("temperatur_c", "mean"),
        wind_mittel=("wind_ms", "mean"),
        wind_max=("wind_ms", "max"),
        strahlung_mittel=("strahlung_wm2", "mean"),
        strahlung_summe=("strahlung_wm2", "sum"),
    ).round(1)

    # Zusatzkennzahl: Anteil der Stunden mit nutzbarem Wind (> 3 m/s)
    nutzbar = df[df["wind_ms"] > 3].groupby("standort").size()
    kennzahlen["stunden_wind_ueber_3ms"] = nutzbar

    return kennzahlen

def vergleiche_standorte(ergebnisse: dict[str, dict], kennzahl: str, absteigend: bool = True) -> list[tuple]:
    """Sortiert Standorte nach einer Kennzahl.
    
    absteigend=True  → bester zuerst
    absteigend=False → schlechtester zuerst
    """
    return sorted(
        ergebnisse.items(),
        key=lambda eintrag: eintrag[1][kennzahl],
        reverse=absteigend,
    )

def bewerte_standort(zeilen: list[dict]) -> dict:
    """Berechnet Kennzahlen für die Standortbewertung."""
    wind = [z["wind_ms"] for z in zeilen]
    strahlung = [z["strahlung_wm2"] for z in zeilen]
    
    return {
        "wind_mittel": sum(wind) / len(wind),
        "wind_nutzbar_prozent": len([w for w in wind if 3 <= w <= 25]) / len(wind) * 100,
        "strahlung_summe_kwh": sum(strahlung) / 1000
    }

def main() -> None:
    print("Wetterdaten werden abgerufen...")

    alle_zeilen = []
    for name, (lat, lon) in STANDORTE.items():
        alle_zeilen.extend(
            hole_wetterdaten(name, lat, lon)
        )

    pfad = "wetterdaten.csv"
    schreibe_csv(alle_zeilen, pfad)

    if alle_zeilen:
        print("\nKennzahlen je Standort:")
        print(auswerten(pfad).to_string())

        # je Standort bewerten und in ein Dictionary sammeln
        ergebnisse = {}
        for name in STANDORTE:
            zeilen_dieses_standorts = [z for z in alle_zeilen if z["standort"] == name]
            if zeilen_dieses_standorts:
               ergebnisse[name] = bewerte_standort(zeilen_dieses_standorts)

        # jetzt erst vergleichen
        jetzt = datetime.now()
        zeitpunkt = jetzt.strftime("%d.%m.%Y %H:%M")
        beste = vergleiche_standorte(ergebnisse, "strahlung_summe_kwh", absteigend=True)[0]
        schlechteste = vergleiche_standorte(ergebnisse, "strahlung_summe_kwh", absteigend=False)[0]

        print(f"Beste Einstrahlung am {zeitpunkt}: {beste[0]} mit {beste[1]['strahlung_summe_kwh']:.1f} kWh/m²")
        print(f"Schwächste Einstrahlung am {zeitpunkt} : {schlechteste[0]} mit {schlechteste[1]['strahlung_summe_kwh']:.1f} kWh/m²")


if __name__ == "__main__":
    main()
