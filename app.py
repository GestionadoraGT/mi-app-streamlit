import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# ========================
# CONFIGURACIÓN
# ========================
st.set_page_config(page_title="Prueba Conexión DB", layout="centered")
st.title("🔗 Test conexión PostgreSQL")

DB_URL = "postgresql+psycopg2://neondb_owner:npg_3nHTy8MfYejc@ep-patient-union-abhem53z-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"

# ========================
# PROBAR CONEXIÓN
# ========================
try:
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    st.success("✅ Conexión exitosa con la base de datos.")

    # Mostrar tablas disponibles
    query = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tablas = pd.read_sql(query, engine)

    if not tablas.empty:
        st.write("**Tablas encontradas en la base:**")
        st.dataframe(tablas)
    else:
        st.warning("⚠️ No hay tablas en el esquema 'public'.")

except Exception as e:
    st.error(f"❌ Error conectando a la base de datos: {e}")
