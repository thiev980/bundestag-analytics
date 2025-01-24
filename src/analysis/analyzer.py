from datetime import datetime
from collections import Counter
from sqlalchemy import func
from src.database.models import Plenarprotokoll, Vorgangsbezug

class BundestagAnalyzer:
    def __init__(self, session):
        self.session = session

    def get_basic_stats(self):
        total = self.session.query(Plenarprotokoll).count()
        avg_vorgaenge = self.session.query(func.avg(Plenarprotokoll.vorgangsbezug_anzahl)).scalar()
        max_vorgaenge = self.session.query(func.max(Plenarprotokoll.vorgangsbezug_anzahl)).scalar()
        
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