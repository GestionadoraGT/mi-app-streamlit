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
META = 6912854.00

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
    if cumplimiento >= 75:
        color = "green"
    elif cumplimiento >= 50:
        color = "yellow"
    elif cumplimiento >= 25:
        color = "orange"
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

# ========================
# MOSTRAR RESULTADOS Y SEMÁFORO
# ========================
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(f"""
    ### 📌 Meta: **{META:,.2f}**
    ### 💰 Recuperado: **{st.session_state['total_monto']:,.2f}**
    ### 📈 Cumplimiento: **{st.session_state['cumplimiento']:.2f}%**
    """)

with col2:
    ruta_imagen = f"imagenes/semaforo_{st.session_state['color']}.png"
    if os.path.exists(ruta_imagen):
        st.image(ruta_imagen, width=120)  # Tamaño ajustado para que no sea gigante
    else:
        st.warning(f"No se encontró la imagen para el color **{st.session_state['color']}**")
    