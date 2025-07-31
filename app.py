import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from datetime import datetime

# ========================
# CONFIGURACIÓN STREAMLIT
# ========================
st.set_page_config(page_title="Semáforo de Cumplimiento", layout="centered")

st.title("📊 Cumplimiento de Meta de País")

# ========================
# CONEXIÓN A POSTGRESQL
# ========================
DB_URL = "postgresql+psycopg2://postgres:vZveOcrYtjNytGbiMrFJJordeIEfIBkQ@centerbeam.proxy.rlwy.net:48362/railway"
engine = create_engine(DB_URL)

# Meta fija
META = 6868529.00

# ========================
# FUNCIÓN PARA OBTENER DATOS ACTUALIZADOS
# ========================
def obtener_datos_actualizados():
    query = 'SELECT * FROM pagos_mes WHERE "Tipo_Cartera" = \'Propia\''
    df = pd.read_sql(query, engine)
    return df

# ========================
# CÁLCULOS Y SEMÁFORO
# ========================
def calcular_cumplimiento(df):
    total_monto = df["Monto"].sum()
    cumplimiento = (total_monto / META) * 100

    # Determinar el color del semáforo
    if cumplimiento >= 90:
        color = "green"
    elif cumplimiento >= 60:
        color = "yellow"
    else:
        color = "red"
    
    return total_monto, cumplimiento, color

# ========================
# BOTÓN PARA OBTENER DATOS ACTUALIZADOS
# ========================
if st.button('Actualizar Datos'):
    df = obtener_datos_actualizados()
    total_monto, cumplimiento, color = calcular_cumplimiento(df)

    # Mostrar resultados
    st.markdown(f"""
    ### 📌 Meta: **{META:,.2f}**
    ### 💰 Recuperado: **{total_monto:,.2f}**
    ### 📈 Cumplimiento: **{cumplimiento:.2f}%**
    """)

    st.markdown(
        f"""
        <div style="text-align: center;">
            <div style="width: 150px; height: 150px; border-radius: 50%; background-color: {color}; margin: auto;"></div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.write("Haz clic en el botón 'Actualizar Datos' para cargar los datos más recientes.")
