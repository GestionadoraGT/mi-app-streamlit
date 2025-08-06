import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
import os
from datetime import datetime, timedelta

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
# INICIALIZAR VARIABLES EN SESSION STATE
# ========================
if "total_monto" not in st.session_state:
    st.session_state["total_monto"] = 0.0
if "cumplimiento" not in st.session_state:
    st.session_state["cumplimiento"] = 0.0
if "color" not in st.session_state:
    st.session_state["color"] = "red"
if "datos" not in st.session_state:
    st.session_state["datos"] = pd.DataFrame()

# ========================
# FUNCIÓN PARA OBTENER DATOS ACTUALIZADOS
# ========================
@st.cache_data(ttl=300)
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
# CÁLCULO AUTOMÁTICO DE DÍAS RESTANTES
# ========================
def calcular_dias_restantes():
    hoy = datetime.now()
    # último día del mes
    if hoy.month == 12:
        fin_mes = hoy.replace(day=31)
    else:
        fin_mes = (hoy.replace(day=1, month=hoy.month + 1) - timedelta(days=1))
    
    dias_restantes = (fin_mes - hoy).days + 1  # incluir hoy

    # Lista de feriados fijos en Guatemala (día, mes)
    feriados = [
        (15, 8),  # 15 de agosto
        (15, 9),  # 15 de septiembre
        # Agrega más feriados si quieres
    ]
    
    # Restar feriados dentro del rango
    for dia, mes in feriados:
        fecha_feriado = datetime(hoy.year, mes, dia)
        if hoy <= fecha_feriado <= fin_mes:
            dias_restantes -= 1

    return dias_restantes

# ========================
# CARGA AUTOMÁTICA Y REFRESCO
# ========================
if st.button('🔄 Actualizar Datos') or st.session_state["total_monto"] == 0:
    st.session_state["datos"] = obtener_datos_actualizados()
    st.session_state["total_monto"], st.session_state["cumplimiento"], st.session_state["color"] = calcular_cumplimiento(st.session_state["datos"])

# ========================
# MOSTRAR RESULTADOS Y SEMÁFORO
# ========================
dias_restantes = calcular_dias_restantes()

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"""
    ###  
    ### 📌 Meta: **{META:,.2f}**
    ### 💰 Recuperado: **{st.session_state['total_monto']:,.2f}**
    ### 📈 Cumplimiento: **{st.session_state['cumplimiento']:.2f}%**
    ### 📅 Días Restantes: **{dias_restantes} hábiles**
    """)

with col2:
    ruta_imagen = f"imagenes/semaforo_{st.session_state['color']}.png"
    if os.path.exists(ruta_imagen):
        st.image(ruta_imagen, width=220)
    else:
        st.warning(f"No se encontró la imagen para el color **{st.session_state['color']}**")
