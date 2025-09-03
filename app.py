import pandas as pd
from sqlalchemy import create_engine

DB_URL = "postgresql+psycopg2://neondb_owner:npg_3nHTy8MfYejc@ep-patient-union-abhem53z-pooler.eu-west-2.aws.neon.tech:5432/neondb?sslmode=require&channel_binding=require"

engine = create_engine(DB_URL)

try:
    df = pd.read_sql("SELECT * FROM pagos_mes", engine)
    print("✅ Registros obtenidos de pagos_mes:")
    print(df.head())
    print(f"Total de registros: {len(df)}")
except Exception as e:
    print("❌ Error al consultar la tabla:", e)
