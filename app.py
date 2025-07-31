import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from datetime import datetime
import pyautogui

# ========================
# CONFIGURACIÓN STREAMLIT
# ========================
st.set_page_config(page_title="Semáforo de Cumplimiento", layout="centered")

st.title("📊 Semáforo de Cumplimiento de Meta")

# ========================
# CONEXIÓN A POSTGRESQL
# ========================
DB_URL = "postgresql+psycopg2://postgres:vZveOcrYtjNytGbiMrFJJordeIEfIBkQ@centerbeam.proxy.rlwy.net:48362/railway"
engine = create_engine(DB_URL)

# Meta fija
META = 6868529.00

# ========================
# FUNCIÓN PARA CARGAR DATOS
# ========================
@st.cache_data
def cargar_datos():
    query = 'SELECT * FROM pagos_mes WHERE "Tipo_Cartera" = \'Propia\''
    df = pd.read_sql(query, engine)
    return df

df = cargar_datos()

# ========================
# CÁLCULOS
# ========================
total_monto = df["Monto"].sum()
cumplimiento = (total_monto / META) * 100

# ========================
# DETERMINAR COLOR DEL SEMÁFORO
# ========================
if cumplimiento >= 90:
    color = "green"
elif cumplimiento >= 70:
    color = "yellow"
else:
    color = "red"

# ========================
# MOSTRAR RESULTADOS
# ========================
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

# ========================
# BOTÓN PARA CAPTURA DE PANTALLA
# ========================
if st.button("📷 Guardar captura de pantalla"):
    archivo = f"semaforo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pyautogui.screenshot(archivo)
    st.success(f"Captura guardada como {archivo}")
    st.image(archivo, caption="Vista actual")

# ========================
# MOSTRAR TABLA DE DATOS
# ========================
with st.expander("Ver datos filtrados"):
    st.dataframe(df)
