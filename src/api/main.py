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