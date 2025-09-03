import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# URL de conexión a PostgreSQL en Neon
DB_URL = "postgresql+psycopg2://neondb_owner:npg_3nHTy8MfYejc@ep-patient-union-abhem53z-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"

# ========================
# CONFIGURACIÓN STREAMLIT
# ========================
st.set_page_config(page_title="Cargar PAGOS_MES", layout="centered")

st.title("📤 Cargar PAGOS")

# ========================
# FUNCIÓN PARA SUBIR EXCEL
# ========================
def subir_excel(archivo_excel):
    try:
        # Crear conexión a PostgreSQL
        engine = create_engine(DB_URL)

        # Leer el archivo Excel en memoria
        df = pd.read_excel(archivo_excel, engine="openpyxl")

        # Limpiar nombres de columnas (opcional pero recomendado)
        df.columns = df.columns.str.strip()

        # Subir a PostgreSQL (reemplaza si existe)
        df.to_sql("pagos_mes", engine, if_exists="replace", index=False, method='multi')

        st.success(f"✅ Archivo cargado correctamente. {len(df)} filas insertadas en la tabla 'pagos_mes'.")
        
        # Mostrar información adicional
        st.info(f"📊 Columnas: {', '.join(df.columns.tolist())}")
        
    except Exception as e:
        st.error(f"❌ No se pudo subir el archivo:\n{e}")
        # Mostrar más detalles del error para debugging
        st.write("Detalles del error:", str(e))

# ========================
# FUNCIÓN PARA PROBAR CONEXIÓN
# ========================
def probar_conexion():
    try:
        engine = create_engine(DB_URL)
        connection = engine.connect()
        connection.close()
        st.success("✅ Conexión a la base de datos exitosa")
        return True
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return False

# ========================
# INTERFAZ DE CARGA
# ========================

# Botón para probar conexión
if st.button("🔗 Probar Conexión"):
    probar_conexion()

st.divider()

archivo = st.file_uploader("Selecciona el archivo PAGOS", type=["xlsx", "xls"])

if archivo:
    # Mostrar información del archivo
    st.write("📁 **Información del archivo:**")
    
    # Leer y mostrar vista previa
    try:
        df_preview = pd.read_excel(archivo, engine="openpyxl")
        st.write(f"- Filas: {len(df_preview)}")
        st.write(f"- Columnas: {len(df_preview.columns)}")
        
        st.write("**Vista previa del archivo:**")
        st.dataframe(df_preview.head())
        
        # Botón para subir
        if st.button("📤 Subir a Base de Datos"):
            with st.spinner("Subiendo archivo..."):
                subir_excel(archivo)
                
    except Exception as e:
        st.error(f"Error leyendo el archivo: {e}")
else:
    st.info("👆 Por favor, selecciona un archivo Excel (.xlsx o .xls) para cargar.")

# ========================
# INFORMACIÓN ADICIONAL
# ========================
with st.expander("ℹ️ Información"):
    st.write("""
    **Instrucciones:**
    1. Primero prueba la conexión con el botón "🔗 Probar Conexión"
    2. Selecciona tu archivo Excel con los datos de pagos
    3. Revisa la vista previa para asegurar que los datos se leen correctamente
    4. Haz clic en "📤 Subir a Base de Datos"
    
    **Notas:**
    - El archivo reemplazará completamente la tabla 'pagos_mes'
    - Asegúrate de que el archivo Excel tenga el formato correcto
    - La primera fila debe contener los nombres de las columnas
    """)