# src/data/fetch_daily.py
from datetime import datetime, timedelta
from src.data.collector import BundestagCollector

def main():
    collector = BundestagCollector()
    # Nur Dokumente des letzten Tages prüfen
    today = datetime.now()
    yesterday = today.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    
    print(f"Starte Datenabfrage für Dokumente seit: {yesterday.strftime('%Y-%m-%d %H:%M:%S')}")
    
    collector.collect_and_save_protokolle(
        batch_size=50,
        since_date=yesterday
    )

if __name__ == "__main__":
    main()