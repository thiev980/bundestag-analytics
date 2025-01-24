from data.collector import BundestagCollector
from database.models import Plenarprotokoll

def check_database():
    collector = BundestagCollector()
    
    protokoll_count = collector.session.query(Plenarprotokoll).count()
    print(f"Anzahl gespeicherter Protokolle: {protokoll_count}")
    
    if protokoll_count > 0:
        protokolle = collector.session.query(Plenarprotokoll).limit(3).all()
        for p in protokolle:
            print(f"\nProtokoll {p.dokumentnummer}:")
            print(f"- Aktualisiert: {p.aktualisiert}")
            print(f"- Vorgangsbezüge: {p.vorgangsbezug_anzahl}")

if __name__ == "__main__":
    check_database()