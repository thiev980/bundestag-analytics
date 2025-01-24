import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import './App.css';

function App() {
  const [stats, setStats] = useState(null);
  const [vorgangstypen, setVorgangstypen] = useState([]);
  const [protokolle, setProtokolle] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, typenRes, protokolleRes] = await Promise.all([
          axios.get('http://localhost:8000/stats'),
          axios.get('http://localhost:8000/vorgangstypen'),
          axios.get('http://localhost:8000/protokolle')
        ]);

        setStats(statsRes.data);
        setVorgangstypen(typenRes.data);
        setProtokolle(protokolleRes.data);
      } catch (error) {
        console.error('Fehler beim Laden der Daten:', error);
      }
    };

    fetchData();
  }, []);

  if (!stats) return <div>Lade Daten...</div>;

  return (
    <div className="App">
      <h1>Bundestag Analytics Dashboard</h1>
      
      <div className="stats-cards">
        <div className="card">
          <h3>Gesamtanzahl Protokolle</h3>
          <p>{stats.total_protokolle}</p>
        </div>
        <div className="card">
          <h3>Durchschnittliche Vorgänge</h3>
          <p>{stats.durchschnitt_vorgaenge}</p>
        </div>
        <div className="card">
          <h3>Maximum Vorgänge</h3>
          <p>{stats.max_vorgaenge}</p>
        </div>
      </div>

      <div className="chart-section">
        <h2>Top Vorgangstypen</h2>
        <BarChart width={1000} height={400} data={vorgangstypen}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="typ" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="anzahl" fill="#8884d8" />
        </BarChart>
      </div>

      <div className="protokolle-section">
        <h2>Neueste Protokolle</h2>
        <table>
          <thead>
            <tr>
              <th>Nummer</th>
              <th>Datum</th>
              <th>Vorgänge</th>
            </tr>
          </thead>
          <tbody>
            {protokolle.map((p) => (
              <tr key={p.id}>
                <td>{p.nummer}</td>
                <td>{new Date(p.datum).toLocaleDateString()}</td>
                <td>{p.vorgaenge}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;