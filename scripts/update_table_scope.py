with open("src/main.jsx", "rb") as f:
    content = f.read()

# 1. State and memoized list replacement
old_list_code = b"""  // Tableau comparatif des communes du m\xc3\xaame district
  const districtComparisonList = React.useMemo(() => {
    if (!activeCommuneObj?.district || !vegData?.timeSeries?.modis || !precipRecords) return [];
    const sameDistrictCommunes = communes.filter((c) => c.district === activeCommuneObj.district);

    return sameDistrictCommunes.map((c) => {
      const seasons = vegData.timeSeries.modis[c.code];
      if (!Array.isArray(seasons) || seasons.length === 0) {
        return { code: c.code, nom: c.nom || c.code, r0: "-", r1: "-", opt: "-", r2: "-" };
      }

      // Quick lag 0 & lag 1 computation
      const pMap = {};
      precipRecords.forEach((r) => {
        if (r.code === c.code && r.year != null && r.month != null) {
          pMap[`${r.year}_${r.month}`] = Number(r.precip);
        }
      });

      const pVals = [];
      const nVals = [];
      seasons.forEach((s) => {
        const sYear = s.startYear || Number(String(s.season).split(/[-\xe2\x80\x93]/)[0]);
        if (!sYear || !Array.isArray(s.ndvi)) return;
        const mDefs = [
          { m: 10, y: sYear }, { m: 11, y: sYear }, { m: 12, y: sYear },
          { m: 1, y: sYear + 1 }, { m: 2, y: sYear + 1 }, { m: 3, y: sYear + 1 },
          { m: 4, y: sYear + 1 }, { m: 5, y: sYear + 1 }, { m: 6, y: sYear + 1 },
          { m: 7, y: sYear + 1 }, { m: 8, y: sYear + 1 }, { m: 9, y: sYear + 1 },
        ];
        mDefs.forEach((def, idx) => {
          const nv = s.ndvi[idx];
          const pv = pMap[`${def.y}_${def.m}`];
          if (Number.isFinite(nv) && Number.isFinite(pv)) {
            pVals.push(pv);
            nVals.push(nv);
          }
        });
      });

      if (pVals.length < 12) {
        return { code: c.code, nom: c.nom || c.code, r0: "-", r1: "-", opt: "-", r2: "-" };
      }

      const calcQuickR = (x, y) => {
        const n = Math.min(x.length, y.length);
        const mx = x.slice(0, n).reduce((a, b) => a + b, 0) / n;
        const my = y.slice(0, n).reduce((a, b) => a + b, 0) / n;
        let cv = 0, vx = 0, vy = 0;
        for (let i = 0; i < n; i++) {
          const dx = x[i] - mx;
          const dy = y[i] - my;
          cv += dx * dy;
          vx += dx * dx;
          vy += dy * dy;
        }
        const den = Math.sqrt(vx * vy);
        return den > 1e-9 ? cv / den : 0;
      };

      const qR0 = calcQuickR(pVals, nVals);
      const qR1 = calcQuickR(pVals.slice(0, -1), nVals.slice(1));
      const qR2 = calcQuickR(pVals.slice(0, -2), nVals.slice(2));

      let opt = 0;
      let maxR = qR0;
      if (qR1 > maxR) { opt = 1; maxR = qR1; }
      if (qR2 > maxR) { opt = 2; maxR = qR2; }

      return {
        code: c.code,
        nom: c.nom || c.code,
        r0: Number(qR0.toFixed(2)),
        r1: Number(qR1.toFixed(2)),
        opt: `${opt} mois`,
        r2: `${Math.round(Math.pow(maxR, 2) * 100)}%`,
        status: maxR >= 0.7 ? "Tr\xc3\xa8s forte d\xc3\xa9pendance" : maxR >= 0.5 ? "Forte d\xc3\xa9pendance" : "D\xc3\xa9pendance mod\xc3\xa9r\xc3\xa9e",
        statusColor: maxR >= 0.7 ? "#16a34a" : maxR >= 0.5 ? "#2563eb" : "#d97706",
      };
    }).sort((a, b) => (typeof b.r1 === "number" ? b.r1 : 0) - (typeof a.r1 === "number" ? a.r1 : 0));
  }, [activeCommuneObj, communes, vegData, precipRecords]);"""

