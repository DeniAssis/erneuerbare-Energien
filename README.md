# Standortanalyse für erneuerbare Energien

Ein Python-Tool, das Wetter- und Einstrahlungsdaten für mehrere Standorte über eine
offene API abruft, auswertet und miteinander vergleicht.

**Fachlicher Hintergrund:** Windgeschwindigkeit und Globalstrahlung sind die beiden
Kerngrößen für die Bewertung von Wind- und PV-Standorten. Das Tool berechnet
Kennzahlen je Standort und zeigt, welcher Ort sich für welche Nutzungsart eignet.

---

## Funktionen

- Abruf stündlicher Wetterdaten über die offene **Open-Meteo-API**
  (Temperatur, Windgeschwindigkeit, Globalstrahlung)
- Speicherung als CSV
- Auswertung mit **pandas**: Mittelwerte, Maxima und Summen je Standort
- Kennzahl **nutzbare Windstunden** auf Basis der technischen Betriebsgrenzen
- Sortierung der Standorte nach frei wählbarer Kennzahl – bester und schwächster Standort
- Fehlertolerante API-Abfrage mit Timeout und Statusprüfung

---

## Beispielausgabe

```
Wetterdaten werden abgerufen...
  Oberstdorf: 72 Stundenwerte geladen.
  Reussenköge: 72 Stundenwerte geladen.
  Osnabrück: 72 Stundenwerte geladen.
  Kempten: 72 Stundenwerte geladen.
  München: 72 Stundenwerte geladen.
  Buttenwiesen: 72 Stundenwerte geladen.
  Stuttgart: 72 Stundenwerte geladen.
  Husum: 72 Stundenwerte geladen.
  Augsburg: 72 Stundenwerte geladen.
  Hamburg: 72 Stundenwerte geladen.
CSV geschrieben: wetterdaten.csv

Kennzahlen je Standort:
              temperatur_mittel  wind_mittel  wind_max  strahlung_mittel  strahlung_summe  stunden_wind_ueber_3ms
standort                                                                                                         
Augsburg                   20.0          6.9      14.6             135.5           9756.0                      67
Buttenwiesen               18.9          8.2      20.6             140.2          10097.0                      68
Hamburg                    17.2         10.1      18.1             119.9           8635.0                      72
Husum                      16.3         11.2      23.5             159.0          11450.0                      72
Kempten                    19.1          6.5      14.5             145.7          10491.0                      65
München                    20.3          6.4      16.6             138.8           9991.0                      67
Oberstdorf                 18.0          5.0      14.0             134.0           9648.0                      52
Osnabrück                  17.3          9.1      16.7             117.4           8456.0                      70
Reussenköge                16.9         15.3      30.3             164.8          11867.0                      71
Stuttgart                  21.7          6.7      14.8             148.1          10664.0                      66
Beste Einstrahlung am 19.08.2026 08:58: Reussenköge mit 11.9 kWh/m²
Schwächste Einstrahlung am 19.08.2026 08:58 : Osnabrück mit 8.5 kWh/m²´´´

Hinweis: Die Werte beruhen auf einer 3-Tages-Prognose und sind daher wetterabhängig, nicht klimatologisch
repräsentativ. Für belastbare Standortvergleiche würde man mehrjährige historische Daten heranziehen.

## Installation

```bash
git clone https://github.com/DeniAssis/erneuerbare-Energien.git
cd erneuerbare-Energien

python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
```

## Verwendung

```bash
python wetterdaten.py
```

Die Standorte lassen sich in der Konstante `STANDORTE` am Anfang der Datei anpassen –
je Eintrag ein Name und ein Koordinatenpaar aus Breiten- und Längengrad.

---

## Aufbau

| Funktion | Aufgabe |
|---|---|
| `hole_wetterdaten()` | Fragt Stundenwerte für einen Standort über die API ab |
| `schreibe_csv()` | Speichert alle Zeilen als CSV |
| `auswerten()` | Berechnet Kennzahlen je Standort mit pandas |
| `bewerte_standort()` | Kennzahlen für einen einzelnen Standort |
| `vergleiche_standorte()` | Sortiert alle Standorte nach einer wählbaren Kennzahl |

Jede Funktion hat eine klar abgegrenzte Aufgabe. Der Vergleich mehrerer Standorte
findet bewusst außerhalb der Einzelbewertung statt, da eine Bewertungsfunktion nur
die Daten eines Standorts kennt.

---

## Technische Hinweise

**Nutzbare Windstunden:** Windkraftanlagen benötigen etwa 3 m/s zum Anlaufen und
schalten bei über 25 m/s aus Sicherheitsgründen ab. Die Kennzahl zählt den Anteil
der Stunden innerhalb dieses Bereichs – aussagekräftiger als der reine Mittelwert,
da die Leistung mit der dritten Potenz der Windgeschwindigkeit wächst.

**Globalstrahlung:** Die API liefert Stundenwerte in W/m². Ihre Summe ergibt die
Einstrahlung in Wh/m², geteilt durch 1000 die übliche Vergleichsgröße kWh/m².

**Fehlerbehandlung:** Die API-Abfrage läuft mit Timeout und Statusprüfung. Fällt ein
Standort aus, werden die übrigen dennoch verarbeitet – das Programm bricht nicht ab.
Auch die JSON-Struktur wird geprüft, bevor auf Schlüssel zugegriffen wird.

---

## Verwendete Bibliotheken

| Bibliothek | Zweck |
|---|---|
| requests | API-Abfragen |
| pandas | Auswertung und Aggregation |

---

## Mögliche Erweiterungen

- Koordinaten über die Geocoding-API automatisch aus Ortsnamen ermitteln
- Räumliche Analyse mit GeoPandas: Entfernungen, Pufferflächen, Kartendarstellung
- Historische Daten statt Prognose für belastbare Standortvergleiche

---

## Datenquelle

Wetterdaten: [Open-Meteo](https://open-meteo.com) – freie API, keine Anmeldung
erforderlich, für nicht-kommerzielle Nutzung kostenlos.

---

## Hinweis

Übungsprojekt zur Vertiefung von Python und API-Anbindung. Das Grundgerüst entstand
mit KI-Unterstützung und wurde anschließend eigenständig durchgearbeitet, erweitert
und angepasst.

---

## Autorin

**Denise De Assis** · Data Analyst / Data Scientist
[LinkedIn]([https://www.linkedin.com/in/prof-dr-denise-assis-24693621/) · [GitHub](https://github.com/DeniAssis)
