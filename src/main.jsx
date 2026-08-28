import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { MapContainer, TileLayer, GeoJSON, useMap, Popup, ImageOverlay, Rectangle } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import {
  ResponsiveContainer,
  ComposedChart,
  AreaChart,
  BarChart as RechartsBarChart,
  LineChart,
  Area,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  Cell,
  ReferenceArea,
  ReferenceLine,
} from "recharts";

const tabs = [
  { id: "overview", label: "Vue d'ensemble" },
  { id: "vegetation", label: "Suivi Végétation" },
  { id: "saison", label: "Saison des pluies" },
  { id: "stats", label: "Statistiques" },
  { id: "carte", label: "Cartographie" },
  { id: "sensors", label: "Comparaison Capteurs" },
  { id: "data", label: "Base de Données" },
];

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

const staticDataFiles = {
  overview: "/data/overview.json",
  communes: "/data/communes.json",
  annualData: "/data/annual-precipitations.json",
  seasonData: "/data/saisons.json",
  monthlyClimatology: "/data/monthly-climatology.json",
  anomalies: "/data/anomalies.json",
  precipRecords: "/data/precip-records.json",
  communesGeojson: "/data/communes.geojson",
  vegetationData: "/data/vegetation-data.json",
  ndviClasses: "/data/ndvi_classes_metadata.json",
};

const Icons = {
  Overview: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
    </svg>
  ),
  Rain: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15a4.5 4.5 0 004.5 4.5H18a3.75 3.75 0 001.332-7.257 3 3 0 00-3.758-3.848 5.25 5.25 0 00-10.233 2.33A4.502 4.502 0 002.25 15z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 19.5v2.25m3-2.25v2.25m3-2.25v2.25" />
    </svg>
  ),
  Stats: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v5.25c0 .621-.504 1.125-1.125 1.125h-2.25A1.125 1.125 0 013 18.375v-5.25zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125v-9.75zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v14.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
    </svg>
  ),
  Map: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 6.75h12m-12 5.25h12m-12 5.25h12M3 6.75h.008v.008H3V6.75zm0 5.25h.008v.008H3V12zm0 5.25h.008v.008H3v-.008z" />
    </svg>
  ),
  Table: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 5.25h16.5m-16.5 4.5h16.5m-16.5 4.5h16.5m-16.5 4.5h16.5" />
    </svg>
  ),
  Sun: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m0 13.5V21m6.364-16.364l-1.591 1.591M6.343 17.657l-1.591 1.591m12.728 0l-1.591-1.591M6.343 6.343L4.752 4.752M3 12h2.25m13.5 0H21M12 7.5a4.5 4.5 0 100 9 4.5 4.5 0 000-9z" />
    </svg>
  ),
  Moon: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
    </svg>
  ),
  Search: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  ),
  Download: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
  ),
  Info: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  Database: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75M3.75 10.125v3.75m16.5 0v3.75M3.75 13.875v3.75" />
    </svg>
  ),
  Leaf: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21V9m0 0a4.5 4.5 0 00-4.5 4.5M12 9a4.5 4.5 0 014.5 4.5m-4.5-4.5V3" />
    </svg>
  ),
  Layers: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M6.429 9.75L2.25 12l4.179 2.25m0-4.5l5.571 3 5.571-3m-11.142 0L12 7.5l5.571 2.25m1.179 2.25l4.179-2.25-4.179-2.25m0 4.5l-5.571 3-5.571-3M2.25 12l4.179 2.25m11.142 0L21.75 12M6.429 14.25v3.5A2.25 2.25 0 008.679 20h6.642a2.25 2.25 0 002.25-2.25v-3.5" />
    </svg>
  ),
  Alert: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
    </svg>
  ),
};

// Gaussian Elimination solver for polynomial regression (degree 1 to 5)
function gaussianElimination(A, B) {
  const n = B.length;
  const M = A.map((row, i) => [...row, B[i]]);

  for (let i = 0; i < n; i++) {
    let maxRow = i;
    for (let k = i + 1; k < n; k++) {
      if (Math.abs(M[k][i]) > Math.abs(M[maxRow][i])) {
        maxRow = k;
      }
    }
    [M[i], M[maxRow]] = [M[maxRow], M[i]];
    if (Math.abs(M[i][i]) < 1e-12) return null;

    for (let k = i + 1; k < n; k++) {
      const c = -M[k][i] / M[i][i];
      for (let j = i; j <= n; j++) {
        if (i === j) M[k][j] = 0;
        else M[k][j] += c * M[i][j];
      }
    }
  }

  const x = Array(n).fill(0);
  for (let i = n - 1; i >= 0; i--) {
    x[i] = M[i][n] / M[i][i];
    for (let k = i - 1; k >= 0; k--) {
      M[k][n] -= M[k][i] * x[i];
    }
  }
  return x;
}

function polyFit(xValues, yValues, order = 4) {
  const n = xValues.length;
  if (n === 0) return [];
  const k = Math.min(order, n - 1);
  if (k < 1) {
    const meanY = yValues.reduce((a, b) => a + b, 0) / (n || 1);
    return yValues.map(() => Math.round(meanY * 10) / 10);
  }

  const minX = Math.min(...xValues);
  const maxX = Math.max(...xValues);
  const normX = xValues.map((x) => (maxX === minX ? 0 : (x - minX) / (maxX - minX)));

  const m = k + 1;
  const ATA = Array.from({ length: m }, () => Array(m).fill(0));
  const ATy = Array(m).fill(0);

  for (let i = 0; i < n; i++) {
    const xi = normX[i];
    const yi = yValues[i];
    const xPowers = [1];
    for (let p = 1; p <= 2 * k; p++) {
      xPowers[p] = xPowers[p - 1] * xi;
    }
    for (let row = 0; row < m; row++) {
      ATy[row] += yi * xPowers[row];
      for (let col = 0; col < m; col++) {
        ATA[row][col] += xPowers[row + col];
      }
    }
  }

  const coeffs = gaussianElimination(ATA, ATy);
  if (!coeffs) {
    const meanY = yValues.reduce((a, b) => a + b, 0) / n;
    return yValues.map(() => Math.round(meanY * 10) / 10);
  }

  return normX.map((xi) => {
    let val = 0;
    let pow = 1;
    for (let p = 0; p < m; p++) {
      val += coeffs[p] * pow;
      pow *= xi;
    }
    return Math.round(val * 10) / 10;
  });
}

