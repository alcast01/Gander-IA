import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog

# Configuración de la página
st.set_page_config(page_title="NutriZacatecas Móvil", page_icon="🐄", layout="centered")

st.title("🐄 NutriZacatecas App")
st.markdown("### Optimizador Comercial con Catálogo Personalizado")

# --- 1. CARGA SEGURA DE LA BASE DE DATOS ---
sheet_url = "https://docs.google.com/spreadsheets/d/1FQhA3ldcSJGOtAZLfQr4XA5gPutKULeR-F_eytfq1fY/export?format=csv"

@st.cache_data(ttl=10)
def cargar_datos(url):
    return pd.read_csv(url)

# Intentamos cargar desde la nube; si falla, usamos datos locales de respaldo
try:
    df_base = cargar_datos(sheet_url)
    source_status = "☁️ Conectado a Google Sheets (En vivo)"
except Exception as e:
    source_status = "⚠️ Usando base de datos local de emergencia (No se pudo conectar a la nube)"
    # Datos de respaldo por si falla la red o los permisos
    data_respaldo = {
        "Nombre del Ingrediente": ["Rastrojo de maiz", "Harina de soya", "Grano de maiz", "Urea", "Ensilado de maiz", "Pasta de canola"],
        "Categoria": ["Forraje", "Concentrado", "Concentrado", "Suplemento", "Ensilado", "Concentrado"],
        "Precio Estimado (MXN/ton)": [2500.0, 12500.0, 5800.0, 16000.0, 1200.0, 8500.0],
        "Proteina Cruda (PC % MS)": [4.675, 42.72, 7.31, 278.1, 2.8, 33.82],
        "NEg (Mcal/kg)": [0.2975, 1.3172, 1.333, 0.0, 0.2975, 1.0235]
    }
    df_base = pd.DataFrame(data_respaldo)

st.caption(source_status)

# --- 2. MÓDULO DE CATÁLOGO PERSONALIZADO (LABORATORIO Y PRECIOS) ---
st.markdown("---")
st.subheader("🧪 1. Ajuste de Ingredientes y Análisis de Laboratorio")
st.markdown(
    "Puedes modificar directamente los precios o los valores analíticos de laboratorio "
    "de tu inventario actual, o incluso agregar nuevos ingredientes para esta corrida."
)

# Tabla interactiva para que el cliente modifique datos en tiempo real
df_ingredientes = st.data_editor(
    df_base, 
    num_rows="dynamic", 
    use_container_width=True,
    key="editor_ingredientes"
)

st.markdown("---")

# --- 3. EXTRACCIÓN Y VALIDACIÓN DE VECTORES ---
try:
    nombres = df_ingredientes["Nombre del Ingrediente"].astype(str).values
    c = df_ingredientes["Precio Estimado (MXN/ton)"].astype(float).values
    pc = df_ingredientes["Proteina Cruda (PC % MS)"].astype(float).values / 100.0  # Conversión a fracción
    neg = df_ingredientes["NEg (Mcal/kg)"].astype(float).values
except KeyError as err:
    st.error(f"Falta una columna clave en la tabla: {err}. Revisa los nombres de las columnas en tu Google Sheet.")
    st.stop()

# Restricciones automáticas de inclusión inteligentes
bounds = []
for idx, row in df_ingredientes.iterrows():
    nombre = str(row["Nombre del Ingrediente"]).lower()
    cat = str(row.get("Categoria", "concentrado")).lower()
    
    if "urea" in nombre:
        bounds.append((0.0, 0.012))  # Tope estricto de seguridad biológica (1.2%)
    elif "forraje" in cat or "ensilado" in cat or "rastrojo" in nombre:
        bounds.append((0.15, 0.60))  # Mínimo de forraje para salud ruminal
    else:
        bounds.append((0.0, 0.70))   # Concentrados y granos

# --- 4. CONTROLES MÓVILES (BARRA LATERAL) ---
st.sidebar.header("Parámetros del Lote")
peso_actual = st.sidebar.slider("Peso Vivo Actual (kg)", min_value=200.0, max_value=450.0, value=250.0, step=10.0)
gde = st.sidebar.slider("Ganancia Diaria Esperada (kg/día)", min_value=1.0, max_value=2.0, value=1.4, step=0.1)
estacion = st.sidebar.selectbox("Temporada / Clima", ["Templado", "Invierno", "Verano"])

st.info(f"Evaluando lote de **{peso_actual} kg** en temporada de **{estacion.lower()}**.")

# --- 5. LÓGICA NUTRICIONAL POR FASE ---
if peso_actual < 300:
    fase = "Crecimiento (Becerro Ligero)"
    meta_pc_min = 0.150  
    meta_neg_min = 0.88  
elif peso_actual < 380:
    fase = "Desarrollo / Transición"
    meta_pc_min = 0.135  
    meta_neg_min = 0.95  
else:
    fase = "Finalización (Engorda Pesada)"
    meta_pc_min = 0.115  
    meta_neg_min = 1.15  

st.write(f"**Etapa Detectada:** {fase}")

# --- 6. MOTOR DE PROGRAMACIÓN LINEAL ---
A_eq = np.ones((1, len(c)))
b_eq = np.array([1.0])
A_ub = np.array([-pc, -neg])
b_ub = np.array([-meta_pc_min, -meta_neg_min])

resultado = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

# --- 7. RESULTADOS EN PANTALLA ---
st.markdown("---")
st.subheader("📊 2. Resultado de la Optimización")

if resultado.success:
    st.success("¡Dieta optimizada con éxito utilizando tus parámetros personalizados!")
    st.metric(label="Costo Óptimo por Tonelada", value=f"${resultado.fun:,.2f} MXN")
    
    st.markdown("#### 📋 Mezcla exacta para la batea (por tonelada):")
    for i, ingrediente in enumerate(nombres):
        porcentaje = resultado.x[i] * 100
        kilos = resultado.x[i] * 1000
        if porcentaje > 0.01:
            st.write(f"- **{ingrediente}:** {porcentaje:.1f}% `({kilos:.1f} kg)`")
            st.progress(float(resultado.x[i]))
            
    for i, ingrediente in enumerate(nombres):
        if "urea" in str(nombres[i]).lower() and resultado.x[i] >= 0.0119:
            st.warning("⚠️ Nota: La urea alcanzó su límite máximo de seguridad biológica (1.2%).")
else:
    st.error("No se encontró una solución factible con los precios o valores analíticos actuales. Revisa los límites o los aportes nutricionales ingresados.")
