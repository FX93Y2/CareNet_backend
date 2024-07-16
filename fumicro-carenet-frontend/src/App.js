import React, { useEffect, useRef, useState } from 'react';
import '@arcgis/core/assets/esri/themes/light/main.css';
import Map from "@arcgis/core/Map";
import MapView from "@arcgis/core/views/MapView";
import esriConfig from "@arcgis/core/config";

import './App.css';

function App() {
  const mapDiv = useRef(null);
  const [config, setConfig] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:3001/api/config')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Fetched config:', data);
        setConfig(data);
      })
      .catch(error => {
        console.error('Error fetching config:', error);
        setError('Failed to load map configuration. Please check if the backend server is running.');
      });
  }, []);

  useEffect(() => {
    if (mapDiv.current && config && config.arcgisApiKey) {
      try {
        console.log('Initializing map with API key:', config.arcgisApiKey);
        esriConfig.apiKey = config.arcgisApiKey;

        const map = new Map({
          basemap: "streets-vector"
        });

        new MapView({
          container: mapDiv.current,
          map: map,
          center: [117.2808, 31.8639], // Longitude, Latitude for Hefei, China
          zoom: 10 // Adjusted zoom level for city view
        });

        console.log('Map initialized successfully');
      } catch (error) {
        console.error('Error initializing map:', error);
        setError('Failed to initialize map. Please check your ArcGIS API key.');
      }
    }
  }, [config]);

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Fumicro Carenet</h1>
      </header>
      <div className="mapDiv" ref={mapDiv}></div>
    </div>
  );
}

export default App;