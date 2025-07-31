import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# URL de conexión a PostgreSQL en Railway
DB_URL = "postgresql://postgres:vZveOcrYtjNytGbiMrFJJordeIEfIBkQ@centerbeam.proxy.rlwy.net:48362/railway"

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

        # Subir a PostgreSQL (reemplaza si existe)
        df.to_sql("pagos_mes", engine, if_exists="replace", index=False)

        st.success("Archivo cargado correctamente.")
    except Exception as e:
        st.error(f"No se pudo subir el archivo:\n{e}")

# ========================
# INTERFAZ DE CARGA
# ========================
archivo = st.file_uploader("Selecciona el archivo PAGOS", type=["xlsx", "xls"])

if archivo:
    # Mostrar una vista previa del archivo cargado
    st.write("Vista previa del archivo:")
    st.dataframe(pd.read_excel(archivo, engine="openpyxl").head())

    # Llamar la función para subir el archivo a PostgreSQL
    if st.button("Subir"):
        subir_excel(archivo)
else:
    st.info("Por favor, selecciona un archivo para cargar.")