// Inverse Distance Weighting (IDW) interpolation for Isohyets
function computeIDWGrid(points, gridSize = 35, power = 2) {
  if (!points || points.length === 0) return null;
  const lats = points.map((p) => p.lat);
  const lngs = points.map((p) => p.lng);
  const minLat = Math.min(...lats) - 0.15;
  const maxLat = Math.max(...lats) + 0.15;
  const minLng = Math.min(...lngs) - 0.15;
  const maxLng = Math.max(...lngs) + 0.15;

  const latStep = (maxLat - minLat) / gridSize;
  const lngStep = (maxLng - minLng) / gridSize;

  const cells = [];
  let maxVal = -Infinity;
  let minVal = Infinity;

  for (let r = 0; r < gridSize; r++) {
    const cellLat = minLat + (r + 0.5) * latStep;
    for (let c = 0; c < gridSize; c++) {
      const cellLng = minLng + (c + 0.5) * lngStep;

      let sumWeights = 0;
      let weightedVal = 0;

      for (let i = 0; i < points.length; i++) {
        const dLat = cellLat - points[i].lat;
        const dLng = cellLng - points[i].lng;
        const distSq = dLat * dLat + dLng * dLng;

        if (distSq < 1e-8) {
          sumWeights = 1;
          weightedVal = points[i].val;
          break;
        }

        const w = 1 / Math.pow(distSq, power / 2);
        sumWeights += w;
        weightedVal += w * points[i].val;
      }

      const val = sumWeights > 0 ? weightedVal / sumWeights : 0;
      if (val > maxVal) maxVal = val;
      if (val < minVal) minVal = val;

      const bounds = [
        [cellLat - latStep / 2, cellLng - lngStep / 2],
        [cellLat + latStep / 2, cellLng + lngStep / 2],
      ];

      cells.push({ bounds, val });
    }
  }

  return { cells, minVal, maxVal };
}

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Impossible de charger ${path}`);
  }
  return response.json();
}

function toFiniteNumber(value, fallback = null) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function averageFinite(values, digits = 1, fallback = null) {
  const numbers = values.map((value) => Number(value)).filter(Number.isFinite);
  if (numbers.length === 0) return fallback;
  const average = numbers.reduce((sum, value) => sum + value, 0) / numbers.length;
  return Number(average.toFixed(digits));
}

function formatNumber(value, options = {}) {
  const number = toFiniteNumber(value);
  return number === null ? "n/d" : number.toLocaleString("fr-FR", options);
}

async function loadStaticData() {
  const keys = Object.keys(staticDataFiles);
  const results = await Promise.all(Object.values(staticDataFiles).map((path) => fetchJson(path)));

  const data = {};
  keys.forEach((key, i) => {
    data[key] = results[i];
  });

  return {
    data,
    source: "Fichiers JSON Statiques",
  };
}

async function loadAppData() {
  const apiData = await fetchJson(`${API_BASE_URL}/api/data`);
  try {
    const ndviClasses = await fetchJson(`/data/ndvi_classes_metadata.json`);
    apiData.ndviClasses = ndviClasses;
  } catch (e) {
    console.warn("ndviclasses non trouvées", e);
  }
  return {
    data: apiData,
    source: "Base PostgreSQL via API Python",
  };
}

function App() {
  const [activeTab, setActiveTab] = React.useState("overview");
  const [selectedCommune, setSelectedCommune] = React.useState("MG1102");
  const [selectedRegion, setSelectedRegion] = React.useState("");
  const [data, setData] = React.useState(null);
  const [dataSource, setDataSource] = React.useState("");
  const [apiFallbackMessage, setApiFallbackMessage] = React.useState("");
  const [loadError, setLoadError] = React.useState("");
  const [loading, setLoading] = React.useState(true);
  const [isApiConnected, setIsApiConnected] = React.useState(false);
  const [retryTrigger, setRetryTrigger] = React.useState(0);
  const [theme, setTheme] = React.useState(() => {
    return localStorage.getItem("dynatsimo-theme") || "light";
  });

  React.useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("dynatsimo-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  React.useEffect(() => {
    let ignore = false;

    async function loadData() {
      setLoading(true);
      setLoadError("");
      try {
        const result = await loadAppData();
        if (!ignore) {
          setData(result.data);
          setDataSource(result.source);
          setApiFallbackMessage("");
          setIsApiConnected(true);
        }
      } catch (error) {
        console.warn("Python API failed, trying static files...", error);
        try {
          const result = await loadStaticData();
          if (!ignore) {
            setData(result.data);
            setDataSource(result.source);
            setApiFallbackMessage("Serveur API hors-ligne (mode secours)");
            setIsApiConnected(false);
          }
        } catch (staticError) {
          if (!ignore) {
            setLoadError(
              `Erreur lors du chargement des données. API : ${error.message}. Fichiers locaux : ${staticError.message}`
            );
          }
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    loadData();

    return () => {
      ignore = true;
    };
  }, [retryTrigger]);

  React.useEffect(() => {
    if (!selectedCommune && data?.communes?.length > 0) {
      setSelectedCommune(data.communes[0].code);
    }
  }, [data, selectedCommune]);

  if (loadError) {
    return (
      <div className="state-screen">
        <strong>Erreur de chargement</strong>
        <p>{loadError}</p>
        <button onClick={() => setRetryTrigger((prev) => prev + 1)}>Réessayer</button>
      </div>
    );
  }

  if (loading || !data) {
    return (
      <div className="state-screen">
        <div className="loader-spinner"></div>
        <strong>Dynatsimo</strong>
        <p>Connexion à la base de données et chargement des ressources...</p>
      </div>
    );
  }

  const filteredCommunesList = selectedRegion
    ? data.communes.filter((c) => c.region === selectedRegion)
    : data.communes;

  const currentCommune = selectedCommune || filteredCommunesList[0]?.code || "";
  const selectedCommuneObj =
    data.communes.find((commune) => commune.code === currentCommune) || data.communes[0];
  const selectedCommuneName = selectedCommuneObj?.nom ?? "Commune";

  const regionsList = [...new Set(data.communes.map((c) => c.region).filter(Boolean))].sort();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="brand">
            <span className="brand-mark">D</span>
            <div>
              <strong>DYNATSIMO</strong>
              <span>Gestion Agro-Végétale</span>
            </div>
          </div>

          <nav className="nav-list" aria-label="Navigation principale">
            {tabs.map((tab) => {
              let Icon = Icons.Overview;
              if (tab.id === "vegetation") Icon = Icons.Leaf;
              if (tab.id === "saison") Icon = Icons.Rain;
              if (tab.id === "stats") Icon = Icons.Stats;
              if (tab.id === "carte") Icon = Icons.Map;
              if (tab.id === "sensors") Icon = Icons.Layers;
              if (tab.id === "data") Icon = Icons.Database;

              return (
                <button
                  key={tab.id}
                  className={activeTab === tab.id ? "nav-item active" : "nav-item"}
                  onClick={() => setActiveTab(tab.id)}
                  type="button"
                >
                  <Icon />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="sidebar-footer">
          <div
            style={{
              fontSize: "10px",
              color: "var(--text-light)",
              fontWeight: "500",
              textAlign: "center",
            }}
          >
            Dynatsimo v2.1.0 (R-Aligned)
          </div>
        </div>
      </aside>

      <div className="main-stage">
        <header className="navbar-top">
          <div className="breadcrumb">
            <span>Dynatsimo</span>
            <span className="breadcrumb-separator">/</span>
            <span className="breadcrumb-active">{tabs.find((t) => t.id === activeTab)?.label}</span>
          </div>

          <div className="navbar-right">
            <div className="status-badge">
              <span className={`status-dot ${isApiConnected ? "api" : "static"}`}></span>
              <span style={{ color: "var(--text-main)", marginLeft: "4px" }}>
                {isApiConnected ? "Base PostgreSQL" : "Fichiers Statiques"}
              </span>
              {!isApiConnected && (
                <button
                  className="api-retry-btn"
                  onClick={() => setRetryTrigger((prev) => prev + 1)}
                >
                  Reconnexion
                </button>
              )}
            </div>

            <button
              onClick={toggleTheme}
              className="theme-toggle-btn"
              type="button"
              title={theme === "light" ? "Mode Sombre" : "Mode Clair"}
            >
              {theme === "light" ? <Icons.Moon /> : <Icons.Sun />}
            </button>

            <div className="profile-badge">
              <div className="avatar">FD</div>
              <div className="avatar-info">
                <span className="avatar-name">Fandresena</span>
                <span className="avatar-role">Administrateur</span>
              </div>
            </div>
          </div>
        </header>

        <div className="stage-content">
          {activeTab === "overview" && (
            <Overview
              annualData={data.annualData}
              communes={data.communes}
              overview={data.overview}
              vegData={data.vegetationData}
            />
          )}
          {activeTab === "vegetation" && (
            <SuiviVegetation
              communes={data.communes}
              regions={regionsList}
              selectedRegion={selectedRegion}
              setSelectedRegion={setSelectedRegion}
              selectedCommune={currentCommune}
              setSelectedCommune={setSelectedCommune}
              selectedCommuneName={selectedCommuneName}
              vegData={data.vegetationData}
            />
          )}
          {activeTab === "saison" && (
            <Saison
              communes={filteredCommunesList}
              regions={regionsList}
              selectedRegion={selectedRegion}
              setSelectedRegion={setSelectedRegion}
              seasonData={data.seasonData}
              selectedCommune={currentCommune}
              selectedCommuneName={selectedCommuneName}
              setSelectedCommune={setSelectedCommune}
            />
          )}
          {activeTab === "stats" && (
            <Statistiques
              communes={data.communes}
              annualData={data.annualData}
              seasonData={data.seasonData}
              monthlyClimatology={data.monthlyClimatology}
              anomalies={data.anomalies}
              precipRecords={data.precipRecords}
            />
          )}
          {activeTab === "carte" && (
            <Carte
              geojson={data.communesGeojson}
              communes={data.communes}
              precipRecords={data.precipRecords}
              annualData={data.annualData}
              ndviClasses={data.ndviClasses}
            />
          )}
          {activeTab === "sensors" && (
            <ComparaisonCapteurs vegData={data.vegetationData} selectedCommune={currentCommune} />
          )}
          {activeTab === "data" && (
            <TableauExplorer geojson={data.communesGeojson} communesList={data.communes} />
          )}
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value, type }) {
  let Icon = Icons.Overview;
  if (type === "communes") Icon = Icons.Map;
  if (type === "years") Icon = Icons.Stats;
  if (type === "records") Icon = Icons.Database;
  if (type === "ndvi") Icon = Icons.Leaf;

  return (
    <article className="metric-card">
      <div className="metric-icon-wrap">
        <Icon />
      </div>
      <div className="metric-info">
        <strong>{value}</strong>
        <span>{label}</span>
      </div>
    </article>
  );
}

function Overview({ annualData, communes, overview, vegData }) {
  const [polyOrder, setPolyOrder] = React.useState(4);

  const computedTrendData = React.useMemo(() => {
    if (!annualData || annualData.length === 0) return [];
    const years = annualData.map((d) => d.year);
    const precipVals = annualData.map((d) => d.precip);
    const polyFits = polyFit(years, precipVals, polyOrder);

    return annualData.map((d, i) => ({
      ...d,
      trend: polyFits[i],
    }));
  }, [annualData, polyOrder]);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="recharts-custom-tooltip">
          <p className="recharts-custom-tooltip-title">Année {payload[0].payload.year}</p>
          <div className="recharts-custom-tooltip-item">
            <span>Pluie moyenne :</span>
            <span>{payload[0].value.toLocaleString("fr-FR")} mm</span>
          </div>
          {payload[1] && (
            <div className="recharts-custom-tooltip-item">
              <span>Tendance (Ordre {polyOrder}) :</span>
              <span>{payload[1].value.toLocaleString("fr-FR")} mm</span>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  const avgNDVI = React.useMemo(() => {
    if (!vegData?.ecoregions) return "0.38";
    const average = averageFinite(
      Object.values(vegData.ecoregions).map((e) => e?.baselineNdvi?.[5]),
      2,
      0.38
    );
    return average.toFixed(2);
  }, [vegData]);

  return (
    <>
      <section className="metric-grid">
        <Metric
          label="Communes Suivies"
          value={overview.nb_communes ?? communes.length}
          type="communes"
        />
        <Metric label="NDVI Moyen (Pic)" value={avgNDVI} type="ndvi" />
        <Metric label="Historique Données" value={overview.nb_years} type="years" />
      </section>

      <div className="info-bulletin">
        <strong>À propos de Dynatsimo v2.1 :</strong> Plateforme d'analyse agro-pluviométrique et de l'état de la végétation alignée avec la méthodologie R (CHIRPS & PostgreSQL).
      </div>

      <section className="panel">
        <div className="panel-heading" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h2>
              <Icons.Stats /> Précipitations annuelles moyennes (1981–2025)
            </h2>
            <span>Tendance des précipitations annuelles moyennes (poly ordre {polyOrder})</span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <label htmlFor="poly-order-sel" style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "600" }}>Ordre de tendance :</label>
            <select
              id="poly-order-sel"
              value={polyOrder}
              onChange={(e) => setPolyOrder(Number(e.target.value))}
              style={{ padding: "4px 8px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", fontSize: "12px" }}
            >
              <option value={1}>1 (Linéaire)</option>
              <option value={2}>2 (Quadratique)</option>
              <option value={3}>3 (Cubique)</option>
              <option value={4}>4 (Polynomiale R - Défaut)</option>
              <option value={5}>5 (Degré 5)</option>
            </select>
          </div>
        </div>

        <div style={{ width: "100%", height: 320 }}>
          <ResponsiveContainer>
            <ComposedChart
              data={computedTrendData}
              margin={{ top: 20, right: 20, bottom: 20, left: 10 }}
            >
              <defs>
                <linearGradient id="colorPrecip" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="var(--primary)" stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
              <XAxis dataKey="year" stroke="var(--text-muted)" fontSize={12} dy={10} />
              <YAxis stroke="var(--text-muted)" fontSize={12} unit=" mm" dx={-10} />
              <RechartsTooltip content={<CustomTooltip />} />
              <Legend verticalAlign="top" height={36} />
              <Bar
                name="Précipitations moyennes (mm)"
                dataKey="precip"
                fill="url(#colorPrecip)"
                radius={[4, 4, 0, 0]}
                barSize={20}
              />
              <Line
                name={`Tendance polynomiale (Ordre ${polyOrder})`}
                type="monotone"
                dataKey="trend"
                stroke="var(--danger)"
                strokeWidth={2.8}
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </section>
    </>
  );
}

function SuiviVegetation({
  communes,
  regions,
  selectedRegion,
  setSelectedRegion,
  selectedCommune,
  setSelectedCommune,
  selectedCommuneName,
  vegData,
}) {
  const [selectedDistrict, setSelectedDistrict] = React.useState("");
  const [selectedEcoregionTab, setSelectedEcoregionTab] = React.useState("spiny");
  const [activeSeason, setActiveSeason] = React.useState("2024-2025");
  const [activeSensor, setActiveSensor] = React.useState("modis");

  const districtsList = React.useMemo(() => {
    const list = communes
      .filter((c) => !selectedRegion || c.region === selectedRegion)
      .map((c) => c.district)
      .filter(Boolean);
    return [...new Set(list)].sort();
  }, [communes, selectedRegion]);

  React.useEffect(() => {
    setSelectedDistrict("");
  }, [selectedRegion]);

  const filteredCommunesDropdown = React.useMemo(() => {
    return communes.filter((c) => {
      if (selectedRegion && c.region !== selectedRegion) return false;
      if (selectedDistrict && c.district !== selectedDistrict) return false;
      return true;
    });
  }, [communes, selectedRegion, selectedDistrict]);

  React.useEffect(() => {
    if (
      filteredCommunesDropdown.length > 0 &&
      !filteredCommunesDropdown.some((c) => c.code === selectedCommune)
    ) {
      setSelectedCommune(filteredCommunesDropdown[0].code);
    }
  }, [filteredCommunesDropdown, selectedCommune]);

  const activeCommuneObj = communes.find((c) => c.code === selectedCommune) || communes[0];
  const activeEcoregion = activeCommuneObj?.ecoregion || "spiny";
  const activeEcoregionDetails = vegData?.ecoregions?.[activeEcoregion] || {
    id: activeEcoregion,
    name: "Forêt Épineuse",
    description: "Sub-aride",
    baselineNdvi: Array(12).fill(0.3),
    classificationDistrib: {
      foret_dense: 20,
      foret_degradee: 50,
      fourre: 20,
      culture: 8,
      sol_nu: 2,
    },
  };

  const activeCommuneSeries = React.useMemo(() => {
    if (vegData?.timeSeries?.[activeSensor]) {
      const series = vegData.timeSeries[activeSensor][selectedCommune];
      return Array.isArray(series) ? series : [];
    }
    const series = vegData?.timeSeries?.[selectedCommune];
    return Array.isArray(series) ? series : [];
  }, [vegData, selectedCommune, activeSensor]);

  const seasonsList = React.useMemo(
    () => activeCommuneSeries.map((s) => s?.season).filter(Boolean),
    [activeCommuneSeries]
  );

  React.useEffect(() => {
    if (seasonsList.length > 0 && !seasonsList.includes(activeSeason)) {
      setActiveSeason(seasonsList[seasonsList.length - 1]);
    } else if (seasonsList.length === 0 && activeSeason !== "") {
      setActiveSeason("");
    }
  }, [seasonsList, activeSeason]);

  const activeSeasonData =
    activeCommuneSeries.find((s) => s.season === activeSeason) ||
    activeCommuneSeries[activeCommuneSeries.length - 1];

  const chartData = React.useMemo(() => {
    if (!activeSeasonData) return [];
    const months = ["Oct", "Nov", "Dec", "Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep"];
    const baseline = Array.isArray(activeSeasonData.baseline)
      ? activeSeasonData.baseline
      : Array.isArray(activeEcoregionDetails.baselineNdvi)
      ? activeEcoregionDetails.baselineNdvi
      : Array(12).fill(0.3);
    const ndvi = Array.isArray(activeSeasonData.ndvi) ? activeSeasonData.ndvi : [];
    const cumulative = Array.isArray(activeSeasonData.cumulative) ? activeSeasonData.cumulative : [];
    const anomalies = Array.isArray(activeSeasonData.anomalies) ? activeSeasonData.anomalies : [];

    return months.map((m, idx) => ({
      month: m,
      ndvi: toFiniteNumber(ndvi[idx], 0),
      baseline: toFiniteNumber(baseline[idx], 0),
      cumulative: toFiniteNumber(cumulative[idx], 0),
      anomalies: toFiniteNumber(anomalies[idx], 0),
    }));
  }, [activeSeasonData, activeEcoregionDetails]);

  const anomalyValues = Array.isArray(activeSeasonData?.anomalies) ? activeSeasonData.anomalies : [];
  const anomalyPercent = (averageFinite(anomalyValues, 4, 0) ?? 0) * 100;
  let alertLevel = "stable";
  let alertText = "Normal / Stable";
  if (anomalyPercent < -15) {
    alertLevel = "danger";
    alertText = "Alerte Rouge - Dégradation Sévère";
  } else if (anomalyPercent < -6) {
    alertLevel = "vigilance";
    alertText = "Vigilance - Sécheresse Végétale modérée";
  }

  return (
    <section className="split-layout">
      <aside className="filters-panel">
        <h2>Localisation</h2>

        <div className="filter-group">
          <label htmlFor="region-sel">Région</label>
          <select id="region-sel" value={selectedRegion} onChange={(e) => setSelectedRegion(e.target.value)}>
            <option value="">Toutes les régions</option>
            {regions.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="district-sel">District</label>
          <select id="district-sel" value={selectedDistrict} onChange={(e) => setSelectedDistrict(e.target.value)}>
            <option value="">Tous les districts</option>
            {districtsList.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="commune-sel">Commune</label>
          <select id="commune-sel" value={selectedCommune} onChange={(e) => setSelectedCommune(e.target.value)}>
            {filteredCommunesDropdown.map((c) => (
              <option key={c.code} value={c.code}>{c.nom} ({c.code})</option>
            ))}
          </select>
        </div>

        <div className="filter-group" style={{ marginTop: "12px", borderTop: "1px solid var(--border-color)", paddingTop: "8px" }}>
          <label htmlFor="season-sel">Campagne (Saison)</label>
          <select id="season-sel" value={activeSeason} onChange={(e) => setActiveSeason(e.target.value)}>
            {seasonsList.length === 0 ? (
              <option value="">Aucune saison disponible</option>
            ) : (
              seasonsList.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))
            )}
          </select>
        </div>

        <div className="filter-group" style={{ marginTop: "12px", borderTop: "1px solid var(--border-color)", paddingTop: "8px" }}>
          <label htmlFor="sensor-sel">Capteur (Végétation)</label>
          <select id="sensor-sel" value={activeSensor} onChange={(e) => setActiveSensor(e.target.value)}>
            <option value="modis">MODIS (250m)</option>
            <option value="landsat">Landsat (30m)</option>
            <option value="sentinel">Sentinel-2 (10m)</option>
          </select>
        </div>
      </aside>

      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        <section className="metric-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
          <article className="metric-card">
            <div className="metric-icon-wrap" style={{ color: "var(--accent)" }}><Icons.Leaf /></div>
            <div className="metric-info">
              <strong>{activeCommuneObj?.nom}</strong>
              <span>Commune activée</span>
            </div>
          </article>
          <article className="metric-card">
            <div className="metric-icon-wrap" style={{ color: "var(--warning)" }}><Icons.Layers /></div>
            <div className="metric-info">
              <strong>{activeEcoregionDetails.name}</strong>
              <span>Écorégion dominante</span>
            </div>
          </article>
          <article className="metric-card">
            <div className="metric-icon-wrap" style={{ color: alertLevel === "danger" ? "var(--danger)" : alertLevel === "vigilance" ? "var(--warning)" : "var(--accent)" }}>
              <Icons.Alert />
            </div>
            <div className="metric-info">
              <strong style={{ color: alertLevel === "danger" ? "var(--danger)" : alertLevel === "vigilance" ? "var(--warning)" : "var(--accent)", fontSize: "14px" }}>
                {alertText}
              </strong>
              <span>Système d'Alerte Auto</span>
            </div>
          </article>
        </section>
        <div className="panel">
          <div className="panel-heading">
            <h2><Icons.Stats /> Profil de Santé Végétale NDVI - Saison {activeSeasonData?.season ?? activeSeason}</h2>
            <span>NDVI mesuré vs normal</span>
          </div>
          <div style={{ width: "100%", height: 250 }}>
            <ResponsiveContainer>
              <ComposedChart data={chartData} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={11} />
                <YAxis stroke="var(--text-muted)" fontSize={11} domain={[0, 0.8]} />
                <RechartsTooltip />
                <Legend verticalAlign="top" height={36} />
                <Line name="NDVI Normal (Baseline)" type="monotone" dataKey="baseline" stroke="var(--text-light)" strokeWidth={2} dot={false} strokeDasharray="4 4" />
                <Area name="NDVI Observé" type="monotone" dataKey="ndvi" fill="rgba(16, 185, 129, 0.15)" stroke="var(--accent)" strokeWidth={3} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Secondary Charts: Cumulative (Integrated Productivity) & Anomalies */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
          <div className="panel">
            <div className="panel-heading">
              <h3>NDVI Cumulé (Productivité Saisonnière Brute)</h3>
            </div>
            <div style={{ width: "100%", height: 200 }}>
              <ResponsiveContainer>
                <AreaChart data={chartData} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={11} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} />
                  <RechartsTooltip />
                  <Area
                    name="Cumul NDVI"
                    type="monotone"
                    dataKey="cumulative"
                    stroke="var(--primary)"
                    fill="rgba(37, 99, 235, 0.1)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="panel">
            <div className="panel-heading">
              <h3>Écart NDVI mensuel à la normale</h3>
            </div>
            <div style={{ width: "100%", height: 200 }}>
              <ResponsiveContainer>
                <RechartsBarChart data={chartData} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={11} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} />
                  <RechartsTooltip />
                  <Bar name="Anomalie NDVI" dataKey="anomalies">
                    {chartData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.anomalies >= 0 ? "var(--accent)" : "var(--danger)"}
                      />
                    ))}
                  </Bar>
                </RechartsBarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Ecoregions Classification Info Panel */}
        <div className="panel">
          <div className="panel-heading">
            <h2>
              <Icons.Layers /> Reconnaissance automatique de l'Occupation du Sol par Écorégion
            </h2>
            <span>Classification spectrale automatique (2025)</span>
          </div>

          <div className="ecoregion-grid">
            {vegData &&
              vegData.ecoregions &&
              Object.values(vegData.ecoregions).map((eco) => {
                const isActive = eco.id === activeEcoregion;
                const distrib = eco.classificationDistrib || {};
                return (
                  <div
                    key={eco.id}
                    className={`ecoregion-card ${isActive ? "active" : ""}`}
                    onClick={() => setSelectedEcoregionTab(eco.id)}
                  >
                    <div className="ecoregion-header">
                      <span className="ecoregion-name">{eco.name}</span>
                      {eco.id === activeEcoregion && (
                        <span className="alert-badge stable" style={{ fontSize: "8px" }}>
                          Actuelle
                        </span>
                      )}
                    </div>
                    <p className="ecoregion-desc">{eco.description}</p>

                    <div>
                      <div className="distrib-bar-container">
                        <div
                          className="distrib-bar-segment segment-forest"
                          style={{ width: `${distrib.foret_dense}%` }}
                          title={`Forêt Dense: ${toFiniteNumber(distrib.foret_dense, 0)}%`}
                        ></div>
                        <div
                          className="distrib-bar-segment segment-degraded"
                          style={{ width: `${distrib.foret_degradee}%` }}
                          title={`Forêt Dégradée: ${toFiniteNumber(distrib.foret_degradee, 0)}%`}
                        ></div>
                        <div
                          className="distrib-bar-segment segment-thicket"
                          style={{ width: `${distrib.fourre}%` }}
                          title={`Fourré: ${toFiniteNumber(distrib.fourre, 0)}%`}
                        ></div>
                        <div
                          className="distrib-bar-segment segment-crops"
                          style={{ width: `${distrib.culture}%` }}
                          title={`Cultures: ${toFiniteNumber(distrib.culture, 0)}%`}
                        ></div>
                        <div
                          className="distrib-bar-segment segment-soil"
                          style={{ width: `${distrib.sol_nu}%` }}
                          title={`Sols nus/autres: ${toFiniteNumber(distrib.sol_nu, 0)}%`}
                        ></div>
                      </div>

                      <div className="distrib-legend">
                        <div className="legend-item">
                          <span className="legend-color segment-forest"></span> F. Dense (
                          {distrib.foret_dense}%)
                        </div>
                        <div className="legend-item">
                          <span className="legend-color segment-degraded"></span> F. Dégr (
                          {distrib.foret_degradee}%)
                        </div>
                        <div className="legend-item">
                          <span className="legend-color segment-thicket"></span> Fourré (
                          {distrib.fourre}%)
                        </div>
                        <div className="legend-item">
                          <span className="legend-color segment-crops"></span> Cult. (
                          {distrib.culture}%)
                        </div>
                        <div className="legend-item">
                          <span className="legend-color segment-soil"></span> Nu ({distrib.sol_nu}%)
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      </div>
    </section>
  );
}

// Saison Component matching R script sub-tabs and controls
function Saison({
  communes,
  regions,
  selectedRegion,
  setSelectedRegion,
  seasonData,
  selectedCommune,
  setSelectedCommune,
  selectedCommuneName,
}) {
  const [searchTerm, setSearchTerm] = React.useState("");
  const [subTab, setSubTab] = React.useState("start_end"); // 'start_end', 'max_month', 'timeline'

  // Min and Max season slider state
  const availableSeasons = React.useMemo(() => {
    const list = seasonData.map((s) => Number(s.saison)).filter((s) => Number.isFinite(s));
    return list.length ? [Math.min(...list), Math.max(...list)] : [1981, 2025];
  }, [seasonData]);

  const [seasonRange, setSeasonRange] = React.useState([1981, 2025]);

  React.useEffect(() => {
    setSeasonRange(availableSeasons);
  }, [availableSeasons]);

  const searchedCommunes = React.useMemo(() => {
    return communes.filter(
      (c) =>
        c.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.code.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [communes, searchTerm]);

  // Filter season rows for selected commune & season range
  const filteredSeasonRows = React.useMemo(() => {
    return seasonData.filter(
      (row) =>
        row.code_commune === selectedCommune &&
        Number(row.saison) >= seasonRange[0] &&
        Number(row.saison) <= seasonRange[1]
    );
  }, [seasonData, selectedCommune, seasonRange]);

  const hydroMonths = ["Oct", "Nov", "Dec", "Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep"];
  const monthOrderMap = { Oct: 10, Nov: 11, Dec: 12, Jan: 1, Fev: 2, Mar: 3, Avr: 4, Mai: 5, Jun: 6, Jul: 7, Aou: 8, Sep: 9 };
  const monthToVal = { Oct: 10, Nov: 11, Dec: 12, Jan: 13, Fev: 14, Mar: 15, Avr: 16, Mai: 17, Jun: 18 };

  // Data for "Début et fin de saison" chart
  const startEndChartData = React.useMemo(() => {
    return filteredSeasonRows.map((r) => {
      const debutVal = monthToVal[r.debut] || 10;
      let finVal = monthToVal[r.fin] || 15;
      if (finVal < debutVal) finVal += 12;
      return {
        saison: r.saison,
        debut: debutVal,
        fin: finVal,
        debutLabel: r.debut || "Oct",
        finLabel: r.fin || "Mar",
        duree: r.duree || 6,
      };
    });
  }, [filteredSeasonRows]);

  // Month colors for "Mois le plus pluvieux" chart matching R script brewer colors
  const monthColors = {
    Nov: "#1f78b4",
    Dec: "#33a02c",
    Jan: "#e31a1c",
    Fev: "#ff7f00",
    Mar: "#6a3d9a",
    Avr: "#b15928",
  };

  return (
    <section className="split-layout">
      <aside className="filters-panel">
        <h2>Paramètres Saison</h2>

        <div className="filter-group">
          <label htmlFor="region-filter">Région</label>
          <select
            id="region-filter"
            value={selectedRegion}
            onChange={(e) => {
              setSelectedRegion(e.target.value);
              setSelectedCommune("");
            }}
          >
            <option value="">Toutes les régions</option>
            {regions.map((reg) => (
              <option key={reg} value={reg}>{reg}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="search-commune">Chercher Commune</label>
          <input
            id="search-commune"
            type="text"
            placeholder="Nom ou code..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="commune-select">Commune</label>
          <select
            id="commune-select"
            value={selectedCommune}
            onChange={(e) => setSelectedCommune(e.target.value)}
          >
            {searchedCommunes.length === 0 ? (
              <option value="">Aucune commune trouvée</option>
            ) : (
              searchedCommunes.map((c) => (
                <option key={c.code} value={c.code}>
                  {c.nom} ({c.code})
                </option>
              ))
            )}
          </select>
        </div>

        {/* Range filter slider for agricultural seasons */}
        <div className="filter-group" style={{ marginTop: "16px", borderTop: "1px solid var(--border-color)", paddingTop: "12px" }}>
          <label style={{ fontWeight: "700" }}>Filtrer saisons agricoles :</label>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
            <span>{seasonRange[0]}</span>
            <span>{seasonRange[1]}</span>
          </div>
          <div style={{ display: "flex", gap: "8px", marginTop: "6px" }}>
            <input
              type="number"
              min={availableSeasons[0]}
              max={seasonRange[1]}
              value={seasonRange[0]}
              onChange={(e) => setSeasonRange([Math.max(availableSeasons[0], Number(e.target.value)), seasonRange[1]])}
              style={{ width: "50%", padding: "4px 6px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", fontSize: "12px" }}
            />
            <input
              type="number"
              min={seasonRange[0]}
              max={availableSeasons[1]}
              value={seasonRange[1]}
              onChange={(e) => setSeasonRange([seasonRange[0], Math.min(availableSeasons[1], Number(e.target.value))])}
              style={{ width: "50%", padding: "4px 6px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", fontSize: "12px" }}
            />
          </div>
        </div>
      </aside>

      <div className="panel">
        <div className="panel-heading" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h2><Icons.Rain /> Saison des pluies - {selectedCommuneName}</h2>
            <span>Début, durée et mois le plus pluvieux</span>
          </div>

          {/* Sub-tabs matching R script */}
          <div className="scale-tabs">
            <button
              className={`scale-tab-btn ${subTab === "start_end" ? "active" : ""}`}
              onClick={() => setSubTab("start_end")}
            >
              Début et fin
            </button>
            <button
              className={`scale-tab-btn ${subTab === "max_month" ? "active" : ""}`}
              onClick={() => setSubTab("max_month")}
            >
              Mois pluvieux
            </button>
            <button
              className={`scale-tab-btn ${subTab === "timeline" ? "active" : ""}`}
              onClick={() => setSubTab("timeline")}
            >
              Chronogramme
            </button>
          </div>
        </div>

        {filteredSeasonRows.length === 0 ? (
          <div className="placeholder">
            <Icons.Info />
            <strong>Aucune donnée</strong>
            <p>Aucune donnée saisonnière disponible pour les filtres sélectionnés.</p>
          </div>
        ) : (
          <>
            {subTab === "start_end" && (
              <div style={{ width: "100%", height: 360, marginTop: "12px" }}>
                <ResponsiveContainer>
                  <ComposedChart data={startEndChartData} margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                    <XAxis dataKey="saison" stroke="var(--text-muted)" fontSize={11} angle={-45} textAnchor="end" height={50} />
                    <YAxis
                      domain={[10, 17]}
                      ticks={[10, 11, 12, 13, 14, 15, 16, 17]}
                      tickFormatter={(val) => {
                        const labels = { 10: "Oct", 11: "Nov", 12: "Déc", 13: "Jan", 14: "Fév", 15: "Mar", 16: "Avr", 17: "Mai" };
                        return labels[val] || val;
                      }}
                      stroke="var(--text-muted)"
                      fontSize={11}
                    />
                    <RechartsTooltip
                      formatter={(val, name, entry) => [
                        name === "debut" ? entry.payload.debutLabel : entry.payload.finLabel,
                        name === "debut" ? "Mois Début" : "Mois Fin",
                      ]}
                    />
                    <Legend verticalAlign="top" height={36} />
                    <Line name="Mois de Début (Bleu)" type="monotone" dataKey="debut" stroke="#1f78b4" strokeWidth={2} dot={{ r: 4, fill: "#1f78b4" }} />
                    <Line name="Mois de Fin (Vert)" type="monotone" dataKey="fin" stroke="#33a02c" strokeWidth={2} dot={{ r: 4, fill: "#33a02c" }} />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            )}

            {subTab === "max_month" && (
              <div style={{ width: "100%", height: 360, marginTop: "12px" }}>
                <ResponsiveContainer>
                  <RechartsBarChart data={filteredSeasonRows} margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                    <XAxis dataKey="saison" stroke="var(--text-muted)" fontSize={11} angle={-45} textAnchor="end" height={50} />
                    <YAxis stroke="var(--text-muted)" fontSize={11} unit=" mm" />
                    <RechartsTooltip
                      formatter={(val, name, entry) => [
                        `${val || 0} mm (${entry.payload.mois_plus_pluvieux || "N/A"})`,
                        "Précip. Mois Max",
                      ]}
                    />
                    <Bar name="Précipitation Mois Max" dataKey="precip" radius={[4, 4, 0, 0]}>
                      {filteredSeasonRows.map((entry, idx) => (
                        <Cell
                          key={`cell-${idx}`}
                          fill={monthColors[entry.mois_plus_pluvieux] || "#2563eb"}
                        />
                      ))}
                    </Bar>
                  </RechartsBarChart>
                </ResponsiveContainer>
              </div>
            )}

            {subTab === "timeline" && (
              <div className="timeline" style={{ marginTop: "12px" }}>
                {filteredSeasonRows.map((row) => {
                  const startIdx = hydroMonths.indexOf(row.debut);
                  const endIdx = hydroMonths.indexOf(row.fin);

                  const isValidRange = startIdx !== -1 && endIdx !== -1;
                  const cellWidth = 100 / hydroMonths.length;

                  let leftPercent = 0;
                  let widthPercent = 100;
                  if (isValidRange) {
                    leftPercent = startIdx * cellWidth;
                    widthPercent = (endIdx - startIdx + 1) * cellWidth;
                    if (endIdx < startIdx) {
                      widthPercent = (hydroMonths.length - startIdx + endIdx + 1) * cellWidth;
                    }
                  }

                  return (
                    <div className="timeline-row" key={`${row.code_commune}-${row.saison}`}>
                      <span>Saison {row.saison}</span>

                      <div style={{ display: "flex", flexDirection: "column", width: "100%" }}>
                        <div className="timeline-track-container">
                          <div className="timeline-track-bg"></div>
                          <div
                            className="timeline-track-fill"
                            style={{ left: `${leftPercent}%`, width: `${widthPercent}%`, minWidth: "12px" }}
                            title={`Du ${row.debut} au ${row.fin} (${row.duree} mois)`}
                          ></div>
                        </div>

                        <div className="timeline-labels">
                          {hydroMonths.map((m) => (
                            <span key={m}>{m}</span>
                          ))}
                        </div>
                      </div>

                      <div className="timeline-duration">
                        <strong>{row.duree} mois</strong>
                        <div style={{ fontSize: "11px", color: "var(--text-light)", fontWeight: "500", marginTop: "4px" }}>
                          Max : {row.mois_plus_pluvieux ? `${row.mois_plus_pluvieux}` : "N/A"}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </>
        )}
      </div>
    </section>
  );
}

// Dedicated Statistiques Component matching R script tab
function Statistiques({
  communes,
  annualData,
  seasonData,
  monthlyClimatology,
  anomalies,
  precipRecords = [],
}) {
  const [modeCommune, setModeCommune] = React.useState("Toutes les communes");
  const [selectedCommune, setSelectedCommune] = React.useState(communes[0]?.code || "");
  const [typeGraph, setTypeGraph] = React.useState("Histogramme");
  const [ordrePoly, setOrdrePoly] = React.useState(4);

  const selectedCommuneObj = React.useMemo(() => {
    return communes.find((c) => c.code === selectedCommune) || communes[0];
  }, [communes, selectedCommune]);

  const titreStats = modeCommune === "Toutes les communes" ? "Toutes les communes" : (selectedCommuneObj?.nom || selectedCommune);

  // Robust Resolution of Commune Annual Precipitation Series
  const communeAnnualSeries = React.useMemo(() => {
    if (modeCommune === "Toutes les communes") {
      return annualData.map((d) => ({ year: d.year, p: d.precip }));
    }

    const cCode = String(selectedCommune || "").trim().toUpperCase();
    const cNom = selectedCommuneObj?.nom?.toLowerCase() || "";

    if (seasonData && seasonData.length > 0) {
      const matched = seasonData.filter((r) => {
        if (!r) return false;
        const rCode = String(r.code_commune || "").trim().toUpperCase();
        if (rCode && cCode && (rCode === cCode || cCode.includes(rCode))) return true;
        if (r.commune && cNom && String(r.commune).toLowerCase() === cNom) return true;
        return false;
      });

      if (matched.length > 0) {
        const dict = {};
        matched.forEach((r) => {
          const yr = Number(r.saison);
          if (yr >= 1981 && yr <= 2025 && Number.isFinite(Number(r.precip))) {
            dict[yr] = Number(r.precip);
          }
        });
        const years = Object.keys(dict).map(Number).sort((a, b) => a - b);
        if (years.length > 0) {
          return years.map((yr) => ({ year: yr, p: dict[yr] }));
        }
      }
    }

    if (precipRecords && precipRecords.length > 0) {
      const matched = precipRecords.filter((r) => r.code === selectedCommune);
      if (matched.length > 0) {
        const dict = {};
        matched.forEach((r) => {
          dict[r.year] = (dict[r.year] || 0) + r.precip;
        });
        const years = Object.keys(dict).map(Number).sort((a, b) => a - b);
        return years.map((yr) => ({ year: yr, p: Math.round(dict[yr]) }));
      }
    }

    return annualData.map((d) => ({ year: d.year, p: d.precip }));
  }, [modeCommune, selectedCommune, selectedCommuneObj, seasonData, precipRecords, annualData]);

  // Annual Trend & Polynomial Regression Fit
  const trendData = React.useMemo(() => {
    if (communeAnnualSeries.length === 0) return [];
    const years = communeAnnualSeries.map((d) => d.year);
    const vals = communeAnnualSeries.map((d) => d.p);
    const polyFits = polyFit(years, vals, ordrePoly);

    return communeAnnualSeries.map((d, i) => ({
      year: d.year,
      p: d.p,
      trend: polyFits[i],
    }));
  }, [communeAnnualSeries, ordrePoly]);

  // Monthly Climatology (Jan..Dec)
  const climatologyData = React.useMemo(() => {
    const monthNames = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"];

    if (precipRecords && precipRecords.length > 0) {
      const filtered = modeCommune === "Toutes les communes"
        ? precipRecords
        : precipRecords.filter((r) => r.code === selectedCommune);

      if (filtered.length > 0) {
        const dict = {};
        for (let m = 1; m <= 12; m++) dict[m] = [];
        filtered.forEach((r) => {
          if (r.month >= 1 && r.month <= 12 && Number.isFinite(r.precip)) {
            dict[r.month].push(r.precip);
          }
        });
        return monthNames.map((m, idx) => {
          const vals = dict[idx + 1] || [];
          const mean = vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
          return { month: m, p: Math.round(mean * 10) / 10 };
        });
      }
    }

    if (modeCommune === "Toutes les communes" && monthlyClimatology) {
      return monthlyClimatology.map((d) => ({ month: d.month, p: d.precip }));
    }

    const meanAnn = communeAnnualSeries.reduce((a, b) => a + b.p, 0) / (communeAnnualSeries.length || 1);
    const weights = { Jan: 0.26, Fév: 0.22, Mar: 0.18, Dec: 0.14, Nov: 0.09, Avr: 0.05, Mai: 0.02, Jun: 0.01, Jul: 0.01, Aoû: 0.01, Sep: 0.01, Oct: 0.00 };
    return monthNames.map((m) => {
      const key = m === "Déc" ? "Dec" : m === "Aoû" ? "Aoû" : m;
      const w = weights[key] || 0.02;
      return { month: m, p: Math.round(meanAnn * w) };
    });
  }, [modeCommune, selectedCommune, precipRecords, monthlyClimatology, communeAnnualSeries]);

  // Annual Anomalies & Baseline SD (1981-2010)
  const { anomalyData, sdClim, meanClim, driestYear } = React.useMemo(() => {
    if (trendData.length === 0) return { anomalyData: [], sdClim: 0, meanClim: 0, driestYear: null };
    const refData = trendData.filter((d) => d.year >= 1981 && d.year <= 2010);
    const refVals = refData.length ? refData.map((d) => d.p) : trendData.map((d) => d.p);

    const mean = refVals.reduce((a, b) => a + b, 0) / refVals.length;
    const variance = refVals.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / refVals.length;
    const sd = Math.sqrt(variance);

    const minItem = [...trendData].sort((a, b) => a.p - b.p)[0];

    const data = trendData.map((d) => ({
      year: d.year,
      anomaly: Math.round(d.p - mean),
      isPositive: d.p - mean >= 0,
      p: d.p,
    }));

    return { anomalyData: data, sdClim: Math.round(sd), meanClim: Math.round(mean), driestYear: minItem };
  }, [trendData]);

  // Histogram Frequency Bins
  const histogramData = React.useMemo(() => {
    const values = communeAnnualSeries.map((d) => d.p).filter((v) => Number.isFinite(v) && v > 0);
    if (values.length === 0) return [];

    const maxVal = Math.max(...values);
    const minVal = Math.min(...values);
    const numBins = 15;
    const binWidth = Math.max(10, Math.ceil((maxVal - minVal) / numBins));

    const bins = Array.from({ length: numBins }, (_, i) => {
      const start = Math.floor(minVal) + i * binWidth;
      const end = start + binWidth;
      return {
        label: `${start}-${end}`,
        count: 0,
      };
    });

    values.forEach((v) => {
      const idx = Math.min(numBins - 1, Math.floor((v - minVal) / binWidth));
      if (bins[idx]) bins[idx].count += 1;
    });

    return bins;
  }, [communeAnnualSeries]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      {/* Top Executive KPI Cards */}
      <section className="metric-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
        <article className="metric-card">
          <div className="metric-icon-wrap" style={{ color: "var(--primary)" }}><Icons.Map /></div>
          <div className="metric-info">
            <strong style={{ fontSize: "14px" }}>{titreStats}</strong>
            <span>{modeCommune === "Toutes les communes" ? "Échelle Régionale" : `District : ${selectedCommuneObj?.district || "N/A"}`}</span>
          </div>
        </article>
        <article className="metric-card">
          <div className="metric-icon-wrap" style={{ color: "var(--accent)" }}><Icons.Stats /></div>
          <div className="metric-info">
            <strong>{meanClim} mm/an</strong>
            <span>Climatologie (1981–2010)</span>
          </div>
        </article>
        <article className="metric-card">
          <div className="metric-icon-wrap" style={{ color: "var(--warning)" }}><Icons.Rain /></div>
          <div className="metric-info">
            <strong>± {sdClim} mm</strong>
            <span>Écart-Type (Variabilité)</span>
          </div>
        </article>
        <article className="metric-card">
          <div className="metric-icon-wrap" style={{ color: "var(--danger)" }}><Icons.Alert /></div>
          <div className="metric-info">
            <strong style={{ color: "var(--danger)" }}>{driestYear ? `${driestYear.year} (${driestYear.p} mm)` : "N/A"}</strong>
            <span>Année la plus sèche (Crise)</span>
          </div>
        </article>
      </section>

      {/* Main Analysis Section with Split Control Panel */}
      <section className="split-layout">
        <aside className="filters-panel">
          <h2>Paramètres Statistiques</h2>

          <div className="filter-group">
            <label style={{ fontWeight: "700" }}>Affichage des communes :</label>
            <div style={{ display: "flex", gap: "6px", marginTop: "8px" }}>
              <button
                className={`scale-tab-btn ${modeCommune === "Toutes les communes" ? "active" : ""}`}
                onClick={() => setModeCommune("Toutes les communes")}
                style={{ flex: 1, padding: "6px 8px", fontSize: "11px" }}
              >
                Toutes
              </button>
              <button
                className={`scale-tab-btn ${modeCommune === "Choisir une commune" ? "active" : ""}`}
                onClick={() => setModeCommune("Choisir une commune")}
                style={{ flex: 1, padding: "6px 8px", fontSize: "11px" }}
              >
                Par Commune
              </button>
            </div>
          </div>

          {modeCommune === "Choisir une commune" && (
            <div className="filter-group" style={{ marginTop: "12px" }}>
              <label htmlFor="commune-stats-sel">Choisir la commune :</label>
              <select
                id="commune-stats-sel"
                value={selectedCommune}
                onChange={(e) => setSelectedCommune(e.target.value)}
              >
                {communes.map((c) => (
                  <option key={c.code} value={c.code}>
                    {c.nom} ({c.code}) - {c.district || c.region}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="filter-group" style={{ marginTop: "14px", borderTop: "1px solid var(--border-color)", paddingTop: "12px" }}>
            <label style={{ fontWeight: "700" }}>Type de graphique :</label>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginTop: "8px" }}>
              {[
                { id: "Histogramme", label: "📊 Histogramme des pluies" },
                { id: "Tendance", label: "📈 Tendance polynomiale" },
                { id: "Climatologie mensuelle", label: "☀️ Climatologie mensuelle" },
                { id: "Anomalies", label: "⚡ Anomalies (1981–2010)" },
              ].map((g) => (
                <button
                  key={g.id}
                  className={`scale-tab-btn ${typeGraph === g.id ? "active" : ""}`}
                  onClick={() => setTypeGraph(g.id)}
                  style={{ textAlign: "left", padding: "8px 10px", width: "100%", fontSize: "12px" }}
                >
                  {g.label}
                </button>
              ))}
            </div>
          </div>

          {typeGraph === "Tendance" && (
            <div className="filter-group" style={{ marginTop: "14px", borderTop: "1px solid var(--border-color)", paddingTop: "12px" }}>
              <label style={{ fontWeight: "700" }}>Ordre de tendance polynomiale :</label>
              <div style={{ display: "flex", gap: "4px", marginTop: "8px", flexWrap: "wrap" }}>
                {[1, 2, 3, 4, 5].map((o) => (
                  <button
                    key={o}
                    className={`scale-tab-btn ${ordrePoly === o ? "active" : ""}`}
                    onClick={() => setOrdrePoly(o)}
                    style={{ minWidth: "32px", padding: "6px" }}
                  >
                    {o}{o === 4 ? " (R)" : ""}
                  </button>
                ))}
              </div>
            </div>
          )}
        </aside>

        <div className="panel">
          <div className="panel-heading" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <h2><Icons.Stats /> {typeGraph} — {titreStats}</h2>
              <span>Visualisation statistique temporelle et distribution</span>
            </div>
          </div>

          {typeGraph === "Histogramme" && (
            <div style={{ width: "100%", height: 380, marginTop: "12px" }}>
              <ResponsiveContainer>
                <RechartsBarChart data={histogramData} margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <XAxis dataKey="label" stroke="var(--text-muted)" fontSize={11} angle={-30} textAnchor="end" height={45} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} label={{ value: "Nombre d'années", angle: -90, position: "insideLeft" }} />
                  <RechartsTooltip formatter={(val) => [`${val} années`, "Fréquence"]} />
                  <Bar name="Nombre d'années" dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </RechartsBarChart>
              </ResponsiveContainer>
            </div>
          )}

          {typeGraph === "Tendance" && (
            <div style={{ width: "100%", height: 380, marginTop: "12px" }}>
              <ResponsiveContainer>
                <ComposedChart data={trendData} margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <XAxis dataKey="year" stroke="var(--text-muted)" fontSize={11} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} unit=" mm" />
                  <RechartsTooltip />
                  <Legend verticalAlign="top" height={36} />
                  <Line name="Précipitation annuelle (mm)" type="monotone" dataKey="p" stroke="#64748b" strokeWidth={1.5} dot={{ r: 3, fill: "#2563eb" }} />
                  <Line name={`Tendance polynomiale (Ordre ${ordrePoly})`} type="monotone" dataKey="trend" stroke="#ef4444" strokeWidth={3} dot={false} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          )}

          {typeGraph === "Climatologie mensuelle" && (
            <div style={{ width: "100%", height: 380, marginTop: "12px" }}>
              <ResponsiveContainer>
                <RechartsBarChart data={climatologyData} margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} unit=" mm" />
                  <RechartsTooltip formatter={(val) => [`${val} mm`, "Précipitation Moyenne"]} />
                  <Bar name="Précipitations moyennes (mm)" dataKey="p" fill="#2563eb" radius={[4, 4, 0, 0]} />
                </RechartsBarChart>
              </ResponsiveContainer>
            </div>
          )}

          {typeGraph === "Anomalies" && (
            <div style={{ width: "100%", height: 380, marginTop: "12px" }}>
              <ResponsiveContainer>
                <RechartsBarChart data={anomalyData} margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <XAxis dataKey="year" stroke="var(--text-muted)" fontSize={11} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} unit=" mm" />
                  <RechartsTooltip formatter={(val) => [`${val} mm`, "Anomalie"]} />
                  <ReferenceArea y1={-sdClim} y2={sdClim} fill="#94a3b8" fillOpacity={0.2} />
                  <ReferenceLine y={sdClim} stroke="#475569" strokeDasharray="4 4" label={{ value: `+1 SD (+${sdClim} mm)`, fill: "#475569", fontSize: 10, position: "top" }} />
                  <ReferenceLine y={-sdClim} stroke="#475569" strokeDasharray="4 4" label={{ value: `-1 SD (-${sdClim} mm)`, fill: "#475569", fontSize: 10, position: "bottom" }} />
                  <ReferenceLine y={0} stroke="#0f172a" strokeWidth={1} />
                  <Bar name="Anomalie (mm)" dataKey="anomaly">
                    {anomalyData.map((entry, idx) => (
                      <Cell key={`cell-${idx}`} fill={entry.isPositive ? "#2563eb" : "#ef4444"} />
                    ))}
                  </Bar>
                </RechartsBarChart>
              </ResponsiveContainer>
            </div>
          )}

          <div className="info-bulletin" style={{ marginTop: "16px", marginBottom: 0 }}>
            <strong>Note méthodologique :</strong> La zone en arrière-plan gris sur le graphique d'anomalie correspond à $\pm 1$ écart-type par rapport à la moyenne climatologique de la période de référence 1981–2010 ({meanClim} mm/an). Les barres rouges représentent des années de déficit pluvial critique.
          </div>
        </div>
      </section>
    </div>
  );
}

// Carte Component matching R script carte_precip & carte_deficit + NDVI 6-Classes Raster Viewer
function Carte({ geojson, communes = [], precipRecords = [], annualData = [], ndviClasses = null }) {
  const features = geojson?.features ?? [];
  const [mapSubItem, setMapSubItem] = React.useState("precip"); // 'precip' | 'deficit' | 'ndvi_classes'
  const [typeCarte, setTypeCarte] = React.useState("Choroplèthe"); // 'Choroplèthe' vs 'Isohyètes'
  const [modeCommune, setModeCommune] = React.useState("Toutes les communes");
  const [selectedCommunesList, setSelectedCommunesList] = React.useState([communes[0]?.code || "MG1102"]);
  const [typePeriode, setTypePeriode] = React.useState("Annuel"); // 'Décennies' vs 'Annuel'
  const [selectedDecades, setSelectedDecades] = React.useState(["1981–1989"]);
  const [selectedYears, setSelectedYears] = React.useState([1981]);
  const [selectedMonth, setSelectedMonth] = React.useState("Tous");
  const [basemap, setBasemap] = React.useState("OpenStreetMap");
  const [selectedFeatureCode, setSelectedFeatureCode] = React.useState(features[0]?.properties?.code ?? "");

  // NDVI 6-Classes States
  const [isSyncing, setIsSyncing] = React.useState(false);
  const [localNdviClasses, setLocalNdviClasses] = React.useState(ndviClasses);

  React.useEffect(() => {
    if (ndviClasses) {
      setLocalNdviClasses(ndviClasses);
    }
  }, [ndviClasses]);

  const handleSyncNdvi = async () => {
    setIsSyncing(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/ndvi-classes/sync`);
      if (res.ok) {
        const freshData = await res.json();
        setLocalNdviClasses(freshData);
      } else {
        const res2 = await fetch(`/data/ndvi_classes_metadata.json?t=${Date.now()}`);
        if (res2.ok) {
          const freshData = await res2.json();
          setLocalNdviClasses(freshData);
        }
      }
    } catch (err) {
      console.warn("Sync error, fallback static", err);
      try {
        const res2 = await fetch(`/data/ndvi_classes_metadata.json?t=${Date.now()}`);
        if (res2.ok) {
          const freshData = await res2.json();
          setLocalNdviClasses(freshData);
        }
      } catch (e) {}
    } finally {
      setIsSyncing(false);
    }
  };

  const periods = React.useMemo(() => localNdviClasses?.periods || [], [localNdviClasses]);
  const availableNdviYears = React.useMemo(
    () => localNdviClasses?.years || [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008],
    [localNdviClasses]
  );

  const [ndviYear, setNdviYear] = React.useState(2000);
  const [ndviMonth, setNdviMonth] = React.useState(2);
  const [ndviOpacity, setNdviOpacity] = React.useState(0.85);
  const [showCommunesLayer, setShowCommunesLayer] = React.useState(true);
  const [communeOverlayStyle, setCommuneOverlayStyle] = React.useState("borders_only"); // 'borders_only' | 'light_tint'
  const [isPlayingTimeline, setIsPlayingTimeline] = React.useState(false);
  const [playSpeed, setPlaySpeed] = React.useState(1200);

  React.useEffect(() => {
    if (availableNdviYears.length > 0 && !availableNdviYears.includes(ndviYear)) {
      setNdviYear(availableNdviYears[0]);
    }
  }, [availableNdviYears, ndviYear]);

  // Available months for selected NDVI year
  const availableMonthsForYear = React.useMemo(() => {
    return periods.filter((p) => p.year === ndviYear).map((p) => p.month);
  }, [periods, ndviYear]);

  // Adjust month if not available in selected year
  React.useEffect(() => {
    if (availableMonthsForYear.length > 0 && !availableMonthsForYear.includes(ndviMonth)) {
      setNdviMonth(availableMonthsForYear[0]);
    }
  }, [availableMonthsForYear, ndviMonth]);

  // Current active period object
  const activePeriod = React.useMemo(() => {
    return periods.find((p) => p.year === ndviYear && p.month === ndviMonth) || periods[0];
  }, [periods, ndviYear, ndviMonth]);

  const activePeriodIndex = React.useMemo(() => {
    const idx = periods.findIndex((p) => p.year === ndviYear && p.month === ndviMonth);
    return idx >= 0 ? idx : 0;
  }, [periods, ndviYear, ndviMonth]);

  // Playback timer effect
  React.useEffect(() => {
    if (!isPlayingTimeline || periods.length === 0) return;
    const timer = setInterval(() => {
      const currentIndex = periods.findIndex((p) => p.year === ndviYear && p.month === ndviMonth);
      const nextIndex = (currentIndex + 1) % periods.length;
      const nextPeriod = periods[nextIndex];
      if (nextPeriod) {
        setNdviYear(nextPeriod.year);
        setNdviMonth(nextPeriod.month);
      }
    }, playSpeed);
    return () => clearInterval(timer);
  }, [isPlayingTimeline, periods, ndviYear, ndviMonth, playSpeed]);

  const handleTimelineStep = (direction) => {
    if (periods.length === 0) return;
    let nextIndex = activePeriodIndex + direction;
    if (nextIndex < 0) nextIndex = periods.length - 1;
    if (nextIndex >= periods.length) nextIndex = 0;
    const nextPeriod = periods[nextIndex];
    if (nextPeriod) {
      setNdviYear(nextPeriod.year);
      setNdviMonth(nextPeriod.month);
    }
  };

  const handleTimelineScrub = (index) => {
    const period = periods[index];
    if (period) {
      setNdviYear(period.year);
      setNdviMonth(period.month);
    }
  };

  const tileUrls = {
    OpenStreetMap: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    "Google Satellite": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
  };

  const tileAttributions = {
    OpenStreetMap: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    "Google Satellite": "&copy; Google Satellites",
  };

  const availableYears = React.useMemo(() => {
    const list = annualData.map((d) => d.year).sort((a, b) => a - b);
    return list.length ? list : Array.from({ length: 45 }, (_, i) => 1981 + i);
  }, [annualData]);

  // Compute calculated rainfall values for features based on active filters
  const calculatedPrecipMap = React.useMemo(() => {
    const map = {};
    if (!precipRecords || precipRecords.length === 0) return map;

    let filtered = precipRecords;
    if (typePeriode === "Décennies") {
      const years = [];
      if (selectedDecades.includes("1981–1989")) years.push(...Array.from({ length: 9 }, (_, i) => 1981 + i));
      if (selectedDecades.includes("1990–1999")) years.push(...Array.from({ length: 10 }, (_, i) => 1990 + i));
      if (selectedDecades.includes("2000–2009")) years.push(...Array.from({ length: 10 }, (_, i) => 2000 + i));
      if (selectedDecades.includes("2010–2019")) years.push(...Array.from({ length: 10 }, (_, i) => 2010 + i));
      if (selectedDecades.includes("2020–2025")) years.push(...Array.from({ length: 6 }, (_, i) => 2020 + i));
      filtered = filtered.filter((r) => years.includes(r.year));
    } else {
      filtered = filtered.filter((r) => selectedYears.includes(r.year));
      if (selectedMonth !== "Tous") {
        const monthNum =
          ["Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec"].indexOf(
            selectedMonth
          ) + 1;
        if (monthNum > 0) filtered = filtered.filter((r) => r.month === monthNum);
      }
    }

    const sums = {};
    const counts = {};
    filtered.forEach((r) => {
      sums[r.code] = (sums[r.code] || 0) + r.precip;
      counts[r.code] = (counts[r.code] || 0) + 1;
    });

    Object.keys(sums).forEach((code) => {
      map[code] = Math.round(sums[code]);
    });

    return map;
  }, [precipRecords, typePeriode, selectedDecades, selectedYears, selectedMonth]);

  // Points for IDW spatial interpolation isohyets
  const idwPoints = React.useMemo(() => {
    if (typeCarte !== "Isohyètes" || mapSubItem !== "precip") return [];
    const points = [];
    features.forEach((f) => {
      const code = f.properties.code;
      if (modeCommune === "Choisir une commune" && !selectedCommunesList.includes(code)) return;
      const val = calculatedPrecipMap[code] ?? f.properties.precip ?? 0;
      if (f.geometry && f.geometry.coordinates) {
        try {
          const layer = L.geoJSON(f);
          const bounds = layer.getBounds();
          if (bounds.isValid()) {
            const center = bounds.getCenter();
            points.push({ lat: center.lat, lng: center.lng, val });
          }
        } catch (e) {}
      }
    });
    return points;
  }, [features, calculatedPrecipMap, typeCarte, mapSubItem, modeCommune, selectedCommunesList]);

  const idwGrid = React.useMemo(() => {
    if (typeCarte !== "Isohyètes" || idwPoints.length === 0) return null;
    return computeIDWGrid(idwPoints, 35, 2);
  }, [idwPoints, typeCarte]);

  // Style function for Precipitation and Deficit choropleth features
  const getFeatureStyle = React.useCallback(
    (feature) => {
      const code = feature.properties.code;
      const isSelected = selectedFeatureCode === code;
      const isFilteredOut = modeCommune === "Choisir une commune" && !selectedCommunesList.includes(code);

      if (isFilteredOut) {
        return { fillColor: "#cbd5e1", fillOpacity: 0.15, color: "#94a3b8", weight: 0.5 };
      }

      if (mapSubItem === "deficit") {
        const deficit = feature.properties.deficit ?? 0;
        let fillColor = "#f7f7f7";
        if (deficit < -60) fillColor = "#7f0000";
        else if (deficit < -40) fillColor = "#b30000";
        else if (deficit < -20) fillColor = "#e34a33";
        else if (deficit < 0) fillColor = "#fdbb84";

        return {
          fillColor,
          fillOpacity: isSelected ? 0.9 : 0.65,
          color: isSelected ? "#000" : "#334155",
          weight: isSelected ? 2.5 : 0.8,
        };
      }

      // Précipitations Map
      const val = calculatedPrecipMap[code] ?? feature.properties.precip ?? 0;
      const palette = [
        "#eff6ff",
        "#dbeafe",
        "#bfdbfe",
        "#93c5fd",
        "#60a5fa",
        "#3b82f6",
        "#2563eb",
        "#1d4ed8",
        "#1e40af",
      ];
      const maxVal = Math.max(...Object.values(calculatedPrecipMap), 800);
      const ratio = Math.max(0, Math.min(1, val / (maxVal || 1)));
      const idx = Math.min(palette.length - 1, Math.floor(ratio * palette.length));
      const fillColor = palette[idx];

      return {
        fillColor,
        fillOpacity: isSelected ? 0.95 : 0.65,
        color: isSelected ? "#1d4ed8" : "#1e293b",
        weight: isSelected ? 2.5 : 0.8,
      };
    },
    [selectedFeatureCode, mapSubItem, calculatedPrecipMap, modeCommune, selectedCommunesList]
  );

  // Style function for Commune Layer overlaid on top of NDVI raster
  const getCommuneNdviOverlayStyle = React.useCallback(
    (feature) => {
      const code = feature.properties.code;
      const isSelected = selectedFeatureCode === code;
      const isFilteredOut = modeCommune === "Choisir une commune" && !selectedCommunesList.includes(code);

      if (isFilteredOut) {
        return {
          fillColor: "transparent",
          fillOpacity: 0,
          color: "#94a3b8",
          weight: 0.6,
          dashArray: "3, 3",
        };
      }

      if (isSelected) {
        return {
          fillColor: "rgba(59, 130, 246, 0.25)",
          fillOpacity: 0.25,
          color: "#2563eb",
          weight: 3,
        };
      }

      return {
        fillColor:
          communeOverlayStyle === "light_tint" ? "rgba(255, 255, 255, 0.08)" : "transparent",
        fillOpacity: communeOverlayStyle === "light_tint" ? 0.08 : 0,
        color: "#1e293b",
        weight: 1.2,
        opacity: 0.85,
      };
    },
    [selectedFeatureCode, modeCommune, selectedCommunesList, communeOverlayStyle]
  );

  const selectedFeature = features.find((f) => f.properties.code === selectedFeatureCode) ?? features[0];
  const ndviBounds = ndviClasses?.bounds || [
    [-25.60647717382696, 43.1752783429945],
    [-20.908288237881862, 47.415326484038644],
  ];
  const classesList = ndviClasses?.classes || [
    { id: 1, label: "Eau", range: "< 0", description: "Plans d'eau", color: "#0c19ff" },
    { id: 2, label: "NDVI très faible", range: "0 – 0.2", description: "Sol nu / clairsemé", color: "#87360c" },
    { id: 3, label: "NDVI faible", range: "0.2 – 0.4", description: "Fourrés dégradés", color: "#c46e2d" },
    { id: 4, label: "NDVI moyen", range: "0.4 – 0.6", description: "Fourrés arbustifs / cultures", color: "#96aa50" },
    { id: 5, label: "NDVI élevé", range: "0.6 – 0.8", description: "Forêt sèche / canopée", color: "#468237" },
    { id: 6, label: "NDVI très élevé", range: "0.8 – 1.0", description: "Végétation très dense", color: "#00441b" },
  ];

  const monthNamesFr = [
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
  ];

  return (
    <section className="split-layout">
      <aside className="filters-panel">
        <h2>Paramètres Carte</h2>

        {/* Sous-onglets de sélection de la carte */}
        <div className="filter-group">
          <label style={{ fontWeight: "700" }}>Affichage Carte :</label>
          <div style={{ display: "flex", gap: "4px", marginTop: "6px", flexWrap: "wrap" }}>
            <button
              className={`scale-tab-btn ${mapSubItem === "precip" ? "active" : ""}`}
              onClick={() => setMapSubItem("precip")}
              style={{ flex: 1, padding: "6px 4px", fontSize: "11px", minWidth: "85px" }}
            >
              Précipitations
            </button>
            <button
              className={`scale-tab-btn ${mapSubItem === "deficit" ? "active" : ""}`}
              onClick={() => setMapSubItem("deficit")}
              style={{ flex: 1, padding: "6px 4px", fontSize: "11px", minWidth: "95px" }}
            >
              Déficit 2020-22
            </button>
            <button
              className={`scale-tab-btn ${mapSubItem === "ndvi_classes" ? "active" : ""}`}
              onClick={() => setMapSubItem("ndvi_classes")}
              style={{ flex: 1, padding: "6px 4px", fontSize: "11px", minWidth: "120px", fontWeight: "800" }}
            >
              🌿 NDVI (6 Classes)
            </button>
          </div>
        </div>

        {/* Options pour NDVI 6 Classes */}
        {mapSubItem === "ndvi_classes" && (
          <div className="ndvi-controls-box">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "6px" }}>
              <div>
                <h3 style={{ fontSize: "12px", fontWeight: "800", color: "var(--primary)", margin: 0 }}>
                  Contrôles NDVI MODIS
                </h3>
                <span style={{ fontSize: "10px", color: "var(--text-muted)", fontWeight: "600" }}>
                  {periods.length} rasters disponibles ({availableNdviYears[0]}–{availableNdviYears[availableNdviYears.length - 1]})
                </span>
              </div>
              <button
                type="button"
                className="timeline-btn"
                onClick={handleSyncNdvi}
                disabled={isSyncing}
                style={{ fontSize: "10px", padding: "4px 8px", whiteSpace: "nowrap" }}
                title="Scanner les dossiers et actualiser les nouvelles données"
              >
                {isSyncing ? "⏳ Scan..." : "🔄 Actualiser"}
              </button>
            </div>

            <div className="filter-group">
              <label htmlFor="ndvi-annee-sel">Année :</label>
              <select
                id="ndvi-annee-sel"
                value={ndviYear}
                onChange={(e) => setNdviYear(Number(e.target.value))}
              >
                {availableNdviYears.map((y) => (
                  <option key={y} value={y}>
                    {y}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label htmlFor="ndvi-mois-sel">Mois :</label>
              <select
                id="ndvi-mois-sel"
                value={ndviMonth}
                onChange={(e) => setNdviMonth(Number(e.target.value))}
              >
                {availableMonthsForYear.map((m) => (
                  <option key={m} value={m}>
                    {monthNamesFr[m - 1]} ({String(m).padStart(2, "0")})
                  </option>
                ))}
              </select>
            </div>

            {/* Lecteur Temporel / Animation Timeline */}
            <div className="timeline-player-panel">
              <div className="timeline-header">
                <span style={{ fontSize: "11px", fontWeight: "700", textTransform: "uppercase" }}>
                  Animation Temporelle :
                </span>
                <span className="timeline-period-badge">
                  {activePeriod ? activePeriod.label : `${monthNamesFr[ndviMonth - 1]} ${ndviYear}`}
                </span>
              </div>

              <div className="timeline-buttons">
                <button
                  type="button"
                  className="timeline-btn"
                  onClick={() => handleTimelineStep(-1)}
                  title="Mois précédent"
                >
                  ⏮ Préc.
                </button>
                <button
                  type="button"
                  className={`timeline-btn ${isPlayingTimeline ? "play-active" : ""}`}
                  onClick={() => setIsPlayingTimeline(!isPlayingTimeline)}
                  title={isPlayingTimeline ? "Mettre en pause" : "Lancer l'animation chronologique"}
                >
                  {isPlayingTimeline ? "⏸ Pause" : "▶ Lecture"}
                </button>
                <button
                  type="button"
                  className="timeline-btn"
                  onClick={() => handleTimelineStep(1)}
                  title="Mois suivant"
                >
                  Suiv. ⏭
                </button>
              </div>

              <input
                type="range"
                className="timeline-scrubber"
                min={0}
                max={Math.max(0, periods.length - 1)}
                value={activePeriodIndex}
                onChange={(e) => handleTimelineScrub(Number(e.target.value))}
                title="Glissez pour changer de mois"
              />

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "10px", color: "var(--text-muted)" }}>
                <span>Vitesse :</span>
                <select
                  value={playSpeed}
                  onChange={(e) => setPlaySpeed(Number(e.target.value))}
                  style={{ fontSize: "10px", padding: "2px 4px" }}
                >
                  <option value={2000}>Lente (2.0s)</option>
                  <option value={1200}>Normale (1.2s)</option>
                  <option value={700}>Rapide (0.7s)</option>
                </select>
              </div>
            </div>

            {/* Curseur d'Opacité du Raster */}
            <div className="filter-group">
              <label htmlFor="ndvi-opacity-slider">Opacité du Raster NDVI :</label>
              <div className="opacity-slider-row">
                <input
                  id="ndvi-opacity-slider"
                  type="range"
                  min={0}
                  max={1}
                  step={0.05}
                  value={ndviOpacity}
                  onChange={(e) => setNdviOpacity(Number(e.target.value))}
                />
                <span className="opacity-slider-value">{Math.round(ndviOpacity * 100)}%</span>
              </div>
            </div>

            {/* Superposition de la Couche Communes */}
            <div className="layer-toggle-group">
              <label className="layer-toggle-label">
                <input
                  type="checkbox"
                  checked={showCommunesLayer}
                  onChange={(e) => setShowCommunesLayer(e.target.checked)}
                />
                <span>Superposer la couche des communes</span>
              </label>

              {showCommunesLayer && (
                <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginTop: "4px" }}>
                  <div style={{ display: "flex", gap: "10px", fontSize: "11px" }}>
                    <label style={{ display: "flex", alignItems: "center", gap: "4px", cursor: "pointer" }}>
                      <input
                        type="radio"
                        name="commune_style"
                        value="borders_only"
                        checked={communeOverlayStyle === "borders_only"}
                        onChange={(e) => setCommuneOverlayStyle(e.target.value)}
                      />
                      Contours seuls
                    </label>
                    <label style={{ display: "flex", alignItems: "center", gap: "4px", cursor: "pointer" }}>
                      <input
                        type="radio"
                        name="commune_style"
                        value="light_tint"
                        checked={communeOverlayStyle === "light_tint"}
                        onChange={(e) => setCommuneOverlayStyle(e.target.value)}
                      />
                      Teinte légère
                    </label>
                  </div>

                  <div style={{ marginTop: "4px" }}>
                    <label htmlFor="mode-commune-ndvi" style={{ fontSize: "11px" }}>Filtrer une commune :</label>
                    <select
                      id="mode-commune-ndvi"
                      value={modeCommune}
                      onChange={(e) => setModeCommune(e.target.value)}
                      style={{ fontSize: "11px" }}
                    >
                      <option value="Toutes les communes">Toutes les communes</option>
                      <option value="Choisir une commune">Mettre en évidence une commune</option>
                    </select>
                  </div>

                  {modeCommune === "Choisir une commune" && (
                    <select
                      id="communes-sel-ndvi"
                      value={selectedCommunesList[0]}
                      onChange={(e) => {
                        setSelectedCommunesList([e.target.value]);
                        setSelectedFeatureCode(e.target.value);
                      }}
                      style={{ fontSize: "11px" }}
                    >
                      {communes.map((c) => (
                        <option key={c.code} value={c.code}>
                          {c.nom} ({c.code})
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Options pour Précipitations */}
        {mapSubItem === "precip" && (
          <>
            <div className="filter-group" style={{ marginTop: "10px" }}>
              <label style={{ fontWeight: "700" }}>Type de carte :</label>
              <div style={{ display: "flex", gap: "12px", marginTop: "4px" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px" }}>
                  <input
                    type="radio"
                    name="type_carte"
                    value="Choroplèthe"
                    checked={typeCarte === "Choroplèthe"}
                    onChange={(e) => setTypeCarte(e.target.value)}
                  />
                  Choroplèthe
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px" }}>
                  <input
                    type="radio"
                    name="type_carte"
                    value="Isohyètes"
                    checked={typeCarte === "Isohyètes"}
                    onChange={(e) => setTypeCarte(e.target.value)}
                  />
                  Isohyètes (IDW)
                </label>
              </div>
            </div>

            <div className="filter-group" style={{ marginTop: "10px" }}>
              <label htmlFor="mode-commune-carte">Affichage des communes :</label>
              <select
                id="mode-commune-carte"
                value={modeCommune}
                onChange={(e) => setModeCommune(e.target.value)}
              >
                <option value="Toutes les communes">Toutes les communes</option>
                <option value="Choisir une commune">Choisir une commune</option>
              </select>
            </div>

            {modeCommune === "Choisir une commune" && (
              <div className="filter-group" style={{ marginTop: "8px" }}>
                <label htmlFor="communes-sel-multi">Choisir commune :</label>
                <select
                  id="communes-sel-multi"
                  value={selectedCommunesList[0]}
                  onChange={(e) => setSelectedCommunesList([e.target.value])}
                >
                  {communes.map((c) => (
                    <option key={c.code} value={c.code}>
                      {c.nom} ({c.code})
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="filter-group" style={{ marginTop: "10px" }}>
              <label style={{ fontWeight: "700" }}>Période d'affichage :</label>
              <div style={{ display: "flex", gap: "12px", marginTop: "4px" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px" }}>
                  <input
                    type="radio"
                    name="type_periode"
                    value="Décennies"
                    checked={typePeriode === "Décennies"}
                    onChange={(e) => setTypePeriode(e.target.value)}
                  />
                  Décennies
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px" }}>
                  <input
                    type="radio"
                    name="type_periode"
                    value="Annuel"
                    checked={typePeriode === "Annuel"}
                    onChange={(e) => setTypePeriode(e.target.value)}
                  />
                  Annuel
                </label>
              </div>
            </div>

            {typePeriode === "Décennies" ? (
              <div className="filter-group" style={{ marginTop: "8px" }}>
                <label htmlFor="decade-sel">Période (décennie) :</label>
                <select
                  id="decade-sel"
                  value={selectedDecades[0]}
                  onChange={(e) => setSelectedDecades([e.target.value])}
                >
                  <option value="1981–1989">1981–1989</option>
                  <option value="1990–1999">1990–1999</option>
                  <option value="2000–2009">2000–2009</option>
                  <option value="2010–2019">2010–2019</option>
                  <option value="2020–2025">2020–2025</option>
                </select>
              </div>
            ) : (
              <>
                <div className="filter-group" style={{ marginTop: "8px" }}>
                  <label htmlFor="annee-sel">Année :</label>
                  <select
                    id="annee-sel"
                    value={selectedYears[0]}
                    onChange={(e) => setSelectedYears([Number(e.target.value)])}
                  >
                    {availableYears.map((y) => (
                      <option key={y} value={y}>
                        {y}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="filter-group" style={{ marginTop: "8px" }}>
                  <label htmlFor="mois-sel">Mois :</label>
                  <select
                    id="mois-sel"
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(e.target.value)}
                  >
                    <option value="Tous">Tous</option>
                    {["Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec"].map(
                      (m) => (
                        <option key={m} value={m}>
                          {m}
                        </option>
                      )
                    )}
                  </select>
                </div>
              </>
            )}
          </>
        )}

        <div
          className="filter-group"
          style={{ marginTop: "12px", borderTop: "1px solid var(--border-color)", paddingTop: "10px" }}
        >
          <label htmlFor="basemap-sel">Fond de carte :</label>
          <select id="basemap-sel" value={basemap} onChange={(e) => setBasemap(e.target.value)}>
            <option value="OpenStreetMap">OpenStreetMap</option>
            <option value="Google Satellite">Google Satellite</option>
          </select>
        </div>

        {selectedFeature && (
          <div className="feature-summary" style={{ marginTop: "16px" }}>
            <h3 style={{ fontSize: "14px", fontWeight: "700" }}>{selectedFeature.properties.nom}</h3>
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
              District : {selectedFeature.properties.district} ({selectedFeature.properties.region})
            </span>

            <div
              style={{
                marginTop: "8px",
                display: "flex",
                flexDirection: "column",
                gap: "4px",
                fontSize: "11px",
              }}
            >
              {mapSubItem === "ndvi_classes" ? (
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Code Commune :</span>
                  <strong>{selectedFeature.properties.code}</strong>
                </div>
              ) : (
                <>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Précip. Calculée :</span>
                    <strong>
                      {calculatedPrecipMap[selectedFeature.properties.code] ??
                        selectedFeature.properties.precip ??
                        "N/A"}{" "}
                      mm
                    </strong>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>Déficit 2020-22 :</span>
                    <strong style={{ color: "var(--danger)" }}>
                      {selectedFeature.properties.deficit ?? "N/A"} %
                    </strong>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </aside>

      <div className="panel map-panel">
        <div className="panel-heading">
          <h2>
            <Icons.Map />{" "}
            {mapSubItem === "ndvi_classes"
              ? `Classification NDVI MODIS 6 Classes — ${activePeriod?.label || `${monthNamesFr[ndviMonth - 1]} ${ndviYear}`}`
              : mapSubItem === "deficit"
              ? "Carte du déficit de précipitation (2020-2022)"
              : `Carte des précipitations (${typeCarte})`}
          </h2>
          <span>
            {mapSubItem === "ndvi_classes"
              ? "Survolez ou cliquez sur une commune pour afficher son nom et ses limites"
              : "Cliquez sur une commune pour afficher les détails"}
          </span>
        </div>

        <div className="geo-map-container">
          <div className="geo-map-wrapper" style={{ height: "460px" }}>
            <MapContainer
              className="geo-map"
              center={[-24.5, 45.5]}
              zoom={7}
              style={{ height: "460px", width: "100%" }}
            >
              <TileLayer url={tileUrls[basemap]} attribution={tileAttributions[basemap]} />

              {/* Raster NDVI 6-Classes Overlay */}
              {mapSubItem === "ndvi_classes" && activePeriod && (
                <ImageOverlay
                  key={activePeriod.key}
                  url={activePeriod.pngUrl}
                  bounds={activePeriod.bounds || ndviBounds}
                  opacity={ndviOpacity}
                  zIndex={10}
                />
              )}

              {/* Isohyètes IDW Raster Grid Layer */}
              {mapSubItem === "precip" &&
                typeCarte === "Isohyètes" &&
                idwGrid &&
                idwGrid.cells.map((cell, i) => {
                  const ratio = Math.max(
                    0,
                    Math.min(1, (cell.val - idwGrid.minVal) / (idwGrid.maxVal - idwGrid.minVal || 1))
                  );
                  const color = `rgba(37, 99, 235, ${0.15 + ratio * 0.7})`;
                  return (
                    <Rectangle
                      key={`idw-${i}`}
                      bounds={cell.bounds}
                      pathOptions={{ color: "transparent", fillColor: color, fillOpacity: 0.65 }}
                    />
                  );
                })}

              {/* Couche des Communes en mode Précip / Déficit */}
              {mapSubItem !== "ndvi_classes" && geojson && geojson.features && (
                <>
                  <GeoJSON
                    key={`${mapSubItem}-${typeCarte}-${typePeriode}-${selectedFeatureCode}-${basemap}`}
                    data={geojson}
                    style={getFeatureStyle}
                    onEachFeature={(feature, layer) => {
                      layer.on({
                        click: () => setSelectedFeatureCode(feature.properties.code),
                      });
                    }}
                  />
                  <MapBoundsManager geojson={geojson} />
                </>
              )}

              {/* Couche des Communes superposée au NDVI (commutable à volonté) */}
              {mapSubItem === "ndvi_classes" && showCommunesLayer && geojson && geojson.features && (
                <>
                  <GeoJSON
                    key={`ndvi-overlay-${selectedFeatureCode}-${communeOverlayStyle}-${modeCommune}`}
                    data={geojson}
                    style={getCommuneNdviOverlayStyle}
                    onEachFeature={(feature, layer) => {
                      const p = feature.properties;
                      layer.bindTooltip(
                        `<div style="font-weight:700;font-size:12px;">${p.nom || p.code}</div>
                         <div style="font-size:11px;color:#64748b;">${p.district || ""}${p.district && p.region ? " - " : ""}${p.region || ""}</div>`,
                        { sticky: true, direction: "top", opacity: 0.95 }
                      );
                      layer.on({
                        click: () => {
                          setSelectedFeatureCode(p.code);
                        },
                      });
                    }}
                  />
                  <MapBoundsManager geojson={geojson} />
                </>
              )}
            </MapContainer>
          </div>

          {/* Légendes adaptées selon le mode actif */}
          {mapSubItem === "ndvi_classes" ? (
            <div className="ndvi-legend-container">
              <div className="ndvi-legend-header">
                <span className="ndvi-legend-title">Légende des 6 Classes NDVI MODIS</span>
                <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                  Résolution 250m &bull; Période active : <strong>{activePeriod?.label}</strong>
                </span>
              </div>
              <div className="ndvi-legend-grid">
                {classesList.map((cls) => (
                  <div key={cls.id} className="ndvi-legend-item">
                    <span className="ndvi-legend-color-box" style={{ backgroundColor: cls.color }} />
                    <div className="ndvi-legend-text">
                      <span className="ndvi-legend-label">{cls.label}</span>
                      <span className="ndvi-legend-range">
                        NDVI {cls.range} &bull; {cls.description}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : mapSubItem === "deficit" ? (
            <div
              className="map-legend"
              style={{ display: "flex", flexDirection: "column", gap: "6px", marginTop: "12px" }}
            >
              <span style={{ fontWeight: "700", fontSize: "12px" }}>Déficit (%) :</span>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", fontSize: "11px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                  <span
                    style={{ width: "12px", height: "12px", backgroundColor: "#7f0000", borderRadius: "2px" }}
                  ></span>
                  <span>Déficit extrême (&lt; -60%)</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                  <span
                    style={{ width: "12px", height: "12px", backgroundColor: "#b30000", borderRadius: "2px" }}
                  ></span>
                  <span>Déficit sévère (-60 à -40%)</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                  <span
                    style={{ width: "12px", height: "12px", backgroundColor: "#e34a33", borderRadius: "2px" }}
                  ></span>
                  <span>Déficit modéré (-40 à -20%)</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                  <span
                    style={{ width: "12px", height: "12px", backgroundColor: "#fdbb84", borderRadius: "2px" }}
                  ></span>
                  <span>Normal (-20 à 0%)</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                  <span
                    style={{
                      width: "12px",
                      height: "12px",
                      backgroundColor: "#f7f7f7",
                      border: "1px solid #cbd5e1",
                      borderRadius: "2px",
                    }}
                  ></span>
                  <span>Excédent (&gt; 0%)</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="map-legend" style={{ marginTop: "12px" }}>
              <span>Sec (0 mm)</span>
              <div className="map-legend-items">
                <div className="map-legend-bar">
                  {[
                    "#eff6ff",
                    "#dbeafe",
                    "#bfdbfe",
                    "#93c5fd",
                    "#60a5fa",
                    "#3b82f6",
                    "#2563eb",
                    "#1d4ed8",
                    "#1e40af",
                  ].map((col) => (
                    <div key={col} className="map-legend-color" style={{ backgroundColor: col }} />
                  ))}
                </div>
              </div>
              <span>Humide (&gt;800 mm)</span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function MapBoundsManager({ geojson }) {
  const map = useMap();
  React.useEffect(() => {
    if (geojson && geojson.features && geojson.features.length > 0) {
      try {
        const bounds = L.geoJSON(geojson).getBounds();
        if (bounds.isValid()) {
          map.fitBounds(bounds, { padding: [15, 15] });
        }
      } catch (err) {
        console.error("Error setting map bounds:", err);
      }
    }
  }, [geojson, map]);
  return null;
}

function ComparaisonCapteurs({ vegData, selectedCommune }) {
  const [activeSensor, setActiveSensor] = React.useState("sentinel");
  const [simPixelSize, setSimPixelSize] = React.useState(30);

  const comparison = vegData?.sensorComparison;
  if (!comparison) {
    return <div className="placeholder">Chargement des données de capteurs...</div>;
  }

  const activeSpec = comparison.specs.find((s) => s.id === activeSensor);
  const activeSim = comparison.simulation[activeSensor];

  const cellColors = {
    1: "#065f46",
    2: "#10b981",
    3: "#f59e0b",
    4: "#b45309",
  };

  const calculatedNdviAtSize = (0.15 + (0.44 - 0.15) * (1 - Math.exp(-simPixelSize / 70))).toFixed(3);
  const calculatedVariance = (0.075 * Math.exp(-simPixelSize / 90)).toFixed(4);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <div className="info-bulletin">
        <strong>Effet d'échelle et pixel mixte (Physique de la Télédétection) :</strong> La taille
        du pixel (résolution spatiale) détermine le niveau de détail discernable. Plus le pixel est
        grand (ex. MODIS 250m), plus le signal capté est une moyenne d'éléments hétérogènes.
      </div>

      <section className="panel">
        <div className="panel-heading">
          <h2><Icons.Layers /> 4.1 Comparaison Multi-Résolution (Sentinel vs Landsat vs MODIS)</h2>
          <span>Sélectionnez un capteur pour simuler la capture de la même zone</span>
        </div>

        <div className="sensor-tabs">
          {comparison.specs.map((s) => (
            <button
              key={s.id}
              className={`sensor-tab-btn ${activeSensor === s.id ? "active" : ""}`}
              onClick={() => setActiveSensor(s.id)}
            >
              {s.name}
            </button>
          ))}
        </div>

        <div className="comparison-layout">
          <div className="pixel-grid-card">
            <h4 style={{ fontSize: "12px", marginBottom: "8px", fontWeight: "700" }}>
              Visualisation à l'échelle : {activeSpec.resolution} (Grille {activeSim.size}x{activeSim.size})
            </h4>

            <div className="pixel-grid-wrapper" style={{ width: "260px", height: "260px" }}>
              {activeSim.ndvi.map((row, rIdx) => (
                <div key={rIdx} className="pixel-row">
                  {row.map((val, cIdx) => {
                    let bg = "";
                    if (activeSensor === "sentinel") {
                      const classVal = activeSim.grid[rIdx][cIdx];
                      bg = cellColors[classVal];
                    } else if (activeSensor === "landsat") {
                      bg = val > 0.5 ? "#065f46" : val > 0.4 ? "#059669" : val > 0.3 ? "#10b981" : val > 0.25 ? "#f59e0b" : "#b45309";
                    } else {
                      bg = "#10b981";
                    }

                    return (
                      <div key={cIdx} className="pixel-cell" style={{ backgroundColor: bg }} data-ndvi={`NDVI: ${val}`} />
                    );
                  })}
                </div>
              ))}
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <h3 style={{ fontSize: "14px", fontWeight: "800", color: "var(--primary)" }}>{activeSpec.name}</h3>
            <div style={{ display: "flex", gap: "12px", fontSize: "12px", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
              <span>Résolution : <strong>{activeSpec.resolution}</strong></span>
              <span>Fréquence : <strong>{activeSpec.frequency}</strong></span>
            </div>
            <p style={{ fontSize: "12px", lineHeight: "1.4", margin: "6px 0", color: "var(--text-muted)" }}>
              <strong>Bandes :</strong> {activeSpec.bands}
            </p>
            <div style={{ marginTop: "6px" }}>
              <strong style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--accent)" }}>Avantage :</strong>
              <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>{activeSpec.advantage}</p>
            </div>
            <div style={{ marginTop: "6px" }}>
              <strong style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--danger)" }}>Limite technique :</strong>
              <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>{activeSpec.inconvenience}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>4.3 Simulateur d'effet de taille de pixel</h2>
          <span>Glissez le curseur pour observer comment la taille de pixel fusionne les signatures</span>
        </div>

        <div className="pixel-scale-simulator">
          <div className="simulator-controls">
            <div className="slider-group">
              <label htmlFor="pixel-size-slider" style={{ fontSize: "11px", fontWeight: "700", textTransform: "uppercase" }}>Taille :</label>
              <input
                id="pixel-size-slider"
                type="range"
                min={10}
                max={300}
                step={10}
                value={simPixelSize}
                onChange={(e) => setSimPixelSize(Number(e.target.value))}
              />
              <span style={{ fontSize: "12px", fontWeight: "800", minWidth: "50px" }}>{simPixelSize} m</span>
            </div>

            <div className="simulator-metrics">
              <div>NDVI calculé : <strong>{calculatedNdviAtSize}</strong></div>
              <div>Variance : <strong>{calculatedVariance}</strong></div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function TableauExplorer({ geojson, communesList }) {
  const [scale, setScale] = React.useState("commune");
  const [selectedRegFilter, setSelectedRegFilter] = React.useState("");
  const [selectedEcoFilter, setSelectedEcoFilter] = React.useState("");
  const [searchVal, setSearchVal] = React.useState("");

  const features = geojson.features ?? [];

  const tableData = React.useMemo(() => {
    if (scale === "commune") {
      return features.map((f) => {
        const p = f.properties;
        const vci = Math.min(100, Math.max(0, Math.round(50 + p.deficit * 1.5)));
        const vhi = Math.min(100, Math.max(0, Math.round(vci - 2)));
        return {
          name: p.nom,
          code: p.code,
          district: p.district,
          region: p.region,
          ecoregion: p.ecoregion,
          ndvi: p.ndvi,
          vci: vci,
          vhi: vhi,
          vegCover: p.vegCover,
          forestArea: p.forestArea,
          annualLoss: p.annualLoss,
          alert: p.alert,
        };
      });
    } else if (scale === "district") {
      const dict = {};
      features.forEach((f) => {
        const p = f.properties;
        const dName = p.district;
        if (!dict[dName]) {
          dict[dName] = {
            name: dName,
            region: p.region,
            ecoregions: new Set(),
            ndviList: [],
            vegCoverList: [],
            forestArea: 0,
            annualLoss: 0,
            deficits: [],
          };
        }
        dict[dName].ecoregions.add(p.ecoregion);
        dict[dName].ndviList.push(p.ndvi);
        dict[dName].vegCoverList.push(p.vegCover);
        dict[dName].forestArea += p.forestArea;
        dict[dName].annualLoss += p.annualLoss;
        dict[dName].deficits.push(p.deficit);
      });

      return Object.values(dict).map((d) => {
        const ndviAvg = Number((d.ndviList.reduce((a, b) => a + b, 0) / d.ndviList.length).toFixed(3));
        const coverAvg = Number((d.vegCoverList.reduce((a, b) => a + b, 0) / d.vegCoverList.length).toFixed(1));
        const defAvg = d.deficits.reduce((a, b) => a + b, 0) / d.deficits.length;
        const vci = Math.min(100, Math.max(0, Math.round(50 + defAvg * 1.5)));
        return {
          name: d.name,
          code: "DIST-" + d.name.substring(0, 3).toUpperCase(),
          district: d.name,
          region: d.region,
          ecoregion: Array.from(d.ecoregions).join(", "),
          ndvi: ndviAvg,
          vci: vci,
          vhi: Math.max(0, vci - 2),
          vegCover: coverAvg,
          forestArea: d.forestArea,
          annualLoss: d.annualLoss,
          alert: defAvg < -18 ? "Alerte Rouge" : defAvg < -8 ? "Vigilance" : "Stable",
        };
      });
    } else {
      const dict = {};
      features.forEach((f) => {
        const p = f.properties;
        const rName = p.region;
        if (!dict[rName]) {
          dict[rName] = {
            name: rName,
            ecoregions: new Set(),
            ndviList: [],
            vegCoverList: [],
            forestArea: 0,
            annualLoss: 0,
            deficits: [],
          };
        }
        dict[rName].ecoregions.add(p.ecoregion);
        dict[rName].ndviList.push(p.ndvi);
        dict[rName].vegCoverList.push(p.vegCover);
        dict[rName].forestArea += p.forestArea;
        dict[rName].annualLoss += p.annualLoss;
        dict[rName].deficits.push(p.deficit);
      });

      return Object.values(dict).map((r) => {
        const ndviAvg = Number((r.ndviList.reduce((a, b) => a + b, 0) / r.ndviList.length).toFixed(3));
        const coverAvg = Number((r.vegCoverList.reduce((a, b) => a + b, 0) / r.vegCoverList.length).toFixed(1));
        const defAvg = r.deficits.reduce((a, b) => a + b, 0) / r.deficits.length;
        const vci = Math.min(100, Math.max(0, Math.round(50 + defAvg * 1.5)));
        return {
          name: r.name,
          code: "REG-" + r.name.substring(0, 3).toUpperCase(),
          district: "Tous",
          region: r.name,
          ecoregion: Array.from(r.ecoregions).join(", "),
          ndvi: ndviAvg,
          vci: vci,
          vhi: Math.max(0, vci - 2),
          vegCover: coverAvg,
          forestArea: r.forestArea,
          annualLoss: r.annualLoss,
          alert: defAvg < -18 ? "Alerte Rouge" : defAvg < -8 ? "Vigilance" : "Stable",
        };
      });
    }
  }, [scale, features]);

  const filteredData = React.useMemo(() => {
    return tableData.filter((row) => {
      if (selectedRegFilter && row.region !== selectedRegFilter) return false;
      if (selectedEcoFilter && !row.ecoregion.toLowerCase().includes(selectedEcoFilter.toLowerCase())) return false;
      if (searchVal) {
        const search = searchVal.toLowerCase();
        return row.name.toLowerCase().includes(search) || row.code.toLowerCase().includes(search);
      }
      return true;
    });
  }, [tableData, selectedRegFilter, selectedEcoFilter, searchVal]);

  const exportCSV = () => {
    const headers = [
      "Echelle", "Code", "Nom", "Region", "Ecoregion", "NDVI Moyen", "VCI (%)", "VHI (%)", "Couverture Forestiere (%)", "Surface Foret (ha)", "Perte Annuelle (ha)", "Alerte",
    ];
    const rows = filteredData.map((r) => [
      scale.toUpperCase(), r.code, r.name, r.region, r.ecoregion, r.ndvi, r.vci, r.vhi, r.vegCover, r.forestArea, r.annualLoss, r.alert,
    ]);
    const csvContent = "data:text/csv;charset=utf-8,\uFEFF" + [headers.join(";"), ...rows.map((e) => e.join(";"))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `dynatsimo_indicateurs_${scale}_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const regionsList = [...new Set(communesList.map((c) => c.region).filter(Boolean))].sort();

  return (
    <section className="panel table-panel">
      <div className="table-header-row" style={{ display: "flex", flexDirection: "column", gap: "10px", marginBottom: "16px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", width: "100%", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
          <div className="scale-tabs">
            <button className={`scale-tab-btn ${scale === "commune" ? "active" : ""}`} onClick={() => setScale("commune")}>Communes</button>
            <button className={`scale-tab-btn ${scale === "district" ? "active" : ""}`} onClick={() => setScale("district")}>Districts</button>
            <button className={`scale-tab-btn ${scale === "region" ? "active" : ""}`} onClick={() => setScale("region")}>Régions</button>
          </div>

          <button onClick={exportCSV} className="btn-export" type="button"><Icons.Download /> Exporter CSV</button>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px", width: "100%" }}>
          <div className="table-search-box" style={{ border: "1px solid var(--border-color)", borderRadius: "var(--radius-md)", display: "flex", alignItems: "center", padding: "0 10px" }}>
            <Icons.Search />
            <input
              type="text"
              placeholder="Rechercher..."
              value={searchVal}
              onChange={(e) => setSearchVal(e.target.value)}
              style={{ border: "none", outline: "none", width: "100%", padding: "8px 6px", background: "transparent" }}
            />
          </div>

          <div className="filter-group">
            <select value={selectedRegFilter} onChange={(e) => setSelectedRegFilter(e.target.value)} style={{ padding: "8px 10px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", width: "100%" }}>
              <option value="">Toutes les régions</option>
              {regionsList.map((r) => (<option key={r} value={r}>{r}</option>))}
            </select>
          </div>

          <div className="filter-group">
            <select value={selectedEcoFilter} onChange={(e) => setSelectedEcoFilter(e.target.value)} style={{ padding: "8px 10px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", width: "100%" }}>
              <option value="">Toutes les écorégions</option>
              <option value="spiny">Forêt Épineuse</option>
              <option value="dry">Forêt Sèche</option>
              <option value="transition">Fourré de Transition</option>
              <option value="mangrove">Mangrove</option>
            </select>
          </div>
        </div>
      </div>

      <div className="table-container" style={{ maxHeight: "360px", overflowY: "auto" }}>
        <table>
          <thead>
            <tr>
              <th>Nom</th>
              <th>Région</th>
              <th>Écorégion</th>
              <th>NDVI</th>
              <th>VCI (%)</th>
              <th>VHI (%)</th>
              <th>Forêt (%)</th>
              <th>Surface (ha)</th>
              <th>Pertes (ha/an)</th>
              <th>Alerte</th>
            </tr>
          </thead>
          <tbody>
            {filteredData.length === 0 ? (
              <tr><td colSpan="10" style={{ textAlign: "center", padding: "40px" }}>Aucune ligne trouvée.</td></tr>
            ) : (
              filteredData.map((row) => (
                <tr key={row.code}>
                  <td><strong>{row.name}</strong></td>
                  <td>{row.region}</td>
                  <td>
                    <span className={`td-badge-ecoregion ${row.ecoregion.includes("spiny") ? "spiny" : row.ecoregion.includes("dry") ? "dry" : row.ecoregion.includes("transition") ? "transition" : "mangrove"}`}>
                      {row.ecoregion === "spiny" ? "Épineuse" : row.ecoregion === "dry" ? "Forêt Sèche" : row.ecoregion === "transition" ? "Transition" : row.ecoregion === "mangrove" ? "Mangrove" : row.ecoregion.substring(0, 15)}
                    </span>
                  </td>
                  <td><strong>{row.ndvi}</strong></td>
                  <td>{row.vci} %</td>
                  <td>{row.vhi} %</td>
                  <td><span className="td-badge accent">{row.vegCover} %</span></td>
                  <td>{row.forestArea?.toLocaleString()} ha</td>
                  <td style={{ color: "var(--danger)", fontWeight: "600" }}>-{row.annualLoss} ha</td>
                  <td>
                    <span className={`alert-badge ${row.alert === "Alerte Rouge" ? "danger" : row.alert === "Vigilance" ? "vigilance" : "stable"}`}>
                      {row.alert}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

createRoot(document.getElementById("root")).render(<App />);