new_list_code = b"""  // Scope et pagination du tableau comparatif des communes
  const [comparisonScope, setComparisonScope] = React.useState("district"); // 'district' | 'region' | 'all'
  const [comparisonSearch, setComparisonSearch] = React.useState("");
  const [comparisonPage, setComparisonPage] = React.useState(1);
  const comparisonPageSize = 10;

  // R\xc3\xa9initialisation de la page en cas de changement
  React.useEffect(() => {
    setComparisonPage(1);
  }, [comparisonScope, comparisonSearch, activeCommuneObj?.district, activeCommuneObj?.region]);

  const districtCount = React.useMemo(() => {
    return communes.filter((c) => c.district && c.district === activeCommuneObj?.district).length;
  }, [communes, activeCommuneObj]);

  const regionCount = React.useMemo(() => {
    return communes.filter((c) => c.region && c.region === activeCommuneObj?.region).length;
  }, [communes, activeCommuneObj]);

  // Communes cibl\xc3\xa9es selon le p\xc3\xa9rim\xc3\xa8tre choisi
  const comparisonPool = React.useMemo(() => {
    if (!communes || communes.length === 0) return [];
    if (comparisonScope === "district") {
      return activeCommuneObj?.district ? communes.filter((c) => c.district === activeCommuneObj.district) : communes;
    }
    if (comparisonScope === "region") {
      return activeCommuneObj?.region ? communes.filter((c) => c.region === activeCommuneObj.region) : communes;
    }
    return communes; // 'all'
  }, [communes, activeCommuneObj, comparisonScope]);

  // Filtrage par texte de recherche
  const searchedComparisonPool = React.useMemo(() => {
    if (!comparisonSearch.trim()) return comparisonPool;
    const q = comparisonSearch.toLowerCase().trim();
    return comparisonPool.filter((c) => {
      const nom = (c.nom || "").toLowerCase();
      const code = (c.code || "").toLowerCase();
      const dist = (c.district || "").toLowerCase();
      const reg = (c.region || "").toLowerCase();
      return nom.includes(q) || code.includes(q) || dist.includes(q) || reg.includes(q);
    });
  }, [comparisonPool, comparisonSearch]);

  // Calcul dynamique des statistiques de r\xc3\xa9activit\xc3\xa9 pour les communes
  const fullComparisonList = React.useMemo(() => {
    if (!vegData?.timeSeries?.modis || !precipRecords || precipRecords.length === 0) return [];

    const pIndex = {};
    precipRecords.forEach((r) => {
      if (r.code && r.year != null && r.month != null && Number.isFinite(r.precip)) {
        if (!pIndex[r.code]) pIndex[r.code] = {};
        pIndex[r.code][`${r.year}_${r.month}`] = Number(r.precip);
      }
    });

    const mDefs = [
      { m: 10, yOffset: 0 }, { m: 11, yOffset: 0 }, { m: 12, yOffset: 0 },
      { m: 1, yOffset: 1 }, { m: 2, yOffset: 1 }, { m: 3, yOffset: 1 },
      { m: 4, yOffset: 1 }, { m: 5, yOffset: 1 }, { m: 6, yOffset: 1 },
      { m: 7, yOffset: 1 }, { m: 8, yOffset: 1 }, { m: 9, yOffset: 1 },
    ];

    const calcQuickR = (x, y) => {
      const n = Math.min(x.length, y.length);
      if (n < 6) return 0;
      const mx = x.slice(0, n).reduce((a, b) => a + b, 0) / n;
      const my = y.slice(0, n).reduce((a, b) => a + b, 0) / n;
      let cv = 0, vx = 0, vy = 0;
      for (let i = 0; i < n; i++) {
        const dx = x[i] - mx;
        const dy = y[i] - my;
        cv += dx * dy;
        vx += dx * dx;
        vy += dy * dy;
      }
      const den = Math.sqrt(vx * vy);
      return den > 1e-9 ? cv / den : 0;
    };

    return searchedComparisonPool.map((c) => {
      const seasons = vegData.timeSeries.modis[c.code];
      const pMap = pIndex[c.code] || {};
      if (!Array.isArray(seasons) || seasons.length === 0) {
        return {
          code: c.code,
          nom: c.nom || c.code,
          district: c.district || "n/d",
          region: c.region || "n/d",
          r0: "-",
          r1: "-",
          opt: "-",
          r2: "-",
          status: "Donn\xc3\xa9es n/d",
          statusColor: "#94a3b8",
        };
      }

      const pVals = [];
      const nVals = [];
      seasons.forEach((s) => {
        const sYear = s.startYear || Number(String(s.season).split(/[-\xe2\x80\x93]/)[0]);
        if (!sYear || !Array.isArray(s.ndvi)) return;
        mDefs.forEach((def, idx) => {
          const nv = s.ndvi[idx];
          const pv = pMap[`${sYear + def.yOffset}_${def.m}`];
          if (Number.isFinite(nv) && Number.isFinite(pv)) {
            pVals.push(pv);
            nVals.push(nv);
          }
        });
      });

      if (pVals.length < 12) {
        return {
          code: c.code,
          nom: c.nom || c.code,
          district: c.district || "n/d",
          region: c.region || "n/d",
          r0: "-",
          r1: "-",
          opt: "-",
          r2: "-",
          status: "Donn\xc3\xa9es n/d",
          statusColor: "#94a3b8",
        };
      }

      const qR0 = calcQuickR(pVals, nVals);
      const qR1 = calcQuickR(pVals.slice(0, -1), nVals.slice(1));
      const qR2 = calcQuickR(pVals.slice(0, -2), nVals.slice(2));

      let opt = 0;
      let maxR = qR0;
      if (qR1 > maxR) { opt = 1; maxR = qR1; }
      if (qR2 > maxR) { opt = 2; maxR = qR2; }

      return {
        code: c.code,
        nom: c.nom || c.code,
        district: c.district || "n/d",
        region: c.region || "n/d",
        r0: Number(qR0.toFixed(2)),
        r1: Number(qR1.toFixed(2)),
        opt: `${opt} mois`,
        r2: `${Math.round(Math.pow(maxR, 2) * 100)}%`,
        status: maxR >= 0.7 ? "Tr\xc3\xa8s forte d\xc3\xa9pendance" : maxR >= 0.5 ? "Forte d\xc3\xa9pendance" : "D\xc3\xa9pendance mod\xc3\xa9r\xc3\xa9e",
        statusColor: maxR >= 0.7 ? "#16a34a" : maxR >= 0.5 ? "#2563eb" : "#d97706",
      };
    }).sort((a, b) => (typeof b.r1 === "number" ? b.r1 : 0) - (typeof a.r1 === "number" ? a.r1 : 0));
  }, [searchedComparisonPool, vegData, precipRecords]);

  // Pagination calcul\xc3\xa9e
  const totalComparisonPages = Math.max(1, Math.ceil(fullComparisonList.length / comparisonPageSize));
  const paginatedComparisonList = React.useMemo(() => {
    const start = (comparisonPage - 1) * comparisonPageSize;
    return fullComparisonList.slice(start, start + comparisonPageSize);
  }, [fullComparisonList, comparisonPage, comparisonPageSize]);"""

