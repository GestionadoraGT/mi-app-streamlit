import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
import os
from datetime import datetime, timedelta

# 🔹 Desactivar watcher de archivos de Streamlit
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

# ========================
# CONFIGURACIÓN STREAMLIT
# ========================
st.set_page_config(page_title="Semáforo de Cumplimiento", layout="centered")
st.title("📊 Cumplimiento de Meta de País")

# ========================
# CONEXIÓN A POSTGRESQL
# ========================
DB_URL = "postgresql+psycopg2://neondb_owner:npg_3nHTy8MfYejc@ep-patient-union-abhem53z-pooler.eu-west-2.aws.neon.tech:5432/neondb?sslmode=require"

@st.cache_resource
def crear_conexion():
    try:
        engine = create_engine(DB_URL)
        # Probar conexión mínima
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"❌ Error conectando a la base de datos: {e}")
        return None

engine = crear_conexion()

# Meta fija
META = 6912843.60

# ========================
# FUNCIÓN PARA OBTENER DATOS
# ========================
@st.cache_data(ttl=300)
def obtener_datos_actualizados():
    if engine is None:
        return pd.DataFrame()
    
    try:
        # Verificar si la tabla existe
        tablas = pd.read_sql(
            "SELECT table_name FROM information_schema.tables WHERE table_name = 'pagos_mes'",
            engine
        )
        
        if tablas.empty:
            st.warning("⚠️ La tabla 'pagos_mes' no existe en la base.")
            return pd.DataFrame()
        
        # Traer solo Tipo_Cartera = 'Propia'
        df = pd.read_sql('SELECT * FROM pagos_mes WHERE "Tipo_Cartera" = \'Propia\'', engine)
        
        if df.empty:
            st.warning("⚠️ No hay registros con Tipo_Cartera = 'Propia'")
            return pd.DataFrame()
        
        if "Monto" not in df.columns:
            st.error("❌ No existe columna 'Monto'. Columnas disponibles:")
            st.write(df.columns.tolist())
            return pd.DataFrame()
        
        return df
    except Exception as e:
        st.error(f"❌ Error consultando datos: {e}")
        return pd.DataFrame()
