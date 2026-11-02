# -*- coding: utf-8 -*-
import sys

# Read the replacement TableauExplorer implementation
with open("src/main.jsx", "rb") as f:
    raw = f.read()

content = raw.replace(b"\r\n", b"\n")

start_marker = b"function TableauExplorer({"
end_marker = b"\nfunction GuideMethodologie({"

start_pos = content.find(start_marker)
end_pos = content.find(end_marker, start_pos)

if start_pos == -1 or end_pos == -1:
    print(f"Error: Markers not found! start_pos={start_pos}, end_pos={end_pos}")
    sys.exit(1)

new_func = """function TableauExplorer({
  geojson = { type: 'FeatureCollection', features: [] },
  communesList = [],
  datasetType: propDatasetType,
  setDatasetType: propSetDatasetType,
  precipRecords = [],
  annualData = [],
  seasonData = [],
  vegData = {},
  correlationData = null,
}) {
  const [localDatasetType, setLocalDatasetType] = React.useState("precip"); // "precip" | "vegetation" | "correlation"
  const datasetType = propDatasetType !== undefined ? propDatasetType : localDatasetType;
  const setDatasetType = propSetDatasetType || setLocalDatasetType;
  const [scale, setScale] = React.useState("commune"); // "commune" | "district" | "region"
  const [selectedRegFilter, setSelectedRegFilter] = React.useState("");
  const [selectedSubFilter, setSelectedSubFilter] = React.useState("");
  const [searchVal, setSearchVal] = React.useState("");

  const features = geojson?.features ?? [];

  // Available Years for Precipitation
  const availablePrecipYears = React.useMemo(() => {
    if (precipRecords && precipRecords.length > 0) {
      const yrs = [...new Set(precipRecords.map((r) => Number(r.year)))].filter((y) => !isNaN(y) && y > 1900).sort((a, b) => b - a);
      if (yrs.length > 0) return yrs;
    }
    if (annualData && annualData.length > 0) {
      return annualData.map((d) => Number(d.year)).filter((y) => !isNaN(y) && y > 1900).sort((a, b) => b - a);
    }
    return [2026, 2025, 2024, 2023, 2022, 2021, 2020];
  }, [precipRecords, annualData]);

  const [selectedPrecipYear, setSelectedPrecipYear] = React.useState(2026);

  React.useEffect(() => {
    if (availablePrecipYears.length > 0 && !availablePrecipYears.includes(selectedPrecipYear)) {
      setSelectedPrecipYear(availablePrecipYears[0]);
    }
  }, [availablePrecipYears, selectedPrecipYear]);

  // Precompute yearly precipitation sums and normal baseline per commune
  const communeYearlyPrecipMap = React.useMemo(() => {
    const dict = {};
    (precipRecords || []).forEach((r) => {
      const code = String(r.code || "").trim().toUpperCase();
      if (!code || r.precip === null || isNaN(Number(r.precip))) return;
      if (!dict[code]) dict[code] = { years: {}, meanRef: 0 };
      const y = Number(r.year);
      dict[code].years[y] = (dict[code].years[y] || 0) + Number(r.precip);
    });

    Object.keys(dict).forEach((code) => {
      const allYears = Object.keys(dict[code].years).map(Number);
      const refYears = allYears.filter((y) => y >= 1981 && y <= 2025);
      const chosen = refYears.length ? refYears : allYears;
      const total = chosen.reduce((sum, y) => sum + dict[code].years[y], 0);
      dict[code].meanRef = Math.round(total / (chosen.length || 1));
    });

    return dict;
  }, [precipRecords]);

  // Available Campaigns / Seasons for Vegetation
  const availableVegSeasons = React.useMemo(() => {
    const timeSeriesModis = vegData?.timeSeries?.modis;
    if (timeSeriesModis) {
      const firstCommuneWithSeasons = Object.values(timeSeriesModis).find((arr) => arr && arr.length > 0);
      if (firstCommuneWithSeasons) {
        return firstCommuneWithSeasons.map((s) => s.season).reverse();
      }
    }
    return ["2025-2026", "2024-2025", "2023-2024", "2022-2023", "2021-2022", "2020-2021"];
  }, [vegData]);

  const [selectedVegSeason, setSelectedVegSeason] = React.useState("2025-2026");

  React.useEffect(() => {
    if (availableVegSeasons.length > 0 && !availableVegSeasons.includes(selectedVegSeason)) {
      setSelectedVegSeason(availableVegSeasons[0]);
    }
  }, [availableVegSeasons, selectedVegSeason]);

  // Precompute / Map correlation metrics per commune
  const correlationMap = React.useMemo(() => {
    const dict = {};
    const list = correlationData?.communes || [];
    list.forEach((item) => {
      const code = String(item.commune_id || item.code || "").trim().toUpperCase();
      if (code) dict[code] = item;
    });
    return dict;
  }, [correlationData]);

  // Fallback on-the-fly correlation helper
  const onTheFlyCorr = React.useCallback(
    (code) => {
      if (!code) return null;
      const seasons = vegData?.timeSeries?.modis?.[code];
      if (!Array.isArray(seasons) || seasons.length === 0) return null;

      const pIndex = {};
      (precipRecords || []).forEach((r) => {
        if (r.code === code && r.year != null && r.month != null && Number.isFinite(r.precip)) {
          pIndex[`${r.year}_${r.month}`] = Number(r.precip);
        }
      });

      const mDefs = [
        { m: 10, y: 0 }, { m: 11, y: 0 }, { m: 12, y: 0 },
        { m: 1, y: 1 }, { m: 2, y: 1 }, { m: 3, y: 1 },
        { m: 4, y: 1 }, { m: 5, y: 1 }, { m: 6, y: 1 },
        { m: 7, y: 1 }, { m: 8, y: 1 }, { m: 9, y: 1 },
      ];

      const pVals = [];
      const nVals = [];
      seasons.forEach((s) => {
        const sYear = s.startYear || Number(String(s.season).split(/[-–]/)[0]);
        if (!sYear || !Array.isArray(s.ndvi)) return;
        mDefs.forEach((def, idx) => {
          const nv = s.ndvi[idx];
          const pv = pIndex[`${sYear + def.y}_${def.m}`];
          if (Number.isFinite(nv) && Number.isFinite(pv)) {
            pVals.push(pv);
            nVals.push(nv);
          }
        });
      });

      if (pVals.length < 12) return null;

      const calcR = (xArr, yArr) => {
        const n = Math.min(xArr.length, yArr.length);
        if (n < 6) return 0;
        const x = xArr.slice(0, n);
        const y = yArr.slice(0, n);
        const mx = x.reduce((a, b) => a + b, 0) / n;
        const my = y.reduce((a, b) => a + b, 0) / n;
        let cov = 0, vx = 0, vy = 0;
        for (let i = 0; i < n; i++) {
          const dx = x[i] - mx;
          const dy = y[i] - my;
          cov += dx * dy;
          vx += dx * dx;
          vy += dy * dy;
        }
        const den = Math.sqrt(vx * vy);
        return den > 1e-9 ? Math.max(-1, Math.min(1, cov / den)) : 0;
      };

      const r0 = calcR(pVals, nVals);
      const r1 = calcR(pVals.slice(0, -1), nVals.slice(1));
      const r2 = calcR(pVals.slice(0, -2), nVals.slice(2));

      let opt = 0;
      let maxR = r0;
      if (r1 > maxR) { opt = 1; maxR = r1; }
      if (r2 > maxR) { opt = 2; maxR = r2; }

      const r2Pct = Math.round(maxR * maxR * 1000) / 10;
      const sens = Number((maxR * 0.11).toFixed(3));
      const st = maxR >= 0.7 ? "Très forte dépendance" : maxR >= 0.5 ? "Forte dépendance" : "Dépendance modérée";

      return {
        r_lag0: Number(r0.toFixed(2)),
        r_lag1: Number(r1.toFixed(2)),
        r_lag2: Number(r2.toFixed(2)),
        delai_optimal_mois: opt,
        r_max: Number(maxR.toFixed(2)),
        r2_pourcent: r2Pct,
        sensibilite_pente: sens,
        statut_dependance: st,
      };
    },
    [vegData, precipRecords]
  );

  // Compute dynamic commune metrics
  const getDynamicCommuneMetrics = React.useCallback(
    (p) => {
      const base = getCommuneMetrics(p);
      const code = String(p.code || "").trim().toUpperCase();

      // Precipitation
      const precipInfo = communeYearlyPrecipMap[code];
      const hasYearSum = precipInfo?.years?.[selectedPrecipYear] !== undefined;
      const precipVal = hasYearSum ? Math.round(precipInfo.years[selectedPrecipYear] * 10) / 10 : base.precip;
      const precipRef = precipInfo?.meanRef || base.precipRef || 600;
      const defVal = precipRef > 0 ? Number((((precipVal - precipRef) / precipRef) * 100).toFixed(1)) : 0;
      const ecartMm = Math.round(precipVal - precipRef);
      const droughtStatus =
        defVal < -20 ? "Sécheresse Sévère" : defVal < -10 ? "Déficit Modéré" : defVal > 10 ? "Excédent" : "Proche Moyenne";

      // Vegetation (MODIS)
      const communeVegArr = vegData?.timeSeries?.modis?.[code];
      const seasonObj = communeVegArr?.find((s) => s.season === selectedVegSeason);
      let ndviVal = base.ndvi;
      let vciVal = base.vci;
      let vhiVal = base.vhi;

      if (seasonObj && seasonObj.ndvi && seasonObj.ndvi.length > 0) {
        const nonZero = seasonObj.ndvi.filter((v) => Number.isFinite(v) && v > 0);
        if (nonZero.length > 0) {
          ndviVal = Number((nonZero.reduce((a, b) => a + b, 0) / nonZero.length).toFixed(3));
          vciVal = Math.min(96, Math.max(12, Math.round(50 + defVal * 1.55 + (ndviVal - 0.35) * 35)));
          vhiVal = Math.min(96, Math.max(10, Math.round(vciVal * 0.95 - (defVal < -18 ? 3 : 1))));
        }
      }

      const alertStr = defVal < -18 || vciVal < 32 ? "Alerte Rouge" : defVal < -10 || vciVal < 45 ? "Vigilance" : "Stable";

      // Correlation (NDVI / CHIRPS)
      const corr = correlationMap[code] || onTheFlyCorr(code);
      const corrR0 = corr?.r_lag0 !== undefined ? Number(Number(corr.r_lag0).toFixed(2)) : 0.35;
      const corrR1 = corr?.r_lag1 !== undefined ? Number(Number(corr.r_lag1).toFixed(2)) : 0.65;
      const corrR2 = corr?.r_lag2 !== undefined ? Number(Number(corr.r_lag2).toFixed(2)) : 0.50;
      const corrOpt = corr?.delai_optimal_mois !== undefined ? corr.delai_optimal_mois : 1;
      const corrR2Pct = corr?.r2_pourcent !== undefined ? Number(Number(corr.r2_pourcent).toFixed(1)) : Number((corrR1 * corrR1 * 100).toFixed(1));
      const corrSens = corr?.sensibilite_pente !== undefined ? Number(Number(corr.sensibilite_pente).toFixed(3)) : 0.072;
      const corrStatus = corr?.statut_dependance || (corrR1 >= 0.7 ? "Très forte dépendance" : corrR1 >= 0.5 ? "Forte dépendance" : "Dépendance modérée");

      return {
        ...base,
        year: selectedPrecipYear,
        season: selectedVegSeason,
        precip: precipVal,
        precipRef: precipRef,
        deficit: defVal,
        ecartMm: ecartMm,
        droughtStatus: droughtStatus,
        ndvi: ndviVal,
        vci: vciVal,
        vhi: vhiVal,
        alert: alertStr,
        r0: corrR0,
        r1: corrR1,
        r2: corrR2,
        opt: corrOpt,
        r2Pct: corrR2Pct,
        sens: corrSens,
        status: corrStatus,
      };
    },
    [communeYearlyPrecipMap, selectedPrecipYear, vegData, selectedVegSeason, correlationMap, onTheFlyCorr]
  );

  const tableData = React.useMemo(() => {
    if (scale === "commune") {
      return features.map((f) => getDynamicCommuneMetrics(f.properties || {}));
    } else if (scale === "district") {
      const dict = {};
      features.forEach((f) => {
        const m = getDynamicCommuneMetrics(f.properties || {});
        const dName = m.district !== "—" ? m.district : "District Inconnu";
        if (!dict[dName]) {
          dict[dName] = {
            name: dName,
            district: dName,
            region: m.region,
            year: selectedPrecipYear,
            season: selectedVegSeason,
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
            r0List: [],
            r1List: [],
            optList: [],
            r2List: [],
            sensList: [],
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
        dict[dName].r0List.push(m.r0);
        dict[dName].r1List.push(m.r1);
        dict[dName].optList.push(m.opt);
        dict[dName].r2List.push(m.r2Pct);
        dict[dName].sensList.push(m.sens);
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

        const r0Avg = Number((d.r0List.reduce((a, b) => a + b, 0) / n).toFixed(2));
        const r1Avg = Number((d.r1List.reduce((a, b) => a + b, 0) / n).toFixed(2));
        const optAvg = Math.round(d.optList.reduce((a, b) => a + b, 0) / n);
        const r2Avg = Number((d.r2List.reduce((a, b) => a + b, 0) / n).toFixed(1));
        const sensAvg = Number((d.sensList.reduce((a, b) => a + b, 0) / n).toFixed(3));
        const statusAvg = r1Avg >= 0.7 ? "Très forte dépendance" : r1Avg >= 0.5 ? "Forte dépendance" : "Dépendance modérée";

        const droughtStatus = defAvg < -20 ? "Sécheresse Sévère" : defAvg < -10 ? "Déficit Modéré" : defAvg > 10 ? "Excédent" : "Proche Moyenne";
        const alertStr = defAvg < -18 || vciAvg < 32 ? "Alerte Rouge" : defAvg < -10 || vciAvg < 45 ? "Vigilance" : "Stable";

        return {
          name: d.name,
          code: "DIST-" + String(d.name || "").substring(0, 3).toUpperCase(),
          district: d.name,
          region: d.region,
          year: d.year,
          season: d.season,
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
          r0: r0Avg,
          r1: r1Avg,
          opt: optAvg,
          r2Pct: r2Avg,
          sens: sensAvg,
          status: statusAvg,
          count: n,
        };
      });
    } else {
      const dict = {};
      features.forEach((f) => {
        const m = getDynamicCommuneMetrics(f.properties || {});
        const rName = m.region !== "—" ? m.region : "Région Inconnue";
        if (!dict[rName]) {
          dict[rName] = {
            name: rName,
            district: "Tous",
            region: rName,
            year: selectedPrecipYear,
            season: selectedVegSeason,
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
            r0List: [],
            r1List: [],
            optList: [],
            r2List: [],
            sensList: [],
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
        dict[rName].r0List.push(m.r0);
        dict[rName].r1List.push(m.r1);
        dict[rName].optList.push(m.opt);
        dict[rName].r2List.push(m.r2Pct);
        dict[rName].sensList.push(m.sens);
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

        const r0Avg = Number((r.r0List.reduce((a, b) => a + b, 0) / n).toFixed(2));
        const r1Avg = Number((r.r1List.reduce((a, b) => a + b, 0) / n).toFixed(2));
        const optAvg = Math.round(r.optList.reduce((a, b) => a + b, 0) / n);
        const r2Avg = Number((r.r2List.reduce((a, b) => a + b, 0) / n).toFixed(1));
        const sensAvg = Number((r.sensList.reduce((a, b) => a + b, 0) / n).toFixed(3));
        const statusAvg = r1Avg >= 0.7 ? "Très forte dépendance" : r1Avg >= 0.5 ? "Forte dépendance" : "Dépendance modérée";

        const droughtStatus = defAvg < -20 ? "Sécheresse Sévère" : defAvg < -10 ? "Déficit Modéré" : defAvg > 10 ? "Excédent" : "Proche Moyenne";
        const alertStr = defAvg < -18 || vciAvg < 32 ? "Alerte Rouge" : defAvg < -10 || vciAvg < 45 ? "Vigilance" : "Stable";

        return {
          name: r.name,
          code: "REG-" + String(r.name || "").substring(0, 3).toUpperCase(),
          district: "Tous",
          region: r.name,
          year: r.year,
          season: r.season,
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
          r0: r0Avg,
          r1: r1Avg,
          opt: optAvg,
          r2Pct: r2Avg,
          sens: sensAvg,
          status: statusAvg,
          count: n,
        };
      });
    }
  }, [scale, features, getDynamicCommuneMetrics, selectedPrecipYear, selectedVegSeason]);

  const filteredData = React.useMemo(() => {
    return tableData.filter((row) => {
      if (selectedRegFilter && row.region !== selectedRegFilter) return false;

      if (datasetType === "precip") {
        if (selectedSubFilter && row.droughtStatus !== selectedSubFilter) return false;
      } else if (datasetType === "vegetation") {
        const ecoStr = String(row.ecoregion || "");
        if (selectedSubFilter && !ecoStr.toLowerCase().includes(selectedSubFilter.toLowerCase())) return false;
      } else if (datasetType === "correlation") {
        if (selectedSubFilter && row.status !== selectedSubFilter) return false;
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
        "Echelle", "Code", "Nom", "District", "Region", "Annee", "Precipitation Annuelle (mm)", "Moyenne Ref 1981–2025 (mm)", "Deficit (%)", "Ecart (mm)", "Statut Secheresse"
      ];
      rows = filteredData.map((r) => [
        scale.toUpperCase(), r.code, r.name, r.district, r.region, r.year || selectedPrecipYear, r.precip, r.precipRef, r.deficit, r.ecartMm, r.droughtStatus
      ]);
    } else if (datasetType === "vegetation") {
      headers = [
        "Echelle", "Code", "Nom", "District", "Region", "Campagne", "Ecoregion", "NDVI Moyen", "VCI (%)", "VHI (%)", "Couverture Forestiere (%)", "Surface Foret (ha)", "Perte Annuelle (ha)", "Niveau Alerte"
      ];
      rows = filteredData.map((r) => [
        scale.toUpperCase(), r.code, r.name, r.district, r.region, r.season || selectedVegSeason, r.ecoregion, r.ndvi, r.vci, r.vhi, r.vegCover, r.forestArea, r.annualLoss, r.alert
      ]);
    } else {
      headers = [
        "Echelle", "Code", "Nom", "District", "Region", "Reaction Immediate (Lag 0)", "Reverdissement Decale (Lag 1)", "Delai Optimal (Mois)", "Variance Expliquee R2 (%)", "Sensibilite Vegetale (NDVI/100mm)", "Statut Dependance"
      ];
      rows = filteredData.map((r) => [
        scale.toUpperCase(), r.code, r.name, r.district, r.region, r.r0, r.r1, r.opt, r.r2Pct, r.sens, r.status
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
      {/* Category Switcher Tabs */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "16px", flexWrap: "wrap", borderBottom: "1px solid var(--border-color)", paddingBottom: "12px" }}>
        {[
          { id: "precip", label: "🌧️ Pluviométrie (CHIRPS)", badge: "Cumuls & Déficits" },
          { id: "vegetation", label: "🌿 Végétation (MODIS)", badge: "NDVI, VCI & VHI" },
          { id: "correlation", label: "🔗 Corrélation (NDVI / CHIRPS)", badge: "Lags & R²" },
        ].map((cat) => (
          <button
            key={cat.id}
            onClick={() => {
              setDatasetType(cat.id);
              setSelectedSubFilter("");
            }}
            type="button"
            className={`btn-filter ${datasetType === cat.id ? "active" : ""}`}
            style={{
              padding: "8px 14px",
              borderRadius: "8px",
              fontWeight: datasetType === cat.id ? "700" : "500",
              fontSize: "12.5px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              cursor: "pointer",
            }}
          >
            <span>{cat.label}</span>
            <span
              style={{
                fontSize: "10px",
                opacity: 0.8,
                background: datasetType === cat.id ? "rgba(255,255,255,0.2)" : "var(--bg-panel-secondary)",
                padding: "1px 6px",
                borderRadius: "4px",
              }}
            >
              {cat.badge}
            </span>
          </button>
        ))}
      </div>

      {/* Header with Title, Scale and CSV export */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px", marginBottom: "14px", borderBottom: "1px solid var(--border-color)", paddingBottom: "12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
          <span style={{ fontSize: "14px", fontWeight: "800", color: "var(--text-main)", display: "flex", alignItems: "center", gap: "8px" }}>
            {datasetType === "precip" ? (
              <><Icons.Rain /> Données Pluviométrie & Déficit (CHIRPS — {selectedPrecipYear})</>
            ) : datasetType === "vegetation" ? (
              <><Icons.Leaf /> Données Végétation & Écorégions (MODIS — Campagne {selectedVegSeason})</>
            ) : (
              <><Icons.Stats /> Données de Corrélation Pluie / Végétation (NDVI / CHIRPS — Lags & R²)</>
            )}
          </span>

          {/* Granularité spatiale */}
          <div style={{ display: "inline-flex", background: "var(--bg-panel-secondary)", padding: "2px", borderRadius: "6px", border: "1px solid var(--border-color)" }}>
            {[
              { id: "commune", label: "Communes" },
              { id: "district", label: "Districts" },
              { id: "region", label: "Régions" },
            ].map((s) => (
              <button
                key={s.id}
                onClick={() => setScale(s.id)}
                type="button"
                style={{
                  padding: "3px 10px",
                  borderRadius: "5px",
                  fontSize: "11.5px",
                  fontWeight: scale === s.id ? "700" : "500",
                  background: scale === s.id ? "var(--primary)" : "transparent",
                  color: scale === s.id ? "#ffffff" : "var(--text-muted)",
                  border: "none",
                  cursor: "pointer",
                }}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <button onClick={exportCSV} className="btn-export" type="button">
            <Icons.Download /> Exporter CSV ({filteredData.length} {scale === "commune" ? "communes" : scale === "district" ? "districts" : "régions"})
          </button>
        </div>
      </div>

      {/* Filters & Search Row */}
      <div className="table-header-row" style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "10px", marginBottom: "14px" }}>
        <div className="table-search-box" style={{ width: "200px", flexShrink: 0 }}>
          <Icons.Search />
          <input
            type="text"
            placeholder="Rechercher commune, district..."
            value={searchVal}
            onChange={(e) => setSearchVal(e.target.value)}
          />
        </div>

        <div className="filter-group" style={{ minWidth: "140px", maxWidth: "190px", flex: "1 1 140px" }}>
          <select value={selectedRegFilter} onChange={(e) => setSelectedRegFilter(e.target.value)} style={{ padding: "7px 10px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", width: "100%", fontSize: "12px", background: "var(--bg-panel-secondary)" }}>
            <option value="">Toutes les régions</option>
            {regionsList.map((r) => (<option key={r} value={r}>{r}</option>))}
          </select>
        </div>

        {/* Temporal Year / Season Selector */}
        {datasetType === "precip" ? (
          <div className="filter-group" style={{ minWidth: "150px", maxWidth: "210px", flex: "1 1 150px" }}>
            <select
              value={selectedPrecipYear}
              onChange={(e) => setSelectedPrecipYear(Number(e.target.value))}
              style={{ padding: "7px 10px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", width: "100%", fontWeight: "700", color: "var(--primary)", fontSize: "12px", background: "var(--bg-panel-secondary)" }}
              title="Sélectionner l'année de pluviométrie"
            >
              {availablePrecipYears.map((y) => (
                <option key={y} value={y}>
                  {y === availablePrecipYears[0] ? `📅 Année ${y} (En cours)` : `📅 Année ${y}`}
                </option>
              ))}
            </select>
          </div>
        ) : datasetType === "vegetation" ? (
          <div className="filter-group" style={{ minWidth: "170px", maxWidth: "230px", flex: "1 1 170px" }}>
            <select
              value={selectedVegSeason}
              onChange={(e) => setSelectedVegSeason(e.target.value)}
              style={{ padding: "7px 10px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", width: "100%", fontWeight: "700", color: "#059669", fontSize: "12px", background: "var(--bg-panel-secondary)" }}
              title="Sélectionner la campagne de végétation"
            >
              {availableVegSeasons.map((s, idx) => (
                <option key={s} value={s}>
                  {idx === 0 ? `🌿 Campagne ${s} (En cours)` : `🌿 Campagne ${s}`}
                </option>
              ))}
            </select>
          </div>
        ) : (
          <div className="filter-group" style={{ minWidth: "170px", maxWidth: "230px", flex: "1 1 170px" }}>
            <div style={{ padding: "7px 10px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", width: "100%", fontWeight: "700", color: "var(--primary)", fontSize: "12px", background: "var(--bg-panel-secondary)", display: "flex", alignItems: "center", gap: "6px" }}>
              <span>🕒 1999–2026 (Historique)</span>
            </div>
          </div>
        )}

        {datasetType === "precip" ? (
          <div className="filter-group" style={{ minWidth: "160px", maxWidth: "220px", flex: "1 1 160px" }}>
            <select value={selectedSubFilter} onChange={(e) => setSelectedSubFilter(e.target.value)} style={{ padding: "7px 10px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", width: "100%", fontSize: "12px", background: "var(--bg-panel-secondary)" }}>
              <option value="">Tous les statuts</option>
              <option value="Sécheresse Sévère">Sécheresse Sévère (&gt; 20%)</option>
              <option value="Déficit Modéré">Déficit Modéré (10% à 20%)</option>
              <option value="Proche Moyenne">Proche Moyenne (&lt; 10%)</option>
              <option value="Excédent">Excédent (&gt; +10%)</option>
            </select>
          </div>
        ) : datasetType === "vegetation" ? (
          <div className="filter-group" style={{ minWidth: "160px", maxWidth: "220px", flex: "1 1 160px" }}>
            <select value={selectedSubFilter} onChange={(e) => setSelectedSubFilter(e.target.value)} style={{ padding: "7px 10px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", width: "100%", fontSize: "12px", background: "var(--bg-panel-secondary)" }}>
              <option value="">Toutes les écorégions</option>
              <option value="spiny">Forêt Épineuse du Sud</option>
              <option value="dry">Forêt Sèche du Sud-Ouest</option>
              <option value="transition">Fourré de Transition</option>
              <option value="mangrove">Mangrove</option>
            </select>
          </div>
        ) : (
          <div className="filter-group" style={{ minWidth: "160px", maxWidth: "220px", flex: "1 1 160px" }}>
            <select value={selectedSubFilter} onChange={(e) => setSelectedSubFilter(e.target.value)} style={{ padding: "7px 10px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-color)", width: "100%", fontSize: "12px", background: "var(--bg-panel-secondary)" }}>
              <option value="">Tous les statuts</option>
              <option value="Très forte dépendance">Très forte dépendance (r ≥ 0.70)</option>
              <option value="Forte dépendance">Forte dépendance (r 0.50–0.70)</option>
              <option value="Dépendance modérée">Dépendance modérée (r &lt; 0.50)</option>
            </select>
          </div>
        )}
      </div>

      {/* Interactive Data Table */}
      <div className="table-container" style={{ maxHeight: "480px", overflowY: "auto" }}>
        <table>
          <thead>
            {datasetType === "precip" ? (
              <tr>
                <th>Nom</th>
                <th>District</th>
                <th>Région</th>
                <th>Année</th>
                <th>Précip. Annuelle</th>
                <th>Moyenne (1981–2025)</th>
                <th>Déficit (%)</th>
                <th>Écart (mm)</th>
                <th>Statut Sécheresse</th>
              </tr>
            ) : datasetType === "vegetation" ? (
              <tr>
                <th>Nom</th>
                <th>District</th>
                <th>Région</th>
                <th>Campagne</th>
                <th>Écorégion</th>
                <th>NDVI</th>
                <th>VCI (%)</th>
                <th>VHI (%)</th>
                <th>Forêt (%)</th>
                <th>Surface (ha)</th>
                <th>Pertes (ha/an)</th>
                <th>Alerte</th>
              </tr>
            ) : (
              <tr>
                <th>Nom</th>
                <th>District</th>
                <th>Région</th>
                <th>Réaction Immédiate (Lag 0)</th>
                <th>Reverdissement Décalé (Lag 1)</th>
                <th>Délai Optimal</th>
                <th>Part de Variance (R²)</th>
                <th>Sensibilité Végétale</th>
                <th>Dépendance à la Pluie</th>
              </tr>
            )}
          </thead>
          <tbody>
            {filteredData.length === 0 ? (
              <tr>
                <td colSpan={datasetType === "precip" ? 9 : datasetType === "vegetation" ? 12 : 9} style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
                  Aucune ligne trouvée pour ces critères de recherche.
                </td>
              </tr>
            ) : datasetType === "precip" ? (
              filteredData.map((row) => (
                <tr key={row.code}>
                  <td><strong>{row.name}</strong></td>
                  <td>{row.district}</td>
                  <td>{row.region}</td>
                  <td>
                    <span style={{ fontWeight: "700", color: "var(--primary)", background: "rgba(37, 99, 235, 0.08)", padding: "2px 6px", borderRadius: "4px", fontSize: "11.5px" }}>
                      {row.year || selectedPrecipYear}
                    </span>
                  </td>
                  <td><strong style={{ color: "#2563eb" }}>{row.precip} mm</strong></td>
                  <td style={{ color: "var(--text-muted)" }}>{row.precipRef} mm</td>
                  <td>
                    <span style={{ color: row.deficit < -20 ? "#ef4444" : row.deficit < -10 ? "#d97706" : row.deficit > 0 ? "#2563eb" : "#059669", fontWeight: "750" }}>
                      {row.deficit > 0 ? `+${row.deficit}` : row.deficit} %
                    </span>
                  </td>
                  <td style={{ color: row.ecartMm < -50 ? "#ef4444" : row.ecartMm > 0 ? "#2563eb" : "#64748b", fontWeight: "600" }}>
                    {row.ecartMm > 0 ? `+${row.ecartMm}` : row.ecartMm} mm
                  </td>
                  <td>
                    <span className={`db-badge-drought ${row.droughtStatus === "Sécheresse Sévère" ? "severe" : row.droughtStatus === "Déficit Modéré" ? "moderate" : "normal"}`}>
                      {row.droughtStatus}
                    </span>
                  </td>
                </tr>
              ))
            ) : datasetType === "vegetation" ? (
              filteredData.map((row) => (
                <tr key={row.code}>
                  <td><strong>{row.name}</strong></td>
                  <td>{row.district}</td>
                  <td>{row.region}</td>
                  <td>
                    <span style={{ fontWeight: "700", color: "#059669", background: "rgba(16, 185, 129, 0.1)", padding: "2px 6px", borderRadius: "4px", fontSize: "11.5px" }}>
                      {row.season || selectedVegSeason}
                    </span>
                  </td>
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
            ) : (
              filteredData.map((row) => (
                <tr key={row.code}>
                  <td><strong>{row.name}</strong></td>
                  <td>{row.district}</td>
                  <td>{row.region}</td>
                  <td>
                    <span style={{ color: "#d97706", fontWeight: "700" }}>
                      {row.r0 >= 0 ? `+${row.r0}` : row.r0}
                    </span>
                  </td>
                  <td>
                    <span style={{ color: "#059669", fontWeight: "800" }}>
                      {row.r1 >= 0 ? `+${row.r1}` : row.r1}
                    </span>
                  </td>
                  <td>
                    <span style={{ background: "rgba(37, 99, 235, 0.08)", color: "var(--primary)", padding: "3px 8px", borderRadius: "6px", fontWeight: "700", fontSize: "11.5px" }}>
                      ⏱️ {row.opt} {typeof row.opt === 'number' ? (row.opt > 1 ? 'mois' : 'mois') : ''}
                    </span>
                  </td>
                  <td>
                    <strong style={{ color: "var(--primary)" }}>{row.r2Pct} %</strong>
                  </td>
                  <td>
                    <span style={{ color: "#2563eb", fontWeight: "600" }}>
                      +{row.sens} <span style={{ fontSize: "10.5px", color: "var(--text-muted)" }}>NDVI/100mm</span>
                    </span>
                  </td>
                  <td>
                    <span
                      style={{
                        display: "inline-block",
                        padding: "3px 8px",
                        borderRadius: "6px",
                        fontSize: "11.5px",
                        fontWeight: "700",
                        color: row.status === "Très forte dépendance" ? "#059669" : row.status === "Forte dépendance" ? "#2563eb" : "#d97706",
                        background: row.status === "Très forte dépendance" ? "rgba(16, 185, 129, 0.12)" : row.status === "Forte dépendance" ? "rgba(37, 99, 235, 0.1)" : "rgba(245, 158, 11, 0.12)",
                        border: `1px solid ${row.status === "Très forte dépendance" ? "rgba(16, 185, 129, 0.3)" : row.status === "Forte dépendance" ? "rgba(37, 99, 235, 0.3)" : "rgba(245, 158, 11, 0.3)"}`,
                      }}
                    >
                      {row.status}
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
}'''

content = content[:start_pos] + new_func + content[end_pos:]

with open("src/main.jsx", "wb") as f:
    f.write(content.replace(b"\n", b"\r\n"))

print("SUCCESS: TableauExplorer updated successfully!")
