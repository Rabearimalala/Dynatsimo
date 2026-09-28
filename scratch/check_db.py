from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:admin@localhost:5432/dynatsimo')
with engine.connect() as conn:
    tables = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")).fetchall()
    print('Tables in public schema:', [t[0] for t in tables])
    for t in tables:
        tname = t[0]
        cols = conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{tname}'")).fetchall()
        print(f"\n--- Columns in {tname} ---")
        for col, dtype in cols:
            print(f"  {col}: {dtype}")
        count = conn.execute(text(f'SELECT COUNT(*) FROM "{tname}"')).scalar()
        print(f"  Total rows: {count}")
