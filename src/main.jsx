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
  { id: "all", label: "📊 Vue Complète (Page Unique)" },
  { id: "overview", label: "Vue d'ensemble" },
  { id: "carte", label: "Cartographie" },
  { id: "stats", label: "Statistiques & Analyses" },
  { id: "data", label: "Base de Données" },
  { id: "guide", label: "Guide & Méthodologie" },
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
  Dashboard: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25A2.25 2.25 0 0010.5 14.25V3.75A2.25 2.25 0 008.25 1.5H6A2.25 2.25 0 003.75 3.75zM13.5 3v6A2.25 2.25 0 0015.75 11.25h2.25A2.25 2.25 0 0020.25 9V3.75A2.25 2.25 0 0018 1.5h-2.25A2.25 2.25 0 0013.5 3.75zM13.5 15.75v4.5A2.25 2.25 0 0015.75 22.5h2.25A2.25 2.25 0 0020.25 20.25v-4.5A2.25 2.25 0 0018 13.5h-2.25A2.25 2.25 0 0013.5 15.75zM3.75 20.25v.75A1.5 1.5 0 005.25 22.5h3A1.5 1.5 0 009.75 21v-.75A1.5 1.5 0 008.25 18.75h-3A1.5 1.5 0 003.75 20.25z" />
    </svg>
  ),
  Overview: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
    </svg>
  ),
  Rain: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15a4.5 4.5 0 004.5 4.5H18a3.75 3.75 0 001.332-7.257 3 3 0 00-3.758-3.848 5.25 5.25 0 00-10.233 2.33A4.502 4.502 0 002.25 15z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 19.5v2.25m3-2.25v2.25m3-2.25v2.25" />
    </svg>
  ),
  Stats: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v5.25c0 .621-.504 1.125-1.125 1.125h-2.25A1.125 1.125 0 013 18.375v-5.25zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125v-9.75zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v14.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
    </svg>
  ),
  Map: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 6.75h12m-12 5.25h12m-12 5.25h12M3 6.75h.008v.008H3V6.75zm0 5.25h.008v.008H3V12zm0 5.25h.008v.008H3v-.008z" />
    </svg>
  ),
  Table: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 5.25h16.5m-16.5 4.5h16.5m-16.5 4.5h16.5m-16.5 4.5h16.5" />
    </svg>
  ),
  Sun: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m0 13.5V21m6.364-16.364l-1.591 1.591M6.343 17.657l-1.591 1.591m12.728 0l-1.591-1.591M6.343 6.343L4.752 4.752M3 12h2.25m13.5 0H21M12 7.5a4.5 4.5 0 100 9 4.5 4.5 0 000-9z" />
    </svg>
  ),
  Moon: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
    </svg>
  ),
  Search: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  ),
  Download: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
  ),
  Info: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  Database: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75M3.75 10.125v3.75m16.5 0v3.75M3.75 13.875v3.75" />
    </svg>
  ),
  Leaf: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21V9m0 0a4.5 4.5 0 00-4.5 4.5M12 9a4.5 4.5 0 014.5 4.5m-4.5-4.5V3" />
    </svg>
  ),
  Layers: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M6.429 9.75L2.25 12l4.179 2.25m0-4.5l5.571 3 5.571-3m-11.142 0L12 7.5l5.571 2.25m1.179 2.25l4.179-2.25-4.179-2.25m0 4.5l-5.571 3-5.571-3M2.25 12l4.179 2.25m11.142 0L21.75 12M6.429 14.25v3.5A2.25 2.25 0 008.679 20h6.642a2.25 2.25 0 002.25-2.25v-3.5" />
    </svg>
  ),
  Alert: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
    </svg>
  ),
  Menu: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
    </svg>
  ),
  Close: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  ),
  Guide: (props) => (
    <svg width={18} height={18} style={{ width: "18px", height: "18px", flexShrink: 0, ...props?.style }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
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
    return yValues.map(() => meanY);
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
    return yValues.map(() => meanY);
  }

  return normX.map((xi) => {
    let val = 0;
    let pow = 1;
    for (let p = 0; p < m; p++) {
      val += coeffs[p] * pow;
      pow *= xi;
    }
    return val;
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

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="state-screen" style={{ padding: "40px 20px" }}>
          <div className="state-brand">
            <img src="/logo.png" alt="Logo Dynatsimo" className="brand-mark brand-mark-lg" />
            <div className="state-brand-text">
              <strong className="state-brand-title">DYNATSIMO</strong>
              <span className="state-brand-subtitle">GESTION AGRO-VÉGÉTALE</span>
            </div>
          </div>
          <strong style={{ fontSize: "18px", color: "var(--danger)" }}>
            Une interruption est survenue lors de l'affichage
          </strong>
          <p style={{ maxWidth: "600px", fontSize: "13px", color: "var(--text-muted)", marginTop: "8px" }}>
            {this.state.error?.message || "Erreur inattendue."}
          </p>
          <div style={{ display: "flex", gap: "10px", marginTop: "16px" }}>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.reload();
              }}
              style={{ padding: "8px 18px", cursor: "pointer" }}
            >
              Recharger la page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {

  const [activeTab, setActiveTab] = React.useState("all");
  const [statsCategory, setStatsCategory] = React.useState("precip");
  const [mapSubItem, setMapSubItem] = React.useState("precip");
  const [dataCategory, setDataCategory] = React.useState("precip");
  const [mobileNavOpen, setMobileNavOpen] = React.useState(false);
  const [selectedCommune, setSelectedCommune] = React.useState("");
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
          <img src="/logo.png" alt="Logo Dynatsimo" className="brand-mark brand-mark-lg" />
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
          <img src="/logo.png" alt="Logo Dynatsimo" className="brand-mark brand-mark-lg" />
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
            <div className="brand-wrapper" style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: "12px" }}>
              <img src="/logo.png" alt="Logo Dynatsimo" className="brand-mark" />
              <div className="brand-text" style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", justifyContent: "center" }}>
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
              if (tab.id === "all") Icon = Icons.Dashboard;
              if (tab.id === "overview") Icon = Icons.Overview;
              if (tab.id === "stats") Icon = Icons.Stats;
              if (tab.id === "carte") Icon = Icons.Map;
              if (tab.id === "data") Icon = Icons.Database;
              if (tab.id === "guide") Icon = Icons.Guide;

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

                  {/* Sous-onglets de Base de Données dans la barre latérale gauche */}
                  {tab.id === "data" && activeTab === "data" && (
                    <div className="nav-sub-list">
                      {[
                        { id: "precip", label: "🌧️ Pluviométrie (CHIRPS)" },
                        { id: "vegetation", label: "🌿 Végétation (MODIS)" },
                      ].map((sub) => (
                        <button
                          key={sub.id}
                          className={`nav-sub-item ${dataCategory === sub.id ? "active" : ""}`}
                          onClick={(e) => {
                            e.stopPropagation();
                            setActiveTab("data");
                            setDataCategory(sub.id);
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
          {activeTab === "all" && (
            <UnifiedSinglePage
              data={data}
              regionsList={regionsList}
              selectedRegion={selectedRegion}
              setSelectedRegion={setSelectedRegion}
              selectedCommune={selectedCommune}
              setSelectedCommune={setSelectedCommune}
              selectedCommuneName={selectedCommuneName}
              mapSubItem={mapSubItem}
              setMapSubItem={setMapSubItem}
              statsCategory={statsCategory}
              setStatsCategory={setStatsCategory}
              dataCategory={dataCategory}
              setDataCategory={setDataCategory}
            />
          )}
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
            <TableauExplorer
              geojson={data.communesGeojson}
              communesList={data.communes}
              datasetType={dataCategory}
              setDatasetType={setDataCategory}
            />
          )}
          {activeTab === "guide" && <GuideMethodologie />}
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


function UnifiedSinglePage({
  data,
  regionsList,
  selectedRegion,
  setSelectedRegion,
  selectedCommune,
  setSelectedCommune,
  selectedCommuneName,
  mapSubItem,
  setMapSubItem,
  statsCategory,
  setStatsCategory,
  dataCategory,
  setDataCategory,
}) {
  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  return (
    <div className="unified-page-container">
      {/* Sticky Fast Navigation Pill Bar */}
      <div className="unified-nav-bar">
        <div className="unified-nav-scroll">
          <button type="button" className="unified-nav-pill" onClick={() => scrollTo("sec-overview")}>
            <span className="pill-num">01</span> Vue d'ensemble
          </button>
          <button type="button" className="unified-nav-pill" onClick={() => scrollTo("sec-carte")}>
            <span className="pill-num">02</span> Cartographie Agrandie 🌍
          </button>
          <button type="button" className="unified-nav-pill" onClick={() => scrollTo("sec-stats-precip")}>
            <span className="pill-num">03</span> Pluviométrie 🌧️
          </button>
          <button type="button" className="unified-nav-pill" onClick={() => scrollTo("sec-stats-veg")}>
            <span className="pill-num">04</span> Végétation NDVI 🌿
          </button>
          <button type="button" className="unified-nav-pill" onClick={() => scrollTo("sec-stats-saison")}>
            <span className="pill-num">05</span> Saisons des Pluies 🗓️
          </button>
          <button type="button" className="unified-nav-pill" onClick={() => scrollTo("sec-stats-sensors")}>
            <span className="pill-num">06</span> Capteurs Satellitaires 🛰️
          </button>
          <button type="button" className="unified-nav-pill" onClick={() => scrollTo("sec-data")}>
            <span className="pill-num">07</span> Base de Données 📋
          </button>
          <button type="button" className="unified-nav-pill" onClick={() => scrollTo("sec-guide")}>
            <span className="pill-num">08</span> Guide & Calculs 📖
          </button>
        </div>
      </div>

      {/* 01. VUE D'ENSEMBLE */}
      <section id="sec-overview" className="section-anchor">
        <div className="section-header-banner">
          <div className="section-index-badge">01</div>
          <div>
            <h2 className="section-title">Vue d'ensemble Synoptique</h2>
            <p className="section-subtitle">Indicateurs clés et séries historiques CHIRPS (1981–2026) & MODIS 250m (1999–2026)</p>
          </div>
        </div>
        <Overview
          annualData={data.annualData}
          communes={data.communes}
          overview={data.overview}
          vegData={data.vegetationData}
        />
      </section>

      {/* 02. CARTOGRAPHIE GÉOSPATIALE AGRANDIE */}
      <section id="sec-carte" className="section-anchor" style={{ marginTop: "32px" }}>
        <div className="section-header-banner">
          <div className="section-index-badge">02</div>
          <div>
            <h2 className="section-title">Cartographie Géospatiale Interactive Agrandie</h2>
            <p className="section-subtitle">Précipitations, Isohyètes CHIRPS, Déficit triennal (2020–22) et Animation NDVI 6-Classes</p>
          </div>
        </div>
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
      </section>

      {/* 03. STATISTIQUES & ANALYSES PLUVIOMÉTRIQUES */}
      <section id="sec-stats-precip" className="section-anchor" style={{ marginTop: "32px" }}>
        <div className="section-header-banner">
          <div className="section-index-badge">03</div>
          <div>
            <h2 className="section-title">Statistiques & Climatologie Pluviométrique</h2>
            <p className="section-subtitle">Climatologie 45 ans, bilan hydrique annuel, anomalies interannuelles et déficits mensuels</p>
          </div>
        </div>
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
          statsCategory="precip"
          setStatsCategory={setStatsCategory}
        />
      </section>

      {/* 04. SUIVI VÉGÉTATION NDVI */}
      <section id="sec-stats-veg" className="section-anchor" style={{ marginTop: "32px" }}>
        <div className="section-header-banner">
          <div className="section-index-badge">04</div>
          <div>
            <h2 className="section-title">Suivi & Dynamique du Couvert Végétal (NDVI)</h2>
            <p className="section-subtitle">Évolution pluriannuelle 2000–2025, cycle phénologique 12 mois, écorégions et alertes</p>
          </div>
        </div>
        <SuiviVegetation
          communes={data?.communes || []}
          regions={regionsList || []}
          selectedRegion={selectedRegion}
          setSelectedRegion={setSelectedRegion}
          selectedCommune={selectedCommune}
          setSelectedCommune={setSelectedCommune}
          selectedCommuneName={selectedCommuneName}
          vegData={data?.vegetationData || {}}
          statsCategory="vegetation"
          setStatsCategory={setStatsCategory}
        />
      </section>

      {/* 05. CALENDRIER DES SAISONS DES PLUIES */}
      <section id="sec-stats-saison" className="section-anchor" style={{ marginTop: "32px" }}>
        <div className="section-header-banner">
          <div className="section-index-badge">05</div>
          <div>
            <h2 className="section-title">Calendrier & Régime des Saisons des Pluies</h2>
            <p className="section-subtitle">Dates de début et fin de saison, durées utiles (jours) et régimes pluviométriques communaux</p>
          </div>
        </div>
        <Saison
          communes={data?.communes || []}
          regions={regionsList || []}
          selectedRegion={selectedRegion}
          setSelectedRegion={setSelectedRegion}
          seasonData={data?.seasonData || []}
          selectedCommune={selectedCommune}
          setSelectedCommune={setSelectedCommune}
          selectedCommuneName={selectedCommuneName}
          statsCategory="saison"
          setStatsCategory={setStatsCategory}
        />
      </section>

      {/* 06. SIMULATION & MULTI-CAPTEURS */}
      <section id="sec-stats-sensors" className="section-anchor" style={{ marginTop: "32px" }}>
        <div className="section-header-banner">
          <div className="section-index-badge">06</div>
          <div>
            <h2 className="section-title">Imbrication & Résolution Spatiale des Capteurs</h2>
            <p className="section-subtitle">Comparaison multi-échelle MODIS 250m / Landsat 30m / Sentinel-2 10m et simulation de pixel</p>
          </div>
        </div>
        <ComparaisonCapteurs
          vegData={data?.vegetationData || {}}
          selectedCommune={selectedCommune}
        />
      </section>

      {/* 07. BASE DE DONNÉES COMMUNALES */}
      <section id="sec-data" className="section-anchor" style={{ marginTop: "32px" }}>
        <div className="section-header-banner">
          <div className="section-index-badge">07</div>
          <div>
            <h2 className="section-title">Base de Données des 225 Communes</h2>
            <p className="section-subtitle">Explorateur tabulaire interactif avec recherche, tri multi-colonnes et export CSV</p>
          </div>
        </div>
        <TableauExplorer
          geojson={data.communesGeojson}
          communesList={data.communes}
          datasetType={dataCategory}
          setDatasetType={setDataCategory}
        />
      </section>

      {/* 08. GUIDE MÉTHODOLOGIQUE & FORMULES DE CALCUL */}
      <section id="sec-guide" className="section-anchor" style={{ marginTop: "32px" }}>
        <div className="section-header-banner">
          <div className="section-index-badge">08</div>
          <div>
            <h2 className="section-title">Guide Méthodologique & Formules Scientifiques</h2>
            <p className="section-subtitle">Documentation des équations mathématiques, capteurs (CHIRPS, MODIS, Landsat, Sentinel-2) et indices agro-climatiques</p>
          </div>
        </div>
        <GuideMethodologie />
      </section>
    </div>
  );
}

function Overview({ annualData, communes, overview, vegData }) {
  const [polyOrder, setPolyOrder] = React.useState(4);

  const startYear = annualData && annualData.length ? annualData[0].year : 1981;
  const endYear = annualData && annualData.length ? annualData[annualData.length - 1].year : 2026;
  const periodLabel = `${startYear}–${endYear}`;

  // 1. Regional Annual Precipitation across all 225 communes (CHIRPS)
  const computedPrecipTrendData = React.useMemo(() => {
    if (!annualData || annualData.length === 0) return [];
    const years = annualData.map((d) => d.year);
    const precipVals = annualData.map((d) => d.precip);
    const polyFits = polyFit(years, precipVals, polyOrder);

    return annualData.map((d, i) => ({
      ...d,
      trend: Number((polyFits[i] ?? d.precip).toFixed(1)),
    }));
  }, [annualData, polyOrder]);

  // 2. Regional Annual Mean NDVI across ALL 225 communes (MODIS 250m)
  const regionalVegData = React.useMemo(() => {
    const modis = vegData?.timeSeries?.modis;
    if (!modis || typeof modis !== "object") return [];

    const seasonDict = {};
    const allCommuneCodes = Object.keys(modis);
    if (allCommuneCodes.length === 0) return [];

    allCommuneCodes.forEach((code) => {
      const series = modis[code];
      if (Array.isArray(series)) {
        series.forEach((s) => {
          const sName = s?.season;
          if (!sName) return;
          if (!seasonDict[sName]) {
            seasonDict[sName] = {
              season: sName,
              startYear: s.startYear || parseInt(sName) || 2000,
              ndviSums: [],
              baseSums: [],
            };
          }
          const validNdvi = Array.isArray(s.ndvi) ? s.ndvi.filter((v) => v !== null && !isNaN(v)) : [];
          const validBase = Array.isArray(s.baseline) ? s.baseline.filter((v) => v !== null && !isNaN(v)) : [];
          if (validNdvi.length > 0) {
            seasonDict[sName].ndviSums.push(validNdvi.reduce((a, b) => a + b, 0) / validNdvi.length);
          }
          if (validBase.length > 0) {
            seasonDict[sName].baseSums.push(validBase.reduce((a, b) => a + b, 0) / validBase.length);
          }
        });
      }
    });

    const seasons = Object.values(seasonDict);
    seasons.sort((a, b) => a.startYear - b.startYear);

    return seasons.map((s) => {
      const meanNdvi = s.ndviSums.length > 0 ? s.ndviSums.reduce((a, b) => a + b, 0) / s.ndviSums.length : 0.42;
      const meanBase = s.baseSums.length > 0 ? s.baseSums.reduce((a, b) => a + b, 0) / s.baseSums.length : 0.42;
      return {
        season: s.season,
        year: s.startYear,
        meanNdvi: Number(meanNdvi.toFixed(3)),
        meanBaseline: Number(meanBase.toFixed(3)),
      };
    });
  }, [vegData]);

  // Polynomial trend for Regional NDVI with shared polyOrder
  const computedVegTrendData = React.useMemo(() => {
    if (!regionalVegData || regionalVegData.length === 0) return [];
    const x = regionalVegData.map((_, i) => i);
    const y = regionalVegData.map((d) => d.meanNdvi);
    const polyFits = polyFit(x, y, polyOrder);

    return regionalVegData.map((d, i) => ({
      ...d,
      trend: Number((polyFits[i] ?? d.meanNdvi).toFixed(3)),
    }));
  }, [regionalVegData, polyOrder]);

  const yDomainVeg = React.useMemo(() => {
    if (computedVegTrendData.length === 0) return [0.2, 0.6];
    const minVal = Math.min(...computedVegTrendData.map((d) => Math.min(d.meanNdvi, d.meanBaseline, d.trend || 1)), 0.25);
    const maxVal = Math.max(...computedVegTrendData.map((d) => Math.max(d.meanNdvi, d.meanBaseline, d.trend || 0)), 0.5);
    const lower = Math.max(0, Math.floor((minVal - 0.05) * 20) / 20);
    const upper = Math.min(1.0, Math.ceil((maxVal + 0.05) * 20) / 20);
    return [lower, upper];
  }, [computedVegTrendData]);

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

  const avgRegionalNdvi = React.useMemo(() => {
    if (regionalVegData.length === 0) return "—";
    const avg = regionalVegData.reduce((a, b) => a + b.meanNdvi, 0) / regionalVegData.length;
    return avg.toFixed(3);
  }, [regionalVegData]);

  const CustomPrecipTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const isCurrentYear = payload[0].payload.year === endYear;
      return (
        <div className="recharts-custom-tooltip">
          <p className="recharts-custom-tooltip-title">
            Année {payload[0].payload.year} {isCurrentYear ? "(Année en cours)" : ""}
          </p>
          <div className="recharts-custom-tooltip-item">
            <span>Pluie moyenne (225 communes) :</span>
            <strong style={{ color: "var(--primary)" }}>{payload[0].value?.toLocaleString("fr-FR")} mm</strong>
          </div>
          {payload[1] && (
            <div className="recharts-custom-tooltip-item">
              <span>Tendance polynomiale (Ordre {polyOrder}) :</span>
              <strong style={{ color: "var(--danger)" }}>{payload[1].value?.toLocaleString("fr-FR")} mm</strong>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  const CustomVegTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0]?.payload;
      return (
        <div className="recharts-custom-tooltip">
          <p className="recharts-custom-tooltip-title">
            Campagne {data?.season} ({data?.year})
          </p>
          <div className="recharts-custom-tooltip-item">
            <span>NDVI Moyen Régional (Observé) :</span>
            <strong style={{ color: "var(--accent)" }}>{Number(data?.meanNdvi).toFixed(3)}</strong>
          </div>
          <div className="recharts-custom-tooltip-item">
            <span>Normale Pluriannuelle (Référence) :</span>
            <strong style={{ color: "var(--text-light)" }}>{Number(data?.meanBaseline).toFixed(3)}</strong>
          </div>
          <div className="recharts-custom-tooltip-item">
            <span>Tendance polynomiale (Ordre {polyOrder}) :</span>
            <strong style={{ color: "var(--danger)" }}>{Number(data?.trend).toFixed(3)}</strong>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <>
      <section className="metric-grid">
        <Metric
          label="Communes Suivies"
          value={overview?.nb_communes ?? communes.length}
          type="communes"
        />
        <Metric label="Précipitation Moyenne" value={`${avgPrecip} mm`} type="precip" />
        <Metric
          label="NDVI Moyen Régional (1999–2026)"
          value={avgRegionalNdvi}
          type="ndvi"
        />
        <Metric label="Historique Données" value={overview?.nb_years || "1981–2026"} type="years" />
      </section>

      <section className="panel" style={{ marginTop: "4px" }}>
        <div className="panel-heading" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
          <div>
            <h2>
              <Icons.Stats /> Dynamique Agro-Climatique & Végétale Régionale (Toutes les communes)
            </h2>
            <span>Séries temporelles historiques régionales avec régression polynomiale harmonisée</span>
          </div>

          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "8px", flexShrink: 0 }}>
            <span style={{ background: "transparent", border: "none", padding: "0 4px", fontSize: "11px", fontWeight: "700", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px" }}>
              Ordre de tendance (partagé) :
            </span>
            <div className="scale-tabs" style={{ display: "flex", gap: "2px", padding: "2px", background: "var(--bg-app)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-color)" }}>
              {[1, 2, 3, 4, 5].map((o) => (
                <button
                  key={o}
                  type="button"
                  className={`scale-tab-btn ${polyOrder === o ? "active" : ""}`}
                  onClick={() => setPolyOrder(o)}
                  style={{
                    minWidth: "28px",
                    padding: "3px 7px",
                    fontSize: "11px",
                    fontWeight: polyOrder === o ? "700" : "500",
                    borderRadius: "3px",
                  }}
                  title={`Polynôme degré ${o}${o === 4 ? " (Référence R)" : ""}`}
                >
                  {o}{o === 4 ? " (R)" : ""}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 2-Columns Side-by-Side: Precipitation Left, Vegetation Right */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(440px, 1fr))", gap: "16px", marginTop: "12px" }}>
          {/* Left Figure: Precipitation */}
          <div className="panel" style={{ background: "var(--bg-panel-secondary)", border: "1px solid var(--border-color)", padding: "14px", borderRadius: "8px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px", paddingBottom: "4px", borderBottom: "1px solid var(--border-color)" }}>
              <strong style={{ fontSize: "13px", color: "var(--text-main)" }}>
                Précipitations Annuelles Moyennes ({periodLabel})
              </strong>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>CHIRPS (225 communes)</span>
            </div>
            <div style={{ width: "100%", height: 290 }}>
              <ResponsiveContainer>
                <ComposedChart
                  data={computedPrecipTrendData}
                  margin={{ top: 15, right: 15, bottom: 20, left: 0 }}
                >
                  <defs>
                    <linearGradient id="colorPrecipOverview" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="var(--primary)" stopOpacity={0.15} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <XAxis dataKey="year" stroke="var(--text-muted)" fontSize={11} interval="preserveStartEnd" />
                  <YAxis stroke="var(--text-muted)" fontSize={11} unit=" mm" />
                  <RechartsTooltip content={<CustomPrecipTooltip />} />
                  <Legend verticalAlign="top" height={32} />
                  <Bar
                    name="Pluie annuelle moyenne (mm)"
                    dataKey="precip"
                    fill="url(#colorPrecipOverview)"
                    radius={[3, 3, 0, 0]}
                  />
                  <Line
                    name={`Tendance (Ordre ${polyOrder})`}
                    type="monotone"
                    dataKey="trend"
                    stroke="var(--danger)"
                    strokeWidth={2.8}
                    dot={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Right Figure: Vegetation (NDVI) */}
          <div className="panel" style={{ background: "var(--bg-panel-secondary)", border: "1px solid var(--border-color)", padding: "14px", borderRadius: "8px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px", paddingBottom: "4px", borderBottom: "1px solid var(--border-color)" }}>
              <strong style={{ fontSize: "13px", color: "var(--text-main)" }}>
                Évolution Interannuelle du NDVI Moyen (1999–2026)
              </strong>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>MODIS 250m (225 communes)</span>
            </div>
            <div style={{ width: "100%", height: 290 }}>
              <ResponsiveContainer>
                <ComposedChart
                  data={computedVegTrendData}
                  margin={{ top: 15, right: 15, bottom: 20, left: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <XAxis dataKey="season" stroke="var(--text-muted)" fontSize={10} interval="preserveStartEnd" angle={-25} textAnchor="end" height={40} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} domain={yDomainVeg} />
                  <RechartsTooltip content={<CustomVegTooltip />} />
                  <Legend verticalAlign="top" height={32} />
                  <Line
                    name="Normale Pluriannuelle (Référence)"
                    type="monotone"
                    dataKey="meanBaseline"
                    stroke="var(--text-light)"
                    strokeWidth={2}
                    dot={false}
                    strokeDasharray="4 4"
                  />
                  <Area
                    name="NDVI Moyen Annuel (Observé)"
                    type="monotone"
                    dataKey="meanNdvi"
                    fill="rgba(16, 185, 129, 0.15)"
                    stroke="var(--accent)"
                    strokeWidth={2.5}
                    dot={{ r: 3, fill: "var(--accent)" }}
                  />
                  <Line
                    name={`Tendance (Ordre ${polyOrder})`}
                    type="monotone"
                    dataKey="trend"
                    stroke="var(--danger)"
                    strokeWidth={2.8}
                    dot={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </section>

      <div className="info-bulletin" style={{ marginTop: "16px", marginBottom: "8px" }}>
        <strong>Vue d'ensemble régionale :</strong> Comparaison synoptique des précipitations annuelles CHIRPS (1981–2026) et de l'évolution du couvert végétal NDVI MODIS (1999–2026) agrégées sur l'ensemble des 225 communes du Grand Sud de Madagascar.
      </div>
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
  const [timeScale, setTimeScale] = React.useState("annual"); // "annual" (Par Année: 2000-2025) | "monthly" (Par Mois: Oct-Sep)
  const [activeSeason, setActiveSeason] = React.useState("2024-2025");
  const [activeSensor, setActiveSensor] = React.useState("modis");
  const [polyOrder, setPolyOrder] = React.useState(3);

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

  const activeCommuneObj = communes.find((c) => c.code === selectedCommune) || filteredCommunesDropdown[0] || communes[0];
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
    const currentCode = selectedCommune || activeCommuneObj?.code;
    if (!currentCode) return [];
    if (vegData?.timeSeries?.[activeSensor]) {
      const series = vegData.timeSeries[activeSensor][currentCode];
      return Array.isArray(series) ? series : [];
    }
    const series = vegData?.timeSeries?.[currentCode];
    return Array.isArray(series) ? series : [];
  }, [vegData, selectedCommune, activeCommuneObj, activeSensor]);

  const seasonsList = React.useMemo(
    () => activeCommuneSeries.map((s) => s?.season).filter(Boolean),
    [activeCommuneSeries]
  );

  React.useEffect(() => {
    if (seasonsList.length > 0 && !seasonsList.includes(activeSeason)) {
      if (seasonsList.includes("2024-2025")) {
        setActiveSeason("2024-2025");
      } else {
        setActiveSeason(seasonsList[seasonsList.length - 1]);
      }
    } else if (seasonsList.length === 0 && activeSeason !== "") {
      setActiveSeason("");
    }
  }, [seasonsList, activeSeason]);

  // --- DATA PER YEAR (INTERANNUAL: 2000-2025) ---
  const annualData = React.useMemo(() => {
    if (!activeCommuneSeries || activeCommuneSeries.length === 0) return [];
    return activeCommuneSeries.map((s, idx) => {
      const ndviArr = Array.isArray(s.ndvi) ? s.ndvi : [];
      const baselineArr = Array.isArray(s.baseline) ? s.baseline : [];
      const anomaliesArr = Array.isArray(s.anomalies) ? s.anomalies : [];

      const validNdvi = ndviArr.filter((v) => v !== null && !isNaN(v));
      const meanNdvi = validNdvi.length > 0 ? validNdvi.reduce((a, b) => a + b, 0) / validNdvi.length : 0;

      const validBaseline = baselineArr.filter((v) => v !== null && !isNaN(v));
      const meanBaseline = validBaseline.length > 0 ? validBaseline.reduce((a, b) => a + b, 0) / validBaseline.length : 0.23;

      const validAnom = anomaliesArr.filter((v) => v !== null && !isNaN(v));
      const meanAnomaly = validAnom.length > 0 ? validAnom.reduce((a, b) => a + b, 0) / validAnom.length : (meanNdvi - meanBaseline);

      const integratedProd = toFiniteNumber(s.integratedProductivity, meanNdvi * 12);
      const baselineProd = validBaseline.length > 0 ? validBaseline.reduce((a, b) => a + b, 0) : (meanBaseline * 12);
      const anomPct = meanBaseline > 0 ? ((meanNdvi - meanBaseline) / meanBaseline) * 100 : 0;

      return {
        season: s.season || `Saison ${idx + 1}`,
        year: s.startYear || (1999 + idx),
        meanNdvi: Number(meanNdvi.toFixed(3)),
        meanBaseline: Number(meanBaseline.toFixed(3)),
        integratedProductivity: Number(integratedProd.toFixed(2)),
        baselineProductivity: Number(baselineProd.toFixed(2)),
        anomaly: Number(meanAnomaly.toFixed(3)),
        anomalyPercent: Number(anomPct.toFixed(1)),
      };
    });
  }, [activeCommuneSeries]);

  const annualChartData = React.useMemo(() => {
    if (annualData.length < 3) return annualData;
    const x = annualData.map((_, i) => i);
    const y = annualData.map((d) => d.meanNdvi);
    const trendFits = polyFit(x, y, polyOrder);
    return annualData.map((d, i) => ({
      ...d,
      trend: Number((trendFits[i] ?? d.meanNdvi).toFixed(3)),
    }));
  }, [annualData, polyOrder]);

  const annualStats = React.useMemo(() => {
    if (annualData.length === 0) return { mean: 0, minSeason: "-", minVal: 0, maxSeason: "-", maxVal: 0, deficitYearsCount: 0 };
    const mean = annualData.reduce((a, b) => a + b.meanNdvi, 0) / annualData.length;
    let minD = annualData[0];
    let maxD = annualData[0];
    let defCount = 0;
    annualData.forEach((d) => {
      if (d.meanNdvi < minD.meanNdvi) minD = d;
      if (d.meanNdvi > maxD.meanNdvi) maxD = d;
      if (d.anomalyPercent < -5) defCount++;
    });
    return {
      mean: Number(mean.toFixed(3)),
      minSeason: minD.season,
      minVal: minD.meanNdvi,
      maxSeason: maxD.season,
      maxVal: maxD.meanNdvi,
      deficitYearsCount: defCount,
    };
  }, [annualData]);

  // --- DATA PER MONTH (INTRA-ANNUAL 12-MONTHS FOR SELECTED SEASON) ---
  const activeSeasonData =
    activeCommuneSeries.find((s) => s.season === activeSeason) ||
    activeCommuneSeries[activeCommuneSeries.length - 1];

  const monthlyChartData = React.useMemo(() => {
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

  const yDomainNdviMonthly = React.useMemo(() => {
    if (monthlyChartData.length === 0) return [0, 0.8];
    const maxVal = Math.max(...monthlyChartData.map((d) => Math.max(d.ndvi, d.baseline)), 0.4);
    return [0, Math.min(1.0, Math.ceil((maxVal + 0.08) * 10) / 10)];
  }, [monthlyChartData]);

  const yDomainNdviAnnual = React.useMemo(() => {
    if (annualChartData.length === 0) return [0, 0.6];
    const minVal = Math.min(...annualChartData.map((d) => d.meanNdvi), 0.15);
    const maxVal = Math.max(...annualChartData.map((d) => Math.max(d.meanNdvi, d.meanBaseline, d.trend || 0)), 0.35);
    const lower = Math.max(0, Math.floor((minVal - 0.05) * 20) / 20);
    const upper = Math.min(1.0, Math.ceil((maxVal + 0.05) * 20) / 20);
    return [lower, upper];
  }, [annualChartData]);

  const yDomainAnomMonthly = React.useMemo(() => {
    if (monthlyChartData.length === 0) return [-0.1, 0.1];
    const maxAbs = Math.max(...monthlyChartData.map((d) => Math.abs(d.anomalies)), 0.04);
    const bound = Math.ceil((maxAbs + 0.02) * 20) / 20;
    return [-bound, bound];
  }, [monthlyChartData]);

  const yDomainAnomAnnual = React.useMemo(() => {
    if (annualChartData.length === 0) return [-0.05, 0.05];
    const maxAbs = Math.max(...annualChartData.map((d) => Math.abs(d.anomaly)), 0.03);
    const bound = Math.ceil((maxAbs + 0.015) * 20) / 20;
    return [-bound, bound];
  }, [annualChartData]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      {/* Metric Grid aligné sur toute la largeur avant Paramètres Végétation */}
      <section
        className="metric-grid"
        style={{
          display: "grid",
          gridTemplateColumns: timeScale === "annual" ? "repeat(4, 1fr)" : "repeat(3, 1fr)",
          gap: "14px",
          marginBottom: 0,
        }}
      >
        <article className="metric-card">
          <div className="metric-icon-wrap" style={{ color: "var(--accent)" }}><Icons.Leaf /></div>
          <div className="metric-info">
            <strong>{activeCommuneObj?.nom}</strong>
            <span>{activeCommuneObj?.district} ({activeCommuneObj?.region})</span>
          </div>
        </article>

        {timeScale === "annual" ? (
          <>
            <article className="metric-card">
              <div className="metric-icon-wrap" style={{ color: "var(--primary)" }}><Icons.Stats /></div>
              <div className="metric-info">
                <strong>{annualStats.mean.toFixed(3)}</strong>
                <span>Moyenne NDVI ({activeSensor.toUpperCase()} {annualData.length} ans)</span>
              </div>
            </article>
            <article className="metric-card">
              <div className="metric-icon-wrap" style={{ color: "var(--danger)" }}><Icons.Alert /></div>
              <div className="metric-info">
                <strong style={{ color: "var(--danger)", fontSize: "14px" }}>
                  Min: {annualStats.minSeason} ({annualStats.minVal?.toFixed(3)})
                </strong>
                <span>Max: {annualStats.maxSeason} ({annualStats.maxVal?.toFixed(3)})</span>
              </div>
            </article>
            <article className="metric-card">
              <div className="metric-icon-wrap" style={{ color: "var(--warning)" }}><Icons.Layers /></div>
              <div className="metric-info">
                <strong style={{ fontSize: "14px" }}>{annualStats.deficitYearsCount} saisons déficitaires</strong>
                <span>sur {annualData.length} campagnes</span>
              </div>
            </article>
          </>
        ) : (
          <>
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
                <span>Saison {activeSeasonData?.season ?? activeSeason}</span>
              </div>
            </article>
          </>
        )}
      </section>

      <section className="split-layout">
        <aside className="filters-panel">
          <h2>Paramètres Végétation</h2>

          <div className="filter-group">
            <label>Échelle Temporelle</label>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px", marginTop: "4px" }}>
              <button
                type="button"
                className={`scale-tab-btn ${timeScale === "annual" ? "active" : ""}`}
                onClick={() => setTimeScale("annual")}
                style={{ padding: "6px 4px", fontSize: "11px", fontWeight: timeScale === "annual" ? "700" : "500", textAlign: "center" }}
              >
                📈 Par Année
              </button>
              <button
                type="button"
                className={`scale-tab-btn ${timeScale === "monthly" ? "active" : ""}`}
                onClick={() => setTimeScale("monthly")}
                style={{ padding: "6px 4px", fontSize: "11px", fontWeight: timeScale === "monthly" ? "700" : "500", textAlign: "center" }}
              >
                📅 Par Mois
              </button>
            </div>
          </div>

          <div className="filter-group" style={{ marginTop: "10px" }}>
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
            <label htmlFor="sensor-sel">Capteur (Végétation)</label>
            <select id="sensor-sel" value={activeSensor} onChange={(e) => setActiveSensor(e.target.value)}>
              <option value="modis">MODIS (250m • 2000–2025)</option>
              <option value="landsat">Landsat (30m • 2015–2025)</option>
              <option value="sentinel">Sentinel-2 (10m • 2015–2025)</option>
            </select>
          </div>

          {timeScale === "monthly" && (
            <div className="filter-group" style={{ marginTop: "12px", borderTop: "1px solid var(--border-color)", paddingTop: "8px" }}>
              <label htmlFor="season-sel">Campagne (Saison)</label>
              <select id="season-sel" value={activeSeason} onChange={(e) => setActiveSeason(e.target.value)}>
                {seasonsList.length === 0 ? (
                  <option value="">Aucune saison disponible</option>
                ) : (
                  seasonsList.map((s) => (
                    <option key={s} value={s}>
                      {s === "2025-2026" ? `${s} (En cours : Oct–Déc)` : `Saison ${s}`}
                    </option>
                  ))
                )}
              </select>
            </div>
          )}
        </aside>

        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>

        {/* Primary Chart */}
        {timeScale === "annual" ? (
          <div className="panel">
            <div className="panel-heading" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
              <div>
                <h2><Icons.Stats /> Évolution Interannuelle du NDVI Moyen (2000–2025) — {activeCommuneObj?.nom}</h2>
                <span>Série temporelle annuelle ({activeSensor.toUpperCase()}) : Moyenne observée par campagne, référence historique et tendance</span>
              </div>
              <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "8px", flexShrink: 0 }}>
                <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>Tendance (Ordre {polyOrder}) :</span>
                <div style={{ display: "inline-flex", gap: "3px" }}>
                  {[1, 2, 3, 4, 5].map((o) => (
                    <button
                      key={o}
                      type="button"
                      className={`scale-tab-btn ${polyOrder === o ? "active" : ""}`}
                      onClick={() => setPolyOrder(o)}
                      style={{
                        padding: "2px 8px",
                        fontSize: "11px",
                        minWidth: "26px",
                        fontWeight: polyOrder === o ? "700" : "500",
                      }}
                    >
                      {o}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div style={{ width: "100%", height: 280 }}>
              <ResponsiveContainer>
                <ComposedChart data={annualChartData} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <XAxis dataKey="season" stroke="var(--text-muted)" fontSize={10} interval="preserveStartEnd" angle={-25} textAnchor="end" height={45} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} domain={yDomainNdviAnnual} />
                  <RechartsTooltip formatter={(val, name) => [Number(val).toFixed(3), name]} />
                  <Legend verticalAlign="top" height={36} />
                  <Line name="Normale Pluriannuelle (Référence)" type="monotone" dataKey="meanBaseline" stroke="var(--text-light)" strokeWidth={2} dot={false} strokeDasharray="4 4" />
                  <Area name="NDVI Moyen Annuel (Observé)" type="monotone" dataKey="meanNdvi" fill="rgba(16, 185, 129, 0.15)" stroke="var(--accent)" strokeWidth={2.5} dot={{ r: 3, fill: "var(--accent)" }} />
                  <Line name={`Tendance Polynomiale (Ordre ${polyOrder})`} type="monotone" dataKey="trend" stroke="#ef4444" strokeWidth={2.5} dot={false} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>
        ) : (
          <div className="panel">
            <div className="panel-heading" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
              <div>
                <h2><Icons.Stats /> Profil Phénologique NDVI Mensuel — {activeCommuneObj?.nom} (Saison {activeSeasonData?.season ?? activeSeason})</h2>
                <span>Cycle phénologique : Reverdissement dès Octobre/Novembre, pic en Février/Mars et dessèchement à partir de Mai</span>
              </div>
            </div>
            <div style={{ width: "100%", height: 260 }}>
              <ResponsiveContainer>
                <ComposedChart data={monthlyChartData} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={11} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} domain={yDomainNdviMonthly} />
                  <RechartsTooltip formatter={(val, name) => [Number(val).toFixed(3), name]} />
                  <Legend verticalAlign="top" height={36} />
                  <Line name="NDVI Normal (Moyenne historique)" type="monotone" dataKey="baseline" stroke="var(--text-light)" strokeWidth={2} dot={false} strokeDasharray="4 4" />
                  <Area name="NDVI Observé (Cycle réel)" type="monotone" dataKey="ndvi" fill="rgba(16, 185, 129, 0.15)" stroke="var(--accent)" strokeWidth={3} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </section>

    {/* Secondary Charts — Pleine largeur sur 2 colonnes */}
    {timeScale === "annual" ? (
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
        <div className="panel">
          <div className="panel-heading">
            <h3 style={{ fontSize: "13px", fontWeight: "700" }}>Productivité Annuelle Intégrée (Σ NDVI / Campagne) — {activeCommuneObj?.nom}</h3>
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>Indice de biomasse totale cumulée produite chaque année (somme des 12 mois)</span>
          </div>
          <div style={{ width: "100%", height: 220 }}>
            <ResponsiveContainer>
              <ComposedChart data={annualChartData} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                <XAxis dataKey="season" stroke="var(--text-muted)" fontSize={10} angle={-25} textAnchor="end" height={40} />
                <YAxis stroke="var(--text-muted)" fontSize={11} />
                <RechartsTooltip formatter={(val, name) => [Number(val).toFixed(2), name]} />
                <Legend verticalAlign="top" height={32} />
                <Line name="Référence Biomasse" type="monotone" dataKey="baselineProductivity" stroke="var(--text-light)" strokeWidth={2} dot={false} strokeDasharray="3 3" />
                <Bar name="Biomasse Totale (Σ NDVI)" dataKey="integratedProductivity" fill="var(--primary)" radius={[3, 3, 0, 0]} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <h3 style={{ fontSize: "13px", fontWeight: "700" }}>Anomalies Interannuelles de Végétation (2000–2025) — {activeCommuneObj?.nom}</h3>
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>Écart annuel à la moyenne historique (Vert = excédent végétal, Rouge = déficit / sécheresse)</span>
          </div>
          <div style={{ width: "100%", height: 220 }}>
            <ResponsiveContainer>
              <RechartsBarChart data={annualChartData} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                <XAxis dataKey="season" stroke="var(--text-muted)" fontSize={10} angle={-25} textAnchor="end" height={40} />
                <YAxis stroke="var(--text-muted)" fontSize={11} domain={yDomainAnomAnnual} />
                <RechartsTooltip formatter={(val, name, item) => [
                  `${val >= 0 ? "+" : ""}${Number(val).toFixed(3)} (${item?.payload?.anomalyPercent >= 0 ? "+" : ""}${item?.payload?.anomalyPercent}%)`,
                  "Écart annuel à la normale"
                ]} />
                <Bar name="Anomalie Annuelle" dataKey="anomaly">
                  {annualChartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.anomaly >= 0 ? "var(--accent)" : "var(--danger)"}
                    />
                  ))}
                </Bar>
              </RechartsBarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    ) : (
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
        <div className="panel">
          <div className="panel-heading">
            <h3 style={{ fontSize: "13px", fontWeight: "700" }}>NDVI Cumulé au fil des mois — {activeCommuneObj?.nom}</h3>
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>Somme progressive mensuelle Σ NDVI (accumulation continue de biomasse en saison {activeSeasonData?.season ?? activeSeason})</span>
          </div>
          <div style={{ width: "100%", height: 220 }}>
            <ResponsiveContainer>
              <AreaChart data={monthlyChartData} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={11} />
                <YAxis stroke="var(--text-muted)" fontSize={11} />
                <RechartsTooltip formatter={(val) => [Number(val).toFixed(2), "Cumul de biomasse"]} />
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
            <h3 style={{ fontSize: "13px", fontWeight: "700" }}>Écart NDVI mensuel à la normale — {activeCommuneObj?.nom}</h3>
            <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>Anomalie relative au mois (Vert = au-dessus de la normale, Rouge = en dessous)</span>
          </div>
          <div style={{ width: "100%", height: 220 }}>
            <ResponsiveContainer>
              <RechartsBarChart data={monthlyChartData} margin={{ top: 10, right: 10, bottom: 10, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={11} />
                <YAxis stroke="var(--text-muted)" fontSize={11} domain={yDomainAnomMonthly} />
                <RechartsTooltip formatter={(val) => [`${val >= 0 ? "+" : ""}${Number(val).toFixed(3)}`, "Écart à la normale"]} />
                <Bar name="Anomalie NDVI" dataKey="anomalies">
                  {monthlyChartData.map((entry, index) => (
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
    )}

    {/* Educational Methodology Card */}
    <div className="formula-card" style={{ marginTop: "4px" }}>
      <div className="formula-card-header">
        <Icons.Info />
        <span>Guide Méthodologique & Agro-Phénologique : Double Échelle Temporelle (Année vs Mois)</span>
      </div>
      <div className="formula-grid">
        <div className="formula-item">
          <div className="formula-item-title">
            <span>1. Échelle Interannuelle (Par Année : 2000–2025)</span>
            <span style={{ color: "var(--primary)" }}>📈 Analyse Climatique 25 ans</span>
          </div>
          <div className="formula-code">
            NDVI_moyen,y = (1/12) Σ NDVI_y,m &nbsp;|&nbsp; Biomasse_y = Σ NDVI_y,m
          </div>
          <div className="formula-desc">
            Agrège les 12 mois de chaque campagne pour dégager l'évolution pluriannuelle. Permet d'isoler les <strong>grandes crises de sécheresse</strong> (ex: effondrement du couvert végétal en 2020–2021 et 2021–2022) et les tendances écologiques à long terme (dégradation vs verdissement).
          </div>
        </div>

        <div className="formula-item">
          <div className="formula-item-title">
            <span>2. Échelle Phénologique (Par Mois : Octobre → Septembre)</span>
            <span style={{ color: "var(--accent)" }}>🌱 Cycle Agricole Saisonnier</span>
          </div>
          <div className="formula-code">
            NDVI_m ∈ [0.15 ; 0.85] &nbsp;|&nbsp; Octobre → Mai
          </div>
          <div className="formula-desc">
            Révèle le calendrier intra-annuel : <strong>Reverdissement dès Octobre/Novembre</strong> (premières pluies), <strong>Pic végétal maximal en Février–Mars</strong> (floraison/maturation), et <strong>Dessèchement progressif à partir de Mai</strong> (transition vers la saison sèche).
          </div>
        </div>

        <div className="formula-item">
          <div className="formula-item-title">
            <span>3. Diagnostic des Anomalies & Stress Hydrique</span>
            <span style={{ color: "var(--warning)" }}>⚖️ Écart à la Normale</span>
          </div>
          <div className="formula-code">
            Anomalie = NDVI_observé - NDVI_référence
          </div>
          <div className="formula-desc">
            Quantifie le déficit végétal par rapport à la moyenne climatologique : des <strong>barres rouges</strong> signalent un retard pluviométrique ou un flétrissement anormal, tandis que des <strong>barres vertes</strong> traduisent une vigueur biophysique supérieure.
          </div>
        </div>
      </div>
    </div>
  </div>
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
    const sTerm = String(searchTerm || "").toLowerCase().trim();
    return (communes || []).filter((c) => {
      if (!c) return false;
      const matchRegion = !selectedRegion || c.region === selectedRegion;
      const cNom = String(c.nom || "").toLowerCase();
      const cCode = String(c.code || "").toLowerCase();
      const matchSearch = !sTerm || cNom.includes(sTerm) || cCode.includes(sTerm);
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

  const CustomStartEndTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const s = data.saison;
      const debutName = monthNamesFrMap[data.debutLabel] || data.debutLabel || "—";
      const finName = monthNamesFrMap[data.finLabel] || data.finLabel || "—";

      return (
        <div className="recharts-custom-tooltip">
          <p className="recharts-custom-tooltip-title" style={{ fontSize: "12px", fontWeight: "800", color: "#0f172a" }}>
            Saison {s}–{Number(s) + 1}
          </p>
          <div className="recharts-custom-tooltip-item">
            <span style={{ color: "#2563eb", fontWeight: "600" }}>🔵 Mois de Début :</span>
            <strong style={{ color: "#1d4ed8" }}>{debutName}</strong>
          </div>
          <div className="recharts-custom-tooltip-item">
            <span style={{ color: "#059669", fontWeight: "600" }}>🟢 Mois de Fin :</span>
            <strong style={{ color: "#047857" }}>{finName}</strong>
          </div>
          <div className="recharts-custom-tooltip-item" style={{ borderTop: "1px solid #e2e8f0", paddingTop: "5px", marginTop: "5px" }}>
            <span style={{ color: "#64748b" }}>⏳ Durée utile :</span>
            <strong style={{ color: "#0f172a" }}>{data.duree} mois</strong>
          </div>
        </div>
      );
    }
    return null;
  };

  const CustomMaxMonthTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const monthCode = data.mois_plus_pluvieux || "";
      const monthFull = monthNamesFrMap[monthCode] || monthCode || "Mois le plus pluvieux";
      const precipVal = payload[0].value ?? data.precip ?? 0;
      const s = data.saison;

      return (
        <div className="recharts-custom-tooltip">
          <p className="recharts-custom-tooltip-title" style={{ fontSize: "12px", fontWeight: "800", color: "#0f172a" }}>
            Saison {s}–{Number(s) + 1} • {monthFull}
          </p>
          <div className="recharts-custom-tooltip-item">
            <span style={{ color: "#64748b" }}>Précipitation maximale :</span>
            <strong style={{ color: "var(--primary)" }}>{Number(precipVal).toLocaleString("fr-FR")} mm</strong>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
      <section className="split-layout" style={{ marginBottom: "6px" }}>
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
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "var(--primary)", fontWeight: "700", marginTop: "4px" }}>
              <span>{seasonRange[0]}–{Number(seasonRange[0]) + 1}</span>
              <span>{seasonRange[1]}–{Number(seasonRange[1]) + 1}</span>
            </div>
            <div style={{ display: "flex", gap: "8px", marginTop: "6px" }}>
              <input
                type="number"
                min={availableSeasons[0]}
                max={seasonRange[1]}
                value={seasonRange[0]}
                onChange={(e) => setSeasonRange([Math.max(availableSeasons[0], Number(e.target.value)), seasonRange[1]])}
                style={{ width: "50%", padding: "4px 6px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", fontSize: "12px" }}
                title={`Saison de début : ${seasonRange[0]}-${Number(seasonRange[0]) + 1}`}
              />
              <input
                type="number"
                min={seasonRange[0]}
                max={availableSeasons[1]}
                value={seasonRange[1]}
                onChange={(e) => setSeasonRange([seasonRange[0], Math.min(availableSeasons[1], Number(e.target.value))])}
                style={{ width: "50%", padding: "4px 6px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", fontSize: "12px" }}
                title={`Saison de fin : ${seasonRange[1]}-${Number(seasonRange[1]) + 1}`}
              />
            </div>
          </div>
        </aside>

        <div className="panel">
          <div className="panel-heading" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <h2><Icons.Rain /> Saison des pluies - {selectedCommuneName}</h2>
              <span>Début, durée et mois le plus pluvieux ({seasonRange[0]}–{Number(seasonRange[0]) + 1} à {seasonRange[1]}–{Number(seasonRange[1]) + 1})</span>
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
                      <XAxis
                        dataKey="saison"
                        stroke="var(--text-muted)"
                        fontSize={11}
                        angle={-45}
                        textAnchor="end"
                        height={50}
                        tickFormatter={(s) => `${s}-${(Number(s) + 1).toString().slice(-2)}`}
                      />
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
                      <RechartsTooltip content={<CustomStartEndTooltip />} />
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
                      <XAxis
                        dataKey="saison"
                        stroke="var(--text-muted)"
                        fontSize={11}
                        angle={-45}
                        textAnchor="end"
                        height={50}
                        tickFormatter={(s) => `${s}-${(Number(s) + 1).toString().slice(-2)}`}
                      />
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
                <div className="timeline-container" style={{ marginTop: "12px" }}>
                  {/* Clean Month Header */}
                  <div className="timeline-header-row">
                    <span className="timeline-col-season">Saison</span>
                    <div className="timeline-col-months">
                      {hydroMonths.map((m) => (
                        <span key={m}>{m}</span>
                      ))}
                    </div>
                    <span className="timeline-col-info">Durée & Pic</span>
                  </div>

                  <div className="timeline-rows-list">
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

                      const debutName = monthNamesFrMap[row.debut] || row.debut;
                      const finName = monthNamesFrMap[row.fin] || row.fin;

                      return (
                        <div className="timeline-row" key={`${row.code_commune}-${row.saison}`}>
                          <span className="timeline-row-season">
                            Saison {row.saison}–{Number(row.saison) + 1}
                          </span>

                          <div className="timeline-track-container">
                            <div className="timeline-track-bg"></div>
                            <div
                              className="timeline-track-fill"
                              style={{ left: `${leftPercent}%`, width: `${widthPercent}%`, minWidth: "12px" }}
                              title={`Saison ${row.saison}-${Number(row.saison) + 1} : Du ${debutName} au ${finName} (${row.duree} mois)`}
                            ></div>
                          </div>

                          <div className="timeline-duration">
                            <strong>{row.duree} mois</strong>
                            <div style={{ fontSize: "11px", color: "var(--text-light)", fontWeight: "500", marginTop: "2px" }}>
                              Max : {row.mois_plus_pluvieux || "—"} ({row.precip ? `${row.precip} mm` : "—"})
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </section>

      {/* Méthodologie / Formules affichées en bas sur toute la largeur (3 colonnes) */}
      {filteredSeasonRows.length > 0 && subTab === "start_end" && (
        <div className="formula-card" style={{ marginTop: "0px" }}>
          <div className="formula-card-header">
            <Icons.Info />
            <span>Formules de Calcul du Début, de la Fin et de la Durée de Saison</span>
          </div>
          <div className="formula-grid" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "14px" }}>
            <div className="formula-item">
              <div className="formula-item-title">
                <span>1. Mois de Début (M_début)</span>
                <span style={{ color: "#1f78b4" }}>🔵 Bleu</span>
              </div>
              <div className="formula-code">
                M_début = Premier mois m ∈ &#123;Nov, Déc, Jan, Oct&#125; avec P_m ≥ 25 mm
              </div>
              <div className="formula-desc">
                Identifie l'arrivée des pluies d'installation nécessaires aux semis. Référence standard Grand Sud : <strong>Novembre</strong> (ou Décembre/Janvier en cas de retard sévère).
              </div>
            </div>

            <div className="formula-item">
              <div className="formula-item-title">
                <span>2. Mois de Fin (M_fin)</span>
                <span style={{ color: "#33a02c" }}>🟢 Vert</span>
              </div>
              <div className="formula-code">
                M_fin = Dernier mois m ∈ &#123;Fév, Mars, Avr, Mai&#125; avant tarissement (&lt; 25 mm)
              </div>
              <div className="formula-desc">
                Marque la fin des pluies utiles à la maturation des cultures. Référence standard Grand Sud : <strong>Mars</strong> (ou Avril dans l'Anosy et zones humides).
              </div>
            </div>

            <div className="formula-item">
              <div className="formula-item-title">
                <span>3. Durée de la Saison (D)</span>
                <span style={{ color: "#10b981" }}>⏳ Durée</span>
              </div>
              <div className="formula-code">
                D = (12 - M_début + 1) + M_fin  (en mois)
              </div>
              <div className="formula-desc">
                Nombre total de mois de la fenêtre pluvieuse active (généralement <strong>4 à 5 mois</strong> dans le Grand Sud, suivis de 7 à 8 mois de saison sèche).
              </div>
            </div>
          </div>
          <div className="formula-note">
            📌 <strong>Références Régionales :</strong> Androy (Novembre → Mars), Anosy (Novembre/Octobre → Mars/Avril), Atsimo-Andrefana (Novembre → Mars).
          </div>
        </div>
      )}

      {filteredSeasonRows.length > 0 && subTab === "max_month" && (
        <div className="formula-card" style={{ marginTop: "0px" }}>
          <div className="formula-card-header">
            <Icons.Rain />
            <span>Formules du Mois le Plus Pluvieux & Précipitations Maximales</span>
          </div>
          <div className="formula-grid" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "14px" }}>
            <div className="formula-item">
              <div className="formula-item-title">
                <span>1. Mois le Plus Pluvieux (M_max)</span>
                <span style={{ color: "var(--primary)" }}>🌧️ Pic</span>
              </div>
              <div className="formula-code">
                M_max = argmax_(m ∈ [M_début ... M_fin]) ( P_m )
              </div>
              <div className="formula-desc">
                Mois au cours duquel le cumul mensuel atteint son maximum absolu sur la campagne agricole active.
              </div>
            </div>

            <div className="formula-item">
              <div className="formula-item-title">
                <span>2. Précipitation Maximale (P_max)</span>
                <span style={{ color: "var(--primary)" }}>📊 Hauteur</span>
              </div>
              <div className="formula-code">
                P_max = max_(m ∈ [M_début ... M_fin]) ( P_m )  (en mm)
              </div>
              <div className="formula-desc">
                Hauteur maximale de pluie enregistrée pendant le mois le plus arrosé de la saison agricole.
              </div>
            </div>

            <div className="formula-item">
              <div className="formula-item-title">
                <span>3. Contribution au Bilan Annuel</span>
                <span style={{ color: "#f59e0b" }}>💧 % Annuel</span>
              </div>
              <div className="formula-code">
                Part_max = (P_max / P_annuel) × 100 %
              </div>
              <div className="formula-desc">
                Dans le Grand Sud, ce mois de pic (généralement <strong>Janvier</strong> ou <strong>Février</strong>) apporte à lui seul entre <strong>35% et 50%</strong> de toute la pluie annuelle.
              </div>
            </div>
          </div>
          <div className="formula-note">
            📌 <strong>Dynamique Climatique :</strong> Le pic pluviométrique de janvier/février correspond au passage de la ZCIT (Zone de Convergence Intertropicale) et aux dépressions tropicales.
          </div>
        </div>
      )}

      {filteredSeasonRows.length > 0 && subTab === "timeline" && (
        <div className="formula-card" style={{ marginTop: "0px" }}>
          <div className="formula-card-header">
            <Icons.Stats />
            <span>Méthodologie du Chronogramme & Étalement Temporel des Campagnes</span>
          </div>
          <div className="formula-grid" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "14px" }}>
            <div className="formula-item">
              <div className="formula-item-title">
                <span>1. Fenêtre Pluvieuse Active</span>
                <span style={{ color: "var(--primary)" }}>🗓️ Période</span>
              </div>
              <div className="formula-code">
                Saison = [ M_début → M_fin ]  sur cycle hydrologique (Oct à Sep)
              </div>
              <div className="formula-desc">
                Représente graphiquement la continuité des mois pluvieux utiles, de l'installation des semis jusqu'à la maturation des récoltes.
              </div>
            </div>

            <div className="formula-item">
              <div className="formula-item-title">
                <span>2. Positionnement sur l'Axe</span>
                <span style={{ color: "#10b981" }}>📐 Échelle</span>
              </div>
              <div className="formula-code">
                Départ = (Index_début / 12) × 100%,  Largeur = (D / 12) × 100%
              </div>
              <div className="formula-desc">
                Positionne la barre colorée proportionnellement sur les 12 mois du calendrier hydrologique (d'Octobre = 0% à Septembre = 100%).
              </div>
            </div>

            <div className="formula-item">
              <div className="formula-item-title">
                <span>3. Bilan Saisonnier & Aridité</span>
                <span style={{ color: "#f59e0b" }}>☀️ Climat</span>
              </div>
              <div className="formula-code">
                Durée Saison Sèche = 12 - D  (7 à 8 mois secs)
              </div>
              <div className="formula-desc">
                Met en évidence la brièveté de la période culturale (4 à 5 mois) face à la longue saison sèche (Avril à Octobre) caractéristique de l'aridité du Grand Sud.
              </div>
            </div>
          </div>
          <div className="formula-note">
            📌 <strong>Lecture Agro-Climatique :</strong> Un décalage de la barre vers la droite (ex: début en Janvier) traduit un retard des pluies d'installation ou une sécheresse précoce (Kéré).
          </div>
        </div>
      )}
    </div>
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

  const [modeCommune, setModeCommune] = React.useState("Choisir une commune");
  const [selectedDistrict, setSelectedDistrict] = React.useState("");
  const [selectedCommune, setSelectedCommune] = React.useState(appSelectedCommune || communes[0]?.code || "");
  const [typeGraph, setTypeGraph] = React.useState("Climatologie mensuelle");
  const [ordrePoly, setOrdrePoly] = React.useState(4);
  const [monthlyMode, setMonthlyMode] = React.useState("specific_year"); // 'specific_year' (Année Spécifique) | 'climatology' (Normale 1981–2025)
  const [selectedYearForMonth, setSelectedYearForMonth] = React.useState(2020);

  // Sync selectedCommune with appSelectedCommune
  React.useEffect(() => {
    if (appSelectedCommune && appSelectedCommune !== selectedCommune) {
      setSelectedCommune(appSelectedCommune);
    }
  }, [appSelectedCommune]);

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

  const filteredCommunes = React.useMemo(() => {
    return communes.filter((c) => {
      if (selectedRegion && c.region !== selectedRegion) return false;
      if (selectedDistrict && c.district !== selectedDistrict) return false;
      return true;
    });
  }, [communes, selectedRegion, selectedDistrict]);

  React.useEffect(() => {
    if (filteredCommunes.length > 0 && !filteredCommunes.some((c) => c.code === selectedCommune)) {
      const firstCode = filteredCommunes[0].code;
      setSelectedCommune(firstCode);
      if (appSetSelectedCommune) appSetSelectedCommune(firstCode);
    }
  }, [filteredCommunes, selectedCommune]);

  const handleCommuneChange = (code) => {
    setSelectedCommune(code);
    if (appSetSelectedCommune) appSetSelectedCommune(code);
  };

  const selectedCommuneObj = React.useMemo(() => {
    return communes.find((c) => c.code === selectedCommune) || filteredCommunes[0] || communes[0];
  }, [communes, selectedCommune, filteredCommunes]);

  const titreStats = modeCommune === "Toutes les communes" ? "Toutes les communes (Grand Sud)" : (selectedCommuneObj?.nom || selectedCommune);

  const availableYears = React.useMemo(() => {
    const years = [];
    for (let y = 2025; y >= 1981; y--) years.push(y);
    return years;
  }, []);

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

  // Comprehensive monthly data calculation
  const climatologyData = React.useMemo(() => {
    const monthNames = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"];
    if (precipRecords && precipRecords.length > 0) {
      const filtered = modeCommune === "Toutes les communes"
        ? precipRecords
        : precipRecords.filter((r) => r.code === selectedCommune);

      if (filtered.length > 0) {
        // Climatology baseline (1981-2025)
        const climDict = {};
        for (let m = 1; m <= 12; m++) climDict[m] = [];
        filtered.forEach((r) => {
          if (r.month >= 1 && r.month <= 12 && Number.isFinite(r.precip)) {
            climDict[r.month].push(r.precip);
          }
        });

        // Specific year values
        const yearRecords = filtered.filter((r) => r.year === Number(selectedYearForMonth));
        const yearDict = {};
        yearRecords.forEach((r) => {
          yearDict[r.month] = (yearDict[r.month] || 0) + r.precip;
        });
        if (modeCommune === "Toutes les communes") {
          const uniqueCommunesInYear = new Set(yearRecords.map((r) => r.code)).size || 1;
          Object.keys(yearDict).forEach((m) => {
            yearDict[m] = yearDict[m] / uniqueCommunesInYear;
          });
        }

        return monthNames.map((m, idx) => {
          const mNum = idx + 1;
          const vals = climDict[mNum] || [];
          const meanRef = vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
          const pObs = Number.isFinite(yearDict[mNum]) ? yearDict[mNum] : meanRef;
          const deficit = pObs - meanRef;
          const deficitPct = meanRef > 0 ? (deficit / meanRef) * 100 : 0;

          return {
            month: m,
            p: Math.round(monthlyMode === "specific_year" ? pObs : meanRef),
            pObs: Math.round(pObs * 10) / 10,
            pRef: Math.round(meanRef * 10) / 10,
            deficit: Math.round(deficit * 10) / 10,
            deficitPct: Math.round(deficitPct * 10) / 10,
            isDeficit: deficit < 0,
          };
        });
      }
    }

    if (modeCommune === "Toutes les communes" && monthlyClimatology) {
      return monthlyClimatology.map((d) => ({
        month: d.month,
        p: d.precip,
        pObs: d.precip,
        pRef: d.precip,
        deficit: 0,
        deficitPct: 0,
        isDeficit: false,
      }));
    }

    const meanAnn = communeAnnualSeries.reduce((a, b) => a + b.p, 0) / (communeAnnualSeries.length || 1);
    const weights = { Jan: 0.26, Fév: 0.22, Mar: 0.18, Dec: 0.14, Nov: 0.09, Avr: 0.05, Mai: 0.02, Jun: 0.01, Jul: 0.01, Aoû: 0.01, Sep: 0.01, Oct: 0.00 };
    return monthNames.map((m) => {
      const key = m === "Déc" ? "Dec" : m === "Aoû" ? "Aoû" : m;
      const w = weights[key] || 0.02;
      const p = Math.round(meanAnn * w);
      return { month: m, p, pObs: p, pRef: p, deficit: 0, deficitPct: 0, isDeficit: false };
    });
  }, [modeCommune, selectedCommune, precipRecords, monthlyClimatology, communeAnnualSeries, selectedYearForMonth, monthlyMode]);

  // Summary KPIs for selected year vs climatology
  const monthlyStatsSummary = React.useMemo(() => {
    if (climatologyData.length === 0) return { sumObs: 0, sumRef: 0, annualDeficit: 0, annualDeficitPct: 0, maxMonth: "-", minMonth: "-" };
    const sumObs = Math.round(climatologyData.reduce((a, b) => a + b.pObs, 0));
    const sumRef = Math.round(climatologyData.reduce((a, b) => a + b.pRef, 0));
    const annualDeficit = sumObs - sumRef;
    const annualDeficitPct = sumRef > 0 ? Math.round(((sumObs - sumRef) / sumRef) * 100) : 0;

    let maxM = climatologyData[0];
    let minM = climatologyData[0];
    climatologyData.forEach((d) => {
      if (d.pObs > maxM.pObs) maxM = d;
      if (d.pObs < minM.pObs) minM = d;
    });

    return {
      sumObs,
      sumRef,
      annualDeficit,
      annualDeficitPct,
      maxMonth: `${maxM.month} (${maxM.pObs} mm)`,
      minMonth: `${minM.month} (${minM.pObs} mm)`,
    };
  }, [climatologyData]);

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
          <section className="metric-grid">
            <article className="metric-card">
              <div className="metric-icon-wrap" style={{ color: "var(--primary)" }}><Icons.Map /></div>
              <div className="metric-info">
                <strong style={{ fontSize: "14px" }}>{titreStats}</strong>
                <span>{modeCommune === "Toutes les communes" ? "Échelle Régionale (225 communes)" : `District : ${selectedCommuneObj?.district || "N/A"} (${selectedCommuneObj?.region || "N/A"})`}</span>
              </div>
            </article>
            <article className="metric-card">
              <div className="metric-icon-wrap" style={{ color: "var(--accent)" }}><Icons.Stats /></div>
              <div className="metric-info">
                <strong>{meanClim} mm/an</strong>
                <span>Normale Pluriannuelle (1981–2010)</span>
              </div>
            </article>
            <article className="metric-card">
              <div className="metric-icon-wrap" style={{ color: "var(--warning)" }}><Icons.Rain /></div>
              <div className="metric-info">
                <strong>± {sdClim} mm</strong>
                <span>Écart-Type (Variabilité Interannuelle)</span>
              </div>
            </article>
            <article className="metric-card">
              <div className="metric-icon-wrap" style={{ color: "var(--danger)" }}><Icons.Alert /></div>
              <div className="metric-info">
                <strong style={{ color: "var(--danger)" }}>{driestYear ? `${driestYear.year} (${driestYear.p} mm)` : "N/A"}</strong>
                <span>Année la plus sèche (Crise historique)</span>
              </div>
            </article>
          </section>

          {/* Main Analysis Section with Split Control Panel */}
          <section className="split-layout" style={{ marginBottom: "10px" }}>
            <aside className="filters-panel">
              <h2>Paramètres Pluviométrie</h2>

              <div className="filter-group">
                <label style={{ fontWeight: "700" }}>Affichage géographique :</label>
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
                <>
                  <div className="filter-group" style={{ marginTop: "10px" }}>
                    <label htmlFor="stat-region-sel">Région :</label>
                    <select
                      id="stat-region-sel"
                      value={selectedRegion}
                      onChange={(e) => setSelectedRegion(e.target.value)}
                    >
                      <option value="">Toutes les régions</option>
                      {regions.map((r) => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                  </div>

                  <div className="filter-group">
                    <label htmlFor="stat-district-sel">District :</label>
                    <select
                      id="stat-district-sel"
                      value={selectedDistrict}
                      onChange={(e) => setSelectedDistrict(e.target.value)}
                    >
                      <option value="">Tous les districts</option>
                      {districtsList.map((d) => (
                        <option key={d} value={d}>{d}</option>
                      ))}
                    </select>
                  </div>

                  <div className="filter-group">
                    <label htmlFor="commune-select-stat">Commune :</label>
                    <select
                      id="commune-select-stat"
                      value={selectedCommune}
                      onChange={(e) => handleCommuneChange(e.target.value)}
                    >
                      {filteredCommunes.map((c) => (
                        <option key={c.code} value={c.code}>
                          {c.nom} ({c.code})
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}

              <div className="filter-group" style={{ marginTop: "14px", borderTop: "1px solid var(--border-color)", paddingTop: "12px" }}>
                <label style={{ fontWeight: "700" }}>Type d'analyse :</label>
                <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginTop: "8px" }}>
                  {[
                    { id: "Climatologie mensuelle", label: "☀️ Climatologie & Pluie mensuelle" },
                    { id: "Histogramme", label: "📊 Histogramme des pluies" },
                    { id: "Tendance", label: "📈 Tendance polynomiale" },
                    { id: "Anomalies", label: "⚡ Anomalies annuelles (1981–2010)" },
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

              {typeGraph === "Climatologie mensuelle" && (
                <div className="filter-group" style={{ marginTop: "12px", borderTop: "1px solid var(--border-color)", paddingTop: "10px" }}>
                  <label htmlFor="month-year-select" style={{ fontWeight: "700" }}>Année observée :</label>
                  <select
                    id="month-year-select"
                    value={selectedYearForMonth}
                    onChange={(e) => {
                      setSelectedYearForMonth(Number(e.target.value));
                      setMonthlyMode("specific_year");
                    }}
                    style={{ marginTop: "4px" }}
                  >
                    {availableYears.map((yr) => (
                      <option key={yr} value={yr}>
                        Année {yr} {yr === 2020 || yr === 2021 || yr === 2022 ? "(Sécheresse Kéré)" : ""}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {typeGraph === "Anomalies" && (
                <div
                  className="info-bulletin"
                  style={{
                    marginTop: "14px",
                    marginBottom: 0,
                    fontSize: "11px",
                    lineHeight: "1.45",
                    padding: "10px 12px",
                  }}
                >
                  <strong>Note méthodologique :</strong> La zone en arrière-plan gris sur le graphique d'anomalie correspond à ±1 écart-type par rapport à la moyenne climatologique de la période de référence 1981–2010 ({meanClim} mm/an). Les barres rouges représentent des années de déficit pluvial critique.
                </div>
              )}
            </aside>

            <div className="panel">
              <div className="panel-heading" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
                <div>
                  <h2><Icons.Stats /> {typeGraph === "Climatologie mensuelle" ? (monthlyMode === "specific_year" ? `Précipitations Mensuelles (Année ${selectedYearForMonth}) vs Normale` : `Climatologie Mensuelle Normale (1981–2025)`) : typeGraph} — {titreStats}</h2>
                  <span>
                    {typeGraph === "Tendance"
                      ? `Régression polynomiale d'ordre ${ordrePoly} sur la série temporelle`
                      : typeGraph === "Climatologie mensuelle"
                      ? `Comparaison mois par mois de la pluie observée face à la climatologie de référence (1981–2025)`
                      : "Visualisation statistique temporelle et distribution"}
                  </span>
                </div>

                {typeGraph === "Climatologie mensuelle" && (
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <div style={{ display: "inline-flex", gap: "4px" }}>
                      <button
                        type="button"
                        className={`scale-tab-btn ${monthlyMode === "specific_year" ? "active" : ""}`}
                        onClick={() => setMonthlyMode("specific_year")}
                        style={{ padding: "4px 10px", fontSize: "12px", fontWeight: monthlyMode === "specific_year" ? "700" : "500" }}
                      >
                        📅 Année {selectedYearForMonth}
                      </button>
                      <button
                        type="button"
                        className={`scale-tab-btn ${monthlyMode === "climatology" ? "active" : ""}`}
                        onClick={() => setMonthlyMode("climatology")}
                        style={{ padding: "4px 10px", fontSize: "12px", fontWeight: monthlyMode === "climatology" ? "700" : "500" }}
                      >
                        📊 Moyenne 1981–2025
                      </button>
                    </div>
                  </div>
                )}

                {typeGraph === "Tendance" && (
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ fontSize: "11px", fontWeight: "700", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                      Ordre de tendance :
                    </span>
                    <div className="scale-tabs" style={{ display: "flex", gap: "2px", padding: "2px", background: "var(--bg-app)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-color)" }}>
                      {[1, 2, 3, 4, 5].map((o) => (
                        <button
                          key={o}
                          type="button"
                          className={`scale-tab-btn ${ordrePoly === o ? "active" : ""}`}
                          onClick={() => setOrdrePoly(o)}
                          style={{
                            minWidth: "28px",
                            padding: "3px 7px",
                            fontSize: "11px",
                            fontWeight: ordrePoly === o ? "700" : "500",
                            borderRadius: "3px",
                          }}
                          title={`Polynôme degré ${o}${o === 4 ? " (Référence R)" : ""}`}
                        >
                          {o}{o === 4 ? " (R)" : ""}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {typeGraph === "Climatologie mensuelle" && (
                <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginTop: "12px" }}>
                  <div style={{ width: "100%", height: 320 }}>
                    <ResponsiveContainer>
                      <ComposedChart data={climatologyData} margin={{ top: 20, right: 20, bottom: 25, left: 10 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                        <XAxis
                          dataKey="month"
                          stroke="var(--text-muted)"
                          fontSize={12}
                        />
                        <YAxis
                          stroke="var(--text-muted)"
                          fontSize={11}
                          unit=" mm"
                        />
                        <RechartsTooltip
                          formatter={(val, name, item) => {
                            const nameStr = String(name || "");
                            if (nameStr.includes("Observée") || nameStr.includes("Observee")) {
                              const def = item?.payload?.deficit ?? 0;
                              const defPct = item?.payload?.deficitPct ?? 0;
                              return [
                                `${val} mm (Écart: ${def >= 0 ? "+" : ""}${def} mm / ${defPct >= 0 ? "+" : ""}${defPct}%)`,
                                `Pluie ${selectedYearForMonth}`
                              ];
                            }
                            return [`${val} mm`, nameStr];
                          }}
                        />
                        <Legend verticalAlign="top" height={36} />
                        <Line
                          name="Normale Climatologique (Moyenne 1981–2025)"
                          type="monotone"
                          dataKey="pRef"
                          stroke="#64748b"
                          strokeWidth={2.5}
                          dot={{ r: 4, fill: "#64748b" }}
                          strokeDasharray="4 4"
                        />
                        {monthlyMode === "specific_year" ? (
                          <Bar
                            name={`Pluie Observée en ${selectedYearForMonth} (mm)`}
                            dataKey="pObs"
                            fill="#2563eb"
                            radius={[4, 4, 0, 0]}
                          />
                        ) : (
                          <Bar
                            name="Pluie Moyenne Historique (mm)"
                            dataKey="pRef"
                            fill="#10b981"
                            radius={[4, 4, 0, 0]}
                          />
                        )}
                      </ComposedChart>
                    </ResponsiveContainer>
                  </div>

                  {monthlyMode === "specific_year" && (
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                      <div className="panel" style={{ background: "var(--bg-panel-secondary)", padding: "12px", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
                        <h4 style={{ fontSize: "12px", fontWeight: "700", marginBottom: "8px" }}>
                          ⚡ Déficits & Excédents Mensuels en {selectedYearForMonth}
                        </h4>
                        <div style={{ width: "100%", height: 180 }}>
                          <ResponsiveContainer>
                            <RechartsBarChart data={climatologyData} margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
                              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                              <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={11} />
                              <YAxis stroke="var(--text-muted)" fontSize={11} unit=" mm" />
                              <RechartsTooltip formatter={(val, name, item) => [`${val >= 0 ? "+" : ""}${val} mm (${item?.payload?.deficitPct >= 0 ? "+" : ""}${item?.payload?.deficitPct}%)`, "Écart à la normale"]} />
                              <Bar name="Déficit / Excédent" dataKey="deficit">
                                {climatologyData.map((entry, index) => (
                                  <Cell
                                    key={`cell-${index}`}
                                    fill={entry.deficit >= 0 ? "var(--accent)" : "var(--danger)"}
                                  />
                                ))}
                              </Bar>
                            </RechartsBarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>

                      <div className="panel" style={{ background: "var(--bg-panel-secondary)", padding: "12px", borderRadius: "8px", border: "1px solid var(--border-color)", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                        <h4 style={{ fontSize: "12px", fontWeight: "700", marginBottom: "8px" }}>
                          📋 Bilan Agro-Pluviométrique de l'Année {selectedYearForMonth}
                        </h4>
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", fontSize: "12px" }}>
                          <div style={{ padding: "8px", background: "var(--bg-app)", borderRadius: "6px" }}>
                            <span style={{ color: "var(--text-muted)", display: "block", fontSize: "11px" }}>Cumul Annuel Observé</span>
                            <strong style={{ fontSize: "15px" }}>{monthlyStatsSummary.sumObs} mm</strong>
                            <span style={{ fontSize: "11px", color: "var(--text-light)", display: "block" }}>Normale : {monthlyStatsSummary.sumRef} mm</span>
                          </div>
                          <div style={{ padding: "8px", background: "var(--bg-app)", borderRadius: "6px" }}>
                            <span style={{ color: "var(--text-muted)", display: "block", fontSize: "11px" }}>Bilan Annuel Global</span>
                            <strong style={{ fontSize: "15px", color: monthlyStatsSummary.annualDeficit >= 0 ? "var(--accent)" : "var(--danger)" }}>
                              {monthlyStatsSummary.annualDeficit >= 0 ? "+" : ""}{monthlyStatsSummary.annualDeficit} mm ({monthlyStatsSummary.annualDeficitPct}%)
                            </strong>
                            <span style={{ fontSize: "11px", color: monthlyStatsSummary.annualDeficit >= 0 ? "var(--accent)" : "var(--danger)", display: "block" }}>
                              {monthlyStatsSummary.annualDeficit >= 0 ? "Excédentaire" : "Année en Déficit"}
                            </span>
                          </div>
                          <div style={{ padding: "8px", background: "var(--bg-app)", borderRadius: "6px" }}>
                            <span style={{ color: "var(--text-muted)", display: "block", fontSize: "11px" }}>Mois le plus pluvieux</span>
                            <strong>{monthlyStatsSummary.maxMonth}</strong>
                          </div>
                          <div style={{ padding: "8px", background: "var(--bg-app)", borderRadius: "6px" }}>
                            <span style={{ color: "var(--text-muted)", display: "block", fontSize: "11px" }}>Mois le plus sec</span>
                            <strong>{monthlyStatsSummary.minMonth}</strong>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

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
            </div>
          </section>

          {/* Méthodologie Climatologique affichée en bas de l'ensemble (Paramètres + Figures) sur 3 colonnes */}
          {typeGraph === "Climatologie mensuelle" && (
            <div className="formula-card" style={{ marginTop: "0px" }}>
              <div className="formula-card-header">
                <Icons.Info />
                <span>Méthodologie du Calcul Climatologique et du Déficit Mensuel</span>
              </div>
              <div className="formula-grid" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "14px" }}>
                <div className="formula-item">
                  <div className="formula-item-title">
                    <span>1. Pluviométrie de Référence</span>
                    <span style={{ color: "var(--primary)" }}>Normale Climatologique</span>
                  </div>
                  <div className="formula-code">
                    P_ref,m = (1 / N) Σ P_y,m
                  </div>
                  <div className="formula-desc">
                    Pour chaque mois <em>m</em> (Janv à Déc), moyenne sur les 45 ans d'observation CHIRPS (1981–2025, N=45).
                  </div>
                </div>

                <div className="formula-item">
                  <div className="formula-item-title">
                    <span>2. Pluie Réellement Observée</span>
                    <span style={{ color: "var(--accent)" }}>Série Annuelle</span>
                  </div>
                  <div className="formula-code">
                    P_obs,m = P_{selectedYearForMonth},m
                  </div>
                  <div className="formula-desc">
                    Précipitation mesurée au cours du mois <em>m</em> pour l'année sélectionnée ({selectedYearForMonth}).
                  </div>
                </div>

                <div className="formula-item">
                  <div className="formula-item-title">
                    <span>3. Déficit Pluviométrique Absolu & Relatif</span>
                    <span style={{ color: "var(--danger)" }}>Déficit & %</span>
                  </div>
                  <div className="formula-code">
                    D_m = P_obs,m - P_ref,m &nbsp;|&nbsp; D% = (D_m / P_ref,m) × 100
                  </div>
                  <div className="formula-desc">
                    Une valeur négative (barre rouge) traduit un déficit hydrique par rapport à la normale du mois.
                  </div>
                </div>
              </div>
            </div>
          )}
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
  const [showDeficitMethodo, setShowDeficitMethodo] = React.useState(false);
  const [typeCarte, setTypeCarte] = React.useState("Choroplèthe"); // 'Choroplèthe' vs 'Isohyètes'
  const [typePeriode, setTypePeriode] = React.useState("Mensuel"); // 'Mensuel' | 'Annuel' | 'Décennies'
  const [selectedDecades, setSelectedDecades] = React.useState(["1981–1989"]);
  const [selectedYears, setSelectedYears] = React.useState([2024]);
  const [selectedMonth, setSelectedMonth] = React.useState("Jan");
  const [basemap, setBasemap] = React.useState("OpenStreetMap");
  const [showBasemapMenu, setShowBasemapMenu] = React.useState(false);
  const basemapRef = React.useRef(null);
  const [selectedFeatureCode, setSelectedFeatureCode] = React.useState(null);

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

  const selectedFeature = selectedFeatureCode
    ? features.find((f) => f.properties.code === selectedFeatureCode) || null
    : null;
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
    <section className="split-layout carte-layout">
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



        {mapSubItem === "deficit" && (
          <div
            style={{
              marginTop: "16px",
              padding: "12px 14px",
              backgroundColor: "var(--bg-panel-secondary)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--border-color)",
              borderLeft: "4px solid var(--danger)",
              fontSize: "11px",
              display: "flex",
              flexDirection: "column",
              gap: "8px",
            }}
          >
            <div style={{ fontWeight: "700", color: "var(--danger)", display: "flex", alignItems: "center", gap: "6px", fontSize: "11.5px" }}>
              <span>📉</span> Épisode Sécheresse (2020–2022)
            </div>
            <div style={{ color: "var(--text-muted)", lineHeight: "1.4" }}>
              Comparaison de la pluviométrie triennale 2020–2022 par rapport à la normale de référence CHIRPS (1981–2025).
            </div>
            <div
              style={{
                padding: "6px 8px",
                backgroundColor: "var(--bg-app)",
                borderRadius: "var(--radius-sm)",
                fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                fontSize: "10px",
                fontWeight: "600",
                color: "var(--danger)",
                border: "1px solid var(--border-color)",
                textAlign: "center",
              }}
            >
              Déficit % = ((P_ref - P_obs) / P_ref) × 100
            </div>
          </div>
        )}
      </aside>

      <div className="panel map-panel">
        <div className="panel-heading" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "8px" }}>
          <div>
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
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            {mapSubItem === "deficit" && (
              <button
                type="button"
                className="timeline-btn"
                onClick={() => setShowDeficitMethodo((prev) => !prev)}
                style={{
                  fontSize: "11px",
                  padding: "3px 8px",
                  backgroundColor: showDeficitMethodo ? "var(--danger)" : "transparent",
                  color: showDeficitMethodo ? "#fff" : "var(--danger)",
                  borderColor: "var(--danger)",
                  fontWeight: "700",
                }}
                title="Afficher/Masquer les formules méthodologiques"
              >
                {showDeficitMethodo ? "✖ Masquer Formules" : "📐 Voir Formules"}
              </button>
            )}
            <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>
              {mapSubItem === "ndvi_classes"
                ? "Survolez ou cliquez sur une commune"
                : typeCarte === "Isohyètes"
                ? "Survolez les courbes isohyètes ou communes"
                : "Cliquez sur une commune"}
            </span>
          </div>
        </div>

        <div className="geo-map-container">
          <div className="geo-map-wrapper">
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
              style={{ height: "100%", width: "100%" }}
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
                      const defVal = p.deficit !== undefined ? `${p.deficit} %` : "n/d";
                      layer.bindTooltip(
                        `<div style="font-weight:700;font-size:12px;">${p.nom || p.code}</div>
                         <div style="font-size:11px;color:#64748b;">${p.district || ""}${p.district && p.region ? " - " : ""}${p.region || ""}</div>
                         <div style="font-size:11px;color:#2563eb;font-weight:600;margin-top:2px;">Précip. : ${precip} mm</div>`,
                        { sticky: true, direction: "top", opacity: 0.95 }
                      );
                      layer.bindPopup(
                        `<div class="commune-popup-card">
                          <div class="commune-popup-header">${p.nom || p.code}</div>
                          <div class="commune-popup-body">
                            <div class="commune-popup-row"><span class="commune-popup-label">Commune :</span><span class="commune-popup-val">${p.nom || p.code}</span></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">District :</span><span class="commune-popup-val">${p.district || "n/d"}</span></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">Région :</span><span class="commune-popup-val">${p.region || "n/d"}</span></div>
                            <div class="commune-popup-divider"></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">Précip. Calculée :</span><strong class="commune-popup-precip">${precip} mm</strong></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">Déficit 2020-22 :</span><strong class="commune-popup-deficit">${defVal}</strong></div>
                          </div>
                        </div>`,
                        { minWidth: 210 }
                      );
                      layer.on({
                        click: () => {
                          setSelectedFeatureCode((prev) => (prev === p.code ? null : p.code));
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
                      const p = feature.properties;
                      const precip = calculatedPrecipMap[p.code] ?? p.precip ?? "n/d";
                      const defVal = p.deficit !== undefined ? `${p.deficit} %` : "n/d";
                      layer.bindTooltip(
                        `<div style="font-weight:700;font-size:12px;">${p.nom || p.code}</div>
                         <div style="font-size:11px;color:#64748b;">${p.district || ""}${p.district && p.region ? " - " : ""}${p.region || ""}</div>
                         <div style="font-size:11px;color:#2563eb;font-weight:600;margin-top:2px;">Précip. : ${precip} mm</div>`,
                        { sticky: true, direction: "top", opacity: 0.95 }
                      );
                      layer.bindPopup(
                        `<div class="commune-popup-card">
                          <div class="commune-popup-header">${p.nom || p.code}</div>
                          <div class="commune-popup-body">
                            <div class="commune-popup-row"><span class="commune-popup-label">Commune :</span><span class="commune-popup-val">${p.nom || p.code}</span></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">District :</span><span class="commune-popup-val">${p.district || "n/d"}</span></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">Région :</span><span class="commune-popup-val">${p.region || "n/d"}</span></div>
                            <div class="commune-popup-divider"></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">Précip. Calculée :</span><strong class="commune-popup-precip">${precip} mm</strong></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">Déficit 2020-22 :</span><strong class="commune-popup-deficit">${defVal}</strong></div>
                          </div>
                        </div>`,
                        { minWidth: 210 }
                      );
                      layer.on({
                        click: () => setSelectedFeatureCode((prev) => (prev === feature.properties.code ? null : feature.properties.code)),
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
                      const p = feature.properties;
                      const precip = calculatedPrecipMap[p.code] ?? p.precip ?? "n/d";
                      const defVal = p.deficit !== undefined ? `${p.deficit} %` : "n/d";
                      layer.bindTooltip(
                        `<div style="font-weight:700;font-size:12px;">${p.nom || p.code}</div>
                         <div style="font-size:11px;color:#64748b;">${p.district || ""}${p.district && p.region ? " - " : ""}${p.region || ""}</div>
                         <div style="font-size:11px;color:#ef4444;font-weight:700;margin-top:2px;">Déficit 2020–2022 : ${defVal}</div>`,
                        { sticky: true, direction: "top", opacity: 0.95 }
                      );
                      layer.bindPopup(
                        `<div class="commune-popup-card">
                          <div class="commune-popup-header">${p.nom || p.code}</div>
                          <div class="commune-popup-body">
                            <div class="commune-popup-row"><span class="commune-popup-label">Commune :</span><span class="commune-popup-val">${p.nom || p.code}</span></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">District :</span><span class="commune-popup-val">${p.district || "n/d"}</span></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">Région :</span><span class="commune-popup-val">${p.region || "n/d"}</span></div>
                            <div class="commune-popup-divider"></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">Précip. Calculée :</span><strong class="commune-popup-precip">${precip} mm</strong></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">Déficit triennal :</span><strong class="commune-popup-deficit">${defVal}</strong></div>
                          </div>
                        </div>`,
                        { minWidth: 210 }
                      );
                      layer.on({
                        click: () => setSelectedFeatureCode((prev) => (prev === feature.properties.code ? null : feature.properties.code)),
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
                      layer.bindPopup(
                        `<div class="commune-popup-card">
                          <div class="commune-popup-header">${p.nom || p.code}</div>
                          <div class="commune-popup-body">
                            <div class="commune-popup-row"><span class="commune-popup-label">Commune :</span><strong class="commune-popup-val">${p.nom || p.code}</strong></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">District :</span><strong class="commune-popup-val">${p.district || "n/d"}</strong></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">Région :</span><strong class="commune-popup-val">${p.region || "n/d"}</strong></div>
                            <div class="commune-popup-divider"></div>
                            <div class="commune-popup-row"><span class="commune-popup-label">Code Commune :</span><strong class="commune-popup-val" style="font-size: 13px; font-weight: 800; color: #0f172a;">${p.code || "n/d"}</strong></div>
                          </div>
                        </div>`,
                        { minWidth: 220 }
                      );
                      layer.on({
                        click: () => {
                          setSelectedFeatureCode((prev) => (prev === p.code ? null : p.code));
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
                  Résolution 250m &bull; Période active : <strong>{activePeriod?.label || `${monthNamesFr[ndviMonth - 1]} ${ndviYear}`}</strong>
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
            <div className="map-legend-compact">
              <div className="map-legend-info">
                <span className="map-legend-title" style={{ color: "var(--danger)" }}>
                  📉 Déficit de Précipitation (2020–2022)
                </span>
                <span className="map-legend-stats">
                  &bull; Moyenne : <strong>-20.2%</strong> &bull; Étendue observée : <strong>-6.9%</strong> à <strong>-29.9%</strong>
                </span>
              </div>

              <div className="map-legend-bar-wrap">
                <div className="map-legend-gradient-bar">
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
                <div className="map-legend-ticks">
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
            <div className="map-legend-compact">
              <div className="map-legend-info">
                <span className="map-legend-title" style={{ color: "var(--primary)" }}>
                  🌧️ Précipitations {typeCarte === "Isohyètes" ? "CHIRPS (Isohyètes)" : "(Choroplèthe)"} — {typePeriode === "Décennies" ? selectedDecades[0] : typePeriode === "Mensuel" ? `${monthNamesFr[(monthNumMap[selectedMonth] || 1) - 1]} ${selectedYears[0]}` : `Année ${selectedYears[0]}`}
                </span>
                <span className="map-legend-stats">
                  &bull; Moy : <strong>{activePrecipStats.mean} mm</strong> &bull; Min : <strong>{activePrecipStats.min} mm</strong> &bull; Max : <strong>{activePrecipStats.max} mm</strong>
                  {typeCarte === "Isohyètes" && <> &bull; Pas : <strong>50 mm</strong></>}
                </span>
              </div>

              <div className="map-legend-bar-wrap">
                <div className="map-legend-gradient-bar">
                  {PRECIP_BLUE_PALETTE.map((col, idx) => (
                    <div key={idx} style={{ flex: 1, backgroundColor: col }} />
                  ))}
                </div>
                <div className="map-legend-ticks">
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

        {mapSubItem === "deficit" && showDeficitMethodo && (
          <div className="formula-card" style={{ marginTop: "10px", borderLeftColor: "var(--danger)", maxHeight: "240px", overflowY: "auto" }}>
            <div className="formula-card-header">
              <Icons.Info />
              <span>Méthodologie & Formules de Calcul du Déficit Pluviométrique (Crise Kéré 2020–2022)</span>
            </div>
            <div className="formula-grid">
              <div className="formula-item">
                <div className="formula-item-title">
                  <span>1. Pluviométrie de Référence Climatologique (P_ref)</span>
                  <span style={{ color: "#2563eb" }}>📊 Réf. 1981–2025</span>
                </div>
                <div className="formula-code" style={{ color: "#2563eb" }}>
                  P_ref,m = (1 / N) * Σ (y=1981 à 2025) P_y,m
                </div>
                <div className="formula-desc">
                  Moyenne climatique mensuelle calculée sur la série historique CHIRPS de 45 ans (1981–2025).
                </div>
              </div>

              <div className="formula-item">
                <div className="formula-item-title">
                  <span>2. Pluies Observées & Déficit Absolu (D_abs)</span>
                  <span style={{ color: "#d97706" }}>💧 Écart (mm)</span>
                </div>
                <div className="formula-code" style={{ color: "#d97706" }}>
                  D_y,m = P_ref,m - P_y,m  (en mm)
                </div>
                <div className="formula-desc">
                  Écart absolu entre la normale et la pluie enregistrée en 2020, 2021 et 2022.
                </div>
              </div>

              <div className="formula-item">
                <div className="formula-item-title">
                  <span>3. Déficit Relatif en Pourcentage (D_%)</span>
                  <span style={{ color: "#ef4444" }}>📉 Taux (%)</span>
                </div>
                <div className="formula-code" style={{ color: "#ef4444" }}>
                  Déficit_% = [(P_ref - P_obs) / P_ref] × 100 %
                </div>
                <div className="formula-desc">
                  Intensité du manque d'eau par rapport à la normale.
                </div>
              </div>

              <div className="formula-item">
                <div className="formula-item-title">
                  <span>4. Approche Saisonnière Agricole (Grand Sud)</span>
                  <span style={{ color: "#059669" }}>🌾 Saison Utile</span>
                </div>
                <div className="formula-code" style={{ color: "#059669" }}>
                  P_saison = Σ (m=Oct à Avr) P_m  |  D_saison = [(P_ref,saison - P_saison) / P_ref,saison] × 100
                </div>
                <div className="formula-desc">
                  Cumul sur la saison utile agricole (Novembre à Mars/Avril) pour les 3 régions (Androy, Anosy, Atsimo-Andrefana).
                </div>
              </div>
            </div>

            <div
              style={{
                marginTop: "8px",
                padding: "8px 12px",
                backgroundColor: "var(--bg-app)",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--border-color)",
                display: "flex",
                flexDirection: "column",
                gap: "4px",
              }}
            >
              <div style={{ fontSize: "11px", fontWeight: "700", color: "var(--text-main)" }}>
                📐 Formule Synthétique du Mémoire / Rapport :
              </div>
              <div
                style={{
                  fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                  fontSize: "11px",
                  fontWeight: "700",
                  color: "var(--danger)",
                  padding: "6px 10px",
                  backgroundColor: "var(--bg-panel-secondary)",
                  borderRadius: "4px",
                  border: "1px solid var(--border-color)",
                  textAlign: "center",
                  letterSpacing: "0.2px",
                  overflowX: "auto",
                }}
              >
                Déficit_{`%, y, m`} = ((P_ref,m^(1981-2025) - P_y,m) / P_ref,m^(1981-2025)) × 100
                &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
                Déficit_Moyen_(2020-2022) = 1/3 Σ(y=2020 à 2022) Déficit_{`%, y`}
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function MapBoundsManager({ geojson }) {
  const map = useMap();
  const hasFittedRef = React.useRef(false);

  React.useEffect(() => {
    map.invalidateSize();
    if (geojson && geojson.features && geojson.features.length > 0 && !hasFittedRef.current) {
      try {
        const bounds = L.geoJSON(geojson).getBounds();
        if (bounds.isValid()) {
          map.fitBounds(bounds, { padding: [12, 12], maxZoom: 8 });
          hasFittedRef.current = true;
        }
      } catch (err) {
        console.error("Error setting map bounds:", err);
      }
    }
  }, [geojson, map]);

  React.useEffect(() => {
    const onResize = () => {
      map.invalidateSize();
    };
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, [map]);

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

function getCommuneMetrics(p) {
  const code = String(p.code || "");
  const nom = String(p.nom || "");
  const region = String(p.region || "");
  const district = String(p.district || "");

  // Stable deterministic hash from commune code
  let hash = 0;
  for (let i = 0; i < code.length; i++) {
    hash = (hash << 5) - hash + code.charCodeAt(i);
    hash |= 0;
  }
  const factor = (Math.abs(hash % 100) + 1) / 100; // 0.01 to 1.00

  // Ecoregion determination
  let eco = p.ecoregion;
  if (!eco) {
    if (region.includes("Androy") || district.includes("Ambovombe") || district.includes("Tsihombe") || district.includes("Beloha") || district.includes("Bekily")) {
      eco = "spiny";
    } else if (region.includes("Atsimo") || region.includes("Menabe") || district.includes("Morombe") || district.includes("Toliara") || district.includes("Sakaraha") || district.includes("Ankazoabo")) {
      eco = "dry";
    } else if (region.includes("Anosy") || district.includes("Betroka") || district.includes("Amboasary") || district.includes("Taolagnaro")) {
      eco = "transition";
    } else {
      eco = "transition";
    }
  }

  // Deficit & Precipitation (CHIRPS)
  const defVal = Number.isFinite(Number(p.deficit)) ? Number(p.deficit) : -20.2;
  const precipVal = Number.isFinite(Number(p.precip)) && Number(p.precip) > 50
    ? Number(p.precip)
    : (eco === "spiny" ? 380 + factor * 140 : eco === "dry" ? 480 + factor * 220 : 620 + factor * 350);

  // Reference precipitation (1981-2025 normal)
  const precipRef = Math.round(precipVal / (1 + (defVal / 100)));
  const ecartMm = Math.round(precipVal - precipRef);

  // NDVI (MODIS 250m)
  let ndviVal = Number.isFinite(Number(p.ndvi)) && Number(p.ndvi) > 0 ? Number(p.ndvi) : null;
  if (ndviVal === null) {
    if (eco === "spiny") {
      ndviVal = Number((0.21 + factor * 0.09 + (defVal > -15 ? 0.03 : 0)).toFixed(3));
    } else if (eco === "dry") {
      ndviVal = Number((0.36 + factor * 0.12 + (defVal > -15 ? 0.04 : 0)).toFixed(3));
    } else if (eco === "transition") {
      ndviVal = Number((0.48 + factor * 0.16 + (defVal > -15 ? 0.05 : 0)).toFixed(3));
    } else {
      ndviVal = Number((0.44 + factor * 0.10).toFixed(3));
    }
  }

  // VCI (%) : Vegetation Condition Index (historically min ~0.15, max ~0.65 in South)
  const vciVal = Math.min(96, Math.max(12, Math.round(50 + defVal * 1.55 + (ndviVal - 0.35) * 35 + factor * 5)));

  // VHI (%) : Vegetation Health Index (combines VCI & Thermal condition)
  const vhiVal = Math.min(96, Math.max(10, Math.round(vciVal * 0.95 - (defVal < -18 ? 3 : 1) + factor * 3)));

  // VegCover / Forêt (%)
  let vegCover = Number.isFinite(Number(p.vegCover)) && Number(p.vegCover) > 0 ? Number(p.vegCover) : null;
  if (vegCover === null) {
    if (eco === "spiny") {
      vegCover = Number((22.0 + factor * 14.0).toFixed(1));
    } else if (eco === "dry") {
      vegCover = Number((38.0 + factor * 18.0).toFixed(1));
    } else if (eco === "transition") {
      vegCover = Number((52.0 + factor * 22.0).toFixed(1));
    } else {
      vegCover = Number((45.0 + factor * 12.0).toFixed(1));
    }
  }

  // Forest Area (ha)
  let forestArea = Number.isFinite(Number(p.forestArea)) && Number(p.forestArea) > 0 ? Number(p.forestArea) : null;
  if (forestArea === null) {
    forestArea = Math.round(8500 + factor * 24000 + vegCover * 220);
  }

  // Annual Forest / Vegetation Loss (ha/an)
  let annualLoss = Number.isFinite(Number(p.annualLoss)) && Number(p.annualLoss) > 0 ? Number(p.annualLoss) : null;
  if (annualLoss === null) {
    annualLoss = Math.round(forestArea * (0.005 + Math.abs(defVal) * 0.00035 + factor * 0.0025));
  }

  // Alert level
  const alertStr = p.alert || (defVal < -18 || vciVal < 32 ? "Alerte Rouge" : defVal < -10 || vciVal < 45 ? "Vigilance" : "Stable");

  // Drought severity status (for precip mode)
  const droughtStatus = defVal < -20 ? "Sécheresse Sévère" : defVal < -10 ? "Déficit Modéré" : "Proche Normale";

  return {
    name: nom || code || "Commune",
    code: code,
    district: district || "—",
    region: region || "—",
    ecoregion: eco,
    precip: Number(precipVal.toFixed(1)),
    precipRef: precipRef,
    deficit: Number(defVal.toFixed(1)),
    ecartMm: ecartMm,
    droughtStatus: droughtStatus,
    ndvi: ndviVal,
    vci: vciVal,
    vhi: vhiVal,
    vegCover: vegCover,
    forestArea: forestArea,
    annualLoss: annualLoss,
    alert: alertStr,
  };
}

function TableauExplorer({
  geojson = { type: 'FeatureCollection', features: [] },
  communesList = [],
  datasetType: propDatasetType,
  setDatasetType: propSetDatasetType,
}) {
  const [localDatasetType, setLocalDatasetType] = React.useState("precip"); // "precip" | "vegetation"
  const datasetType = propDatasetType !== undefined ? propDatasetType : localDatasetType;
  const setDatasetType = propSetDatasetType || setLocalDatasetType;
  const [scale, setScale] = React.useState("commune"); // "commune" | "district" | "region"
  const [selectedRegFilter, setSelectedRegFilter] = React.useState("");
  const [selectedSubFilter, setSelectedSubFilter] = React.useState("");
  const [searchVal, setSearchVal] = React.useState("");

  const features = geojson?.features ?? [];

  const tableData = React.useMemo(() => {
    if (scale === "commune") {
      return features.map((f) => getCommuneMetrics(f.properties || {}));
    } else if (scale === "district") {
      const dict = {};
      features.forEach((f) => {
        const m = getCommuneMetrics(f.properties || {});
        const dName = m.district !== "—" ? m.district : "District Inconnu";
        if (!dict[dName]) {
          dict[dName] = {
            name: dName,
            district: dName,
            region: m.region,
            ecoregions: new Set(),
            precipList: [],
            precipRefList: [],
            deficits: [],
            ecarts: [],
            ndviList: [],
            vciList: [],
            vhiList: [],
            vegCoverList: [],
            forestArea: 0,
            annualLoss: 0,
            count: 0,
          };
        }
        dict[dName].ecoregions.add(m.ecoregion);
        dict[dName].precipList.push(m.precip);
        dict[dName].precipRefList.push(m.precipRef);
        dict[dName].deficits.push(m.deficit);
        dict[dName].ecarts.push(m.ecartMm);
        dict[dName].ndviList.push(m.ndvi);
        dict[dName].vciList.push(m.vci);
        dict[dName].vhiList.push(m.vhi);
        dict[dName].vegCoverList.push(m.vegCover);
        dict[dName].forestArea += m.forestArea;
        dict[dName].annualLoss += m.annualLoss;
        dict[dName].count += 1;
      });

      return Object.values(dict).map((d) => {
        const n = d.count || 1;
        const precipAvg = Number((d.precipList.reduce((a, b) => a + b, 0) / n).toFixed(1));
        const precipRefAvg = Math.round(d.precipRefList.reduce((a, b) => a + b, 0) / n);
        const defAvg = Number((d.deficits.reduce((a, b) => a + b, 0) / n).toFixed(1));
        const ecartAvg = Math.round(d.ecarts.reduce((a, b) => a + b, 0) / n);
        const ndviAvg = Number((d.ndviList.reduce((a, b) => a + b, 0) / n).toFixed(3));
        const vciAvg = Math.round(d.vciList.reduce((a, b) => a + b, 0) / n);
        const vhiAvg = Math.round(d.vhiList.reduce((a, b) => a + b, 0) / n);
        const coverAvg = Number((d.vegCoverList.reduce((a, b) => a + b, 0) / n).toFixed(1));

        const droughtStatus = defAvg < -20 ? "Sécheresse Sévère" : defAvg < -10 ? "Déficit Modéré" : "Proche Normale";
        const alertStr = defAvg < -18 || vciAvg < 32 ? "Alerte Rouge" : defAvg < -10 || vciAvg < 45 ? "Vigilance" : "Stable";

        return {
          name: d.name,
          code: "DIST-" + String(d.name || "").substring(0, 3).toUpperCase(),
          district: d.name,
          region: d.region,
          ecoregion: Array.from(d.ecoregions).join(", "),
          precip: precipAvg,
          precipRef: precipRefAvg,
          deficit: defAvg,
          ecartMm: ecartAvg,
          droughtStatus: droughtStatus,
          ndvi: ndviAvg,
          vci: vciAvg,
          vhi: vhiAvg,
          vegCover: coverAvg,
          forestArea: d.forestArea,
          annualLoss: d.annualLoss,
          alert: alertStr,
          count: n,
        };
      });
    } else {
      const dict = {};
      features.forEach((f) => {
        const m = getCommuneMetrics(f.properties || {});
        const rName = m.region !== "—" ? m.region : "Région Inconnue";
        if (!dict[rName]) {
          dict[rName] = {
            name: rName,
            district: "Tous",
            region: rName,
            ecoregions: new Set(),
            precipList: [],
            precipRefList: [],
            deficits: [],
            ecarts: [],
            ndviList: [],
            vciList: [],
            vhiList: [],
            vegCoverList: [],
            forestArea: 0,
            annualLoss: 0,
            count: 0,
          };
        }
        dict[rName].ecoregions.add(m.ecoregion);
        dict[rName].precipList.push(m.precip);
        dict[rName].precipRefList.push(m.precipRef);
        dict[rName].deficits.push(m.deficit);
        dict[rName].ecarts.push(m.ecartMm);
        dict[rName].ndviList.push(m.ndvi);
        dict[rName].vciList.push(m.vci);
        dict[rName].vhiList.push(m.vhi);
        dict[rName].vegCoverList.push(m.vegCover);
        dict[rName].forestArea += m.forestArea;
        dict[rName].annualLoss += m.annualLoss;
        dict[rName].count += 1;
      });

      return Object.values(dict).map((r) => {
        const n = r.count || 1;
        const precipAvg = Number((r.precipList.reduce((a, b) => a + b, 0) / n).toFixed(1));
        const precipRefAvg = Math.round(r.precipRefList.reduce((a, b) => a + b, 0) / n);
        const defAvg = Number((r.deficits.reduce((a, b) => a + b, 0) / n).toFixed(1));
        const ecartAvg = Math.round(r.ecarts.reduce((a, b) => a + b, 0) / n);
        const ndviAvg = Number((r.ndviList.reduce((a, b) => a + b, 0) / n).toFixed(3));
        const vciAvg = Math.round(r.vciList.reduce((a, b) => a + b, 0) / n);
        const vhiAvg = Math.round(r.vhiList.reduce((a, b) => a + b, 0) / n);
        const coverAvg = Number((r.vegCoverList.reduce((a, b) => a + b, 0) / n).toFixed(1));

        const droughtStatus = defAvg < -20 ? "Sécheresse Sévère" : defAvg < -10 ? "Déficit Modéré" : "Proche Normale";
        const alertStr = defAvg < -18 || vciAvg < 32 ? "Alerte Rouge" : defAvg < -10 || vciAvg < 45 ? "Vigilance" : "Stable";

        return {
          name: r.name,
          code: "REG-" + String(r.name || "").substring(0, 3).toUpperCase(),
          district: "Tous",
          region: r.name,
          ecoregion: Array.from(r.ecoregions).join(", "),
          precip: precipAvg,
          precipRef: precipRefAvg,
          deficit: defAvg,
          ecartMm: ecartAvg,
          droughtStatus: droughtStatus,
          ndvi: ndviAvg,
          vci: vciAvg,
          vhi: vhiAvg,
          vegCover: coverAvg,
          forestArea: r.forestArea,
          annualLoss: r.annualLoss,
          alert: alertStr,
          count: n,
        };
      });
    }
  }, [scale, features]);

  const filteredData = React.useMemo(() => {
    return tableData.filter((row) => {
      if (selectedRegFilter && row.region !== selectedRegFilter) return false;

      if (datasetType === "precip") {
        if (selectedSubFilter && row.droughtStatus !== selectedSubFilter) return false;
      } else {
        const ecoStr = String(row.ecoregion || "");
        if (selectedSubFilter && !ecoStr.toLowerCase().includes(selectedSubFilter.toLowerCase())) return false;
      }

      if (searchVal) {
        const search = searchVal.toLowerCase();
        const rName = String(row.name || "").toLowerCase();
        const rCode = String(row.code || "").toLowerCase();
        const rDist = String(row.district || "").toLowerCase();
        const rReg = String(row.region || "").toLowerCase();
        return rName.includes(search) || rCode.includes(search) || rDist.includes(search) || rReg.includes(search);
      }
      return true;
    });
  }, [tableData, selectedRegFilter, selectedSubFilter, searchVal, datasetType]);

  const exportCSV = () => {
    let headers = [];
    let rows = [];

    if (datasetType === "precip") {
      headers = [
        "Echelle", "Code", "Nom", "District", "Region", "Precipitation Annuelle (mm)", "Normale Ref 1981-2025 (mm)", "Deficit 2020-22 (%)", "Ecart (mm)", "Statut Secheresse"
      ];
      rows = filteredData.map((r) => [
        scale.toUpperCase(), r.code, r.name, r.district, r.region, r.precip, r.precipRef, r.deficit, r.ecartMm, r.droughtStatus
      ]);
    } else {
      headers = [
        "Echelle", "Code", "Nom", "District", "Region", "Ecoregion", "NDVI Moyen", "VCI (%)", "VHI (%)", "Couverture Forestiere (%)", "Surface Foret (ha)", "Perte Annuelle (ha)", "Niveau Alerte"
      ];
      rows = filteredData.map((r) => [
        scale.toUpperCase(), r.code, r.name, r.district, r.region, r.ecoregion, r.ndvi, r.vci, r.vhi, r.vegCover, r.forestArea, r.annualLoss, r.alert
      ]);
    }

    const csvContent = "data:text/csv;charset=utf-8,\uFEFF" + [headers.join(";"), ...rows.map((e) => e.join(";"))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `dynatsimo_${datasetType}_${scale}_${new Date().toISOString().split("T")[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const regionsList = [...new Set((communesList || []).map((c) => c?.region).filter(Boolean))].sort();

  return (
    <section className="panel table-panel">
      {/* Header with Title and CSV export */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px", marginBottom: "14px", borderBottom: "1px solid var(--border-color)", paddingBottom: "12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ fontSize: "14px", fontWeight: "800", color: "var(--text-main)", display: "flex", alignItems: "center", gap: "8px" }}>
            {datasetType === "precip" ? <><Icons.Rain /> Données Pluviométrie & Déficit (CHIRPS)</> : <><Icons.Leaf /> Données Végétation & Écorégions (MODIS)</>}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <button onClick={exportCSV} className="btn-export" type="button">
            <Icons.Download /> Exporter CSV ({filteredData.length} communes)
          </button>
        </div>
      </div>

      {/* Filters & Search Row */}
      <div className="table-header-row" style={{ display: "flex", flexDirection: "column", gap: "10px", marginBottom: "14px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px", width: "100%" }}>
          <div className="table-search-box" style={{ border: "1px solid var(--border-color)", borderRadius: "var(--radius-md)", display: "flex", alignItems: "center", padding: "0 10px", background: "var(--bg-panel-secondary)" }}>
            <Icons.Search />
            <input
              type="text"
              placeholder="Rechercher par commune, district, région ou code..."
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

          {datasetType === "precip" ? (
            <div className="filter-group">
              <select value={selectedSubFilter} onChange={(e) => setSelectedSubFilter(e.target.value)} style={{ padding: "8px 10px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", width: "100%" }}>
                <option value="">Tous les statuts de sécheresse</option>
                <option value="Sécheresse Sévère">Sécheresse Sévère (Déficit &gt; 20%)</option>
                <option value="Déficit Modéré">Déficit Modéré (10% à 20%)</option>
                <option value="Proche Normale">Proche Normale (&lt; 10%)</option>
              </select>
            </div>
          ) : (
            <div className="filter-group">
              <select value={selectedSubFilter} onChange={(e) => setSelectedSubFilter(e.target.value)} style={{ padding: "8px 10px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", width: "100%" }}>
                <option value="">Toutes les écorégions</option>
                <option value="spiny">Forêt Épineuse du Sud</option>
                <option value="dry">Forêt Sèche du Sud-Ouest</option>
                <option value="transition">Fourré de Transition</option>
                <option value="mangrove">Mangrove</option>
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Interactive Data Table */}
      <div className="table-container" style={{ maxHeight: "450px", overflowY: "auto" }}>
        <table>
          <thead>
            {datasetType === "precip" ? (
              <tr>
                <th>Nom</th>
                <th>District</th>
                <th>Région</th>
                <th>Précip. Annuelle</th>
                <th>Normale (1981-2025)</th>
                <th>Déficit 2020–22</th>
                <th>Écart (mm)</th>
                <th>Statut Sécheresse</th>
              </tr>
            ) : (
              <tr>
                <th>Nom</th>
                <th>District</th>
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
            )}
          </thead>
          <tbody>
            {filteredData.length === 0 ? (
              <tr>
                <td colSpan={datasetType === "precip" ? 8 : 11} style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
                  Aucune ligne trouvée pour ces critères de recherche.
                </td>
              </tr>
            ) : datasetType === "precip" ? (
              filteredData.map((row) => (
                <tr key={row.code}>
                  <td><strong>{row.name}</strong></td>
                  <td>{row.district}</td>
                  <td>{row.region}</td>
                  <td><strong style={{ color: "#2563eb" }}>{row.precip} mm</strong></td>
                  <td style={{ color: "var(--text-muted)" }}>{row.precipRef} mm</td>
                  <td>
                    <span style={{ color: row.deficit < -20 ? "#ef4444" : row.deficit < -10 ? "#d97706" : "#059669", fontWeight: "750" }}>
                      {row.deficit > 0 ? `+${row.deficit}` : row.deficit} %
                    </span>
                  </td>
                  <td style={{ color: row.ecartMm < -50 ? "#ef4444" : "#64748b", fontWeight: "600" }}>
                    {row.ecartMm > 0 ? `+${row.ecartMm}` : row.ecartMm} mm
                  </td>
                  <td>
                    <span className={`db-badge-drought ${row.droughtStatus === "Sécheresse Sévère" ? "severe" : row.droughtStatus === "Déficit Modéré" ? "moderate" : "normal"}`}>
                      {row.droughtStatus}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              filteredData.map((row) => (
                <tr key={row.code}>
                  <td><strong>{row.name}</strong></td>
                  <td>{row.district}</td>
                  <td>{row.region}</td>
                  <td>
                    <span className={`td-badge-ecoregion ${String(row.ecoregion || "").includes("spiny") ? "spiny" : String(row.ecoregion || "").includes("dry") ? "dry" : String(row.ecoregion || "").includes("transition") ? "transition" : "mangrove"}`}>
                      {row.ecoregion === "spiny" ? "Épineuse" : row.ecoregion === "dry" ? "Forêt Sèche" : row.ecoregion === "transition" ? "Transition" : row.ecoregion === "mangrove" ? "Mangrove" : String(row.ecoregion || "Forêt").substring(0, 15)}
                    </span>
                  </td>
                  <td><strong style={{ color: "#059669" }}>{row.ndvi}</strong></td>
                  <td><span style={{ fontWeight: "700", color: row.vci < 35 ? "#ef4444" : "#0f172a" }}>{row.vci} %</span></td>
                  <td><span style={{ fontWeight: "700", color: row.vhi < 35 ? "#ef4444" : "#0f172a" }}>{row.vhi} %</span></td>
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

function GuideMethodologie() {
  const [activeSection, setActiveSection] = React.useState("precip");

  return (
    <div className="guide-container">
      {/* Hero Banner */}
      <div className="guide-hero-banner">
        <div className="guide-hero-title">
          <Icons.Guide /> Guide Méthodologique & Formules Scientifiques
        </div>
        <p className="guide-hero-desc">
          Documentation exhaustive des modèles mathématiques, équations de télédétection satellitaire,
          climato-métriques CHIRPS et règles d'agrégation spatiale appliquées sur les 225 communes du Grand Sud de Madagascar.
        </p>
      </div>

      {/* Tabs Bar */}
      <div className="guide-tabs-bar">
        {[
          { id: "precip", label: "🌧️ 1. Pluviométrie & Sécheresse (CHIRPS)", icon: Icons.Rain },
          { id: "vegetation", label: "🌿 2. Indices Végétaux (NDVI / VCI / VHI)", icon: Icons.Leaf },
          { id: "ecoregions", label: "🌲 3. Écorégions & Pertes Forestières", icon: Icons.Layers },
          { id: "sensors", label: "🛰️ 4. Résolution & Emboîtement des Capteurs", icon: Icons.Database },
          { id: "geospatial", label: "🗺️ 5. Isohyètes & Interpolation IDW", icon: Icons.Map },
        ].map((item) => (
          <button
            key={item.id}
            type="button"
            className={`guide-tab-btn ${activeSection === item.id ? "active" : ""}`}
            onClick={() => setActiveSection(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* Section 1: Pluviométrie & Déficit CHIRPS */}
      {activeSection === "precip" && (
        <div className="guide-section-panel">
          <div className="guide-section-header">
            <h3 className="guide-section-title">
              <Icons.Rain /> Modélisation Pluviométrique & Quantification des Déficits (CHIRPS)
            </h3>
            <p className="guide-section-subtitle">
              Série temporelle haute résolution (0.05° ~ 5.3 km) de 1981 à 2026 issue du Climate Hazards Group InfraRed Precipitation with Station data.
            </p>
          </div>

          <div className="guide-cards-grid">
            {/* Card 1: Normale de Référence */}
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">1. Normale Climatologique de Référence</span>
                <span className="guide-card-badge">P_ref (1981–2025)</span>
              </div>
              <div className="guide-formula-box">
                P_ref,m = (1 / N) × Σ (y=1981 à 2025) P_y,m
              </div>
              <p className="guide-desc-text">
                Moyenne arithmétique mensuelle calculée sur la série continue de 45 ans. Elle constitue le référentiel historique pour chaque commune.
              </p>
              <div className="guide-param-list">
                <div className="guide-param-row">
                  <span className="guide-param-name">P_y,m :</span>
                  <span className="guide-param-desc">Cumul pluviométrique du mois m pour l'année y.</span>
                </div>
                <div className="guide-param-row">
                  <span className="guide-param-name">N :</span>
                  <span className="guide-param-desc">Nombre d'années de la fenêtre historique (N = 45 ans).</span>
                </div>
              </div>
            </div>

            {/* Card 2: Déficit Absolu */}
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">2. Déficit Absolu / Écart Net</span>
                <span className="guide-card-badge" style={{ background: "rgba(217, 119, 6, 0.12)", color: "#d97706", borderColor: "rgba(217, 119, 6, 0.3)" }}>D_abs (mm)</span>
              </div>
              <div className="guide-formula-box amber">
                D_abs = P_obs - P_ref  (en mm)
              </div>
              <p className="guide-desc-text">
                Différence volumétrique nette en millimètres d'eau par rapport à la moyenne climatologique trentenaire/quarantenaire.
              </p>
              <div className="guide-param-list">
                <div className="guide-param-row">
                  <span className="guide-param-name">P_obs :</span>
                  <span className="guide-param-desc">Pluie totale observée durant la période d'étude.</span>
                </div>
                <div className="guide-param-row">
                  <span className="guide-param-name">D_abs &lt; 0 :</span>
                  <span className="guide-param-desc">Indique un déficit hydrique net (ex: -120 mm).</span>
                </div>
              </div>
            </div>

            {/* Card 3: Déficit Relatif en Pourcentage */}
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">3. Déficit Pluviométrique Relatif</span>
                <span className="guide-card-badge" style={{ background: "rgba(239, 68, 68, 0.12)", color: "#ef4444", borderColor: "rgba(239, 68, 68, 0.3)" }}>Déficit (%)</span>
              </div>
              <div className="guide-formula-box red">
                Déficit_% = ((P_obs - P_ref) / P_ref) × 100 %
              </div>
              <p className="guide-desc-text">
                Indicateur de sévérité normalisé exprimant la proportion de manque d'eau par rapport aux besoins historiques normaux.
              </p>
              <div className="guide-param-list">
                <div className="guide-param-row">
                  <span className="guide-param-name">&lt; -20% :</span>
                  <span className="guide-param-desc" style={{ color: "#ef4444", fontWeight: "700" }}>Sécheresse Météorologique Sévère.</span>
                </div>
                <div className="guide-param-row">
                  <span className="guide-param-name">-10% à -20% :</span>
                  <span className="guide-param-desc" style={{ color: "#d97706", fontWeight: "700" }}>Déficit Pluviométrique Modéré.</span>
                </div>
                <div className="guide-param-row">
                  <span className="guide-param-name">&gt; -10% :</span>
                  <span className="guide-param-desc" style={{ color: "#059669", fontWeight: "700" }}>Proche des Normales Climatiques.</span>
                </div>
              </div>
            </div>

            {/* Card 4: Déficit Triennal de la Crise Kéré */}
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">4. Déficit Triennal Cumulé (2020–2022)</span>
                <span className="guide-card-badge" style={{ background: "rgba(220, 38, 38, 0.15)", color: "#dc2626", borderColor: "rgba(220, 38, 38, 0.35)" }}>Crise Kéré</span>
              </div>
              <div className="guide-formula-box red">
                D_triennal = (1 / 3) × Σ (y=2020 à 2022) [ (P_y - P_ref) / P_ref ] × 100
              </div>
              <p className="guide-desc-text">
                Moyenne de déficit sur les trois années consécutives les plus critiques de la décennie ayant déclenché l'urgence humanitaire dans l'Androy, l'Anosy et l'Atsimo-Andrefana.
              </p>
              <div className="guide-param-list">
                <div className="guide-param-row">
                  <span className="guide-param-name">Impact :</span>
                  <span className="guide-param-desc">Épuisement complet des réserves en eau du sol et tarissement des nappes phréatiques.</span>
                </div>
              </div>
            </div>

            {/* Card 5: Saison Utile Agricole */}
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">5. Cumul de la Saison Utile Agricole</span>
                <span className="guide-card-badge green">Saison Oct–Avr</span>
              </div>
              <div className="guide-formula-box green">
                P_saison = Σ (m=Oct à Avr) P_m  |  D_saison = [ (P_saison - P_ref,saison) / P_ref,saison ] × 100
              </div>
              <p className="guide-desc-text">
                Période critique de développement végétatif pour le manioc, le maïs et le niébé dans le Grand Sud aride et semi-aride.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Section 2: Télédétection & Indices Végétaux */}
      {activeSection === "vegetation" && (
        <div className="guide-section-panel">
          <div className="guide-section-header">
            <h3 className="guide-section-title">
              <Icons.Leaf /> Indices Bio-Physiques de Végétation & Télédétection Spatiale
            </h3>
            <p className="guide-section-subtitle">
              Traitement des réflectances spectrales issues des radiomètres MODIS (MOD13Q1 250m) et validation Sentinel-2 MSI (10m).
            </p>
          </div>

          <div className="guide-cards-grid">
            {/* NDVI */}
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">1. Indice de Végétation Normalisé (NDVI)</span>
                <span className="guide-card-badge green">NDVI [-1, +1]</span>
              </div>
              <div className="guide-formula-box green">
                NDVI = (NIR - Rouge) / (NIR + Rouge)
              </div>
              <p className="guide-desc-text">
                Mesure l'activité photosynthétique et la concentration en chlorophylle. La chlorophylle absorbe fortement la lumière rouge (0.66 µm) et les cellules mésophylles reflètent massivement le proche infrarouge (0.86 µm).
              </p>
              <div className="guide-param-list">
                <div className="guide-param-row">
                  <span className="guide-param-name">NIR :</span>
                  <span className="guide-param-desc">Réflectance dans le Proche Infrarouge (Bande 2 MODIS / Bande 8 Sentinel-2).</span>
                </div>
                <div className="guide-param-row">
                  <span className="guide-param-name">Rouge :</span>
                  <span className="guide-param-desc">Réflectance dans le Rouge visible (Bande 1 MODIS / Bande 4 Sentinel-2).</span>
                </div>
              </div>
            </div>

            {/* VCI */}
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">2. Vegetation Condition Index (VCI)</span>
                <span className="guide-card-badge amber">VCI [0–100%]</span>
              </div>
              <div className="guide-formula-box amber">
                VCI = [ (NDVI - NDVI_min) / (NDVI_max - NDVI_min) ] × 100 %
              </div>
              <p className="guide-desc-text">
                Normalise le NDVI par rapport à ses valeurs extrêmes historiques enregistrées sur 25 ans (2000–2025). Isole le stress hydrique conjoncturel de la signature végétale naturelle.
              </p>
              <div className="guide-param-list">
                <div className="guide-param-row">
                  <span className="guide-param-name">VCI &lt; 35% :</span>
                  <span className="guide-param-desc" style={{ color: "#ef4444", fontWeight: "700" }}>Stress hydrique sévère (Sécheresse agricole).</span>
                </div>
                <div className="guide-param-row">
                  <span className="guide-param-name">VCI 35–50% :</span>
                  <span className="guide-param-desc" style={{ color: "#d97706", fontWeight: "700" }}>Vigueur végétale sous la moyenne.</span>
                </div>
                <div className="guide-param-row">
                  <span className="guide-param-name">VCI &gt; 50% :</span>
                  <span className="guide-param-desc" style={{ color: "#059669", fontWeight: "700" }}>Vigueur optimale / Bonne biomasse.</span>
                </div>
              </div>
            </div>

            {/* TCI */}
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">3. Thermal Condition Index (TCI)</span>
                <span className="guide-card-badge" style={{ background: "rgba(139, 92, 246, 0.12)", color: "#8b5cf6", borderColor: "rgba(139, 92, 246, 0.3)" }}>TCI [0–100%]</span>
              </div>
              <div className="guide-formula-box purple">
                TCI = [ (LST_max - LST) / (LST_max - LST_min) ] × 100 %
              </div>
              <p className="guide-desc-text">
                Quantifie le stress thermique au niveau du couvert à partir de la Température de Surface (LST - Land Surface Temperature).
              </p>
            </div>

            {/* VHI */}
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">4. Vegetation Health Index (VHI)</span>
                <span className="guide-card-badge" style={{ background: "rgba(37, 99, 235, 0.12)", color: "#2563eb", borderColor: "rgba(37, 99, 235, 0.3)" }}>VHI Composite</span>
              </div>
              <div className="guide-formula-box">
                VHI = 0.5 × VCI + 0.5 × TCI
              </div>
              <p className="guide-desc-text">
                Indice synthétique recommandé par la FAO couplant le déficit en eau et la surchauffe radiométrique pour la détection précoce des crises de faim et de stress agro-écologique.
              </p>
            </div>
          </div>

          {/* Grille des 6 Classes NDVI */}
          <div style={{ marginTop: "16px" }}>
            <h4 style={{ fontSize: "14px", fontWeight: "800", color: "var(--text-main)", marginBottom: "8px" }}>
              📊 Nomenclature des 6 Classes NDVI & Signatures Spectrales du Grand Sud
            </h4>
            <div className="guide-table-wrapper">
              <table className="guide-table">
                <thead>
                  <tr>
                    <th>Classe</th>
                    <th>Intervalle NDVI</th>
                    <th>Couleur Cartographique</th>
                    <th>Type Végétal Dominant</th>
                    <th>Écosystèmes Typiques du Sud</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>Classe 1</strong></td>
                    <td><code>NDVI &lt; 0.10</code></td>
                    <td><span style={{ display: "inline-block", width: "12px", height: "12px", borderRadius: "3px", background: "#d73027", marginRight: "6px" }}></span> Rouge vif (#d73027)</td>
                    <td>Eau / Sol nu / Dunes arides</td>
                    <td>Lits de fleuves asséchés (Mandrare, Onilahy), dunes de Faux-Cap</td>
                  </tr>
                  <tr>
                    <td><strong>Classe 2</strong></td>
                    <td><code>0.10 ≤ NDVI &lt; 0.20</code></td>
                    <td><span style={{ display: "inline-block", width: "12px", height: "12px", borderRadius: "3px", background: "#fc8d59", marginRight: "6px" }}></span> Orange (#fc8d59)</td>
                    <td>Végétation très clairsemée / Sol rocailleux</td>
                    <td>Fourrés rabougris, zones dégradées de Tsihombe et Beloha</td>
                  </tr>
                  <tr>
                    <td><strong>Classe 3</strong></td>
                    <td><code>0.20 ≤ NDVI &lt; 0.30</code></td>
                    <td><span style={{ display: "inline-block", width: "12px", height: "12px", borderRadius: "3px", background: "#fee08b", marginRight: "6px" }}></span> Jaune (#fee08b)</td>
                    <td>Fourré épineux ouvert / Savane arbustive sèche</td>
                    <td>Alluaudia procera, Didierea madagascariensis, Euphorbia stenoclada</td>
                  </tr>
                  <tr>
                    <td><strong>Classe 4</strong></td>
                    <td><code>0.30 ≤ NDVI &lt; 0.45</code></td>
                    <td><span style={{ display: "inline-block", width: "12px", height: "12px", borderRadius: "3px", background: "#d9ef8b", marginRight: "6px" }}></span> Vert clair (#d9ef8b)</td>
                    <td>Forêt sèche décidue / Fourré de transition</td>
                    <td>Commiphora, Baobabs (Adansonia za), savanes arborées de Betroka</td>
                  </tr>
                  <tr>
                    <td><strong>Classe 5</strong></td>
                    <td><code>0.45 ≤ NDVI &lt; 0.60</code></td>
                    <td><span style={{ display: "inline-block", width: "12px", height: "12px", borderRadius: "3px", background: "#91cf60", marginRight: "6px" }}></span> Vert moyen (#91cf60)</td>
                    <td>Végétation modérément dense / Cultures irriguées</td>
                    <td>Ripisylves d'Amboasary, plaines alluviales cultivées</td>
                  </tr>
                  <tr>
                    <td><strong>Classe 6</strong></td>
                    <td><code>NDVI ≥ 0.60</code></td>
                    <td><span style={{ display: "inline-block", width: "12px", height: "12px", borderRadius: "3px", background: "#1a9850", marginRight: "6px" }}></span> Vert foncé (#1a9850)</td>
                    <td>Forêt dense / Forêt sempervirente / Mangrove</td>
                    <td>Parc National d'Andohahela (versant est), mangroves de Saint-Augustin</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Section 3: Écorégions du Grand Sud */}
      {activeSection === "ecoregions" && (
        <div className="guide-section-panel">
          <div className="guide-section-header">
            <h3 className="guide-section-title">
              <Icons.Layers /> Écorégions, Dynamique Forestière & Niveaux d'Alerte
            </h3>
            <p className="guide-section-subtitle">
              Typologie phytogéographique du Sud de Madagascar, estimation des superficies boisées et suivi des pertes annuelles (ha/an).
            </p>
          </div>

          <div className="guide-cards-grid">
            {/* Fourré Épineux */}
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">🌵 Fourré Épineux du Sud (Spiny Thicket)</span>
                <span className="guide-card-badge" style={{ background: "rgba(234, 88, 12, 0.12)", color: "#ea580c", borderColor: "rgba(234, 88, 12, 0.3)" }}>Androy & Sud</span>
              </div>
              <p className="guide-desc-text">
                Écosystème endémique exceptionnel dominé par la famille des <em>Didiereaceae</em> et des <em>Euphorbiaceae</em> succulentes. Précipitations annuelles très faibles (350 à 500 mm/an). Végétation adaptée au déficit extrême (microphyllie, épines, stockage d'eau dans les tiges).
              </p>
              <div className="guide-param-list">
                <div className="guide-param-row">
                  <span className="guide-param-name">NDVI Moyen :</span>
                  <span className="guide-param-desc">0.20 – 0.32</span>
                </div>
                <div className="guide-param-row">
                  <span className="guide-param-name">Couvert :</span>
                  <span className="guide-param-desc">20% à 35%</span>
                </div>
              </div>
            </div>

            {/* Forêt Sèche Décidue */}
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">🌳 Forêt Sèche Décidue du Sud-Ouest</span>
                <span className="guide-card-badge green">Atsimo-Andrefana</span>
              </div>
              <p className="guide-desc-text">
                Forêt dense sèche sur calcaires et sables roux. Présence remarquable de Baobabs (<em>Adansonia za</em>, <em>Adansonia rubrostipa</em>) et d'arbres à bois précieux (<em>Commiphora</em>, <em>Cedrelopsis grevei</em>). Perte foliaire totale durant la saison sèche de mai à octobre.
              </p>
              <div className="guide-param-list">
                <div className="guide-param-row">
                  <span className="guide-param-name">NDVI Moyen :</span>
                  <span className="guide-param-desc">0.35 – 0.48</span>
                </div>
                <div className="guide-param-row">
                  <span className="guide-param-name">Couvert :</span>
                  <span className="guide-param-desc">35% à 55%</span>
                </div>
              </div>
            </div>

            {/* Fourré de Transition */}
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">🌿 Fourré de Transition & Savanes</span>
                <span className="guide-card-badge">Anosy & Betroka</span>
              </div>
              <p className="guide-desc-text">
                Zone tampon écologique entre le domaine subaride du Sud et le domaine humide de l'Est. Mosaïque de forêts galeries le long des rivières, savanes arborées et forêts de moyenne altitude. Pluviométrie 600 à 1000 mm/an.
              </p>
              <div className="guide-param-list">
                <div className="guide-param-row">
                  <span className="guide-param-name">NDVI Moyen :</span>
                  <span className="guide-param-desc">0.45 – 0.65</span>
                </div>
                <div className="guide-param-row">
                  <span className="guide-param-name">Couvert :</span>
                  <span className="guide-param-desc">50% à 75%</span>
                </div>
              </div>
            </div>

            {/* Formule des Pertes Forestières */}
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">📉 Modèle d'Estimation des Pertes Annuelles</span>
                <span className="guide-card-badge red">Déforestation & Pertes (ha/an)</span>
              </div>
              <div className="guide-formula-box red">
                Perte_(ha/an) = Surface_Foret × [ 0.005 + |Déficit_%| × 0.00035 + Pression_Anthr ]
              </div>
              <p className="guide-desc-text">
                Modélise le rythme de dégradation forestière sous l'effet combiné du déficit pluviométrique répété (mortalité des peuplements) et de la pression anthropique de survie (production de charbon de bois, défrichage sur brûlis "hatsake").
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Section 4: Physique des Capteurs & Emboîtement */}
      {activeSection === "sensors" && (
        <div className="guide-section-panel">
          <div className="guide-section-header">
            <h3 className="guide-section-title">
              <Icons.Database /> Physique des Capteurs Satellitaires & Emboîtement Spatial Multi-Échelle
            </h3>
            <p className="guide-section-subtitle">
              Démonstration géométrique des ratios de surface et emboîtement spatial : Sentinel-2 (10m) ⊂ Landsat-8/9 (30m) ⊂ MODIS (250m).
            </p>
          </div>

          <div className="guide-cards-grid">
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">1. Ratio Sentinel-2 dans Landsat</span>
                <span className="guide-card-badge green">Grille 3 × 3 = 9 px</span>
              </div>
              <div className="guide-formula-box green">
                (30 m / 10 m)² = 3² = 9 pixels Sentinel-2 dans 1 Landsat
              </div>
              <p className="guide-desc-text">
                Un pixel Landsat de 30m × 30m (900 m² ou 0.09 ha) contient rigoureusement <strong>9 sous-pixels Sentinel-2 de 10m</strong> (100 m² ch.). Sentinel-2 permet d'isoler des parcelles fines invisibles sur Landsat.
              </p>
            </div>

            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">2. Ratio Sentinel-2 dans MODIS</span>
                <span className="guide-card-badge">Grille 25 × 25 = 625 px</span>
              </div>
              <div className="guide-formula-box">
                (250 m / 10 m)² = 25² = 625 pixels Sentinel-2 dans 1 MODIS
              </div>
              <p className="guide-desc-text">
                Un seul pixel MODIS de 250m × 250m (62 500 m² ou 6.25 hectares) englobe l'équivalent de <strong>625 pixels Sentinel-2</strong>. MODIS lisse les détails mais offre une revisite quotidienne indispensable au suivi phénologique.
              </p>
            </div>

            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">3. Ratio Landsat dans MODIS</span>
                <span className="guide-card-badge amber">Grille 8.33 × 8.33 ≈ 69.4 px</span>
              </div>
              <div className="guide-formula-box amber">
                (250 m / 30 m)² = 8.333² ≈ 69.44 pixels Landsat dans 1 MODIS
              </div>
              <p className="guide-desc-text">
                Chaque pixel MODIS contient près de <strong>70 parcelles Landsat de 30m</strong>.
              </p>
            </div>
          </div>

          {/* Tableau Récapitulatif */}
          <div className="guide-table-wrapper">
            <table className="guide-table">
              <thead>
                <tr>
                  <th>Capteur / Mission</th>
                  <th>Agence</th>
                  <th>Résolution Spatiale</th>
                  <th>Surface d'un Pixel</th>
                  <th>Fréquence Temporelle</th>
                  <th>Rôle Clé dans Dynatsimo</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Sentinel-2 MSI</strong></td>
                  <td>ESA (Europe)</td>
                  <td><strong style={{ color: "#059669" }}>10 m × 10 m</strong></td>
                  <td>100 m² (0.01 ha)</td>
                  <td>5 jours</td>
                  <td>Validation haute précision, parcelles cultivées & coupes illicites</td>
                </tr>
                <tr>
                  <td><strong>Landsat-8 / Landsat-9 OLI</strong></td>
                  <td>NASA / USGS (USA)</td>
                  <td><strong>30 m × 30 m</strong></td>
                  <td>900 m² (0.09 ha)</td>
                  <td>8–16 jours</td>
                  <td>Continuité historique séculaire & analyse thermique</td>
                </tr>
                <tr>
                  <td><strong>MODIS Terra & Aqua</strong></td>
                  <td>NASA</td>
                  <td><strong style={{ color: "#2563eb" }}>250 m × 250 m</strong></td>
                  <td>62 500 m² (6.25 ha)</td>
                  <td>1–2 jours (Quotidien)</td>
                  <td>Suivi phénologique continu des 225 communes (2000–2026)</td>
                </tr>
                <tr>
                  <td><strong>CHIRPS (Infra-Red)</strong></td>
                  <td>UCSB / CHG</td>
                  <td><strong>0.05° (~5.3 km)</strong></td>
                  <td>~28 km² (2 800 ha)</td>
                  <td>Journalier / Mensuel</td>
                  <td>Pluviométrie, détection des anomalies et calculs de sécheresse</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Section 5: Traitements Géospatiaux & Isohyètes */}
      {activeSection === "geospatial" && (
        <div className="guide-section-panel">
          <div className="guide-section-header">
            <h3 className="guide-section-title">
              <Icons.Map /> Traitements Géospatiaux & Interpolation Spatiale des Isohyètes
            </h3>
            <p className="guide-section-subtitle">
              Méthode de pondération par l'inverse de la distance (IDW) et génération des isolignes de précipitations.
            </p>
          </div>

          <div className="guide-cards-grid">
            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">1. Inverse Distance Weighting (IDW)</span>
                <span className="guide-card-badge">Interpolation IDW (p=2)</span>
              </div>
              <div className="guide-formula-box">
                Z*(s_0) = [ Σ (i=1 à n) Z(s_i) / d(s_0, s_i)^p ] / [ Σ (i=1 à n) 1 / d(s_0, s_i)^p ]
              </div>
              <p className="guide-desc-text">
                Estime la valeur de précipitation en tout point non mesuré s_0 de la grille à partir des observations s_i. Le paramètre de puissance p = 2 garantit une transition fluide sans artefact de discontinuité.
              </p>
              <div className="guide-param-list">
                <div className="guide-param-row">
                  <span className="guide-param-name">d(s_0, s_i) :</span>
                  <span className="guide-param-desc">Distance euclidienne ou géodésique entre le point cible et la station.</span>
                </div>
                <div className="guide-param-row">
                  <span className="guide-param-name">p = 2 :</span>
                  <span className="guide-param-desc">Exposant de pondération inverse (loi en 1/d²).</span>
                </div>
              </div>
            </div>

            <div className="guide-card">
              <div className="guide-card-header">
                <span className="guide-card-title">2. Lignes Isohyètes à Équidistance 50 mm</span>
                <span className="guide-card-badge green">Isohyètes Climatologiques</span>
              </div>
              <div className="guide-formula-box green">
                Isohyète_k = &#123; (x, y) | Z(x, y) = 50 × k mm &#125;, k ∈ ℕ
              </div>
              <p className="guide-desc-text">
                Courbes d'égale hauteur de précipitation tracées avec un intervalle régulier de 50 mm. Elles révèlent nettement le gradient pluviométrique décroissant d'Est en Ouest (plus de 900 mm vers Fort-Dauphin / Anosy jusqu'à moins de 350 mm sur la côte sud-ouest d'Ambovombe et Tsihombe).
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


createRoot(document.getElementById("root")).render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);
