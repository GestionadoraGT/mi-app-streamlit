import pandas as pd
from sqlalchemy import create_engine
import tkinter as tk
from tkinter import filedialog, messagebox

# URL de conexión a PostgreSQL en Railway
DB_URL = "postgresql://postgres:vZveOcrYtjNytGbiMrFJJordeIEfIBkQ@centerbeam.proxy.rlwy.net:48362/railway"

def subir_excel():
    # Abrir ventana para seleccionar archivo Excel
    archivo_excel = filedialog.askopenfilename(
        title="Selecciona el archivo PAGOS_MES-.xlsx",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )

    if not archivo_excel:
        messagebox.showwarning("Aviso", "No seleccionaste ningún archivo.")
        return

    try:
        # Crear conexión a PostgreSQL
        engine = create_engine(DB_URL)

        # Leer Excel
        df = pd.read_excel(archivo_excel, engine="openpyxl")

        # Subir a PostgreSQL (reemplaza si existe)
        df.to_sql("pagos_mes", engine, if_exists="replace", index=False)

        messagebox.showinfo("Éxito", "Archivo cargado correctamente en PostgreSQL en Railway.")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo subir el archivo:\n{e}")

# Crear ventana principal
root = tk.Tk()
root.title("Cargar PAGOS_MES a PostgreSQL en Railway")
root.geometry("400x200")

# Botón para subir archivo
btn_subir = tk.Button(root, text="Seleccionar y Subir Excel", command=subir_excel, font=("Arial", 14))
btn_subir.pack(expand=True, pady=40)

# Ejecutar interfaz
root.mainloop()
