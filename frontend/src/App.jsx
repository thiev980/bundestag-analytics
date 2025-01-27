import { Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import axios from 'axios';
import ProtokollDetail from './components/ProtokollDetail';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, LineChart, Line, Legend } from 'recharts';
import { Link } from 'react-router-dom';
import './App.css';

function App() {
 const [stats, setStats] = useState(null);
 const [vorgangstypen, setVorgangstypen] = useState([]);
 const [protokolle, setProtokolle] = useState([]);
 const [topThemen, setTopThemen] = useState([]);
 const [vorgangstypenTrend, setVorgangstypenTrend] = useState([]);

 useEffect(() => {
   const fetchData = async () => {
     try {
       const [statsRes, typenRes, protokolleRes, themenRes, trendRes] = await Promise.all([
         axios.get('http://localhost:8000/stats'),
         axios.get('http://localhost:8000/vorgangstypen'),
         axios.get('http://localhost:8000/protokolle'),
         axios.get('http://localhost:8000/top-themen'),
         axios.get('http://localhost:8000/vorgangstypen-trend')
       ]);
       setStats(statsRes.data);
       setVorgangstypen(typenRes.data);
       setProtokolle(protokolleRes.data);
       setTopThemen(themenRes.data);
       setVorgangstypenTrend(trendRes.data);
     } catch (error) {
       console.error('Fehler beim Laden der Daten:', error);
     }
   };
   fetchData();
 }, []);

 if (!stats) return <div>Lade Daten...</div>;

 const Dashboard = () => (
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

     <div className="chart-section">
      <h2>Entwicklung der Top-Vorgangstypen (Anzahl pro Monat)</h2>
      <LineChart width={1000} height={400} data={vorgangstypenTrend}>
      <CartesianGrid 
        strokeDasharray="3 3" 
        horizontal={true}
        vertical={false}  // Nur horizontale Linien
      />
        <XAxis 
          dataKey="monat" 
          type="category"
          interval="preserveStartEnd"  // Zeigt nur Start, Ende und einige Zwischenwerte
          tickFormatter={(value) => {
            const [year, month] = value.split('-');
            const date = new Date(year, month - 1);
            return date.toLocaleDateString('de-DE', { month: 'short', year: '2-digit' });
          }}
        />
        <YAxis 
          label={{ 
            value: 'Anzahl Vorgänge', 
            angle: -90, 
            position: 'insideLeft',
            style: { textAnchor: 'middle' }
          }}
        />
        <Tooltip 
          content={({ payload, label }) => {
            if (payload && payload.length > 0) {
              return (
                <div className="bg-white p-2 border rounded shadow">
                  <p className="font-bold">{label}</p>
                  {payload
                    .filter(entry => entry.value > 0)
                    .map((entry, index) => (
                      <p key={index} style={{ color: entry.color }}>
                        {entry.name}: {entry.value}
                      </p>
                  ))}
                </div>
              );
            }
            return null;
          }}
        />
        <Legend />
        {Array.from(new Set(vorgangstypenTrend.map(d => d.typ)))
          // Berechne Gesamtanzahl pro Typ
          .map(typ => ({
            typ,
            total: vorgangstypenTrend
              .filter(d => d.typ === typ)
              .reduce((sum, d) => sum + d.anzahl, 0)
          }))
          // Sortiere nach Gesamtanzahl
          .sort((a, b) => b.total - a.total)
          // Nimm nur die Top 10
          .slice(0, 10)
          .map((item, index) => (
            <Line 
              key={item.typ}
              type="monotone"
              dataKey={(value) => {
                const dataPoint = vorgangstypenTrend.find(
                  d => d.monat === value.monat && d.typ === item.typ
                );
                return dataPoint ? dataPoint.anzahl : 0;
              }}
              name={item.typ}
              stroke={`hsl(${index * 36}, 70%, 50%)`}  // Angepasst für bessere Farbverteilung
              dot={false}
            />
          ))}
      </LineChart>
    </div>

     <div className="chart-section">
       <h2>Häufigste Themen</h2>
       <BarChart width={1000} height={300} data={topThemen}>
         <CartesianGrid strokeDasharray="3 3" />
         <XAxis dataKey="thema" />
         <YAxis />
         <Tooltip />
         <Bar dataKey="anzahl" fill="#82ca9d" />
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
               <td>
                 <Link to={`/protokoll/${p.id}`} className="text-blue-600 hover:text-blue-800">
                   {p.nummer}
                 </Link>
               </td>
               <td>{new Date(p.datum).toLocaleDateString()}</td>
               <td>{p.vorgaenge}</td>
             </tr>
           ))}
         </tbody>
       </table>
     </div>
   </div>
 );

 return (
   <Routes>
     <Route path="/" element={<Dashboard />} />
     <Route path="/protokoll/:id" element={<ProtokollDetail />} />
   </Routes>
 );
}

export default App;