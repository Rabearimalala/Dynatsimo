# -*- coding: utf-8 -*-
import sys

with open("src/main.jsx", "rb") as f:
    raw = f.read()

content = raw.replace(b"\r\n", b"\n")

# 1. Update staticDataFiles
old_static_files = b"""  isohyetesMeta: "/data/isohyetes_metadata.json",
  ndviChirpsMeta: "/data/ndvi_chirps_metadata.json",
};"""

new_static_files = b"""  isohyetesMeta: "/data/isohyetes_metadata.json",
  ndviChirpsMeta: "/data/ndvi_chirps_metadata.json",
  correlationNdviChirps: "/data/correlation_ndvi_chirps.json",
};"""

# 2. Update loadAppData
old_load_app = b"""  try {
    if (!apiData.ndviChirpsMeta) {
      const ndviChirpsMeta = await fetchJson(`/data/ndvi_chirps_metadata.json`);
      apiData.ndviChirpsMeta = ndviChirpsMeta;
    }
  } catch (e) {
    console.warn("ndviChirpsMeta non trouv\xc3\xa9es", e);
  }
  return {"""

new_load_app = b"""  try {
    if (!apiData.ndviChirpsMeta) {
      const ndviChirpsMeta = await fetchJson(`/data/ndvi_chirps_metadata.json`);
      apiData.ndviChirpsMeta = ndviChirpsMeta;
    }
  } catch (e) {
    console.warn("ndviChirpsMeta non trouv\xc3\xa9es", e);
  }
  try {
    if (!apiData.correlationNdviChirps) {
      const correlationNdviChirps = await fetchJson(`/data/correlation_ndvi_chirps.json`);
      apiData.correlationNdviChirps = correlationNdviChirps;
    }
  } catch (e) {
    console.warn("correlationNdviChirps non trouv\xc3\xa9es", e);
  }
  return {"""

# 3. Sidebar sub-list for tab.id === "data"
old_sidebar_data = b"""                  {/* Sous-onglets de Base de Donn\xc3\xa9es dans la barre lat\xc3\xa9rale gauche */}
                  {tab.id === "data" && activeTab === "data" && (
                    <div className="nav-sub-list">
                      {[
                        { id: "precip", label: "\xf0\x9f\x8c\xa7\xef\xb8\x8f Pluviom\xc3\xa9trie (CHIRPS)" },
                        { id: "vegetation", label: "\xf0\x9f\x8c\xbf V\xc3\xa9g\xc3\xa9tation (MODIS)" },
                      ].map((sub) => ("""

new_sidebar_data = b"""                  {/* Sous-onglets de Base de Donn\xc3\xa9es dans la barre lat\xc3\xa9rale gauche */}
                  {tab.id === "data" && activeTab === "data" && (
                    <div className="nav-sub-list">
                      {[
                        { id: "precip", label: "\xf0\x9f\x8c\xa7\xef\xb8\x8f Pluviom\xc3\xa9trie (CHIRPS)" },
                        { id: "vegetation", label: "\xf0\x9f\x8c\xbf V\xc3\xa9g\xc3\xa9tation (MODIS)" },
                        { id: "correlation", label: "\xf0\x9f\x94\x97 Corr\xc3\xa9lation (NDVI / CHIRPS)" },
                      ].map((sub) => ("""

# 4. In UnifiedSinglePage and activeTab === "data" pass correlationData
old_tableau_call1 = b"""          {activeTab === "data" && (
            <TableauExplorer
              geojson={data.communesGeojson}
              communesList={data.communes}
              datasetType={dataCategory}
              setDatasetType={setDataCategory}
              precipRecords={data.precipRecords}
              annualData={data.annualData}
              seasonData={data.seasonData}
              vegData={data.vegetationData}
            />
          )}"""

new_tableau_call1 = b"""          {activeTab === "data" && (
            <TableauExplorer
              geojson={data.communesGeojson}
              communesList={data.communes}
              datasetType={dataCategory}
              setDatasetType={setDataCategory}
              precipRecords={data.precipRecords}
              annualData={data.annualData}
              seasonData={data.seasonData}
              vegData={data.vegetationData}
              correlationData={data.correlationNdviChirps}
            />
          )}"""

old_tableau_call2 = b"""        <TableauExplorer
          geojson={data.communesGeojson}
          communesList={data.communes}
          datasetType={dataCategory}
          setDatasetType={setDataCategory}
          precipRecords={data?.precipRecords || []}
          annualData={data?.annualData || []}
          seasonData={data?.seasonData || []}
          vegData={data?.vegetationData || {}}
        />"""

new_tableau_call2 = b"""        <TableauExplorer
          geojson={data.communesGeojson}
          communesList={data.communes}
          datasetType={dataCategory}
          setDatasetType={setDataCategory}
          precipRecords={data?.precipRecords || []}
          annualData={data?.annualData || []}
          seasonData={data?.seasonData || []}
          vegData={data?.vegetationData || {}}
          correlationData={data?.correlationNdviChirps}
        />"""

checks = [
    ("old_static_files", old_static_files in content),
    ("old_load_app", old_load_app in content),
    ("old_sidebar_data", old_sidebar_data in content),
    ("old_tableau_call1", old_tableau_call1 in content),
    ("old_tableau_call2", old_tableau_call2 in content),
]

all_ok = True
for name, found in checks:
    print(f"{name}: {found}")
    if not found:
        all_ok = False

if not all_ok:
    print("ABORTING: Not all targets matched.")
    sys.exit(1)

content = content.replace(old_static_files, new_static_files, 1)
content = content.replace(old_load_app, new_load_app, 1)
content = content.replace(old_sidebar_data, new_sidebar_data, 1)
content = content.replace(old_tableau_call1, new_tableau_call1, 1)
content = content.replace(old_tableau_call2, new_tableau_call2, 1)

with open("src/main.jsx", "wb") as f:
    f.write(content.replace(b"\n", b"\r\n"))

print("SUCCESS: Part 1 (staticFiles, loadAppData, sidebar, callers) updated!")
