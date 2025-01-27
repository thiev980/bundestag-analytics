from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.database.models import Plenarprotokoll, Vorgangsbezug
from src.data.collector import BundestagCollector
from src.analysis.analyzer import BundestagAnalyzer

app = FastAPI(title="Bundestag Analytics API")
collector = BundestagCollector()
analyzer = BundestagAnalyzer(collector.session)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stats")
def get_stats():
    return analyzer.get_basic_stats()

@app.get("/vorgangstypen")
def get_vorgangstypen(limit: int = 10):
    return analyzer.get_top_vorgangstypen(limit)

@app.get("/protokolle")
def get_protokolle(skip: int = 0, limit: int = 10):
    protokolle = collector.session.query(Plenarprotokoll)\
        .offset(skip).limit(limit).all()
    return [{
        "id": p.dokument_id,
        "nummer": p.dokumentnummer,
        "datum": p.aktualisiert,
        "vorgaenge": p.vorgangsbezug_anzahl
    } for p in protokolle]

@app.get("/protokoll/{dokument_id}")
def get_protokoll_detail(dokument_id: str):
    protokoll = collector.session.query(Plenarprotokoll)\
        .filter(Plenarprotokoll.dokument_id == dokument_id)\
        .first()
    
    if not protokoll:
        raise HTTPException(status_code=404, detail="Protokoll nicht gefunden")
    
    return {
        "id": protokoll.dokument_id,
        "nummer": protokoll.dokumentnummer,
        "datum": protokoll.aktualisiert,
        "herausgeber": protokoll.herausgeber,
        "vorgaenge": [
            {
                "id": v.vorgang_id,
                "typ": v.vorgangstyp,
                "titel": v.titel
            }
            for v in protokoll.vorgangsbezuege
        ]
    }

@app.get("/top-themen")
def get_top_themen(limit: int = 10):
    return analyzer.get_top_themen(limit)

@app.get("/vorgangstypen-trend")
def get_vorgangstypen_trend():
    return analyzer.get_vorgangstypen_trend()