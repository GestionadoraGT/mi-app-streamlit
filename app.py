import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from PIL import Image
import time
import os

# ---------------- CONFIGURACIÓN ----------------
DB_URL = "postgresql://postgres:vZveOcrYtjNytGbiMrFJJordeIEfIBkQ@centerbeam.proxy.rlwy.net:48362/railway"
META_OBJETIVO = 6868529.00  # Meta fija

# ---------------- FUNCIONES ----------------
@st.cache_data
def cargar_datos():
    engine = create_engine(DB_URL)
    query = "SELECT * FROM pagos_mes WHERE tipo_cartera = 'Propia'"
    df = pd.read_sql(query, engine)
    return df

def calcular_cumplimiento(df):
    total = df["monto"].sum()
    porcentaje = (total / META_OBJETIVO) * 100
    return total, porcentaje

def mostrar_semaforo(porcentaje):
    if porcentaje < 60:
        color = "red"
    elif porcentaje < 90:
        color = "yellow"
    else:
        color = "green"
    st.markdown(
        f"<div style='background-color:{color};padding:30px;border-radius:15px;'>"
        f"<h2 style='text-align:center;color:white;'>Cumplimiento: {porcentaje:.2f}%</h2></div>",
        unsafe_allow_html=True
    )

def capturar_pantalla():
    # Usaremos PIL para capturar la pantalla sin Selenium
    time.sleep(2)  # Esperar para cargar contenido
    img = Image.open("screenshot.png")
    img.save("captura.png")
    return "captura.png"

# ---------------- APP STREAMLIT ----------------
st.set_page_config(page_title="Cumplimiento de Meta", layout="centered")

# Título y descripción
st.title("📊 **Seguimiento de Cumplimiento de Meta - Cartera Propia**")
st.markdown("### Esta app muestra el cumplimiento de la meta de recuperación de cartera 'Propia'.")

# Cargar datos
df = cargar_datos()

# Calcular cumplimiento
total, porcentaje = calcular_cumplimiento(df)

# Mostrar resultados de cumplimiento
col1, col2 = st.columns(2)
col1.metric("Meta Objetivo", f"${META_OBJETIVO:,.2f}")
col2.metric("Recuperado", f"${total:,.2f}")

# Semáforo de cumplimiento
mostrar_semaforo(porcentaje)

# Mostrar tabla con los datos de recuperación
st.subheader("📝 Tabla de Recuperación - Cartera Propia")
st.dataframe(df)

# Botón para capturar pantalla
if st.button("📸 Capturar Pantalla"):
    archivo = capturar_pantalla()
    st.success("Captura guardada correctamente.")
    st.image(archivo, use_column_width=True)

# Pie de página
st.markdown("### © 2025 - Desarrollo por [Tu Nombre]")
