import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from datetime import datetime
import pyautogui
import base64
from io import BytesIO
import os

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
# FUNCION PARA CAPTURAR LA IMAGEN EN LA NUBE
# ========================
def get_screenshot():
    screenshot = st.capture_screenshot()
    img_buffer = BytesIO(screenshot)
    img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_data}"

# ========================
# BOTÓN PARA CAPTURA DE PANTALLA
# ========================
if st.button("📷 Guardar captura de pantalla"):
    # Verificar si el código está corriendo en Streamlit Cloud o local
    if 'pyautogui' in globals():  # Solo si pyautogui está disponible (local)
        archivo = f"semaforo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(archivo)
        st.success(f"Captura guardada como {archivo}")
        st.image(archivo, caption="Vista actual")
    else:
        # En la nube (Streamlit Cloud)
        st.markdown(f"""
            <div style="display: flex; justify-content: center; align-items: center;">
                <img src="{get_screenshot()}" alt="Captura de pantalla" width="400" />
            </div>
        """, unsafe_allow_html=True)

# ========================
# MOSTRAR TABLA DE DATOS
# ========================
with st.expander("Ver datos filtrados"):
    st.dataframe(df)
