from data.collector import BundestagCollector
from analysis.analyzer import BundestagAnalyzer

def main():
    collector = BundestagCollector()
    analyzer = BundestagAnalyzer(collector.session)
    
    print("Basis-Statistiken:")
    stats = analyzer.get_basic_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\nTop Vorgangstypen:")
    top_typen = analyzer.get_top_vorgangstypen(5)
    for typ in top_typen:
        print(f"{typ['typ']}: {typ['anzahl']}")

if __name__ == "__main__":
    main()