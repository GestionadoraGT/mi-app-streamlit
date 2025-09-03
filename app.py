import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
import os
# 🔹 Desactivar watcher de archivos de Streamlit
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
from datetime import datetime, timedelta

# ========================
# CONFIGURACIÓN STREAMLIT
# ========================
st.set_page_config(page_title="Semáforo de Cumplimiento", layout="centered")
st.title("📊 Cumplimiento de Meta de País")

# ========================
# CONEXIÓN A POSTGRESQL
# ========================
DB_URL = "postgresql+psycopg2://neondb_owner:npg_3nHTy8MfYejc@ep-patient-union-abhem53z-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"

# Función para crear conexión con manejo de errores
@st.cache_resource
def crear_conexion():
    try:
        engine = create_engine(DB_URL)
        # Probar la conexión
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return None

engine = crear_conexion()

# Meta fija
META = 6912843.60  # Corregido: era una tupla, ahora es un float

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
if "error_conexion" not in st.session_state:
    st.session_state["error_conexion"] = False

# ========================
# FUNCIÓN PARA OBTENER DATOS ACTUALIZADOS
# ========================
@st.cache_data(ttl=300)  # Cache por 5 minutos
def obtener_datos_actualizados():
    if engine is None:
        st.error("❌ No hay conexión a la base de datos")
        return pd.DataFrame()
    
    try:
        from sqlalchemy import text
        
        # Verificar si la tabla existe
        query_verificar = text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_name = 'pagos_mes'
        """)
        tablas = pd.read_sql(query_verificar, engine)
        
        if tablas.empty:
            st.warning("⚠️ La tabla 'pagos_mes' no existe. Sube primero los datos.")
            return pd.DataFrame()
        
        # Obtener datos
        query = text('SELECT * FROM pagos_mes WHERE "Tipo_Cartera" = \'Propia\'')
        df = pd.read_sql(query, engine)
        
        if df.empty:
            st.warning("⚠️ No hay datos con Tipo_Cartera = 'Propia'")
            return pd.DataFrame()
            
        # Verificar que existe la columna 'Monto'
        if 'Monto' not in df.columns:
            st.error("❌ La columna 'Monto' no existe en la tabla")
            st.write("Columnas disponibles:", df.columns.tolist())
            return pd.DataFrame()
            
        return df
        
    except Exception as e:
        st.error(f"❌ Error obteniendo datos: {e}")
        return pd.DataFrame()

# ========================
# CÁLCULOS Y SEMÁFORO
# ========================
def calcular_cumplimiento(df):
    if df.empty:
        return 0.0, 0.0, "red"
        
    try:
        # Asegurar que Monto sea numérico
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')
        df = df.dropna(subset=['Monto'])
        
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
# CÁLCULO DE DÍAS HÁBILES RESTANTES (Lunes-Viernes menos feriados)
# ========================
def calcular_dias_restantes():
    hoy = datetime.now()

    # Último día del mes
    if hoy.month == 12:
        fin_mes = hoy.replace(day=31)
    else:
        fin_mes = (hoy.replace(day=1, month=hoy.month + 1) - timedelta(days=1))

    # Lista de feriados fijos en Guatemala (día, mes)
    feriados_fijos = [
        (15, 8),  # Asunción de la Virgen - 15 agosto
        (15, 9),  # Independencia - 15 septiembre
        (20, 10), # Revolución de 1944 - 20 octubre
        (1, 11),  # Día de Todos los Santos - 1 noviembre
        (24, 12), # Nochebuena - 24 diciembre
        (25, 12), # Navidad - 25 diciembre
        (31, 12), # Fin de año - 31 diciembre
        # Agregar más feriados aquí según sea necesario
    ]

    # Convertir feriados a fechas del año actual
    feriados = []
    for dia, mes in feriados_fijos:
        try:
            feriados.append(datetime(hoy.year, mes, dia))
        except ValueError:
            continue  # Ignorar fechas inválidas

    # Contar días hábiles restantes excluyendo feriados
    dias_habiles = 0
    fecha_actual = hoy + timedelta(days=1)  # Empezar desde mañana
    while fecha_actual <= fin_mes:
        if fecha_actual.weekday() < 5 and fecha_actual not in feriados:  # Lunes=0 ... Viernes=4
            dias_habiles += 1
        fecha_actual += timedelta(days=1)

    return dias_habiles

# ========================
# INTERFAZ PRINCIPAL
# ========================

# Verificar conexión
if engine is None:
    st.error("❌ No se pudo conectar a la base de datos. Verifica tu conexión.")
    st.stop()

# Botones de control
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    actualizar = st.button('🔄 Actualizar Datos')

with col_btn2:
    if st.button('🔗 Probar Conexión'):
        if engine:
            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                st.success("✅ Conexión exitosa")
            except Exception as e:
                st.error(f"❌ Error de conexión: {e}")

# ========================
# CARGA AUTOMÁTICA Y REFRESCO
# ========================
if actualizar or st.session_state["total_monto"] == 0:
    with st.spinner("Cargando datos..."):
        st.session_state["datos"] = obtener_datos_actualizados()
        
        if not st.session_state["datos"].empty:
            st.session_state["total_monto"], st.session_state["cumplimiento"], st.session_state["color"] = calcular_cumplimiento(st.session_state["datos"])
            st.success(f"✅ Datos actualizados. {len(st.session_state['datos'])} registros cargados.")
        else:
            st.session_state["total_monto"] = 0.0
            st.session_state["cumplimiento"] = 0.0
            st.session_state["color"] = "red"

# ========================
# MOSTRAR RESULTADOS Y SEMÁFORO
# ========================
if not st.session_state["datos"].empty:
    dias_restantes = calcular_dias_restantes()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
        ###  
        ### 📌 Meta: **Q{META:,.2f}**
        ### 💰 Recuperado: **Q{st.session_state['total_monto']:,.2f}**
        ### 📈 Cumplimiento: **{st.session_state['cumplimiento']:.2f}%**
        ### 📅 Días Restantes: **{dias_restantes} hábiles**
        """)
        
        # Barra de progreso
        st.progress(min(st.session_state['cumplimiento'] / 100, 1.0))

    with col2:
        # Semáforo con emojis como fallback
        semaforo_emoji = {
            "green": "🟢",
            "yellow": "🟡", 
            "orange": "🟠",
            "red": "🔴"
        }
        
        st.markdown(f"""
        <div style='text-align: center; font-size: 80px;'>
        {semaforo_emoji[st.session_state['color']]}
        </div>
        """, unsafe_allow_html=True)
        
        # Intentar cargar imagen si existe
        ruta_imagen = f"imagenes/semaforo_{st.session_state['color']}.png"
        if os.path.exists(ruta_imagen):
            st.image(ruta_imagen, width=220)

    # ========================
    # INFORMACIÓN ADICIONAL
    # ========================
    with st.expander("📊 Detalles de los Datos"):
        st.write(f"**Total de registros:** {len(st.session_state['datos'])}")
        st.write(f"**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if len(st.session_state['datos']) > 0:
            st.dataframe(st.session_state['datos'].head())

else:
    st.info("📋 No hay datos disponibles. Asegúrate de haber subido los datos primero.")
    
    if st.button("🔍 Verificar Tablas Disponibles"):
        try:
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            tablas = pd.read_sql(query, engine)
            if not tablas.empty:
                st.write("**Tablas disponibles:**")
                st.dataframe(tablas)
            else:
                st.write("No hay tablas en la base de datos.")
        except Exception as e:
            st.error(f"Error verificando tablas: {e}")