# 2. JSX Table replacement
old_table_jsx = b"""          {/* Tableau Comparatif des Communes du m\xc3\xaame District */}
          {districtComparisonList.length > 0 && (
            <div className="panel" style={{ padding: "18px", backgroundColor: "var(--bg-panel)" }}>
              <h4 style={{ margin: 0, fontSize: "13px", fontWeight: "800", color: "var(--text-main)", marginBottom: "4px" }}>
                \xf0\x9f\x8f\x98\xef\xb8\x8f Comparatif des Communes du District de {activeCommuneObj?.district || "la zone"}
              </h4>
              <p style={{ fontSize: "11px", color: "var(--text-muted)", margin: "0 0 14px 0" }}>
                Classement par r\xc3\xa9activit\xc3\xa9 v\xc3\xa9g\xc3\xa9tale aux pr\xc3\xa9cipitations &bull; Cliquez sur une commune pour afficher son profil d\xc3\xa9taill\xc3\xa9
              </p>

              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
                  <thead>
                    <tr style={{ borderBottom: "2px solid var(--border-color)", textAlign: "left", color: "var(--text-muted)" }}>
                      <th style={{ padding: "8px 10px" }}>Commune</th>
                      <th style={{ padding: "8px 10px" }}>R\xc3\xa9action imm\xc3\xa9diate (Lag 0)</th>
                      <th style={{ padding: "8px 10px" }}>Reverdissement (Lag 1)</th>
                      <th style={{ padding: "8px 10px" }}>D\xc3\xa9lai optimal</th>
                      <th style={{ padding: "8px 10px" }}>Part de variance (R\xc2\xb2)</th>
                      <th style={{ padding: "8px 10px" }}>D\xc3\xa9pendance \xc3\xa0 la pluie</th>
                      <th style={{ padding: "8px 10px", textAlign: "right" }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {districtComparisonList.map((row) => (
                      <tr
                        key={row.code}
                        style={{
                          borderBottom: "1px solid var(--border-color)",
                          backgroundColor: row.code === activeCommuneObj?.code ? "rgba(22, 163, 74, 0.08)" : "transparent",
                          fontWeight: row.code === activeCommuneObj?.code ? "700" : "400",
                        }}
                      >
                        <td style={{ padding: "8px 10px", color: "var(--text-main)" }}>
                          {row.nom} {row.code === activeCommuneObj?.code && "\xe2\x98\x85"}
                        </td>
                        <td style={{ padding: "8px 10px", color: "#f59e0b" }}>{row.r0 > 0 ? `+${row.r0}` : row.r0}</td>
                        <td style={{ padding: "8px 10px", color: "#16a34a", fontWeight: "700" }}>{row.r1 > 0 ? `+${row.r1}` : row.r1}</td>
                        <td style={{ padding: "8px 10px" }}>{row.opt}</td>
                        <td style={{ padding: "8px 10px", fontWeight: "700" }}>{row.r2}</td>
                        <td style={{ padding: "8px 10px", color: row.statusColor, fontWeight: "600" }}>{row.status}</td>
                        <td style={{ padding: "8px 10px", textAlign: "right" }}>
                          {row.code !== activeCommuneObj?.code ? (
                            <button
                              type="button"
                              onClick={() => handleSelectCommune(row.code)}
                              style={{
                                padding: "3px 8px",
                                fontSize: "11px",
                                borderRadius: "4px",
                                border: "1px solid var(--border-color)",
                                backgroundColor: "var(--bg-panel-secondary)",
                                cursor: "pointer",
                              }}
                            >
                              Analyser
                            </button>
                          ) : (
                            <span style={{ fontSize: "11px", color: "#16a34a", fontWeight: "700" }}>Active</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}"""

