from data.collector import BundestagCollector

def main():
    collector = BundestagCollector()
    
    print("Starte Datensammlung...")
    protokolle = collector.collect_and_save_protokolle(batch_size=10)
    
    print(f"\nGesammelte Protokolle: {len(protokolle)}")
    if protokolle:
        erstes = protokolle[0]
        print("\nDetails zum ersten Protokoll:")
        print(f"Dokumentnummer: {erstes.dokumentnummer}")
        print(f"Aktualisiert: {erstes.aktualisiert}")
        print(f"Anzahl Vorgangsbezüge: {len(erstes.vorgangsbezuege)}")
        if erstes.vorgangsbezuege:
            print(f"Erster Vorgangsbezug: {erstes.vorgangsbezuege[0].titel[:100]}...")

if __name__ == "__main__":
    main()