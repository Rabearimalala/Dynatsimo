import json
import time
import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:admin@localhost:5432/precipitation")

t0 = time.time()
with open("public/data/precip-records.json", "r", encoding="utf-8") as f:
    records = json.load(f)

df = pd.DataFrame(records)
print(f"Chargé {len(df)} enregistrements en {time.time()-t0:.2f}s")

df = df.rename(columns={
    "code": "Commune_Id",
    "year": "Year",
    "month": "Month",
    "precip": "Precip"
})

with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS public.precipitation CASCADE"))
    conn.execute(text("""
        CREATE TABLE public.precipitation (
            "Commune_Id" TEXT NOT NULL,
            "Year" INTEGER NOT NULL,
            "Month" INTEGER NOT NULL,
            "Precip" DOUBLE PRECISION,
            PRIMARY KEY ("Commune_Id", "Year", "Month")
        )
    """))

print("Table public.precipitation créée.")
t1 = time.time()
df.to_sql("precipitation", engine, schema="public", if_exists="append", index=False, chunksize=10000)
print(f"Insertion terminée : {len(df)} lignes en {time.time()-t1:.2f}s !")

with engine.connect() as conn:
    count = conn.execute(text("SELECT COUNT(*) FROM public.precipitation")).scalar()
    print(f"Total lignes vérifiées dans public.precipitation : {count}")
