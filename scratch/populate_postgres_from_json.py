import json
import sys
import time
import pandas as pd
from sqlalchemy import create_engine, text

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

engine = create_engine('postgresql://postgres:admin@localhost:5432/dynatsimo')

t0 = time.time()
with open('public/data/precip-records.json', 'r', encoding='utf-8') as f:
    records = json.load(f)

df = pd.DataFrame(records)
print(f"Charge {len(df)} enregistrements depuis precip-records.json en {time.time()-t0:.2f}s")

df = df.rename(columns={
    'code': 'Commune_Id',
    'year': 'Year',
    'month': 'Month',
    'precip': 'Precip'
})

with engine.begin() as conn:
    conn.execute(text('DROP TABLE IF EXISTS public.precipitation CASCADE'))
    conn.execute(text('''
        CREATE TABLE public.precipitation (
            "Commune_Id" TEXT NOT NULL,
            "Year" INTEGER NOT NULL,
            "Month" INTEGER NOT NULL,
            "Precip" DOUBLE PRECISION,
            PRIMARY KEY ("Commune_Id", "Year", "Month")
        )
    '''))

print("Table public.precipitation creee.")

t1 = time.time()
df.to_sql('precipitation', engine, schema='public', if_exists='append', index=False, chunksize=10000)
print(f"Insertion terminee : {len(df)} lignes inserees en {time.time()-t1:.2f}s !")

with engine.connect() as conn:
    count = conn.execute(text('SELECT COUNT(*) FROM public.precipitation')).scalar()
    distinct_dates = conn.execute(text('SELECT COUNT(DISTINCT ("Year", "Month")) FROM public.precipitation')).scalar()
    min_year = conn.execute(text('SELECT MIN("Year"), MIN("Month") FROM public.precipitation')).first()
    max_year = conn.execute(text('SELECT MAX("Year"), MAX("Month") FROM public.precipitation')).first()
    print(f"Verification PostgreSQL : {count} lignes inserees ({distinct_dates} mois uniques de {min_year[0]}-{min_year[1]:02d} a {max_year[0]}-{max_year[1]:02d})")
