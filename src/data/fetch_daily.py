from datetime import datetime, timedelta
from src.data.collector import BundestagCollector

def main():
    collector = BundestagCollector()
    
    # Nur Dokumente der letzten 2 Tage prüfen
    yesterday = datetime.now() - timedelta(days=2)
    print(f"Starte Datenabfrage für Dokumente seit: {yesterday.strftime('%Y-%m-%d')}")
    
    collector.collect_and_save_protokolle(
        batch_size=50,
        since_date=yesterday
    )

if __name__ == "__main__":
    main()