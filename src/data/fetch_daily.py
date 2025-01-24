from src.data.collector import BundestagCollector

def main():
    collector = BundestagCollector()
    collector.collect_and_save_protokolle(batch_size=50)

if __name__ == "__main__":
    main()