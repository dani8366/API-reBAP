import requests
import os
import sys
import pandas as pd
import io  # <--- NEU: Für die Verarbeitung des Text-Streams
from datetime import date, timedelta

# --- DEINE DATEN ---
IPNT_CLIENT_ID = 'HIER CLIENT-ID EINTRAGEN'  #BITTE ÄNDERN!!!
IPNT_CLIENT_SECRET = 'HIER CLIENT-SECRET EINTRAGEN' #BITTE ÄNDERN!!!

# URLs
AUTH_URL = "https://identity.netztransparenz.de/users/connect/token"
BASE_DATA_URL = "https://ds.netztransparenz.de/api/v1/data/NrvSaldo"


def get_token():
    print("1. Hole Token...", end="")
    try:
        resp = requests.post(AUTH_URL, data={
            'grant_type': 'client_credentials',
            'client_id': IPNT_CLIENT_ID,
            'client_secret': IPNT_CLIENT_SECRET
        })
        if resp.ok:
            print(" ✅ OK")
            return resp.json()['access_token']
        sys.exit(f"\n❌ Login Fehler: {resp.status_code}")
    except Exception as e:
        sys.exit(f"\n❌ Fehler: {e}")


def get_safe_period():
    """
    Berechnet den sicheren Vor-Vormonat (3 Monate zurück).
    Beispiel: Heute ist Dez -> wir holen September.
    """
    today = date.today()
    first_current = today.replace(day=1)
    safe_date = first_current - timedelta(days=90)

    start_date = safe_date.replace(day=1)
    next_month = start_date + timedelta(days=32)
    end_date = next_month.replace(day=1) - timedelta(days=1)

    return start_date, end_date


if __name__ == "__main__":
    if "HIER_" in IPNT_CLIENT_ID:
        print("Bitte trage erst ID und Secret ein!")
        sys.exit()

    token = get_token()
    start, end = get_safe_period()

    # Datumsformat für URL (ISO Format)
    start_str = start.strftime("%Y-%m-%dT00:00:00")
    end_str = end.strftime("%Y-%m-%dT23:59:59")

    # URL Aufbau gemäß deinem Swagger-Fund
    datatype = "reBAP"
    product = "Qualitaetsgesichert"
    full_url = f"{BASE_DATA_URL}/{datatype}/{product}/{start_str}/{end_str}"

    print(f"2. Rufe Daten ab (CSV Format)...")
    print(f"   URL: {full_url}")

    resp = requests.get(full_url, headers={'Authorization': f'Bearer {token}'})

    if resp.ok:
        # HIER WAR DER FEHLER: Wir dürfen nicht .json() aufrufen!
        csv_text = resp.text

        # Prüfung ob Daten da sind
        if not csv_text or len(csv_text.strip()) == 0:
            print("❌ Antwort erhalten, aber sie ist leer.")
            sys.exit()

        print(f"3. ✅ ERFOLG! CSV-Daten empfangen ({len(csv_text)} Bytes).")

        # CSV Parsen mit Pandas
        # Wichtig: Deutsches Format -> Trenner ';' und Dezimal ','
        try:
            df = pd.read_csv(io.StringIO(csv_text), sep=';', decimal=',')

            # Spalten bereinigen (manchmal sind Leerzeichen in den Headern)
            df.columns = df.columns.str.strip()

            # Ausgabe der ersten Zeilen zur Kontrolle
            print(f"   Spalten gefunden: {list(df.columns)}")

            # Excel Speichern
            filename = f"reBAP_Export_{start.strftime('%Y-%m')}.xlsx"

            # Wir trennen nach Unterdeckung/Überdeckung basierend auf den Spaltennamen
            # Laut Doku Format 9 gibt es: "reBAP unterdeckt" und "reBAP ueberdeckt"
            if 'reBAP unterdeckt' in df.columns:
                print(f"4. Speichere Excel: {filename} ...")

                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Blatt 1: Rohdaten komplett
                    df.to_excel(writer, sheet_name='Gesamt', index=False)

                    # Blatt 2: Nur Werte wo Unterdeckung existiert (nicht NaN/Null)
                    df_unter = df[df['reBAP unterdeckt'].notna() & (df['reBAP unterdeckt'] != 0)]
                    df_unter.to_excel(writer, sheet_name='Unterdeckung', index=False)

                    # Blatt 3: Nur Werte wo Überdeckung existiert
                    df_ueber = df[df['reBAP ueberdeckt'].notna() & (df['reBAP ueberdeckt'] != 0)]
                    df_ueber.to_excel(writer, sheet_name='Überdeckung', index=False)

                print("🎉 FERTIG! Projekt erfolgreich abgeschlossen.")

            else:
                print("⚠️ Warnung: Erwartete Spalten 'reBAP unterdeckt' nicht gefunden.")
                print("Speichere Rohdaten zur Analyse...")
                df.to_excel(f"Debug_{filename}", index=False)

        except Exception as e:
            print(f"❌ Fehler beim CSV-Lesen: {e}")
            print("Erste 200 Zeichen der Antwort:")
            print(csv_text[:200])

    else:
        print(f"❌ Server Fehler {resp.status_code}")
        print(resp.text)