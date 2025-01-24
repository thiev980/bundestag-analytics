from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Plenarprotokoll(Base):
    """Modell für ein Plenarprotokoll"""
    __tablename__ = 'plenarprotokolle'

    id = Column(Integer, primary_key=True)
    dokument_id = Column(String, unique=True)
    dokumentnummer = Column(String)
    wahlperiode = Column(Integer)
    herausgeber = Column(String)
    pdf_hash = Column(String)
    aktualisiert = Column(DateTime)
    vorgangsbezug_anzahl = Column(Integer)
    
    # Beziehung zu Vorgangsbezügen
    vorgangsbezuege = relationship("Vorgangsbezug", back_populates="protokoll")

class Vorgangsbezug(Base):
    """Modell für einen Vorgangsbezug eines Protokolls"""
    __tablename__ = 'vorgangsbezuege'

    id = Column(Integer, primary_key=True)
    vorgang_id = Column(String)
    titel = Column(String)
    vorgangstyp = Column(String)
    protokoll_id = Column(Integer, ForeignKey('plenarprotokolle.id'))
    
    # Beziehung zum Protokoll
    protokoll = relationship("Plenarprotokoll", back_populates="vorgangsbezuege")

def init_db(database_url: str):
    """Initialisiert die Datenbank"""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)