import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuración de la página para dispositivos móviles y escritorio
st.set_page_config(page_title="Sistema de Asistencia - Admin", layout="wide")

# Nombre del archivo de base de datos local
DB_FILE = "asistencia_db.csv"

# Inicializar base de datos si no existe con las columnas necesarias
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["studentName", "date", "time", "status", "timestamp"])
    df.to_csv(DB_FILE, index=False)

def load_data():
    """Carga los datos del archivo CSV."""
    return pd.read_csv(DB_FILE)

def save_data(new_record):
    """Guarda un nuevo registro en el archivo CSV."""
    df = load_data()
    new_df = pd.DataFrame([new_record])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- LÓGICA DE RECEPCIÓN DE DATOS ---
# Streamlit recibe datos a través de los parámetros de la URL (?name=Juan...)
query_params = st.query_params

if "action" in query_params and query_params["action"] == "register":
    nombre = query_params.get("name")
    fecha = query_params.get("date")
    hora = query_params.get("time")
    estado = query_params.get("status")
    
    if nombre and fecha:
        # Verificar si el alumno ya registró hoy para evitar duplicados por recarga de página
        df_current = load_data()
        ya_existe = ((df_current['studentName'] == nombre) & (df_current['date'] == fecha)).any()
        
        if not ya_existe:
            new_record = {
                "studentName": nombre,
                "date": fecha,
                "time": hora,
                "status": estado,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_data(new_record)
            st.balloons() # Animación de éxito
            st.success(f"✅ ¡Registro exitoso para {nombre}!")
        else:
            st.warning(f"⚠️ {nombre}, ya tienes un registro para el día de hoy ({fecha}).")
    
    # Limpiar la URL para que el mensaje no se repita infinitamente
    if st.button("Ir al Panel de Control"):
        st.query_params.clear()
        st.rerun()

# --- INTERFAZ DEL PROFESOR ---
st.title("🚀 Panel de Control de Asistencia")
st.markdown("---")

data = load_data()

# Métricas rápidas
col1, col2, col3 = st.columns(3)
with col1:
    total_alumnos = len(data["studentName"].unique()) if not data.empty else 0
    st.metric("Alumnos Únicos", total_alumnos)
with col2:
    hoy = datetime.now().strftime("%Y-%m-%d")
    asistencias_hoy = len(data[data["date"] == hoy]) if not data.empty else 0
    st.metric("Asistencias Hoy", asistencias_hoy)
with col3:
    st.metric("Total Registros", len(data))

# Tabla de datos interactiva
st.subheader("📋 Listado Histórico")
if not data.empty:
    # Ordenar por fecha y hora más reciente
    data_sorted = data.sort_values(by="timestamp", ascending=False)
    st.dataframe(data_sorted, use_container_width=True)
    
    # Botón de descarga
    csv = data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte Completo (CSV)",
        data=csv,
        file_name=f"reporte_asistencia_{hoy}.csv",
        mime="text/csv",
    )
else:
    st.info("Aún no hay registros de asistencia en la base de datos.")

st.markdown("---")
st.caption("EduAsistencia Pro - Conectado vía GitHub & Streamlit")