import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import axios from 'axios';

function ProtokollDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [protokoll, setProtokoll] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProtokoll = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/protokoll/${id}`);
        setProtokoll(response.data);
      } catch (error) {
        console.error('Fehler beim Laden des Protokolls:', error);
      }
      setLoading(false);
    };

    fetchProtokoll();
  }, [id]);

  // Gruppiere Vorgänge nach Typ
  const gruppiereVorgaenge = (vorgaenge) => {
    return vorgaenge.reduce((acc, vorgang) => {
      (acc[vorgang.typ] = acc[vorgang.typ] || []).push(vorgang);
      return acc;
    }, {});
  };

  if (loading) {
    return (
      <div className="p-4">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
        </div>
      </div>
    );
  }

  if (!protokoll) return <div className="p-4">Protokoll nicht gefunden</div>;

  const gruppiertVorgaenge = gruppiereVorgaenge(protokoll.vorgaenge);

  return (
    <div className="p-4 max-w-6xl mx-auto">
      {/* Zurück-Button */}
      <button 
        onClick={() => navigate('/')}
        className="mb-4 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg flex items-center gap-2"
      >
        ← Zurück zur Übersicht
      </button>

      <h2 className="text-2xl font-bold mb-4">Protokoll {protokoll.nummer}</h2>
      
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <p><strong>Datum:</strong> {new Date(protokoll.datum).toLocaleDateString()}</p>
        <p><strong>Herausgeber:</strong> {protokoll.herausgeber}</p>
      </div>

      <h3 className="text-xl font-bold mb-4">Vorgänge nach Typ</h3>
      
      {Object.entries(gruppiertVorgaenge).map(([typ, vorgaenge]) => (
        <div key={typ} className="mb-6">
          <h4 className="font-bold mb-2 bg-gray-100 p-2 rounded">
            {typ} ({vorgaenge.length})
          </h4>
          <div className="bg-white rounded-lg shadow divide-y">
            {vorgaenge.map((vorgang) => (
              <div key={vorgang.id} className="p-4">
                <p className="text-gray-800">{vorgang.titel}</p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default ProtokollDetail;