new_table_jsx = b"""          {/* Tableau Comparatif Multi-\xc3\x89chelles des Communes (District / R\xc3\xa9gion / Grand Sud) */}
          {fullComparisonList.length > 0 && (
            <div className="panel" style={{ padding: "20px", backgroundColor: "var(--bg-panel)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px", marginBottom: "14px" }}>
                <div>
                  <h4 style={{ margin: 0, fontSize: "14px", fontWeight: "800", color: "var(--text-main)", display: "flex", alignItems: "center", gap: "8px" }}>
                    <span>\xf0\x9f\x8f\x98\xef\xb8\x8f Comparatif des Communes : {comparisonScope === "district" ? `District de ${activeCommuneObj?.district || "la zone"}` : comparisonScope === "region" ? `R\xc3\xa9gion ${activeCommuneObj?.region || "Grand Sud"}` : "Tout le Grand Sud"}</span>
                    <span style={{ fontSize: "11px", fontWeight: "700", color: "var(--primary)", backgroundColor: "rgba(37,99,235,0.08)", padding: "2px 8px", borderRadius: "12px" }}>
                      {fullComparisonList.length} commune{fullComparisonList.length > 1 ? "s" : ""}
                    </span>
                  </h4>
                  <p style={{ fontSize: "11.5px", color: "var(--text-muted)", margin: "4px 0 0 0" }}>
                    Classement par r\xc3\xa9activit\xc3\xa9 v\xc3\xa9g\xc3\xa9tale aux pr\xc3\xa9cipitations &bull; Cliquez sur \xc2\xab Analyser \xc2\xbb pour charger les graphiques d'une commune
                  </p>
                </div>

                {/* Contr\xc3\xb4les de P\xc3\xa9rim\xc3\xa8tre & Recherche */}
                <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
                  <div className="scale-tabs" style={{ display: "flex", gap: "4px", backgroundColor: "var(--bg-panel-secondary)", padding: "3px", borderRadius: "8px", border: "1px solid var(--border-color)" }}>
                    <button
                      type="button"
                      className={`scale-tab-btn ${comparisonScope === "district" ? "active" : ""}`}
                      onClick={() => setComparisonScope("district")}
                      style={{ fontSize: "11px", padding: "4px 9px", fontWeight: 700 }}
                    >
                      \xf0\x9f\x93\x8d District ({districtCount})
                    </button>
                    <button
                      type="button"
                      className={`scale-tab-btn ${comparisonScope === "region" ? "active" : ""}`}
                      onClick={() => setComparisonScope("region")}
                      style={{ fontSize: "11px", padding: "4px 9px", fontWeight: 700 }}
                    >
                      \xf0\x9f\x8f\x9b\xef\xb8\x8f R\xc3\xa9gion ({regionCount})
                    </button>
                    <button
                      type="button"
                      className={`scale-tab-btn ${comparisonScope === "all" ? "active" : ""}`}
                      onClick={() => setComparisonScope("all")}
                      style={{ fontSize: "11px", padding: "4px 9px", fontWeight: 700 }}
                    >
                      \xf0\x9f\x8c\x8d Tout le Grand Sud ({communes.length})
                    </button>
                  </div>

                  <input
                    type="text"
                    placeholder="\xf0\x9f\x94\x8d Filtrer une commune..."
                    value={comparisonSearch}
                    onChange={(e) => setComparisonSearch(e.target.value)}
                    style={{
                      padding: "5px 10px",
                      fontSize: "11.5px",
                      borderRadius: "6px",
                      border: "1px solid var(--border-color)",
                      backgroundColor: "var(--bg-panel-secondary)",
                      color: "var(--text-main)",
                      width: "180px",
                    }}
                  />
                </div>
              </div>

              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
                  <thead>
                    <tr style={{ borderBottom: "2px solid var(--border-color)", textAlign: "left", color: "var(--text-muted)" }}>
                      <th style={{ padding: "8px 10px" }}>Commune</th>
                      {comparisonScope !== "district" && (
                        <th style={{ padding: "8px 10px" }}>District</th>
                      )}
                      {comparisonScope === "all" && (
                        <th style={{ padding: "8px 10px" }}>R\xc3\xa9gion</th>
                      )}
                      <th style={{ padding: "8px 10px" }}>R\xc3\xa9action imm\xc3\xa9diate (Lag 0)</th>
                      <th style={{ padding: "8px 10px" }}>Reverdissement (Lag 1)</th>
                      <th style={{ padding: "8px 10px" }}>D\xc3\xa9lai optimal</th>
                      <th style={{ padding: "8px 10px" }}>Part de variance (R\xc2\xb2)</th>
                      <th style={{ padding: "8px 10px" }}>D\xc3\xa9pendance \xc3\xa0 la pluie</th>
                      <th style={{ padding: "8px 10px", textAlign: "right" }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedComparisonList.map((row) => {
                      const isActive = row.code === activeCommuneObj?.code;
                      return (
                        <tr
                          key={row.code}
                          style={{
                            borderBottom: "1px solid var(--border-color)",
                            backgroundColor: isActive ? "rgba(22, 163, 74, 0.08)" : "transparent",
                            fontWeight: isActive ? "700" : "400",
                          }}
                        >
                          <td style={{ padding: "8px 10px", color: "var(--text-main)" }}>
                            <strong style={{ color: isActive ? "#16a34a" : "var(--text-main)" }}>{row.nom}</strong>
                            {isActive && <span style={{ marginLeft: "6px", color: "#16a34a" }}>\xe2\x98\x85</span>}
                          </td>
                          {comparisonScope !== "district" && (
                            <td style={{ padding: "8px 10px", color: "var(--text-muted)", fontSize: "11px" }}>{row.district}</td>
                          )}
                          {comparisonScope === "all" && (
                            <td style={{ padding: "8px 10px", color: "var(--text-muted)", fontSize: "11px" }}>{row.region}</td>
                          )}
                          <td style={{ padding: "8px 10px", color: "#f59e0b" }}>{row.r0 > 0 ? `+${row.r0}` : row.r0}</td>
                          <td style={{ padding: "8px 10px", color: "#16a34a", fontWeight: "700" }}>{row.r1 > 0 ? `+${row.r1}` : row.r1}</td>
                          <td style={{ padding: "8px 10px" }}>{row.opt}</td>
                          <td style={{ padding: "8px 10px", fontWeight: "700" }}>{row.r2}</td>
                          <td style={{ padding: "8px 10px", color: row.statusColor, fontWeight: "600" }}>{row.status}</td>
                          <td style={{ padding: "8px 10px", textAlign: "right" }}>
                            {!isActive ? (
                              <button
                                type="button"
                                onClick={() => handleSelectCommune(row.code)}
                                style={{
                                  padding: "4px 10px",
                                  fontSize: "11px",
                                  fontWeight: "700",
                                  borderRadius: "5px",
                                  border: "1px solid var(--border-color)",
                                  backgroundColor: "var(--bg-panel-secondary)",
                                  color: "var(--primary)",
                                  cursor: "pointer",
                                }}
                              >
                                Analyser
                              </button>
                            ) : (
                              <span style={{ fontSize: "11px", color: "#16a34a", fontWeight: "800", padding: "3px 8px", backgroundColor: "rgba(22, 163, 74, 0.12)", borderRadius: "4px" }}>
                                Active
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Contr\xc3\xb4les de Pagination */}
              {totalComparisonPages > 1 && (
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "14px", paddingTop: "12px", borderTop: "1px solid var(--border-color)", flexWrap: "wrap", gap: "8px" }}>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                    Affichage <strong>{(comparisonPage - 1) * comparisonPageSize + 1}</strong> \xc3\xa0 <strong>{Math.min(comparisonPage * comparisonPageSize, fullComparisonList.length)}</strong> sur <strong>{fullComparisonList.length}</strong> communes
                  </span>
                  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <button
                      type="button"
                      disabled={comparisonPage <= 1}
                      onClick={() => setComparisonPage((p) => Math.max(1, p - 1))}
                      style={{
                        padding: "4px 10px",
                        fontSize: "11px",
                        borderRadius: "5px",
                        border: "1px solid var(--border-color)",
                        backgroundColor: comparisonPage <= 1 ? "var(--bg-app)" : "var(--bg-panel-secondary)",
                        color: comparisonPage <= 1 ? "var(--text-muted)" : "var(--text-main)",
                        cursor: comparisonPage <= 1 ? "not-allowed" : "pointer",
                      }}
                    >
                      \xe2\x97\x80 Pr\xc3\xa9c.
                    </button>
                    <span style={{ fontSize: "11px", fontWeight: "700", color: "var(--text-main)", padding: "0 6px" }}>
                      Page {comparisonPage} / {totalComparisonPages}
                    </span>
                    <button
                      type="button"
                      disabled={comparisonPage >= totalComparisonPages}
                      onClick={() => setComparisonPage((p) => Math.min(totalComparisonPages, p + 1))}
                      style={{
                        padding: "4px 10px",
                        fontSize: "11px",
                        borderRadius: "5px",
                        border: "1px solid var(--border-color)",
                        backgroundColor: comparisonPage >= totalComparisonPages ? "var(--bg-app)" : "var(--bg-panel-secondary)",
                        color: comparisonPage >= totalComparisonPages ? "var(--text-muted)" : "var(--text-main)",
                        cursor: comparisonPage >= totalComparisonPages ? "not-allowed" : "pointer",
                      }}
                    >
                      Suiv. \xe2\x96\xb6
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}"""

content_norm = content.replace(b"\r\n", b"\n")
old_list_norm = old_list_code.replace(b"\r\n", b"\n")
new_list_norm = new_list_code.replace(b"\r\n", b"\n")
old_table_norm = old_table_jsx.replace(b"\r\n", b"\n")
new_table_norm = new_table_jsx.replace(b"\r\n", b"\n")

if old_list_norm in content_norm and old_table_norm in content_norm:
    content_norm = content_norm.replace(old_list_norm, new_list_norm)
    content_norm = content_norm.replace(old_table_norm, new_table_norm)
    with open("src/main.jsx", "wb") as f:
        f.write(content_norm.replace(b"\n", b"\r\n"))
    print("SUCCESS: src/main.jsx updated with multi-scale comparison table!")
else:
    print("MATCH ERROR:", old_list_norm in content_norm, old_table_norm in content_norm)
