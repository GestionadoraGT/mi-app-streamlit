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

# ========================
# META FIJA
# ========================
META = 6912843.60

# ========================
# INICIALIZAR VARIABLES
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

# ========================
# CÁLCULOS
# ========================
def calcular_cumplimiento(df):
    if df.empty:
        return 0.0, 0.0, "red"
    try:
        df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce")
        df = df.dropna(subset=["Monto"])
        
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
    except Exception as e:
        st.error(f"Error calculando cumplimiento: {e}")
        return 0.0, 0.0, "red"

# ========================
# CÁLCULO DE DÍAS RESTANTES
# ========================
def calcular_dias_restantes():
    hoy = datetime.now()
    if hoy.month == 12:
        fin_mes = hoy.replace(day=31)
    else:
        fin_mes = (hoy.replace(day=1, month=hoy.month + 1) - timedelta(days=1))

    feriados_fijos = [
        (15, 8), (15, 9), (20, 10), (1, 11),
        (24, 12), (25, 12), (31, 12)
    ]
    feriados = [datetime(hoy.year, m, d) for d, m in feriados_fijos]

    dias_habiles = 0
    fecha_actual = hoy + timedelta(days=1)
    while fecha_actual <= fin_mes:
        if fecha_actual.weekday() < 5 and fecha_actual not in feriados:
            dias_habiles += 1
        fecha_actual += timedelta(days=1)
    return dias_habiles

# ========================
# INTERFAZ PRINCIPAL
# ========================
if engine is None:
    st.error("❌ No se pudo conectar a la base de datos.")
    st.stop()

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    actualizar = st.button("🔄 Actualizar Datos")
with col_btn2:
    if st.button("🔗 Probar Conexión"):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            st.success("✅ Conexión exitosa")
        except Exception as e:
            st.error(f"❌ Error de conexión: {e}")

# ========================
# CARGA Y REFRESCO
# ========================
if actualizar or st.session_state["total_monto"] == 0:
    with st.spinner("Cargando datos..."):
        st.session_state["datos"] = obtener_datos_actualizados()
        if not st.session_state["datos"].empty:
            st.session_state["total_monto"], st.session_state["cumplimiento"], st.session_state["color"] = calcular_cumplimiento(st.session_state["datos"])
            st.success(f"✅ {len(st.session_state['datos'])} registros cargados.")
        else:
            st.session_state["total_monto"] = 0.0
            st.session_state["cumplimiento"] = 0.0
            st.session_state["color"] = "red"

# ========================
# MOSTRAR RESULTADOS
# ========================
if not st.session_state["datos"].empty:
    dias_restantes = calcular_dias_restantes()
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
        ### 📌 Meta: **Q{META:,.2f}**
        ### 💰 Recuperado: **Q{st.session_state['total_monto']:,.2f}**
        ### 📈 Cumplimiento: **{st.session_state['cumplimiento']:.2f}%**
        ### 📅 Días Restantes: **{dias_restantes} hábiles**
        """)
        st.progress(min(st.session_state["cumplimiento"]/100, 1.0))

    with col2:
        semaforo_emoji = {"green": "🟢", "yellow": "🟡", "orange": "🟠", "red": "🔴"}
        st.markdown(f"<div style='text-align: center; font-size: 80px;'>{semaforo_emoji[st.session_state['color']]}</div>", unsafe_allow_html=True)
        ruta_imagen = f"imagenes/semaforo_{st.session_state['color']}.png"
        if os.path.exists(ruta_imagen):
            st.image(ruta_imagen, width=220)

    with st.expander("📊 Detalles de los Datos"):
        st.write(f"**Total de registros:** {len(st.session_state['datos'])}")
        st.write(f"**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.dataframe(st.session_state["datos"].head())

else:
    st.info("📋 No hay datos disponibles.")
    if st.button("🔍 Verificar Tablas Disponibles"):
        try:
            tablas = pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'", engine)
            st.dataframe(tablas if not tablas.empty else pd.DataFrame(["No hay tablas"]))
        except Exception as e:
            st.error(f"Error verificando tablas: {e}")
