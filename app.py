import pandas as pd
from sqlalchemy import create_engine

# 🔗 Conexión (ajusta tus credenciales reales)
DB_URL = "postgresql+psycopg2://<USUARIO>:<PASSWORD>@<HOST>/<DB>"
engine = create_engine(DB_URL)

# 📥 Leer datos de la tabla pagos_mes
try:
    df = pd.read_sql("SELECT * FROM pagos_mes", engine)
    print("✅ Registros obtenidos de pagos_mes:")
    print(df.head())  # muestra los primeros registros
    print(f"Total de registros: {len(df)}")
except Exception as e:
    print("❌ Error al consultar la tabla:", e)
