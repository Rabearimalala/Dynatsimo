# Python script to fix useGeoServerWms in src/main.jsx
with open('src/main.jsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
modified_state = False
modified_toggle = False

for line in lines:
    if 'const [useGeoServerWms, setUseGeoServerWms] = React.useState(true);' in line:
        new_lines.append('  const [useGeoServerWms, setUseGeoServerWms] = React.useState(false);\n')
        new_lines.append('  const [isGeoServerAvailable, setIsGeoServerAvailable] = React.useState(false);\n')
        modified_state = True
    elif 'const geoserverUrl = "/geoserver";' in line:
        new_lines.append(line)
        new_lines.append('\n')
        new_lines.append('  // Vérification de la disponibilité de GeoServer en arrière-plan\n')
        new_lines.append('  React.useEffect(() => {\n')
        new_lines.append('    fetch(`${geoserverUrl}/rest/about/version.json`)\n')
        new_lines.append('      .then((res) => {\n')
        new_lines.append('        if (res.ok) {\n')
        new_lines.append('          setIsGeoServerAvailable(true);\n')
        new_lines.append('        } else {\n')
        new_lines.append('          setIsGeoServerAvailable(false);\n')
        new_lines.append('          setUseGeoServerWms(false);\n')
        new_lines.append('        }\n')
        new_lines.append('      })\n')
        new_lines.append('      .catch(() => {\n')
        new_lines.append('        setIsGeoServerAvailable(false);\n')
        new_lines.append('        setUseGeoServerWms(false);\n')
        new_lines.append('      });\n')
        new_lines.append('  }, []);\n')
    elif '{/* Superposition de la Couche Communes */}' in line and not modified_toggle:
        # Re-add the clean GeoServer WMS / PNG toggle right above Superposition de la Couche Communes
        toggle_code = '''            {/* Sélecteur de Source Raster : PNG local vs GeoServer WMS */}
            <div className="layer-toggle-group" style={{ marginTop: "8px", padding: "8px 10px", background: "var(--bg-secondary, #f8fafc)", borderRadius: "6px", border: "1px solid var(--border-color, #e2e8f0)" }}>
              <label className="layer-toggle-label" style={{ fontWeight: 600, fontSize: "11.5px", display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer" }}>
                <span>Source : Flux GeoServer WMS</span>
                <input
                  type="checkbox"
                  checked={useGeoServerWms}
                  onChange={(e) => setUseGeoServerWms(e.target.checked)}
                />
              </label>
              <div style={{ fontSize: "10.5px", color: useGeoServerWms ? "#16a34a" : "#64748b", marginTop: "3px", display: "flex", alignItems: "center", gap: "4px" }}>
                {useGeoServerWms
                  ? (isGeoServerAvailable ? "● Connecté à GeoServer (WMS)" : "⚠ GeoServer non détecté (port 8080)")
                  : "✓ Mode images PNG locales (319 rasters 250m)"}
              </div>
            </div>

'''
        new_lines.append(toggle_code)
        new_lines.append(line)
        modified_toggle = True
    else:
        new_lines.append(line)

assert modified_state, "Could not find useGeoServerWms state definition!"
assert modified_toggle, "Could not find toggle insertion point!"

with open('src/main.jsx', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("SUCCESS: src/main.jsx updated with useGeoServerWms=false default and UI toggle!")
