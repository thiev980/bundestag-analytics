import requests
import json
from datetime import datetime
from pprint import pprint  # für schönere Ausgabe

BASE_URL = "https://search.dip.bundestag.de/api/v1"
API_KEY = "I9FKdCn.hbfefNWCY336dL6x62vfwNKpoN2RZ1gp21"

headers = {
    "Accept": "application/json",
    "Authorization": f"ApiKey {API_KEY}"
}

params = {
    "format": "json",
    "f.wahlperiode": "20",
    "limit": 5
}

response = requests.get(
    f"{BASE_URL}/plenarprotokoll",
    headers=headers,
    params=params
)

if response.status_code == 200:
    data = response.json()
    print(f"Gefundene Dokumente: {data['numFound']}")
    print("\nDetails der ersten 5 Protokolle:")
    for doc in data['documents']:
        print("\n---")
        print(f"Dokumentnummer: {doc['dokumentnummer']}")
        print(f"Wahlperiode: {doc['wahlperiode']}")
        print(f"Aktualisiert: {doc['aktualisiert']}")
        print(f"Anzahl Vorgangsbezüge: {doc['vorgangsbezug_anzahl']}")
        if 'vorgangsbezug' in doc:
            print("Erster Vorgangsbezug:")
            print(f"- Titel: {doc['vorgangsbezug'][0]['titel'][:100]}...")
else:
    print(f"Fehler: {response.status_code}")
    print(response.text)