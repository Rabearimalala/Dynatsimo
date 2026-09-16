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
  { id: "carte", label: "Cartographie" },
  { id: "stats", label: "Statistiques & Analyses" },
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
  isohyetesMeta: "/data/isohyetes_metadata.json",
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
  Menu: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
    </svg>
  ),
  Close: () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
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

// Palette de référence des précipitations et des courbes isohyètes (6 teintes de bleu contrastées et bien visibles)
const PRECIP_BLUE_PALETTE = [
  "#dbeafe", // Bleu très clair / ciel
  "#93c5fd", // Bleu ciel
  "#3b82f6", // Bleu azur éclatant
  "#1d4ed8", // Bleu roi soutenu
  "#1e40af", // Bleu marine foncé
  "#172554", // Bleu nuit très profond
];

function getIsohyeteColor(val, minVal = 0, maxVal = 1000) {
  const ratio = maxVal > minVal ? Math.max(0, Math.min(1, (val - minVal) / (maxVal - minVal))) : 0.5;
  const idx = Math.min(PRECIP_BLUE_PALETTE.length - 1, Math.floor(ratio * PRECIP_BLUE_PALETTE.length));
  return PRECIP_BLUE_PALETTE[idx];
}

async function fetchJson(path) {
  const url = path.includes("?") ? `${path}&_t=${Date.now()}` : `${path}?_t=${Date.now()}`;
  const response = await fetch(url, { cache: "no-store" });
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
    if (!apiData.ndviClasses) {
      const ndviClasses = await fetchJson(`/data/ndvi_classes_metadata.json`);
      apiData.ndviClasses = ndviClasses;
    }
  } catch (e) {
    console.warn("ndviClasses non trouvées", e);
  }
  try {
    if (!apiData.isohyetesMeta) {
      const isohyetesMeta = await fetchJson(`/data/isohyetes_metadata.json`);
      apiData.isohyetesMeta = isohyetesMeta;
    }
  } catch (e) {
    console.warn("isohyetesMeta non trouvées", e);
  }
  return {
    data: apiData,
    source: "Base PostgreSQL via API Python",
  };
}

