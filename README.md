# API-reBAP
Automatisierte Datenpipeline für Ausgleichsenergiepreise (Python & Excel)

Ein Python-basiertes Tool für das Energiedaten-Management. Es automatisiert den Abruf und die Aufbereitung qualitätsgesicherter reBAP-Daten (regelzonenübergreifender Bilanzausgleichspreis) von der Netztransparenz-Plattform für das finanzielle Controlling.

## 🎯 Projektziel
Im Energiecontrolling ist der Zugriff auf qualitätsgesicherte Abrechnungsdaten oft ein Flaschenhals. Die offiziellen reBAP-Werte werden mit mehrwöchigem Verzug (Settlement-Prozess) veröffentlicht, was manuelle Abfragen fehleranfällig macht. Zudem weist die API technische Hürden bei der Parametrisierung auf. Dieses Tool eliminiert manuelle Prozesse, indem es automatisch das valide Veröffentlichungsfenster berechnet, API-Spezifika abstrahiert und transparente Reports für Unterdeckung (Preissignale bei Mangel) und Überdeckung (Preissignale bei Überschuss) generiert.

## 🛠 Technologie-Stack
**Data Extraction:** Python (Requests, OAuth2 Client-Credentials Flow)

**Data Processing:** Pandas (CSV Parsing, Time-Series Handling)

**Reporting:** OpenPyXL (Automatisierter Excel-Export mit Sheet-Splitting)

**Logik:** Rolling-Window-Algorithmus zur Vermeidung von 404-Fehlern bei Latenzzeiten

## 📊 Funktionalitäten
**Smart Fetching:** Automatische Berechnung der "Safe-Period" (dynamischer 3-Monats-Rückversatz), um die Verfügbarkeit der qualitätsgesicherten Daten sicherzustellen.

**API-Logic Abstraction:** Implementierung der undokumentierten Parameter-Trennung (dataType vs. product), um die Schnittstelle stabil anzusprechen.

**Data Cleansing:** Parsing der Rohdaten-Streams und Normalisierung deutscher Zahlenformate.

**Automated Reporting:** Erstellung einer Excel-Arbeitsmappe mit getrennten Ansichten für Gesamtportfolio, Unterdeckung und Überdeckung.

## 🚀 Installation & Nutzung
1. Dependencies installieren: pip install pandas requests openpyxl

2. Konfiguration: API-Credentials in reBap.py hinterlegen (Client-ID & Secret).

3. Prozess starten: python reBap.py Der ETL-Prozess extrahiert die Daten, transformiert sie und speichert den Report reBAP_Export_YYYY-MM.xlsx lokal ab.
