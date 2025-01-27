import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Plenarprotokoll, Vorgangsbezug, Base

# Logging Setup bleibt gleich
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BundestagCollector:
    def __init__(self):
        # Versuche .env zu laden, aber nicht zwingend
        load_dotenv()
        
        # Hole Werte aus Environment oder .env
        self.base_url = os.getenv('BASE_URL') or "https://search.dip.bundestag.de/api/v1"
        self.api_key = os.getenv('API_KEY')
        self.database_url = os.getenv('DATABASE_URL') or "sqlite:///bundestag.db"
        
        if not self.api_key:
            raise ValueError("API_KEY muss in Umgebungsvariablen oder .env definiert sein")
        
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"ApiKey {self.api_key}"
        }
        
        # Datenbank Setup
        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def save_protokoll(self, data: Dict) -> Plenarprotokoll:
        """Speichert ein Plenarprotokoll und seine Vorgangsbezüge in der Datenbank"""
        
        # Prüfe ob Protokoll bereits existiert
        existing = self.session.query(Plenarprotokoll).filter_by(
            dokument_id=data['id']
        ).first()
        
        if existing:
            # Aktualisiere nur, wenn sich etwas geändert hat
            if existing.aktualisiert != datetime.fromisoformat(data['aktualisiert'].replace('Z', '+00:00')):
                existing.aktualisiert = datetime.fromisoformat(data['aktualisiert'].replace('Z', '+00:00'))
                existing.vorgangsbezug_anzahl = data['vorgangsbezug_anzahl']
                self.session.commit()
                logger.info(f"Protokoll {data['id']} aktualisiert")
            else:
                logger.info(f"Protokoll {data['id']} unverändert")
            return existing
                
        # Erstelle neues Protokoll
        protokoll = Plenarprotokoll(
            dokument_id=data['id'],
            dokumentnummer=data['dokumentnummer'],
            wahlperiode=data['wahlperiode'],
            herausgeber=data.get('herausgeber', ''),
            pdf_hash=data.get('pdf_hash', ''),
            aktualisiert=datetime.fromisoformat(data['aktualisiert'].replace('Z', '+00:00')),
            vorgangsbezug_anzahl=data['vorgangsbezug_anzahl']
        )
        
        # Füge Vorgangsbezüge hinzu
        for vb in data.get('vorgangsbezug', []):
            vorgangsbezug = Vorgangsbezug(
                vorgang_id=vb['id'],
                titel=vb['titel'],
                vorgangstyp=vb['vorgangstyp']
            )
            protokoll.vorgangsbezuege.append(vorgangsbezug)
        
        # Speichere in Datenbank
        try:
            self.session.add(protokoll)
            self.session.commit()
            logger.info(f"Protokoll {data['id']} neu gespeichert")
            return protokoll
        except Exception as e:
            self.session.rollback()
            logger.error(f"Fehler beim Speichern von Protokoll {data['id']}: {e}")
            raise

    def get_plenarprotokolle(
        self, 
        wahlperiode: int = 20, 
        limit: int = 10, 
        offset: int = 0,
        since_date: datetime = None
    ) -> Dict:
        params = {
            "format": "json",
            "f.wahlperiode": str(wahlperiode),
            "limit": limit,
            "offset": offset
        }
        
        if since_date:
            params["f.datum.start"] = since_date.strftime("%Y-%m-%d")
        
        try:
            response = requests.get(
                f"{self.base_url}/plenarprotokoll",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Fehler beim Abrufen der Plenarprotokolle: {e}")
            raise

    def collect_and_save_protokolle(self, wahlperiode: int = 20, batch_size: int = 50, since_date: datetime = None) -> List[Dict]:
        """Sammelt alle Protokolle und speichert sie in der Datenbank"""
        all_protokolle = []
        neue_oder_aktualisierte = 0
        offset = 0
        
        while True:
            logger.info(f"Hole Batch mit Offset {offset}" + 
                    (f" seit {since_date.strftime('%Y-%m-%d')}" if since_date else ""))
            
            batch = self.get_plenarprotokolle(
                wahlperiode=wahlperiode,
                limit=batch_size,
                offset=offset,
                since_date=since_date
            )
            
            if not batch.get('documents'):
                break
                
            for doc in batch['documents']:
                protokoll = self.save_protokoll(doc)
                all_protokolle.append(protokoll)
                if protokoll.aktualisiert >= (since_date or datetime.min):
                    neue_oder_aktualisierte += 1
            
            if len(batch['documents']) < batch_size:
                break
                
            offset += batch_size
        
        logger.info(f"Insgesamt {len(all_protokolle)} Protokolle verarbeitet")
        logger.info(f"Davon {neue_oder_aktualisierte} neu oder aktualisiert")
        return all_protokolle

    def __del__(self):
        """Schließe die Datenbankverbindung beim Beenden"""
        self.session.close()