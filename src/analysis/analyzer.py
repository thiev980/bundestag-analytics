from datetime import datetime
from collections import Counter
from sqlalchemy import func
from src.database.models import Plenarprotokoll, Vorgangsbezug
import re

class BundestagAnalyzer:
    def __init__(self, session):  # Füge session Parameter hinzu
        self.session = session

    def get_basic_stats(self):
        total = self.session.query(Plenarprotokoll).count()
        if total == 0:
            return {
                "total_protokolle": 0,
                "durchschnitt_vorgaenge": 0,
                "max_vorgaenge": 0
            }
            
        avg_vorgaenge = self.session.query(func.avg(Plenarprotokoll.vorgangsbezug_anzahl)).scalar() or 0
        max_vorgaenge = self.session.query(func.max(Plenarprotokoll.vorgangsbezug_anzahl)).scalar() or 0
        
        return {
            "total_protokolle": total,
            "durchschnitt_vorgaenge": round(float(avg_vorgaenge), 2),
            "max_vorgaenge": max_vorgaenge
        }

    def get_top_vorgangstypen(self, limit=10):
        vorgangstypen = self.session.query(
            Vorgangsbezug.vorgangstyp,
            func.count(Vorgangsbezug.vorgangstyp).label('count')
        ).group_by(Vorgangsbezug.vorgangstyp)\
         .order_by(func.count(Vorgangsbezug.vorgangstyp).desc())\
         .limit(limit).all()
        
        return [{"typ": typ, "anzahl": count} for typ, count in vorgangstypen]
    
    def get_top_themen(self, limit=10):
        """Extrahiert und zählt häufige Themen aus Vorgangstiteln"""
        # Hole alle Vorgangstitel
        vorgaenge = self.session.query(Vorgangsbezug).all()
        
        # Wörter extrahieren und bereinigen
        words = []
        stopwords = {'der', 'die', 'das', 'und', 'in', 'im', 'für', 'von', 'zu', 'zur', 'zum', 'mit', 'einen',
                    'über', 'nach', 'bei', 'an', 'auf', 'des', 'dem', 'den', 'ein', 'eine', 'eines', 'beim', 'nicht',
                    'durch', 'um', 'am', 'als', 'aus', 'wird', 'werden', 'wurde', 'wurden', 'einer', 'hinblick', 'bund',
                    'weitere', 'weiterer', 'sowie', 'gemäß', 'europäische', 'europäischen', 'ratsdok', 'kommission', 'bundes',
                    'deutsche', 'deutschen', 'endg', 'deutschland', 'gesetzes', 'einführung', 'umsetzung', 'stärkung',
                    'gesetz', 'massnahmen', 'förderung', 'änderung', 'verordnung', 'parlament', 'parlaments', 'vorschlag',
                    'bericht', 'vorschrift', 'vorschriften', 'richtlinie', 'rat', 'rates', 'bundesregierung', 'absatz',
                    '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2014', '2017', '2009', 'deutschlands', 'ausschuss',
                    'erstes', 'zweites', 'aufhebung', 'stärken', 'entschließung', 'feststellung'}
        
        for vorgang in vorgaenge:
            # Titel in Wörter aufteilen
            title_words = re.findall(r'\b\w+\b', vorgang.titel.lower())
            # Stopwords und kurze Wörter filtern
            meaningful_words = [w for w in title_words 
                              if w not in stopwords and len(w) > 3]
            words.extend(meaningful_words)
        
        # Häufigste Wörter zählen
        word_counts = Counter(words)
        top_themes = word_counts.most_common(limit)
        
        return [{"thema": word, "anzahl": count} for word, count in top_themes]
    
    def get_vorgangstypen_trend(self):
        """Gibt die Anzahl der verschiedenen Vorgangstypen pro Monat zurück"""
        result = self.session.query(
            func.strftime('%Y-%m', Plenarprotokoll.aktualisiert).label('monat'),
            Vorgangsbezug.vorgangstyp,
            func.count(Vorgangsbezug.id).label('anzahl')
        ).join(Plenarprotokoll.vorgangsbezuege)\
        .group_by(func.strftime('%Y-%m', Plenarprotokoll.aktualisiert), Vorgangsbezug.vorgangstyp)\
        .order_by(func.strftime('%Y-%m', Plenarprotokoll.aktualisiert).asc())\
        .all()

        trend_data = []
        for monat, typ, anzahl in result:
            trend_data.append({
                "monat": monat,
                "typ": typ,
                "anzahl": anzahl
            })
        
        return trend_data