function App() {
  const [activeTab, setActiveTab] = React.useState("overview");
  const [statsCategory, setStatsCategory] = React.useState("precip");
  const [mapSubItem, setMapSubItem] = React.useState("precip");
  const [mobileNavOpen, setMobileNavOpen] = React.useState(false);
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

  const regionsList = React.useMemo(() => {
    if (!data?.communes) return [];
    return [...new Set(data.communes.map((c) => c.region).filter(Boolean))].sort();
  }, [data]);

  const selectedCommuneObj = React.useMemo(() => {
    if (!data?.communes) return null;
    return data.communes.find((c) => c.code === selectedCommune) || data.communes[0] || null;
  }, [data, selectedCommune]);

  const selectedCommuneName = selectedCommuneObj?.nom || "";

  if (loadError) {
    return (
      <div className="state-screen">
        <div className="state-brand">
          <span className="brand-mark brand-mark-lg">D</span>
          <div className="state-brand-text">
            <strong className="state-brand-title">DYNATSIMO</strong>
            <span className="state-brand-subtitle">GESTION AGRO-VÉGÉTALE</span>
          </div>
        </div>
        <strong style={{ marginTop: "8px", fontSize: "16px", color: "var(--danger)" }}>Erreur de chargement</strong>
        <p>{loadError}</p>
        <button onClick={() => setRetryTrigger((prev) => prev + 1)}>Réessayer</button>
      </div>
    );
  }

  if (loading || !data) {
    return (
      <div className="state-screen">
        <div className="state-brand">
          <span className="brand-mark brand-mark-lg">D</span>
          <div className="state-brand-text">
            <strong className="state-brand-title">DYNATSIMO</strong>
            <span className="state-brand-subtitle">GESTION AGRO-VÉGÉTALE</span>
          </div>
        </div>
        <div className="loader-spinner" style={{ marginTop: "6px" }}></div>
        <p style={{ marginTop: "10px", color: "var(--text-muted)", fontSize: "13px" }}>Connexion à la base de données et chargement des ressources...</p>
      </div>
    );
  }

  return (
    <div className="app-shell">
      {mobileNavOpen && (
        <div
          className="sidebar-backdrop"
          onClick={() => setMobileNavOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside className={`sidebar ${mobileNavOpen ? "mobile-open" : ""}`}>
        <div>
          <div className="brand">
            <div className="brand-wrapper">
              <span className="brand-mark">D</span>
              <div className="brand-text">
                <strong className="brand-title">DYNATSIMO</strong>
                <span className="brand-subtitle">GESTION AGRO-VÉGÉTALE</span>
              </div>
            </div>
            <button
              className="mobile-sidebar-close"
              onClick={() => setMobileNavOpen(false)}
              aria-label="Fermer le menu"
              type="button"
            >
              <Icons.Close />
            </button>
          </div>

          <nav className="nav-list" aria-label="Navigation principale">
            {tabs.map((tab) => {
              let Icon = Icons.Overview;
              if (tab.id === "stats") Icon = Icons.Stats;
              if (tab.id === "carte") Icon = Icons.Map;
              if (tab.id === "data") Icon = Icons.Database;

              const isStats = tab.id === "stats";
              const isCarte = tab.id === "carte";

              return (
                <div key={tab.id} style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                  <button
                    className={activeTab === tab.id ? "nav-item active" : "nav-item"}
                    onClick={() => {
                      setActiveTab(tab.id);
                      setMobileNavOpen(false);
                    }}
                    type="button"
                  >
                    <Icon />
                    <span>{tab.label}</span>
                  </button>

                  {/* Sous-onglets de Cartographie dans la barre latérale gauche */}
                  {isCarte && activeTab === "carte" && (
                    <div className="nav-sub-list">
                      {[
                        { id: "precip", label: "🌧️ Précipitations" },
                        { id: "deficit", label: "📉 Déficit 2020-22" },
                        { id: "ndvi_classes", label: "🌿 Végétation (NDVI)" },
                      ].map((sub) => (
                        <button
                          key={sub.id}
                          className={`nav-sub-item ${mapSubItem === sub.id ? "active" : ""}`}
                          onClick={(e) => {
                            e.stopPropagation();
                            setActiveTab("carte");
                            setMapSubItem(sub.id);
                            setMobileNavOpen(false);
                          }}
                          type="button"
                        >
                          {sub.label}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Sous-onglets de Statistiques & Analyses dans la barre latérale gauche */}
                  {isStats && activeTab === "stats" && (
                    <div className="nav-sub-list">
                      {[
                        { id: "precip", label: "🌧️ Précipitations" },
                        { id: "vegetation", label: "🌿 Suivi Végétation" },
                        { id: "saison", label: "🗓️ Saison des Pluies" },
                        { id: "sensors", label: "🛰️ Capteurs" },
                      ].map((sub) => (
                        <button
                          key={sub.id}
                          className={`nav-sub-item ${statsCategory === sub.id ? "active" : ""}`}
                          onClick={(e) => {
                            e.stopPropagation();
                            setActiveTab("stats");
                            setStatsCategory(sub.id);
                            setMobileNavOpen(false);
                          }}
                          type="button"
                        >
                          {sub.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
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
          <div style={{ display: "flex", alignItems: "center", gap: "10px", minWidth: 0 }}>
            <button
              className="mobile-menu-btn"
              onClick={() => setMobileNavOpen(true)}
              aria-label="Ouvrir le menu"
              type="button"
            >
              <Icons.Menu />
            </button>
            <div className="breadcrumb">
              <span className="breadcrumb-root">Dynatsimo</span>
              <span className="breadcrumb-separator">/</span>
              <span className="breadcrumb-active">{tabs.find((t) => t.id === activeTab)?.label}</span>
            </div>
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
          {activeTab === "carte" && (
            <Carte
              geojson={data.communesGeojson}
              communes={data.communes}
              precipRecords={data.precipRecords}
              annualData={data.annualData}
              ndviClasses={data.ndviClasses}
              isohyetesMeta={data.isohyetesMeta}
              mapSubItem={mapSubItem}
              setMapSubItem={setMapSubItem}
            />
          )}
          {activeTab === "stats" && (
            <Statistiques
              communes={data.communes}
              regions={regionsList}
              selectedRegion={selectedRegion}
              setSelectedRegion={setSelectedRegion}
              annualData={data.annualData}
              seasonData={data.seasonData}
              monthlyClimatology={data.monthlyClimatology}
              anomalies={data.anomalies}
              precipRecords={data.precipRecords}
              vegData={data.vegetationData}
              selectedCommune={selectedCommune}
              setSelectedCommune={setSelectedCommune}
              selectedCommuneName={selectedCommuneName}
              statsCategory={statsCategory}
              setStatsCategory={setStatsCategory}
            />
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
  if (type === "precip" || type === "rain") Icon = Icons.Rain;

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

  const startYear = annualData && annualData.length ? annualData[0].year : 1981;
  const endYear = annualData && annualData.length ? annualData[annualData.length - 1].year : 2026;
  const periodLabel = `${startYear}–${endYear}`;

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
      const isCurrentYear = payload[0].payload.year === endYear;
      return (
        <div className="recharts-custom-tooltip">
          <p className="recharts-custom-tooltip-title">
            Année {payload[0].payload.year} {isCurrentYear ? "(Année en cours)" : ""}
          </p>
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

  const avgPrecip = React.useMemo(() => {
    if (!annualData || annualData.length === 0) return "—";
    const average = averageFinite(
      annualData.map((d) => d.precip),
      1,
      null
    );
    if (average === null) return "—";
    return `${average.toLocaleString("fr-FR")} mm`;
  }, [annualData]);

  return (
    <>
      <section className="metric-grid">
        <Metric
          label="Communes Suivies"
          value={overview?.nb_communes ?? communes.length}
          type="communes"
        />
        <Metric label="Précipitation Moyenne" value={avgPrecip} type="precip" />
        <Metric label="Historique Données" value={overview?.nb_years || periodLabel} type="years" />
      </section>

      <div className="info-bulletin">
        <strong>À propos de Dynatsimo v2.1 :</strong> Plateforme d'analyse agro-pluviométrique et de l'état de la végétation alignée avec la méthodologie R (CHIRPS & PostgreSQL).
      </div>

      <section className="panel">
        <div className="panel-heading" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h2>
              <Icons.Stats /> Précipitations annuelles moyennes ({periodLabel})
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
  statsCategory,
  setStatsCategory,
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
        <h2>Paramètres Végétation</h2>

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
      </div>
    </section>
  );
}

// Saison Component matching R script sub-tabs and controls
function Saison({
  communes = [],
  regions = [],
  selectedRegion = "",
  setSelectedRegion,
  seasonData = [],
  selectedCommune = "",
  setSelectedCommune,
  selectedCommuneName = "",
  statsCategory,
  setStatsCategory,
}) {
  const [searchTerm, setSearchTerm] = React.useState("");
  const [subTab, setSubTab] = React.useState("start_end"); // 'start_end', 'max_month', 'timeline'

  // Min and Max season slider state
  const availableSeasons = React.useMemo(() => {
    if (!seasonData || seasonData.length === 0) return [1980, 2026];
    const list = seasonData.map((s) => Number(s.saison)).filter((s) => Number.isFinite(s));
    return list.length ? [Math.min(...list), Math.max(...list)] : [1980, 2026];
  }, [seasonData]);

  const [seasonRange, setSeasonRange] = React.useState([1980, 2026]);

  React.useEffect(() => {
    if (availableSeasons && availableSeasons.length === 2) {
      setSeasonRange(availableSeasons);
    }
  }, [availableSeasons]);

  const searchedCommunes = React.useMemo(() => {
    return communes.filter((c) => {
      const matchRegion = !selectedRegion || c.region === selectedRegion;
      const matchSearch =
        !searchTerm ||
        c.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.code.toLowerCase().includes(searchTerm.toLowerCase());
      return matchRegion && matchSearch;
    });
  }, [communes, searchTerm, selectedRegion]);

  // Ensure selectedCommune is aligned with searchedCommunes
  React.useEffect(() => {
    if (searchedCommunes.length > 0) {
      const currentExists = searchedCommunes.some(
        (c) => String(c.code).trim().toUpperCase() === String(selectedCommune).trim().toUpperCase()
      );
      if (!currentExists && setSelectedCommune) {
        setSelectedCommune(searchedCommunes[0].code);
      }
    }
  }, [searchedCommunes, selectedCommune, setSelectedCommune]);

  // Filter season rows for selected commune & season range with flexible matching
  const filteredSeasonRows = React.useMemo(() => {
    const targetCode = String(selectedCommune || (searchedCommunes[0]?.code ?? "")).trim().toUpperCase();
    const targetObj = communes.find((c) => String(c.code).trim().toUpperCase() === targetCode);
    const targetName = String(targetObj?.nom || selectedCommuneName || "").trim().toLowerCase();

    return seasonData.filter((row) => {
      if (!row) return false;
      const rCode = String(row.code_commune || row.code || "").trim().toUpperCase();
      const rNom = String(row.commune || row.nom || "").trim().toLowerCase();

      const isMatch =
        (targetCode && (rCode === targetCode || targetCode.includes(rCode) || rCode.includes(targetCode))) ||
        (targetName && (rNom === targetName || targetName.includes(rNom) || rNom.includes(targetName)));

      if (!isMatch) return false;

      const yr = Number(row.saison);
      return !isNaN(yr) && yr >= seasonRange[0] && yr <= seasonRange[1];
    });
  }, [seasonData, selectedCommune, selectedCommuneName, communes, searchedCommunes, seasonRange]);

  const hydroMonths = ["Oct", "Nov", "Dec", "Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep"];
  const monthOrderMap = { Oct: 10, Nov: 11, Dec: 12, Jan: 1, Fev: 2, Mar: 3, Avr: 4, Mai: 5, Jun: 6, Jul: 7, Aou: 8, Sep: 9 };
  const monthToVal = { Oct: 10, Nov: 11, Dec: 12, Jan: 13, Fev: 14, Mar: 15, Avr: 16, Mai: 17, Jun: 18 };

  // Data for "Début et fin de saison" chart
  const startEndChartData = React.useMemo(() => {
    return filteredSeasonRows
      .filter((r) => r.debut || r.fin)
      .map((r) => {
        const debutVal = monthToVal[r.debut] || 10;
        let finVal = monthToVal[r.fin] || 15;
        if (finVal < debutVal) finVal += 12;
        return {
          saison: r.saison,
          debut: r.debut ? debutVal : null,
          fin: r.fin ? finVal : null,
          debutLabel: r.debut || "—",
          finLabel: r.fin || "—",
          duree: r.duree || (r.debut && r.fin ? finVal - debutVal + 1 : 0),
        };
      });
  }, [filteredSeasonRows]);

  // Chronogram data sorted from most recent season to oldest
  const chronogramRows = React.useMemo(() => {
    return [...filteredSeasonRows].sort((a, b) => Number(b.saison) - Number(a.saison));
  }, [filteredSeasonRows]);

  const monthNamesFrMap = {
    Jan: "Janvier",
    Fev: "Février",
    Mar: "Mars",
    Avr: "Avril",
    Mai: "Mai",
    Jun: "Juin",
    Jul: "Juillet",
    Aou: "Août",
    Sep: "Septembre",
    Oct: "Octobre",
    Nov: "Novembre",
    Dec: "Décembre",
  };

  const CustomMaxMonthTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const monthCode = data.mois_plus_pluvieux || "";
      const monthFull = monthNamesFrMap[monthCode] || monthCode || "Mois le plus pluvieux";
      const precipVal = payload[0].value ?? data.precip ?? 0;

      return (
        <div className="recharts-custom-tooltip">
          <p className="recharts-custom-tooltip-title" style={{ fontSize: "12px", fontWeight: "700" }}>
            {monthFull}
          </p>
          <div className="recharts-custom-tooltip-item">
            <span>Précipitation :</span>
            <span>{Number(precipVal).toLocaleString("fr-FR")} mm</span>
          </div>
        </div>
      );
    }
    return null;
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
                    <defs>
                      <linearGradient id="colorMaxMonthPrecip" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--primary, #2563eb)" stopOpacity={0.85} />
                        <stop offset="95%" stopColor="var(--primary, #2563eb)" stopOpacity={0.35} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                    <XAxis dataKey="saison" stroke="var(--text-muted)" fontSize={11} angle={-45} textAnchor="end" height={50} />
                    <YAxis stroke="var(--text-muted)" fontSize={11} unit=" mm" />
                    <RechartsTooltip content={<CustomMaxMonthTooltip />} />
                    <Bar
                      name="Précipitation Mois Max"
                      dataKey="precip"
                      fill="url(#colorMaxMonthPrecip)"
                      stroke="var(--primary, #2563eb)"
                      strokeWidth={1}
                      radius={[4, 4, 0, 0]}
                    />
                  </RechartsBarChart>
                </ResponsiveContainer>
              </div>
            )}

            {subTab === "timeline" && (
              <div className="timeline" style={{ marginTop: "12px" }}>
                {chronogramRows.map((row) => {
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

function Statistiques({
  communes = [],
  regions = [],
  selectedRegion,
  setSelectedRegion,
  annualData = [],
  seasonData = [],
  monthlyClimatology = [],
  anomalies = [],
  precipRecords = [],
  vegData = [],
  selectedCommune: appSelectedCommune,
  setSelectedCommune: appSetSelectedCommune,
  selectedCommuneName,
  statsCategory: parentStatsCategory,
  setStatsCategory: parentSetStatsCategory,
}) {
  const [localStatsCategory, setLocalStatsCategory] = React.useState("precip");
  const statsCategory = parentStatsCategory || localStatsCategory;
  const setStatsCategory = parentSetStatsCategory || setLocalStatsCategory;

  const [modeCommune, setModeCommune] = React.useState("Toutes les communes");
  const [selectedCommune, setSelectedCommune] = React.useState(appSelectedCommune || communes[0]?.code || "");
  const [typeGraph, setTypeGraph] = React.useState("Histogramme");
  const [ordrePoly, setOrdrePoly] = React.useState(4);

  const selectedCommuneObj = React.useMemo(() => {
    return communes.find((c) => c.code === selectedCommune) || communes[0];
  }, [communes, selectedCommune]);

  const titreStats = modeCommune === "Toutes les communes" ? "Toutes les communes" : (selectedCommuneObj?.nom || selectedCommune);

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
          if (yr >= 1981 && Number.isFinite(Number(r.precip))) {
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

  const histogramData = React.useMemo(() => {
    const values = communeAnnualSeries.map((d) => d.p).filter((v) => Number.isFinite(v) && v > 0);
    if (values.length === 0) return [];
    const minVal = Math.min(...values);
    const maxVal = Math.max(...values);
    const rawSpan = maxVal - minVal;
    const targetBins = 10;
    const rawStep = rawSpan / targetBins;
    const mag = Math.pow(10, Math.floor(Math.log10(rawStep > 0 ? rawStep : 1)));
    const normStep = rawStep / mag;
    let niceStep = 1 * mag;
    if (normStep <= 1.2) niceStep = 1 * mag;
    else if (normStep <= 2.2) niceStep = 2 * mag;
    else if (normStep <= 3.8) niceStep = (mag >= 10 ? 2.5 * mag : 2.5);
    else if (normStep <= 7.5) niceStep = 5 * mag;
    else niceStep = 10 * mag;
    niceStep = niceStep >= 1 ? Math.round(niceStep) : niceStep;
    const start = Math.floor(minVal / niceStep) * niceStep;
    const bins = [];
    let curr = start;
    while (curr < maxVal || bins.length < 5) {
      const bEnd = curr + niceStep;
      bins.push({
        start: curr,
        end: bEnd,
        label: `${curr}–${bEnd}`,
        rangeText: `${curr} à ${bEnd} mm`,
        count: 0,
        years: [],
      });
      curr = bEnd;
      if (bins.length >= 16) break;
    }
    communeAnnualSeries.forEach((d) => {
      const v = d.p;
      if (!Number.isFinite(v) || v <= 0) return;
      let idx = Math.floor((v - start) / niceStep);
      idx = Math.max(0, Math.min(bins.length - 1, idx));
      if (bins[idx]) {
        bins[idx].count += 1;
        if (d.year) bins[idx].years.push(d.year);
      }
    });
    return bins;
  }, [communeAnnualSeries]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      {statsCategory === "vegetation" && (
        <SuiviVegetation
          communes={communes}
          regions={regions}
          selectedRegion={selectedRegion}
          setSelectedRegion={setSelectedRegion}
          selectedCommune={appSelectedCommune}
          setSelectedCommune={appSetSelectedCommune}
          selectedCommuneName={selectedCommuneName}
          vegData={vegData}
          statsCategory={statsCategory}
          setStatsCategory={setStatsCategory}
        />
      )}

      {statsCategory === "saison" && (
        <Saison
          communes={communes}
          regions={regions}
          selectedRegion={selectedRegion}
          setSelectedRegion={setSelectedRegion}
          seasonData={seasonData}
          selectedCommune={appSelectedCommune}
          selectedCommuneName={selectedCommuneName}
          setSelectedCommune={appSetSelectedCommune}
          statsCategory={statsCategory}
          setStatsCategory={setStatsCategory}
        />
      )}

      {statsCategory === "sensors" && (
        <ComparaisonCapteurs
          vegData={vegData}
          selectedCommune={appSelectedCommune}
        />
      )}

      {statsCategory === "precip" && (
        <>
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
              <h2>Paramètres Pluviométrie</h2>

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
                <div className="filter-group" style={{ marginTop: "10px" }}>
                  <label htmlFor="commune-select-stat">Commune :</label>
                  <select
                    id="commune-select-stat"
                    value={selectedCommune}
                    onChange={(e) => setSelectedCommune(e.target.value)}
                  >
                    {communes.map((c) => (
                      <option key={c.code} value={c.code}>
                        {c.nom} ({c.code})
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
                      style={{ textAlign: "left", justifyContent: "flex-start", padding: "8px 10px", fontSize: "12px" }}
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
                <div style={{ width: "100%", height: 390, marginTop: "12px" }}>
                  <ResponsiveContainer>
                    <RechartsBarChart data={histogramData} margin={{ top: 20, right: 20, bottom: 35, left: 15 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                      <XAxis
                        dataKey="label"
                        stroke="var(--text-muted)"
                        fontSize={11}
                        angle={-30}
                        textAnchor="end"
                        height={50}
                        label={{
                          value: "Classes de précipitation annuelle (mm)",
                          position: "insideBottom",
                          offset: -8,
                          fontSize: 12,
                          fill: "var(--text-main)",
                          fontWeight: 600,
                        }}
                      />
                      <YAxis
                        stroke="var(--text-muted)"
                        fontSize={11}
                        allowDecimals={false}
                        label={{
                          value: "Nombre d'années (Fréquence)",
                          angle: -90,
                          position: "insideLeft",
                          fontSize: 12,
                          fill: "var(--text-main)",
                          offset: 5,
                        }}
                      />
                      <RechartsTooltip
                        formatter={(val, name, item) => [
                          `${val} année${val > 1 ? "s" : ""}${item?.payload?.years?.length ? ` (${item.payload.years.join(", ")})` : ""}`,
                          "Fréquence"
                        ]}
                        labelFormatter={(label, items) => {
                          const itm = items?.[0]?.payload;
                          return `Précipitation : ${itm?.rangeText || `${label} mm`}`;
                        }}
                      />
                      <Bar name="Nombre d'années" dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    </RechartsBarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {typeGraph === "Tendance" && (
                <div style={{ width: "100%", height: 390, marginTop: "12px" }}>
                  <ResponsiveContainer>
                    <ComposedChart data={trendData} margin={{ top: 20, right: 20, bottom: 30, left: 15 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                      <XAxis
                        dataKey="year"
                        stroke="var(--text-muted)"
                        fontSize={11}
                        label={{ value: "Année", position: "insideBottom", offset: -5, fontSize: 11, fill: "var(--text-main)" }}
                      />
                      <YAxis
                        stroke="var(--text-muted)"
                        fontSize={11}
                        unit=" mm"
                        label={{ value: "Précipitation annuelle (mm)", angle: -90, position: "insideLeft", fontSize: 11, fill: "var(--text-main)", offset: 5 }}
                      />
                      <RechartsTooltip
                        formatter={(val, name) => [`${Math.round(val)} mm`, name]}
                        labelFormatter={(year) => `Année ${year}`}
                      />
                      <Legend verticalAlign="top" height={36} />
                      <Line name="Précipitation annuelle (mm)" type="monotone" dataKey="p" stroke="#64748b" strokeWidth={1.5} dot={{ r: 3, fill: "#2563eb" }} />
                      <Line name={`Tendance polynomiale (Ordre ${ordrePoly})`} type="monotone" dataKey="trend" stroke="#ef4444" strokeWidth={3} dot={false} />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              )}

              {typeGraph === "Climatologie mensuelle" && (
                <div style={{ width: "100%", height: 390, marginTop: "12px" }}>
                  <ResponsiveContainer>
                    <RechartsBarChart data={climatologyData} margin={{ top: 20, right: 20, bottom: 30, left: 15 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                      <XAxis
                        dataKey="month"
                        stroke="var(--text-muted)"
                        fontSize={12}
                        label={{ value: "Mois de l'année", position: "insideBottom", offset: -5, fontSize: 11, fill: "var(--text-main)" }}
                      />
                      <YAxis
                        stroke="var(--text-muted)"
                        fontSize={11}
                        unit=" mm"
                        label={{ value: "Précipitation moyenne (mm)", angle: -90, position: "insideLeft", fontSize: 11, fill: "var(--text-main)", offset: 5 }}
                      />
                      <RechartsTooltip formatter={(val) => [`${Math.round(val)} mm`, "Précipitation Moyenne"]} />
                      <Bar name="Précipitations moyennes (mm)" dataKey="p" fill="#2563eb" radius={[4, 4, 0, 0]} />
                    </RechartsBarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {typeGraph === "Anomalies" && (
                <div style={{ width: "100%", height: 390, marginTop: "12px" }}>
                  <ResponsiveContainer>
                    <RechartsBarChart data={anomalyData} margin={{ top: 20, right: 20, bottom: 30, left: 15 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                      <XAxis
                        dataKey="year"
                        stroke="var(--text-muted)"
                        fontSize={11}
                        label={{ value: "Année", position: "insideBottom", offset: -5, fontSize: 11, fill: "var(--text-main)" }}
                      />
                      <YAxis
                        stroke="var(--text-muted)"
                        fontSize={11}
                        unit=" mm"
                        label={{ value: "Anomalie pluviométrique (mm)", angle: -90, position: "insideLeft", fontSize: 11, fill: "var(--text-main)", offset: 5 }}
                      />
                      <RechartsTooltip
                        formatter={(val) => [`${val > 0 ? "+" : ""}${Math.round(val)} mm`, "Anomalie"]}
                        labelFormatter={(year) => `Année ${year}`}
                      />
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
        </>
      )}
    </div>
  );
}

// Carte Component matching R script carte_precip & carte_deficit + NDVI 6-Classes + Isohyètes CHIRPS
function Carte({
  geojson,
  communes = [],
  precipRecords = [],
  annualData = [],
  ndviClasses = null,
  isohyetesMeta = null,
  mapSubItem: parentMapSubItem,
  setMapSubItem: parentSetMapSubItem,
}) {
  const features = geojson?.features ?? [];
  const [localMapSubItem, setLocalMapSubItem] = React.useState("precip");
  const mapSubItem = parentMapSubItem || localMapSubItem;
  const setMapSubItem = parentSetMapSubItem || setLocalMapSubItem;
  const [typeCarte, setTypeCarte] = React.useState("Choroplèthe"); // 'Choroplèthe' vs 'Isohyètes'
  const [typePeriode, setTypePeriode] = React.useState("Mensuel"); // 'Mensuel' | 'Annuel' | 'Décennies'
  const [selectedDecades, setSelectedDecades] = React.useState(["1981–1989"]);
  const [selectedYears, setSelectedYears] = React.useState([2024]);
  const [selectedMonth, setSelectedMonth] = React.useState("Jan");
  const [basemap, setBasemap] = React.useState("OpenStreetMap");
  const [showBasemapMenu, setShowBasemapMenu] = React.useState(false);
  const basemapRef = React.useRef(null);
  const [selectedFeatureCode, setSelectedFeatureCode] = React.useState(features[0]?.properties?.code ?? "");

  React.useEffect(() => {
    function handleClickOutside(event) {
      if (basemapRef.current && !basemapRef.current.contains(event.target)) {
        setShowBasemapMenu(false);
      }
    }
    if (showBasemapMenu) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [showBasemapMenu]);

  // Isohyètes CHIRPS States
  const [localIsohyetesMeta, setLocalIsohyetesMeta] = React.useState(isohyetesMeta);
  const [loadedIsohyete, setLoadedIsohyete] = React.useState({ key: "", geojson: null });
  const [showIsohyeteContours, setShowIsohyeteContours] = React.useState(true);
  const [isohyeteLineStyle, setIsohyeteLineStyle] = React.useState("colored"); // 'colored' | 'qgis'

  React.useEffect(() => {
    if (isohyetesMeta) {
      setLocalIsohyetesMeta(isohyetesMeta);
    }
  }, [isohyetesMeta]);

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

  const basemapOptions = React.useMemo(
    () => [
      {
        id: "OpenStreetMap",
        label: "OpenStreetMap",
        shortLabel: "Plan OSM",
        icon: "🗺️",
        desc: "Cartographie standard OSM",
        url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      },
      {
        id: "Google Satellite",
        label: "Google Satellite",
        shortLabel: "Satellite",
        icon: "🛰️",
        desc: "Imagerie satellite HD",
        url: "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attribution: "&copy; Google Satellites",
      },
      {
        id: "Google Hybrid",
        label: "Google Hybride",
        shortLabel: "Hybride",
        icon: "🌍",
        desc: "Satellite + routes & noms",
        url: "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attribution: "&copy; Google Hybride",
      },
      {
        id: "CartoDB Positron",
        label: "CartoDB Clair",
        shortLabel: "Clair",
        icon: "☀️",
        desc: "Fond clair épuré (idéal choroplèthe)",
        url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
      },
      {
        id: "CartoDB Dark",
        label: "CartoDB Sombre",
        shortLabel: "Sombre",
        icon: "🌙",
        desc: "Fond sombre contrasté",
        url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
      },
      {
        id: "ESRI Topo",
        label: "Topographique",
        shortLabel: "Relief",
        icon: "⛰️",
        desc: "Relief et courbes de niveau",
        url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        attribution: '&copy; <a href="https://www.esri.com/">Esri</a>',
      },
    ],
    []
  );

  const tileUrls = React.useMemo(() => {
    const map = {};
    basemapOptions.forEach((b) => {
      map[b.id] = b.url;
    });
    return map;
  }, [basemapOptions]);

  const tileAttributions = React.useMemo(() => {
    const map = {};
    basemapOptions.forEach((b) => {
      map[b.id] = b.attribution;
    });
    return map;
  }, [basemapOptions]);

  const availableYears = React.useMemo(() => {
    const list = annualData.map((d) => d.year).sort((a, b) => a - b);
    return list.length ? list : Array.from({ length: 46 }, (_, i) => 1981 + i);
  }, [annualData]);

  // Precipitation Timeline Player States & Logic
  const [isPlayingPrecipTimeline, setIsPlayingPrecipTimeline] = React.useState(false);
  const [precipPlaySpeed, setPrecipPlaySpeed] = React.useState(1200);

  const monthNumMap = React.useMemo(() => ({
    Jan: 1, Fev: 2, Mar: 3, Avr: 4, Mai: 5, Jun: 6,
    Jul: 7, Aou: 8, Sep: 9, Oct: 10, Nov: 11, Dec: 12,
  }), []);

  const precipTimelineList = React.useMemo(() => {
    if (typePeriode === "Décennies") {
      const decadesFromMeta = localIsohyetesMeta?.decades;
      if (decadesFromMeta && decadesFromMeta.length > 0) {
        return decadesFromMeta.map((dec) => ({
          key: dec,
          label: dec,
          type: "decade",
          value: dec,
        }));
      }
      const maxYear = availableYears[availableYears.length - 1] || 2026;
      return [
        { key: "1981–1989", label: "1981–1989", type: "decade", value: "1981–1989" },
        { key: "1990–1999", label: "1990–1999", type: "decade", value: "1990–1999" },
        { key: "2000–2009", label: "2000–2009", type: "decade", value: "2000–2009" },
        { key: "2010–2019", label: "2010–2019", type: "decade", value: "2010–2019" },
        { key: `2020–${maxYear}`, label: `2020–${maxYear}`, type: "decade", value: `2020–${maxYear}` },
      ];
    }
    if (typePeriode === "Mensuel") {
      const list = [];
      const mCodes = ["Jan", "Fev", "Mar", "Avr", "Mai", "Jun", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec"];
      const mNames = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];
      availableYears.forEach((y) => {
        mCodes.forEach((mCode, idx) => {
          list.push({
            key: `ym_${y}_${mCode}`,
            label: `${mNames[idx]} ${y}`,
            type: "month_year",
            year: y,
            month: mCode,
          });
        });
      });
      return list;
    }
    // typePeriode === "Annuel"
    return availableYears.map((y) => ({
      key: `year_${y}`,
      label: `Année ${y}`,
      type: "year",
      year: y,
    }));
  }, [typePeriode, availableYears]);

  const currentPrecipTimelineIndex = React.useMemo(() => {
    if (typePeriode === "Décennies") {
      const idx = precipTimelineList.findIndex((item) => item.value === selectedDecades[0]);
      return idx >= 0 ? idx : 0;
    }
    if (typePeriode === "Mensuel") {
      const currYear = selectedYears[0] || availableYears[0] || 1981;
      const currMonth = selectedMonth !== "Tous" ? selectedMonth : "Jan";
      const idx = precipTimelineList.findIndex((item) => item.year === currYear && item.month === currMonth);
      return idx >= 0 ? idx : 0;
    }
    const currYear = selectedYears[0] || availableYears[0] || 1981;
    const idx = precipTimelineList.findIndex((item) => item.year === currYear);
    return idx >= 0 ? idx : 0;
  }, [precipTimelineList, typePeriode, selectedDecades, selectedYears, selectedMonth, availableYears]);

  const activePrecipTimelineItem = React.useMemo(() => {
    return precipTimelineList[currentPrecipTimelineIndex] || precipTimelineList[0];
  }, [precipTimelineList, currentPrecipTimelineIndex]);

  // Playback timer effect for Precipitation
  React.useEffect(() => {
    if (!isPlayingPrecipTimeline || precipTimelineList.length === 0) return;
    const timer = setInterval(() => {
      const nextIndex = (currentPrecipTimelineIndex + 1) % precipTimelineList.length;
      const nextItem = precipTimelineList[nextIndex];
      if (nextItem) {
        if (nextItem.type === "decade") {
          setSelectedDecades([nextItem.value]);
        } else if (nextItem.type === "month_year") {
          setSelectedYears([nextItem.year]);
          setSelectedMonth(nextItem.month);
        } else {
          setSelectedYears([nextItem.year]);
        }
      }
    }, precipPlaySpeed);
    return () => clearInterval(timer);
  }, [isPlayingPrecipTimeline, precipTimelineList, currentPrecipTimelineIndex, precipPlaySpeed]);

  const handlePrecipTimelineStep = (direction) => {
    if (precipTimelineList.length === 0) return;
    let nextIndex = currentPrecipTimelineIndex + direction;
    if (nextIndex < 0) nextIndex = precipTimelineList.length - 1;
    if (nextIndex >= precipTimelineList.length) nextIndex = 0;
    const nextItem = precipTimelineList[nextIndex];
    if (nextItem) {
      if (nextItem.type === "decade") {
        setSelectedDecades([nextItem.value]);
      } else if (nextItem.type === "month_year") {
        setSelectedYears([nextItem.year]);
        setSelectedMonth(nextItem.month);
      } else {
        setSelectedYears([nextItem.year]);
      }
    }
  };

  const handlePrecipTimelineScrub = (index) => {
    const item = precipTimelineList[index];
    if (item) {
      if (item.type === "decade") {
        setSelectedDecades([item.value]);
      } else if (item.type === "month_year") {
        setSelectedYears([item.year]);
        setSelectedMonth(item.month);
      } else {
        setSelectedYears([item.year]);
      }
    }
  };

  const activeIsohyeteKey = React.useMemo(() => {
    if (typePeriode === "Décennies") {
      const dec = (selectedDecades[0] || "1981–1989").replace(/–|-/g, "_");
      return `isohyete_decade_${dec}`;
    }
    const year = selectedYears[0] || 1981;
    if (typePeriode === "Annuel") {
      return `isohyete_${year}_annual`;
    }
    // typePeriode === "Mensuel"
    const mNum = monthNumMap[selectedMonth] || 1;
    return `isohyete_${year}_${String(mNum).padStart(2, "0")}`;
  }, [typePeriode, selectedDecades, selectedYears, selectedMonth, monthNumMap]);

  const activeIsohyeteItem = React.useMemo(() => {
    return localIsohyetesMeta?.items?.[activeIsohyeteKey] || null;
  }, [localIsohyetesMeta, activeIsohyeteKey]);

  React.useEffect(() => {
    if (typeCarte !== "Isohyètes" || !activeIsohyeteItem?.geojsonUrl) {
      return;
    }
    let isMounted = true;
    const reqKey = activeIsohyeteKey;
    fetchJson(activeIsohyeteItem.geojsonUrl)
      .then((gj) => {
        if (isMounted) {
          setLoadedIsohyete({ key: reqKey, geojson: gj });
        }
      })
      .catch((e) => {
        console.warn("Erreur chargement GeoJSON isohyètes", e);
      });
    return () => {
      isMounted = false;
    };
  }, [typeCarte, activeIsohyeteItem, activeIsohyeteKey]);

  // Compute calculated rainfall values for features based on active filters
  const calculatedPrecipMap = React.useMemo(() => {
    const map = {};
    if (!precipRecords || precipRecords.length === 0) return map;

    let filtered = precipRecords;
    if (typePeriode === "Décennies") {
      const years = [];
      const selectedDec = selectedDecades[0] || "1981–1989";
      const parts = selectedDec.split(/–|-/);
      if (parts.length === 2) {
        const startY = parseInt(parts[0], 10);
        const endY = parseInt(parts[1], 10);
        if (!isNaN(startY) && !isNaN(endY)) {
          for (let y = startY; y <= endY; y++) years.push(y);
        }
      }
      filtered = filtered.filter((r) => years.includes(r.year));
    } else if (typePeriode === "Mensuel") {
      const currYear = selectedYears[0] || 1981;
      const mNum = monthNumMap[selectedMonth] || 1;
      filtered = filtered.filter((r) => r.year === currYear && r.month === mNum);
    } else {
      // typePeriode === "Annuel" (Cumul annuel complet de tous les mois de l'année)
      const currYear = selectedYears[0] || 1981;
      filtered = filtered.filter((r) => r.year === currYear);
    }

    const sums = {};
    filtered.forEach((r) => {
      sums[r.code] = (sums[r.code] || 0) + r.precip;
    });

    Object.keys(sums).forEach((code) => {
      map[code] = Math.round(sums[code]);
    });

    return map;
  }, [precipRecords, typePeriode, selectedDecades, selectedYears, selectedMonth, monthNumMap]);

  // Statistiques dynamiques et bornes arrondies (nice round numbers : 10, 50, 100, 200...) pour TOUTES les cartes
  const activePrecipStats = React.useMemo(() => {
    if (typeCarte === "Isohyètes" && activeIsohyeteItem) {
      const minV = Math.round(activeIsohyeteItem.minPrecip ?? 0);
      const maxV = Math.round(activeIsohyeteItem.maxPrecip ?? 100);
      const meanV = Math.round(activeIsohyeteItem.meanPrecip ?? ((minV + maxV) / 2));
      return { min: minV, max: maxV, mean: meanV };
    }
    const vals = Object.values(calculatedPrecipMap);
    if (vals.length > 0) {
      const minV = Math.min(...vals);
      const maxV = Math.max(...vals);
      const meanV = Math.round(vals.reduce((a, b) => a + b, 0) / vals.length);
      return { min: minV, max: maxV, mean: meanV };
    }
    return { min: 0, max: 800, mean: 400 };
  }, [typeCarte, activeIsohyeteItem, calculatedPrecipMap]);

  const { precipTicks: activePrecipScaleTicks, scaleMin: precipScaleMin, scaleMax: precipScaleMax } = React.useMemo(() => {
    let minV = activePrecipStats.min;
    let maxV = activePrecipStats.max;
    if (minV >= maxV) {
      minV = 0;
      maxV = maxV > 0 ? maxV : 100;
    }

    const rawSpan = maxV - minV;
    const targetCount = 5;
    const rawStep = rawSpan / targetCount;

    // Calcul d'un pas propre et arrondi (10, 20, 25, 50, 100, 200, 250, 500, etc.)
    const mag = Math.pow(10, Math.floor(Math.log10(rawStep > 0 ? rawStep : 1)));
    const normStep = rawStep / mag;
    let niceStep = 1 * mag;
    if (normStep <= 1.2) niceStep = 1 * mag;
    else if (normStep <= 2.2) niceStep = 2 * mag;
    else if (normStep <= 3.8) niceStep = (mag >= 10 ? 2.5 * mag : 2.5);
    else if (normStep <= 7.5) niceStep = 5 * mag;
    else niceStep = 10 * mag;

    niceStep = niceStep >= 1 ? Math.round(niceStep) : niceStep;

    // Point de départ arrondi
    let start = Math.floor(minV / niceStep) * niceStep;
    if (minV >= 0 && (start < 0 || minV < niceStep * 0.8)) {
      start = 0;
    }

    const ticks = [start];
    let curr = start;
    while (curr < maxV || ticks.length < 5) {
      curr += niceStep;
      ticks.push(Number.isInteger(curr) ? curr : Math.round(curr * 10) / 10);
      if (ticks.length >= 8) break;
    }

    const sMin = ticks[0] ?? minV;
    const sMax = ticks[ticks.length - 1] ?? maxV;

    return { precipTicks: ticks, scaleMin: sMin, scaleMax: sMax };
  }, [activePrecipStats]);

  // Isohyetes Style & Tooltip Handlers avec dégradé bleu (clair à foncé) — Tracé fin et précis
  const getIsohyeteStyle = React.useCallback(
    (feature) => {
      const isohyetVal = feature.properties?.isohyete ?? 0;
      const isIndex = isohyetVal % 100 === 0;
      if (isohyeteLineStyle === "qgis") {
        return {
          color: isIndex ? "#0f172a" : "#334155",
          weight: isIndex ? 1.1 : 0.6,
          opacity: 0.85,
        };
      }
      const color = getIsohyeteColor(isohyetVal, precipScaleMin, precipScaleMax);
      return {
        color: color,
        weight: isIndex ? 1.3 : 0.7,
        opacity: 0.9,
      };
    },
    [isohyeteLineStyle, precipScaleMin, precipScaleMax]
  );

  const onEachIsohyeteFeature = React.useCallback(
    (feature, layer) => {
      const p = feature.properties;
      layer.bindTooltip(
        `<div style="font-weight:700;font-size:12px;color:#1e40af;">🌧️ Isohyète : ${p.label || `${p.isohyete} mm`}</div>
         <div style="font-size:11px;color:#64748b;">Précipitation égale à ${p.isohyete} mm</div>`,
        { sticky: true, direction: "top", opacity: 0.95 }
      );
      layer.on({
        mouseover: (e) => {
          const l = e.target;
          l.setStyle({ weight: 2.8, opacity: 1, color: "#172554" });
        },
        mouseout: (e) => {
          const l = e.target;
          l.setStyle(getIsohyeteStyle(feature));
        },
      });
    },
    [getIsohyeteStyle]
  );

  const getCommuneIsohyeteOverlayStyle = React.useCallback(
    (feature) => {
      const code = feature.properties.code;
      const isSelected = selectedFeatureCode === code;

      if (isSelected) {
        return {
          fillColor: "rgba(37, 99, 235, 0.15)",
          fillOpacity: 0.15,
          color: "#1d4ed8",
          weight: 2.5,
          opacity: 1,
        };
      }

      return {
        fillColor: "transparent",
        fillOpacity: 0,
        color: "#94a3b8", // Gris clair
        weight: 0.9,
        dashArray: "3, 3", // Pointillés
        opacity: 0.85,
      };
    },
    [selectedFeatureCode]
  );

  // Style function for Precipitation and Deficit choropleth features
  const getFeatureStyle = React.useCallback(
    (feature) => {
      const code = feature.properties.code;
      const isSelected = selectedFeatureCode === code;

      if (mapSubItem === "deficit") {
        const deficit = feature.properties.deficit ?? 0;
        const deficitPalette = [
          "#fff5f0",
          "#fee0d2",
          "#fcbba1",
          "#fc9272",
          "#fb6a4a",
          "#ef3b2c",
          "#cb181d",
          "#99000d",
          "#67000d",
        ];
        // Plage de déficit de 0% à -40% (adaptée aux données réelles de -6.9% à -29.9%)
        const absVal = Math.max(0, Math.min(40, Math.abs(deficit)));
        const ratio = absVal / 40.0;
        const idx = Math.min(deficitPalette.length - 1, Math.floor(ratio * deficitPalette.length));
        const fillColor = deficitPalette[idx];

        return {
          fillColor,
          fillOpacity: isSelected ? 0.95 : 0.75,
          color: isSelected ? "#0f172a" : "#334155",
          weight: isSelected ? 2.5 : 0.9,
          opacity: 0.85,
        };
      }

      // Précipitations Map (Carte choroplèthe en dégradé bleu)
      const val = calculatedPrecipMap[code] ?? feature.properties.precip ?? 0;
      const minVal = precipScaleMin;
      const maxVal = precipScaleMax;
      const ratio = maxVal > minVal ? Math.max(0, Math.min(1, (val - minVal) / (maxVal - minVal))) : 0.5;
      const idx = Math.min(PRECIP_BLUE_PALETTE.length - 1, Math.floor(ratio * PRECIP_BLUE_PALETTE.length));
      const fillColor = PRECIP_BLUE_PALETTE[idx];

      return {
        fillColor,
        fillOpacity: isSelected ? 0.95 : 0.8,
        color: isSelected ? "#0f172a" : "#334155",
        weight: isSelected ? 2.5 : 0.9,
        opacity: 0.85,
      };
    },
    [selectedFeatureCode, mapSubItem, calculatedPrecipMap, precipScaleMin, precipScaleMax]
  );

  // Style function for Commune Layer overlaid on top of NDVI raster
  const getCommuneNdviOverlayStyle = React.useCallback(
    (feature) => {
      const code = feature.properties.code;
      const isSelected = selectedFeatureCode === code;

      if (isSelected) {
        return {
          fillColor: "rgba(59, 130, 246, 0.25)",
          fillOpacity: 0.25,
          color: "#2563eb",
          weight: 2.5,
          opacity: 1,
        };
      }

      return {
        fillColor:
          communeOverlayStyle === "light_tint" ? "rgba(255, 255, 255, 0.08)" : "transparent",
        fillOpacity: communeOverlayStyle === "light_tint" ? 0.08 : 0,
        color: "#1e293b",
        weight: 1.0,
        opacity: 0.85,
      };
    },
    [selectedFeatureCode, communeOverlayStyle]
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
                <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", cursor: "pointer" }}>
                  <input
                    type="radio"
                    name="type_carte"
                    value="Choroplèthe"
                    checked={typeCarte === "Choroplèthe"}
                    onChange={(e) => setTypeCarte(e.target.value)}
                  />
                  Choroplèthe
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", cursor: "pointer" }}>
                  <input
                    type="radio"
                    name="type_carte"
                    value="Isohyètes"
                    checked={typeCarte === "Isohyètes"}
                    onChange={(e) => setTypeCarte(e.target.value)}
                  />
                  Isohyètes (CHIRPS)
                </label>
              </div>
            </div>

            {/* Options additionnelles pour Isohyètes */}
            {typeCarte === "Isohyètes" && (
              <div
                style={{
                  marginTop: "10px",
                  background: "var(--bg-secondary)",
                  padding: "10px",
                  borderRadius: "var(--radius-md)",
                  border: "1px solid var(--border-color)",
                }}
              >
                <label
                  style={{
                    fontWeight: "700",
                    color: "var(--primary)",
                    fontSize: "12px",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                  }}
                >
                  🌧️ Options Isohyètes :
                </label>
                <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginTop: "6px" }}>
                  <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "11px", cursor: "pointer" }}>
                    <input
                      type="checkbox"
                      checked={showIsohyeteContours}
                      onChange={(e) => setShowIsohyeteContours(e.target.checked)}
                    />
                    <span>Courbes isohyètes (intervalle 50 mm)</span>
                  </label>

                  {showIsohyeteContours && (
                    <div style={{ display: "flex", gap: "10px", fontSize: "11px", marginLeft: "18px", marginTop: "2px" }}>
                      <label style={{ display: "flex", alignItems: "center", gap: "4px", cursor: "pointer" }}>
                        <input
                          type="radio"
                          name="isohyete_line_style"
                          value="colored"
                          checked={isohyeteLineStyle === "colored"}
                          onChange={(e) => setIsohyeteLineStyle(e.target.value)}
                        />
                        Colorées
                      </label>
                      <label style={{ display: "flex", alignItems: "center", gap: "4px", cursor: "pointer" }}>
                        <input
                          type="radio"
                          name="isohyete_line_style"
                          value="qgis"
                          checked={isohyeteLineStyle === "qgis"}
                          onChange={(e) => setIsohyeteLineStyle(e.target.value)}
                        />
                        Style SIG (QGIS)
                      </label>
                    </div>
                  )}
                </div>

                {activeIsohyeteItem && (
                  <div
                    style={{
                      marginTop: "8px",
                      paddingTop: "6px",
                      borderTop: "1px dashed var(--border-color)",
                      fontSize: "11px",
                      display: "flex",
                      flexDirection: "column",
                      gap: "3px",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <span>Min :</span>
                      <strong>{activeIsohyeteItem.minPrecip} mm</strong>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <span>Moyenne :</span>
                      <strong>{activeIsohyeteItem.meanPrecip} mm</strong>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <span>Max :</span>
                      <strong style={{ color: "var(--primary)" }}>{activeIsohyeteItem.maxPrecip} mm</strong>
                    </div>
                  </div>
                )}
              </div>
            )}

            <div className="filter-group" style={{ marginTop: "10px" }}>
              <label style={{ fontWeight: "700" }}>Période d'affichage :</label>
              <div style={{ display: "flex", gap: "8px", marginTop: "4px", flexWrap: "wrap" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "11px", cursor: "pointer" }}>
                  <input
                    type="radio"
                    name="type_periode"
                    value="Mensuel"
                    checked={typePeriode === "Mensuel"}
                    onChange={() => {
                      setTypePeriode("Mensuel");
                      if (selectedMonth === "Tous") setSelectedMonth("Jan");
                    }}
                  />
                  Mensuel (Mois/Année)
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "11px", cursor: "pointer" }}>
                  <input
                    type="radio"
                    name="type_periode"
                    value="Annuel"
                    checked={typePeriode === "Annuel"}
                    onChange={() => {
                      setTypePeriode("Annuel");
                      setSelectedMonth("Tous");
                    }}
                  />
                  Annuel (Cumul)
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "11px", cursor: "pointer" }}>
                  <input
                    type="radio"
                    name="type_periode"
                    value="Décennies"
                    checked={typePeriode === "Décennies"}
                    onChange={() => setTypePeriode("Décennies")}
                  />
                  Décennies
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
                  {(localIsohyetesMeta?.decades || [
                    "1981–1989",
                    "1990–1999",
                    "2000–2009",
                    "2010–2019",
                    `2020–${availableYears[availableYears.length - 1] || 2026}`,
                  ]).map((dec) => (
                    <option key={dec} value={dec}>
                      {dec}
                    </option>
                  ))}
                </select>
              </div>
            ) : typePeriode === "Mensuel" ? (
              <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
                <div className="filter-group" style={{ flex: 1 }}>
                  <label htmlFor="mois-sel">Mois :</label>
                  <select
                    id="mois-sel"
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(e.target.value)}
                  >
                    {[
                      { code: "Jan", name: "Janvier" },
                      { code: "Fev", name: "Février" },
                      { code: "Mar", name: "Mars" },
                      { code: "Avr", name: "Avril" },
                      { code: "Mai", name: "Mai" },
                      { code: "Jun", name: "Juin" },
                      { code: "Jul", name: "Juillet" },
                      { code: "Aou", name: "Août" },
                      { code: "Sep", name: "Septembre" },
                      { code: "Oct", name: "Octobre" },
                      { code: "Nov", name: "Novembre" },
                      { code: "Dec", name: "Décembre" },
                    ].map((m) => (
                      <option key={m.code} value={m.code}>
                        {m.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="filter-group" style={{ flex: 1 }}>
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
              </div>
            ) : (
              <div className="filter-group" style={{ marginTop: "8px" }}>
                <label htmlFor="annee-sel">Année (Cumul annuel) :</label>
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
            )}

            {/* Lecteur Temporel / Animation Timeline pour Précipitations (Choroplèthe & Isohyètes) */}
            <div className="timeline-player-panel" style={{ marginTop: "12px" }}>
              <div className="timeline-header">
                <span style={{ fontSize: "11px", fontWeight: "700", textTransform: "uppercase" }}>
                  Animation Temporelle :
                </span>
                <span className="timeline-period-badge">
                  {activePrecipTimelineItem?.label || (typePeriode === "Décennies" ? selectedDecades[0] : typePeriode === "Mensuel" ? `${selectedMonth} ${selectedYears[0]}` : `Année ${selectedYears[0]}`)}
                </span>
              </div>

              <div className="timeline-buttons">
                <button
                  type="button"
                  className="timeline-btn"
                  onClick={() => handlePrecipTimelineStep(-1)}
                  title="Période précédente"
                >
                  ⏮ Préc.
                </button>
                <button
                  type="button"
                  className={`timeline-btn ${isPlayingPrecipTimeline ? "play-active" : ""}`}
                  onClick={() => setIsPlayingPrecipTimeline(!isPlayingPrecipTimeline)}
                  title={isPlayingPrecipTimeline ? "Mettre en pause" : "Lancer l'animation chronologique"}
                >
                  {isPlayingPrecipTimeline ? "⏸ Pause" : "▶ Lecture"}
                </button>
                <button
                  type="button"
                  className="timeline-btn"
                  onClick={() => handlePrecipTimelineStep(1)}
                  title="Période suivante"
                >
                  Suiv. ⏭
                </button>
              </div>

              <input
                type="range"
                className="timeline-scrubber"
                min={0}
                max={Math.max(0, precipTimelineList.length - 1)}
                value={currentPrecipTimelineIndex}
                onChange={(e) => handlePrecipTimelineScrub(Number(e.target.value))}
                title="Glissez pour changer de période"
              />

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "10px", color: "var(--text-muted)" }}>
                <span>Vitesse :</span>
                <select
                  value={precipPlaySpeed}
                  onChange={(e) => setPrecipPlaySpeed(Number(e.target.value))}
                  style={{ fontSize: "10px", padding: "2px 4px" }}
                >
                  <option value={2000}>Lente (2.0s)</option>
                  <option value={1200}>Normale (1.2s)</option>
                  <option value={600}>Rapide (0.6s)</option>
                </select>
              </div>
            </div>
          </>
        )}



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
              : typeCarte === "Isohyètes"
              ? `Carte des Isohyètes CHIRPS — ${activeIsohyeteItem?.label || (typePeriode === "Décennies" ? selectedDecades[0] : typePeriode === "Mensuel" ? `${monthNamesFr[(monthNumMap[selectedMonth] || 1) - 1]} ${selectedYears[0]}` : `Année ${selectedYears[0]}`)}`
              : `Carte des précipitations (Choroplèthe) — ${typePeriode === "Décennies" ? selectedDecades[0] : typePeriode === "Mensuel" ? `${monthNamesFr[(monthNumMap[selectedMonth] || 1) - 1]} ${selectedYears[0]}` : `Année ${selectedYears[0]}`}`}
          </h2>
          <span>
            {mapSubItem === "ndvi_classes"
              ? "Survolez ou cliquez sur une commune pour afficher son nom et ses limites"
              : typeCarte === "Isohyètes"
              ? "Survolez les courbes isohyètes ou les communes pour afficher les valeurs de précipitation"
              : "Cliquez sur une commune pour afficher les détails"}
          </span>
        </div>

        <div className="geo-map-container">
          <div className="geo-map-wrapper" style={{ height: "460px" }}>
            {/* Contrôle flottant du Fond de carte directement SUR la carte */}
            <div
              ref={basemapRef}
              className="map-basemap-control"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                type="button"
                className={`map-basemap-toggle-btn ${showBasemapMenu ? "open" : ""}`}
                onClick={() => setShowBasemapMenu((prev) => !prev)}
                title="Changer le fond de carte"
              >
                <Icons.Layers />
                <span>Fond de carte</span>
                <span className="current-basemap-pill">
                  {basemapOptions.find((b) => b.id === basemap)?.shortLabel || basemap}
                </span>
              </button>

              {showBasemapMenu && (
                <div className="map-basemap-dropdown">
                  <div className="map-basemap-dropdown-header">
                    <span>Fonds de carte</span>
                    <button
                      type="button"
                      className="map-basemap-close-btn"
                      onClick={() => setShowBasemapMenu(false)}
                      title="Fermer"
                    >
                      &times;
                    </button>
                  </div>
                  <div className="map-basemap-options-grid">
                    {basemapOptions.map((opt) => {
                      const isActive = basemap === opt.id;
                      return (
                        <button
                          key={opt.id}
                          type="button"
                          className={`map-basemap-card ${isActive ? "active" : ""}`}
                          onClick={() => {
                            setBasemap(opt.id);
                            setShowBasemapMenu(false);
                          }}
                        >
                          <span className="basemap-icon">{opt.icon}</span>
                          <div className="basemap-card-info">
                            <span className="basemap-title">{opt.label}</span>
                            <span className="basemap-desc">{opt.desc}</span>
                          </div>
                          {isActive && <span className="basemap-active-check">✓</span>}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

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



              {/* Courbes vectorielles GeoJSON d'Isohyètes */}
              {mapSubItem === "precip" &&
                typeCarte === "Isohyètes" &&
                showIsohyeteContours &&
                loadedIsohyete.key === activeIsohyeteKey &&
                loadedIsohyete.geojson &&
                loadedIsohyete.geojson.features && (
                  <GeoJSON
                    key={`iso-geojson-${loadedIsohyete.key}`}
                    data={loadedIsohyete.geojson}
                    style={getIsohyeteStyle}
                    onEachFeature={onEachIsohyeteFeature}
                  />
                )}

              {/* Couche des Communes en mode Isohyètes */}
              {mapSubItem === "precip" && typeCarte === "Isohyètes" && geojson && geojson.features && (
                <>
                  <GeoJSON
                    key={`iso-communes-${activeIsohyeteKey}-${selectedFeatureCode}`}
                    data={geojson}
                    style={getCommuneIsohyeteOverlayStyle}
                    onEachFeature={(feature, layer) => {
                      const p = feature.properties;
                      const precip = calculatedPrecipMap[p.code] ?? p.precip ?? "n/d";
                      layer.bindTooltip(
                        `<div style="font-weight:700;font-size:12px;">${p.nom || p.code}</div>
                         <div style="font-size:11px;color:#64748b;">${p.district || ""}${p.district && p.region ? " - " : ""}${p.region || ""}</div>
                         <div style="font-size:11px;color:#2563eb;font-weight:600;margin-top:2px;">Précip. : ${precip} mm</div>`,
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

              {/* Couche des Communes en mode Choroplèthe ou Déficit */}
              {mapSubItem === "precip" && typeCarte === "Choroplèthe" && geojson && geojson.features && (
                <>
                  <GeoJSON
                    key={`choropleth-${activeIsohyeteKey}-${typePeriode}-${selectedFeatureCode}-${basemap}`}
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

              {mapSubItem === "deficit" && geojson && geojson.features && (
                <>
                  <GeoJSON
                    key={`deficit-${selectedFeatureCode}-${basemap}`}
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
                    key={`ndvi-overlay-${selectedFeatureCode}-${communeOverlayStyle}`}
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
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "8px",
                marginTop: "12px",
                background: "var(--bg-secondary)",
                padding: "12px 16px",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--border-color)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "6px" }}>
                <span style={{ fontWeight: "700", fontSize: "12px", color: "var(--danger)" }}>
                  📉 Déficit de Précipitation (2020–2022)
                </span>
                <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                  Moyenne : <strong>-20.2%</strong> &bull; Étendue observée : <strong>-6.9%</strong> à <strong>-29.9%</strong>
                </span>
              </div>

              {/* Barre d'échelle avec 6 bornes de 0% à -40% */}
              <div style={{ display: "flex", flexDirection: "column", gap: "4px", width: "100%", maxWidth: "480px", marginTop: "4px" }}>
                {/* Barre segmentée avec bords arrondis */}
                <div
                  style={{
                    display: "flex",
                    height: "14px",
                    width: "100%",
                    borderRadius: "7px",
                    overflow: "hidden",
                    border: "1px solid rgba(0,0,0,0.12)",
                    boxShadow: "0 1px 2px rgba(0,0,0,0.06)",
                  }}
                >
                  {[
                    "#fff5f0",
                    "#fee0d2",
                    "#fcbba1",
                    "#fc9272",
                    "#fb6a4a",
                    "#ef3b2c",
                    "#cb181d",
                    "#99000d",
                    "#67000d",
                  ].map((col, idx) => (
                    <div key={idx} style={{ flex: 1, backgroundColor: col }} />
                  ))}
                </div>

                {/* 5 Bornes chiffrées arrondies de 0% à -40% alignées sous la barre */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    fontSize: "11px",
                    fontWeight: "600",
                    color: "var(--text-main)",
                    padding: "0 2px",
                  }}
                >
                  {["0%", "-10%", "-20%", "-30%", "-40%"].map((val, idx) => (
                    <span
                      key={idx}
                      style={{
                        textAlign: idx === 0 ? "left" : idx === 4 ? "right" : "center",
                      }}
                    >
                      {val}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : mapSubItem === "precip" ? (
            <div
              className="map-legend"
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "8px",
                marginTop: "12px",
                background: "var(--bg-secondary)",
                padding: "12px 16px",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--border-color)",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "6px" }}>
                <span style={{ fontWeight: "700", fontSize: "12px", color: "var(--primary)" }}>
                  🌧️ Précipitations {typeCarte === "Isohyètes" ? "CHIRPS (Isohyètes)" : "(Choroplèthe)"} — {typePeriode === "Décennies" ? selectedDecades[0] : typePeriode === "Mensuel" ? `${monthNamesFr[(monthNumMap[selectedMonth] || 1) - 1]} ${selectedYears[0]}` : `Année ${selectedYears[0]}`}
                </span>
                <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                  Moyenne : <strong>{activePrecipStats.mean} mm</strong> &bull; Étendue : <strong>{activePrecipStats.min} mm</strong> à <strong>{activePrecipStats.max} mm</strong>
                  {typeCarte === "Isohyètes" && <> &bull; Pas des courbes : <strong>50 mm</strong></>}
                </span>
              </div>

              {/* Barre d'échelle harmonisée avec la palette des courbes d'isohyètes */}
              <div style={{ display: "flex", flexDirection: "column", gap: "4px", width: "100%", maxWidth: "520px", marginTop: "4px" }}>
                {/* Barre de légende (dégradé bleu à 10 segments harmonisé) */}
                <div
                  style={{
                    display: "flex",
                    height: "14px",
                    width: "100%",
                    borderRadius: "7px",
                    overflow: "hidden",
                    border: "1px solid rgba(0,0,0,0.12)",
                    boxShadow: "0 1px 2px rgba(0,0,0,0.06)",
                  }}
                >
                  {PRECIP_BLUE_PALETTE.map((col, idx) => (
                    <div key={idx} style={{ flex: 1, backgroundColor: col }} />
                  ))}
                </div>

                {/* Bornes chiffrées alignées sous la barre (actualisées en temps réel) */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    fontSize: "11px",
                    fontWeight: "600",
                    color: "var(--text-main)",
                    padding: "0 2px",
                  }}
                >
                  {activePrecipScaleTicks.map((val, idx) => (
                    <span
                      key={idx}
                      style={{
                        textAlign:
                          idx === 0
                            ? "left"
                            : idx === activePrecipScaleTicks.length - 1
                            ? "right"
                            : "center",
                      }}
                    >
                      {val} mm
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ) : null}
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

  // Overlay state for each sensor image
  const [sentinelShowLandsat, setSentinelShowLandsat] = React.useState(true);
  const [sentinelShowModis, setSentinelShowModis] = React.useState(true);
  const [landsatViewMode, setLandsatViewMode] = React.useState("grid"); // "grid" | "zoom"
  const [landsatShowSubpixels, setLandsatShowSubpixels] = React.useState(true);
  const [modisViewMode, setModisViewMode] = React.useState("combined"); // "combined" | "sentinel" | "landsat" | "single"

  const comparison = vegData?.sensorComparison;
  if (!comparison) {
    return <div className="placeholder">Chargement des données de capteurs...</div>;
  }

  const activeSpec = comparison.specs.find((s) => s.id === activeSensor) || comparison.specs[0];
  const activeSim = comparison.simulation[activeSensor] || comparison.simulation.sentinel;

  const cellColors = {
    1: "#065f46",
    2: "#10b981",
    3: "#f59e0b",
    4: "#b45309",
  };

  const calculatedNdviAtSize = (0.15 + (0.44 - 0.15) * (1 - Math.exp(-simPixelSize / 70))).toFixed(3);
  const calculatedVariance = (0.075 * Math.exp(-simPixelSize / 90)).toFixed(4);

  // 3x3 Sentinel-2 pixels nested inside 1 Landsat-8/9 pixel (30m x 30m)
  const landsatNestSubpixels = [
    [0.62, 0.58, 0.49],
    [0.55, 0.38, 0.28],
    [0.48, 0.31, 0.22],
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <div className="info-bulletin">
        <strong>Effet d'échelle et pixel mixte (Physique de la Télédétection) :</strong> La taille
        du pixel (résolution spatiale) détermine le niveau de détail discernable. Observez ci-dessous
        comment <strong>9 pixels Sentinel-2 (10m)</strong> s'emboîtent dans <strong>1 pixel Landsat (30m)</strong>,
        et comment <strong>625 pixels Sentinel-2</strong> ainsi que <strong>~69,4 pixels Landsat</strong> sont
        fusionnés dans <strong>1 seul pixel MODIS (250m = 6,25 ha)</strong>.
      </div>

      {/* 4.1 Comparaison Multi-Résolution & Emboîtement */}
      <section className="panel">
        <div className="panel-heading">
          <h2><Icons.Layers /> 4.1 Comparaison Multi-Résolution & Emboîtement Spatial dans les Images</h2>
          <span>Visualisez l'emboîtement des pixels directement sur les images simulées des capteurs</span>
        </div>

        {/* Navigation Tabs */}
        <div className="sensor-tabs" style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
          {comparison.specs.map((s) => (
            <button
              key={s.id}
              className={`sensor-tab-btn ${activeSensor === s.id ? "active" : ""}`}
              onClick={() => setActiveSensor(s.id)}
            >
              {s.name} ({s.resolution})
            </button>
          ))}
          <button
            className={`sensor-tab-btn ${activeSensor === "nest_landsat" ? "active" : ""}`}
            onClick={() => setActiveSensor("nest_landsat")}
            style={{ borderLeft: "2px solid #d97706" }}
          >
            🔍 Zoom : Sentinel dans Landsat (9 px)
          </button>
          <button
            className={`sensor-tab-btn ${activeSensor === "nest_modis" ? "active" : ""}`}
            onClick={() => setActiveSensor("nest_modis")}
            style={{ borderLeft: "2px solid #2563eb" }}
          >
            📦 Zoom : Sentinel & Landsat dans MODIS (625 px)
          </button>
        </div>

        <div className="comparison-layout">
          {/* Visualizer Column */}
          <div className="pixel-grid-card">

            {/* CONTROLS BAR PER SENSOR */}
            {activeSensor === "sentinel" && (
              <div className="pixel-controls-bar">
                <label className="sensor-layer-checkbox-label">
                  <input
                    type="checkbox"
                    checked={sentinelShowLandsat}
                    onChange={(e) => setSentinelShowLandsat(e.target.checked)}
                  />
                  <span>🔶 Grille Landsat 30m (3×3 = 9 px)</span>
                </label>
                <label className="sensor-layer-checkbox-label">
                  <input
                    type="checkbox"
                    checked={sentinelShowModis}
                    onChange={(e) => setSentinelShowModis(e.target.checked)}
                  />
                  <span>🔷 Cadre MODIS 250m (25×25 = 625 px)</span>
                </label>
              </div>
            )}

            {activeSensor === "landsat" && (
              <div className="pixel-controls-bar">
                <div className="sensor-subview-pills">
                  <button
                    className={`sensor-pill-btn ${landsatViewMode === "grid" ? "active-accent" : ""}`}
                    onClick={() => setLandsatViewMode("grid")}
                  >
                    Vue Grille 8×8 (30m)
                  </button>
                  <button
                    className={`sensor-pill-btn ${landsatViewMode === "zoom" ? "active-accent" : ""}`}
                    onClick={() => setLandsatViewMode("zoom")}
                  >
                    🔍 Zoom 1 Pixel (30m) = 9 Sentinel (10m)
                  </button>
                </div>
                {landsatViewMode === "grid" && (
                  <label className="sensor-layer-checkbox-label">
                    <input
                      type="checkbox"
                      checked={landsatShowSubpixels}
                      onChange={(e) => setLandsatShowSubpixels(e.target.checked)}
                    />
                    <span>🌱 Sous-pixels Sentinel-2 (3×3)</span>
                  </label>
                )}
              </div>
            )}

            {activeSensor === "modis" && (
              <div className="pixel-controls-bar">
                <div className="sensor-subview-pills">
                  <button
                    className={`sensor-pill-btn ${modisViewMode === "combined" ? "active" : ""}`}
                    onClick={() => setModisViewMode("combined")}
                    title="Emboîtement complet superposé"
                  >
                    ✨ Vue Combinée
                  </button>
                  <button
                    className={`sensor-pill-btn ${modisViewMode === "sentinel" ? "active-sentinel" : ""}`}
                    onClick={() => setModisViewMode("sentinel")}
                    title="Décomposer en 625 pixels Sentinel-2"
                  >
                    🌱 625 px Sentinel (10m)
                  </button>
                  <button
                    className={`sensor-pill-btn ${modisViewMode === "landsat" ? "active-accent" : ""}`}
                    onClick={() => setModisViewMode("landsat")}
                    title="Décomposer en ~69,4 pixels Landsat"
                  >
                    🔶 ~69,4 px Landsat (30m)
                  </button>
                  <button
                    className={`sensor-pill-btn ${modisViewMode === "single" ? "active" : ""}`}
                    onClick={() => setModisViewMode("single")}
                    title="1 Pixel Brut agrégé 250m"
                  >
                    🔷 1 Pixel Brut 250m
                  </button>
                </div>
              </div>
            )}

            {/* DEDICATED NESTING: SENTINEL IN LANDSAT */}
            {activeSensor === "nest_landsat" || (activeSensor === "landsat" && landsatViewMode === "zoom") ? (
              <>
                <h4 style={{ fontSize: "12px", marginBottom: "8px", fontWeight: "700", color: "#d97706" }}>
                  1 Pixel Landsat (30m) = 9 Pixels Sentinel-2 (10m)
                </h4>
                <div
                  className="pixel-grid-wrapper"
                  style={{
                    width: "270px",
                    height: "270px",
                    border: "3px solid #d97706",
                    position: "relative",
                  }}
                >
                  <div className="pixel-grid-badge top-left">
                    🔶 Pixel Landsat : 30m × 30m (900 m²)
                  </div>
                  {landsatNestSubpixels.map((row, rIdx) => (
                    <div key={rIdx} className="pixel-row">
                      {row.map((val, cIdx) => {
                        const bg =
                          val > 0.5
                            ? "#065f46"
                            : val > 0.4
                            ? "#059669"
                            : val > 0.3
                            ? "#10b981"
                            : val > 0.25
                            ? "#f59e0b"
                            : "#b45309";
                        return (
                          <div
                            key={cIdx}
                            className="pixel-cell"
                            style={{
                              backgroundColor: bg,
                              border: "1.5px dashed rgba(255,255,255,0.45)",
                            }}
                            data-ndvi={`Sentinel 10m [${rIdx + 1},${cIdx + 1}] NDVI: ${val} (1/9 de Landsat)`}
                          />
                        );
                      })}
                    </div>
                  ))}
                  <div className="pixel-grid-badge bottom-center">
                    🌿 9 pixels Sentinel-2 (10m) | NDVI moyen Landsat (30m) : 0.437
                  </div>
                </div>
              </>
            ) : activeSensor === "nest_modis" ? (
              /* DEDICATED NESTING: SENTINEL & LANDSAT IN MODIS */
              <>
                <h4 style={{ fontSize: "12px", marginBottom: "8px", fontWeight: "700", color: "#2563eb" }}>
                  1 Pixel MODIS (250m) = 625 Pixels Sentinel (25×25) / ~69,4 Landsat (8,33×8,33)
                </h4>
                <div
                  className="pixel-grid-wrapper"
                  style={{
                    width: "270px",
                    height: "270px",
                    border: "3.5px solid #2563eb",
                    position: "relative",
                  }}
                >
                  <div className="pixel-grid-badge top-left">
                    🔷 1 Pixel MODIS : 250m × 250m (6,25 ha)
                  </div>
                  {comparison.simulation.sentinel.ndvi.map((row, rIdx) => (
                    <div key={rIdx} className="pixel-row">
                      {row.map((val, cIdx) => {
                        const classVal = comparison.simulation.sentinel.grid[rIdx][cIdx];
                        const bg = cellColors[classVal] || "#10b981";
                        const isLandsatBorderRight = (cIdx + 1) % 3 === 0;
                        const isLandsatBorderBottom = (rIdx + 1) % 3 === 0;

                        return (
                          <div
                            key={cIdx}
                            className="pixel-cell"
                            style={{
                              backgroundColor: bg,
                              borderRight: isLandsatBorderRight ? "1.5px solid rgba(245,158,11,0.75)" : "none",
                              borderBottom: isLandsatBorderBottom ? "1.5px solid rgba(245,158,11,0.75)" : "none",
                            }}
                            data-ndvi={`Sentinel 10m [${rIdx + 1},${cIdx + 1}] NDVI: ${val} | 1/625 de MODIS`}
                          />
                        );
                      })}
                    </div>
                  ))}
                  <div className="pixel-grid-badge bottom-center">
                    🌿 625 Sentinel (10m) & 🔶 ~69,4 Landsat (30m) dans 1 MODIS (250m)
                  </div>
                </div>
              </>
            ) : activeSensor === "sentinel" ? (
              /* SENTINEL-2 IMAGE WITH LANDSAT & MODIS NESTING OVERLAYS */
              <>
                <h4 style={{ fontSize: "12px", marginBottom: "8px", fontWeight: "700", color: "#059669" }}>
                  Sentinel-2 (10m) — Grille {activeSim.size}×{activeSim.size} ({activeSim.size * activeSim.size} pixels = 250m × 250m)
                </h4>
                <div
                  className="pixel-grid-wrapper"
                  style={{
                    width: "270px",
                    height: "270px",
                    border: sentinelShowModis ? "3.5px solid #2563eb" : "4px solid #0f172a",
                    position: "relative",
                  }}
                >
                  <div className="pixel-grid-badge top-left">
                    🌱 Sentinel-2 : 10m / px (100 m²)
                  </div>
                  {activeSim.ndvi.map((row, rIdx) => (
                    <div key={rIdx} className="pixel-row">
                      {row.map((val, cIdx) => {
                        const classVal = activeSim.grid[rIdx][cIdx];
                        const bg = cellColors[classVal] || "#10b981";
                        const isLandsatBorderRight = sentinelShowLandsat && (cIdx + 1) % 3 === 0;
                        const isLandsatBorderBottom = sentinelShowLandsat && (rIdx + 1) % 3 === 0;

                        return (
                          <div
                            key={cIdx}
                            className="pixel-cell"
                            style={{
                              backgroundColor: bg,
                              borderRight: isLandsatBorderRight ? "1.5px solid rgba(245,158,11,0.75)" : "none",
                              borderBottom: isLandsatBorderBottom ? "1.5px solid rgba(245,158,11,0.75)" : "none",
                            }}
                            data-ndvi={`Sentinel 10m [${rIdx + 1},${cIdx + 1}] NDVI: ${val} | 1/9 d'un Landsat | 1/625 d'un MODIS`}
                          />
                        );
                      })}
                    </div>
                  ))}
                  <div className="pixel-grid-badge bottom-center">
                    🔶 9 px (3×3) = 1 Landsat (30m) | 🔷 625 px (25×25) = 1 MODIS (250m)
                  </div>
                </div>
              </>
            ) : activeSensor === "landsat" ? (
              /* LANDSAT-8/9 IMAGE WITH SENTINEL & MODIS OVERLAYS */
              <>
                <h4 style={{ fontSize: "12px", marginBottom: "8px", fontWeight: "700", color: "#d97706" }}>
                  Landsat-8 / 9 (30m) — Grille {activeSim.size}×{activeSim.size} (64 pixels = ~240m × 240m)
                </h4>
                <div
                  className="pixel-grid-wrapper"
                  style={{
                    width: "270px",
                    height: "270px",
                    border: "3.5px solid #2563eb",
                    position: "relative",
                  }}
                >
                  <div className="pixel-grid-badge top-left">
                    🔶 Landsat : 30m / px (900 m²)
                  </div>
                  {activeSim.ndvi.map((row, rIdx) => (
                    <div key={rIdx} className="pixel-row">
                      {row.map((val, cIdx) => {
                        const bg =
                          val > 0.5
                            ? "#065f46"
                            : val > 0.4
                            ? "#059669"
                            : val > 0.3
                            ? "#10b981"
                            : val > 0.25
                            ? "#f59e0b"
                            : "#b45309";

                        return (
                          <div
                            key={cIdx}
                            className="pixel-cell"
                            style={{
                              backgroundColor: bg,
                              border: "1px solid rgba(15,23,42,0.6)",
                              position: "relative",
                            }}
                            data-ndvi={`Landsat 30m [${rIdx + 1},${cIdx + 1}] NDVI: ${val} | Contient 9 sous-pixels Sentinel (10m)`}
                          >
                            {landsatShowSubpixels && (
                              <div className="subpixel-dots">
                                <div /><div /><div />
                                <div /><div /><div />
                                <div /><div /><div />
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  ))}
                  <div className="pixel-grid-badge bottom-center">
                    🌿 1 pixel Landsat = 9 Sentinel (10m) | 🔷 ~69,4 pixels Landsat = 1 MODIS (250m)
                  </div>
                </div>
              </>
            ) : (
              /* MODIS IMAGE WITH MULTI-LAYER NESTING (SENTINEL + LANDSAT IN MODIS) */
              <>
                <h4 style={{ fontSize: "12px", marginBottom: "8px", fontWeight: "700", color: "#2563eb" }}>
                  MODIS (250m) — {modisViewMode === "single" ? "1 Pixel Brut (250m)" : modisViewMode === "sentinel" ? "625 Pixels Sentinel-2 (10m)" : modisViewMode === "landsat" ? "~69,4 Pixels Landsat (30m)" : "Emboîtement Combiné (Sentinel + Landsat dans MODIS)"}
                </h4>
                <div
                  className="pixel-grid-wrapper"
                  style={{
                    width: "270px",
                    height: "270px",
                    border: "4px solid #2563eb",
                    position: "relative",
                  }}
                >
                  <div className="pixel-grid-badge top-left">
                    🔷 1 Pixel MODIS : 250m × 250m (6,25 ha)
                  </div>

                  {modisViewMode === "single" ? (
                    <div
                      style={{
                        flex: 1,
                        backgroundColor: "#10b981",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "#fff",
                        fontWeight: "700",
                        fontSize: "14px",
                        textShadow: "0 1px 3px rgba(0,0,0,0.8)",
                      }}
                      data-ndvi="MODIS (250m) - NDVI moyen agrégé : 0.470 (Moyenne sur 6,25 ha)"
                    >
                      NDVI = 0.470 (Moyenne globale)
                    </div>
                  ) : modisViewMode === "landsat" ? (
                    comparison.simulation.landsat.ndvi.map((row, rIdx) => (
                      <div key={rIdx} className="pixel-row">
                        {row.map((val, cIdx) => {
                          const bg =
                            val > 0.5
                              ? "#065f46"
                              : val > 0.4
                              ? "#059669"
                              : val > 0.3
                              ? "#10b981"
                              : val > 0.25
                              ? "#f59e0b"
                              : "#b45309";
                          return (
                            <div
                              key={cIdx}
                              className="pixel-cell"
                              style={{
                                backgroundColor: bg,
                                border: "1px solid rgba(15,23,42,0.6)",
                              }}
                              data-ndvi={`Landsat 30m dans MODIS [${rIdx + 1},${cIdx + 1}] NDVI: ${val}`}
                            />
                          );
                        })}
                      </div>
                    ))
                  ) : (
                    /* "sentinel" or "combined" view */
                    comparison.simulation.sentinel.ndvi.map((row, rIdx) => (
                      <div key={rIdx} className="pixel-row">
                        {row.map((val, cIdx) => {
                          const classVal = comparison.simulation.sentinel.grid[rIdx][cIdx];
                          const bg = cellColors[classVal] || "#10b981";
                          const isLandsatBorderRight = modisViewMode === "combined" && (cIdx + 1) % 3 === 0;
                          const isLandsatBorderBottom = modisViewMode === "combined" && (rIdx + 1) % 3 === 0;

                          return (
                            <div
                              key={cIdx}
                              className="pixel-cell"
                              style={{
                                backgroundColor: bg,
                                borderRight: isLandsatBorderRight ? "1.5px solid rgba(245,158,11,0.75)" : "none",
                                borderBottom: isLandsatBorderBottom ? "1.5px solid rgba(245,158,11,0.75)" : "none",
                              }}
                              data-ndvi={`Sentinel 10m dans MODIS [${rIdx + 1},${cIdx + 1}] NDVI: ${val} (1/625 de MODIS)`}
                            />
                          );
                        })}
                      </div>
                    ))
                  )}

                  <div className="pixel-grid-badge bottom-center">
                    {modisViewMode === "single"
                      ? "1 pixel unique = 62 500 m² (Contient 625 Sentinel / ~69,4 Landsat)"
                      : modisViewMode === "sentinel"
                      ? "25 × 25 = 625 pixels Sentinel-2 (10m) dans 1 pixel MODIS"
                      : modisViewMode === "landsat"
                      ? "~8,33 × 8,33 ≈ 69,44 pixels Landsat (30m) dans 1 pixel MODIS"
                      : "🌿 625 Sentinel (10m) + 🔶 ~69,4 Landsat (30m) dans 1 MODIS (250m)"}
                  </div>
                </div>
              </>
            )}

            {/* Visual Legend Bar */}
            <div className="pixel-legend-bar">
              <span className="pixel-legend-item">
                <span className="pixel-legend-chip" style={{ background: "#059669" }}></span>
                <strong>Sentinel-2 :</strong> 10m (100 m²)
              </span>
              <span className="pixel-legend-item">
                <span className="pixel-legend-chip" style={{ background: "#d97706" }}></span>
                <strong>Landsat :</strong> 30m (900 m² = 9 Sentinel)
              </span>
              <span className="pixel-legend-item">
                <span className="pixel-legend-chip" style={{ background: "#2563eb" }}></span>
                <strong>MODIS :</strong> 250m (6,25 ha = 625 Sentinel = ~69,4 Landsat)
              </span>
            </div>
          </div>

          {/* Detailed Info Column */}
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {activeSensor === "nest_landsat" || (activeSensor === "landsat" && landsatViewMode === "zoom") ? (
              <>
                <h3 style={{ fontSize: "15px", fontWeight: "800", color: "#d97706" }}>
                  Emboîtement : Sentinel-2 dans Landsat-8/9
                </h3>
                <div style={{ display: "flex", gap: "12px", fontSize: "12px", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                  <span>Ratio : <strong>9 pixels Sentinel-2 / 1 pixel Landsat</strong></span>
                  <span>Surface : <strong>900 m² (0,09 ha)</strong></span>
                </div>
                <div className="nesting-formula-box" style={{ marginTop: "6px" }}>
                  (30 m ÷ 10 m)² = 3 × 3 = <strong>9 pixels Sentinel-2</strong> dans 1 pixel Landsat
                </div>
                <p style={{ fontSize: "12px", lineHeight: "1.4", margin: "4px 0", color: "var(--text-muted)" }}>
                  Un pixel Landsat de 30 mètres intègre et moyenne la signature spectrale de <strong>9 pixels Sentinel-2 de 10 mètres</strong>.
                  Si une petite parcelle défrichée de 10m se trouve au centre, Landsat ne verra qu'une légère baisse globale, alors que Sentinel-2 détectera nettement l'anomalie.
                </p>
                <div style={{ marginTop: "4px" }}>
                  <div className="nesting-detail-row">
                    <span>Pixel Sentinel-2 :</span>
                    <span>10 m × 10 m = 100 m² (0,01 ha)</span>
                  </div>
                  <div className="nesting-detail-row">
                    <span>Pixel Landsat :</span>
                    <span>30 m × 30 m = 900 m² (0,09 ha)</span>
                  </div>
                  <div className="nesting-detail-row">
                    <span>Facteur d'échelle spatiale :</span>
                    <span>3× plus précis en linéaire / 9× en surface</span>
                  </div>
                </div>
              </>
            ) : activeSensor === "nest_modis" ? (
              <>
                <h3 style={{ fontSize: "15px", fontWeight: "800", color: "#2563eb" }}>
                  Emboîtement : Sentinel & Landsat dans MODIS (250m)
                </h3>
                <div style={{ display: "flex", gap: "12px", fontSize: "12px", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                  <span>Dans MODIS 250m : <strong>625 Sentinel-2</strong> / <strong>~69,4 Landsat</strong></span>
                  <span>Surface : <strong>62 500 m² (6,25 ha)</strong></span>
                </div>
                <div className="nesting-formula-box" style={{ marginTop: "6px" }}>
                  • (250 m ÷ 10 m)² = 25 × 25 = <strong>625 pixels Sentinel-2</strong><br />
                  • (250 m ÷ 30 m)² = 8,33 × 8,33 ≈ <strong>69,44 pixels Landsat</strong>
                </div>
                <p style={{ fontSize: "12px", lineHeight: "1.4", margin: "4px 0", color: "var(--text-muted)" }}>
                  Un seul pixel MODIS 250m couvre plus de <strong>6 hectares</strong> ! Il synthétise l'équivalent de <strong>625 pixels Sentinel-2</strong> ou <strong>près de 70 pixels Landsat</strong>.
                  MODIS est parfait pour le suivi phénologique journalier à l'échelle régionale mais masque les hétérogénéités locales.
                </p>
                <div style={{ marginTop: "4px" }}>
                  <div className="nesting-detail-row">
                    <span>Pixel MODIS :</span>
                    <span>250 m × 250 m = 62 500 m² (6,25 ha)</span>
                  </div>
                  <div className="nesting-detail-row">
                    <span>Contenu Sentinel-2 :</span>
                    <span>Grille 25 × 25 = 625 pixels (100 m² ch.)</span>
                  </div>
                  <div className="nesting-detail-row">
                    <span>Contenu Landsat :</span>
                    <span>~8,33 × 8,33 ≈ 69,44 pixels (900 m² ch.)</span>
                  </div>
                </div>
              </>
            ) : (
              <>
                <h3 style={{ fontSize: "14px", fontWeight: "800", color: "var(--primary)" }}>{activeSpec.name}</h3>
                <div style={{ display: "flex", gap: "12px", fontSize: "12px", borderBottom: "1px solid var(--border-color)", paddingBottom: "6px" }}>
                  <span>Résolution : <strong>{activeSpec.resolution}</strong></span>
                  <span>Fréquence : <strong>{activeSpec.frequency}</strong></span>
                </div>
                <p style={{ fontSize: "12px", lineHeight: "1.4", margin: "6px 0", color: "var(--text-muted)" }}>
                  <strong>Bandes :</strong> {activeSpec.bands}
                </p>
                <div style={{ marginTop: "4px" }}>
                  <div className="nesting-formula-box">
                    {activeSensor === "sentinel"
                      ? "9 px Sentinel = 1 Landsat (30m) | 625 px Sentinel = 1 MODIS (250m)"
                      : activeSensor === "landsat"
                      ? "1 px Landsat = 9 px Sentinel (10m) | ~69,4 px Landsat = 1 MODIS (250m)"
                      : "1 px MODIS = 625 px Sentinel (10m) = ~69,4 px Landsat (30m)"}
                  </div>
                </div>
                <div style={{ marginTop: "6px" }}>
                  <strong style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--accent)" }}>Avantage :</strong>
                  <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>{activeSpec.advantage}</p>
                </div>
                <div style={{ marginTop: "6px" }}>
                  <strong style={{ fontSize: "11px", textTransform: "uppercase", color: "var(--danger)" }}>Limite technique :</strong>
                  <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "2px" }}>{activeSpec.inconvenience}</p>
                </div>
              </>
            )}
          </div>
        </div>
      </section>

      {/* 4.2 Synthèse des Ratios d'Emboîtement Spatial */}
      <section className="panel">
        <div className="panel-heading">
          <h2><Icons.Database /> 4.2 Ratios d'Emboîtement Spatial & Équivalences Métriques</h2>
          <span>Combien de sous-pixels peut-on placer dans chaque capteur ?</span>
        </div>

        <div className="nesting-cards-grid">
          {/* Card 1: Sentinel dans Landsat */}
          <div className="nesting-card">
            <div className="nesting-card-header">
              <span className="nesting-tag sentinel-landsat">Sentinel dans Landsat</span>
              <span style={{ fontSize: "11px", color: "var(--text-light)" }}>30m / 10m</span>
            </div>
            <div className="nesting-hero-ratio">
              <span className="nesting-number" style={{ color: "#059669" }}>9</span>
              <span className="nesting-unit">pixels Sentinel-2 (10m)</span>
            </div>
            <div style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-main)" }}>
              dans 1 pixel Landsat (30m)
            </div>
            <div className="nesting-formula-box">
              (30m / 10m)² = 3 × 3 = <strong>9 pixels</strong>
            </div>
            <div style={{ marginTop: "6px" }}>
              <div className="nesting-detail-row">
                <span>Surface 1 pixel Sentinel-2 :</span>
                <span>100 m² (0,01 ha)</span>
              </div>
              <div className="nesting-detail-row">
                <span>Surface 1 pixel Landsat :</span>
                <span>900 m² (0,09 ha)</span>
              </div>
              <div className="nesting-detail-row">
                <span>Disposition :</span>
                <span>Grille 3 × 3 sous-pixels</span>
              </div>
            </div>
          </div>

          {/* Card 2: Sentinel dans MODIS */}
          <div className="nesting-card">
            <div className="nesting-card-header">
              <span className="nesting-tag sentinel-modis">Sentinel dans MODIS</span>
              <span style={{ fontSize: "11px", color: "var(--text-light)" }}>250m / 10m</span>
            </div>
            <div className="nesting-hero-ratio">
              <span className="nesting-number" style={{ color: "#2563eb" }}>625</span>
              <span className="nesting-unit">pixels Sentinel-2 (10m)</span>
            </div>
            <div style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-main)" }}>
              dans 1 pixel MODIS (250m)
            </div>
            <div className="nesting-formula-box">
              (250m / 10m)² = 25 × 25 = <strong>625 pixels</strong>
            </div>
            <div style={{ marginTop: "6px" }}>
              <div className="nesting-detail-row">
                <span>Surface 1 pixel Sentinel-2 :</span>
                <span>100 m² (0,01 ha)</span>
              </div>
              <div className="nesting-detail-row">
                <span>Surface 1 pixel MODIS :</span>
                <span>62 500 m² (6,25 ha)</span>
              </div>
              <div className="nesting-detail-row">
                <span>Disposition :</span>
                <span>Grille 25 × 25 sous-pixels</span>
              </div>
            </div>
          </div>

          {/* Card 3: Landsat dans MODIS */}
          <div className="nesting-card">
            <div className="nesting-card-header">
              <span className="nesting-tag landsat-modis">Landsat dans MODIS</span>
              <span style={{ fontSize: "11px", color: "var(--text-light)" }}>250m / 30m</span>
            </div>
            <div className="nesting-hero-ratio">
              <span className="nesting-number" style={{ color: "#d97706" }}>~69,4</span>
              <span className="nesting-unit">pixels Landsat (30m)</span>
            </div>
            <div style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-main)" }}>
              dans 1 pixel MODIS (250m)
            </div>
            <div className="nesting-formula-box">
              (250m / 30m)² = 8,33² ≈ <strong>69,44 pixels</strong>
            </div>
            <div style={{ marginTop: "6px" }}>
              <div className="nesting-detail-row">
                <span>Surface 1 pixel Landsat :</span>
                <span>900 m² (0,09 ha)</span>
              </div>
              <div className="nesting-detail-row">
                <span>Surface 1 pixel MODIS :</span>
                <span>62 500 m² (6,25 ha)</span>
              </div>
              <div className="nesting-detail-row">
                <span>Disposition :</span>
                <span>~8,33 × 8,33 parcelles Landsat</span>
              </div>
            </div>
          </div>
        </div>

        {/* Summary Table */}
        <div style={{ overflowX: "auto" }}>
          <table className="nesting-summary-table">
            <thead>
              <tr>
                <th>Capteur</th>
                <th>Résolution spatiale</th>
                <th>Surface d'un pixel</th>
                <th>Pixels dans 1 Landsat (30m)</th>
                <th>Pixels dans 1 MODIS (250m)</th>
                <th>Fréquence</th>
                <th>Usage optimal</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Sentinel-2 (ESA)</strong></td>
                <td>10 m × 10 m</td>
                <td>100 m² (0,01 ha)</td>
                <td><strong style={{ color: "#059669" }}>9 pixels (3×3)</strong></td>
                <td><strong style={{ color: "#2563eb" }}>625 pixels (25×25)</strong></td>
                <td>5 jours</td>
                <td>Détection des coupes fines & parcelles agricoles</td>
              </tr>
              <tr>
                <td><strong>Landsat-8 / 9 (NASA)</strong></td>
                <td>30 m × 30 m</td>
                <td>900 m² (0,09 ha)</td>
                <td><strong>1 pixel (1×1)</strong></td>
                <td><strong style={{ color: "#d97706" }}>~69,4 pixels (8,33×8,33)</strong></td>
                <td>8-16 jours</td>
                <td>Séries historiques longues (depuis 1972)</td>
              </tr>
              <tr>
                <td><strong>MODIS (Terra/Aqua)</strong></td>
                <td>250 m × 250 m</td>
                <td>62 500 m² (6,25 ha)</td>
                <td>—</td>
                <td><strong>1 pixel (1×1)</strong></td>
                <td>1-2 jours (Quotidien)</td>
                <td>Suivi phénologique continu & régional</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* 4.3 Simulateur d'effet de taille de pixel */}
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
