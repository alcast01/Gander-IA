import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO VISUAL ---
st.set_page_config(
    page_title="Ganader-IA",
    page_icon="🐄",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-left: 4px solid #2e7d32;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🐄 Ganader-IA")
st.markdown("##### Sistema Inteligente de Optimización y Nutrición Bovina")

# --- 2. CARGA DE LA BASE DE DATOS (CON RESPALDO) ---
sheet_url = "https://docs.google.com/spreadsheets/d/1FQhA3ldcSJGOtAZLfQr4XA5gPutKULeR-F_eytfq1fY/export?format=csv"

@st.cache_data(ttl=10)
def cargar_datos(url):
    return pd.read_csv(url)

try:
    df_base = cargar_datos(sheet_url)
    source_status = "☁️ Conectado a Google Sheets (En vivo)"
except Exception:
    source_status = "⚠️ Usando base de datos local de emergencia"
    data_respaldo = {
        "Nombre del Ingrediente": ["Rastrojo de maiz", "Harina de soya", "Grano de maiz", "Urea", "Ensilado de maiz", "Pasta de canola"],
        "Categoria": ["Forraje", "Concentrado", "Concentrado", "Suplemento", "Ensilado", "Concentrado"],
        "Precio Estimado (MXN/ton)": [2500.0, 12500.0, 5800.0, 16000.0, 1200.0, 8500.0],
        "Proteina Cruda (PC % MS)": [4.675, 42.72, 7.31, 278.1, 2.8, 33.82],
        "NEg (Mcal/kg)": [0.2975, 1.3172, 1.333, 0.0, 0.2975, 1.0235]
    }
    df_base = pd.DataFrame(data_respaldo)

st.caption(source_status)

# --- 3. CONTROLES GENERALES Y RAZA EN LA BARRA LATERAL ---
st.sidebar.header("⚙️ Parámetros del Lote")
peso_actual = st.sidebar.slider("Peso Vivo Actual (kg)", min_value=200.0, max_value=450.0, value=250.0, step=10.0)
gde = st.sidebar.slider("Ganancia Diaria Esperada (kg/día)", min_value=1.0, max_value=2.0, value=1.4, step=0.1)
estacion = st.sidebar.selectbox("Temporada / Clima", ["Templado", "Invierno", "Verano"])

st.sidebar.markdown("---")
st.sidebar.header("🧬 Genética y Raza")
raza_seleccionada = st.sidebar.selectbox(
    "Predominancia Racial",
    [
        "Compuestas / Adaptadas (Beefmaster/Brangus)",
        "Británicas (Angus/Hereford)",
        "Continentales (Charolais/Simmental)",
        "Cebú / Tropicales (Bos indicus)",
        "Ganado Criollo / Local"
    ]
)

# Lógica nutricional base por fase y peso
if peso_actual < 300:
    fase = "Crecimiento (Becerro Ligero)"
    meta_pc_base = 0.150  
    meta_neg_base = 0.88  
elif peso_actual < 380:
    fase = "Desarrollo / Transición"
    meta_pc_base = 0.135  
    meta_neg_base = 0.95  
else:
    fase = "Finalización (Engorda Pesada)"
    meta_pc_base = 0.115  
    meta_neg_base = 1.15  

# Factores de ajuste zootécnico según la raza
if "Británicas" in raza_seleccionada:
    factor_pc = 1.02
    factor_neg = 1.05
elif "Continentales" in raza_seleccionada:
    factor_pc = 1.05
    factor_neg = 1.08
elif "Cebú" in raza_seleccionada:
    factor_pc = 0.98
    factor_neg = 0.93
else:
    factor_pc = 1.00
    factor_neg = 1.00

meta_pc_min = meta_pc_base * factor_pc
meta_neg_min = meta_neg_base * factor_neg

# --- LEYENDA Y CRÉDITOS PROFESIONALES EN EL FIN DE LA BARRA LATERAL ---
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='text-align: center; color: #555; font-size: 0.85em; padding: 5px;'>"
    "<b>Ganader-IA</b><br>"
    "Herramienta de nutrición animal creada por el <b>Dr. Alejandro Castañeda Correa</b>.<br><br>"
    "Desarrollada para Nutriólogos Veterinarios, Técnicos en Nutrición Animal y Ganaderos."
    "</div>",
    unsafe_allow_html=True
)

# --- 4. INTERFAZ MODULAR POR PESTAÑAS (3 TABS) ---
tab1, tab2, tab3 = st.tabs([
    "📋 1. Resumen del Lote", 
    "🧪 2. Catálogo y Lab", 
    "📊 3. Resultados y Gráficas"
])

with tab1:
    st.subheader("Estado Actual del Lote y Perfil Genético")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Etapa Detectada", fase)
        st.metric("Peso Vivo", f"{peso_actual:,.0f} kg")
    with col2:
        st.metric("Ganancia Esperada", f"{gde} kg/día")
        st.metric("Genética Seleccionada", raza_seleccionada.split("(")[0].strip())
    
    st.info("💡 **Guía:** Configura los parámetros del lote y la predominancia racial en la **barra lateral izquierda**. Ve a la pestaña **Catálogo y Lab** para ajustar precios o análisis de laboratorio.")

with tab2:
    st.subheader("Gestión de Inventario y Análisis de Laboratorio")
    st.markdown("Modifica precios o valores analíticos específicos de tus materias primas en tiempo real:")
    df_ingredientes = st.data_editor(
        df_base, 
        num_rows="dynamic", 
        use_container_width=True,
        key="editor_ingredientes"
    )

# --- 5. EXTRACCIÓN Y MOTOR DE PROGRAMACIÓN LINEAL ---
try:
    nombres = df_ingredientes["Nombre del Ingrediente"].astype(str).values
    c = df_ingredientes["Precio Estimado (MXN/ton)"].astype(float).values
    pc = df_ingredientes["Proteina Cruda (PC % MS)"].astype(float).values / 100.0  
    neg = df_ingredientes["NEg (Mcal/kg)"].astype(float).values
except KeyError as err:
    st.error(f"Falta una columna clave en la tabla: {err}.")
    st.stop()

bounds = []
for idx, row in df_ingredientes.iterrows():
    nombre = str(row["Nombre del Ingrediente"]).lower()
    cat = str(row.get("Categoria", "concentrado")).lower()
    if "urea" in nombre:
        bounds.append((0.0, 0.012))  # Tope biológico estricto (1.2%)
    elif "forraje" in cat or "ensilado" in cat or "rastrojo" in nombre:
        bounds.append((0.15, 0.60))  # Mínimo de forraje ruminal
    else:
        bounds.append((0.0, 0.70))   # Concentrados

A_eq = np.ones((1, len(c)))
b_eq = np.array([1.0])
A_ub = np.array([-pc, -neg])
b_ub = np.array([-meta_pc_min, -meta_neg_min])

resultado = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

with tab3:
    st.subheader("Reporte Financiero y Nutricional")
    
    if resultado.success:
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric(label="Costo Óptimo por Tonelada", value=f"${resultado.fun:,.2f} MXN")
        with col_res2:
            st.metric(label="Estado del Proceso", value="Factible (Máxima Eficiencia) 🟢")
        
        st.markdown("#### 📋 Tabla de Ingredientes y Mezcla Exacta por Tonelada:")
        st.markdown("Utiliza esta tabla para la carga en la batea o mezcladora:")
        
        # Construcción de la tabla ejecutiva para el ganadero
        tabla_mezcla = []
        for i, ingrediente in enumerate(nombres):
            fraccion = resultado.x[i]
            porcentaje = fraccion * 100
            kilos = fraccion * 1000
            if porcentaje > 0.01:
                costo_parcial = fraccion * c[i]
                tabla_mezcla.append({
                    "Ingrediente": ingrediente,
                    "Inclusión (%)": round(porcentaje, 1),
                    "Kg por Tonelada (1,000 kg)": round(kilos, 2),
                    "Costo Unitario ($/ton)": f"${c[i]:,.2f}",
                    "Aporte al Costo Total ($)": f"${costo_parcial:,.2f}"
                })
        
        df_mezcla_final = pd.DataFrame(tabla_mezcla)
        st.dataframe(df_mezcla_final, use_container_width=True, hide_index=True)
                
        # --- VISUALIZACIÓN AVANZADA DE DATOS (GRÁFICA) ---
        st.markdown("---")
        st.subheader("📈 Aportes Nutricionales vs. Requerimientos Raciales Ajustados")
        
        aporte_pc = np.sum(resultado.x * pc) * 100
        aporte_neg = np.sum(resultado.x * neg)
        
        df_chart = pd.DataFrame({
            "Parámetro Nutricional": ["Proteína Cruda (%)", "Energía Neta (Mcal/kg)"],
            "Aporte de la Dieta": [aporte_pc, aporte_neg],
            "Requerimiento Ajustado": [meta_pc_min * 100, meta_neg_min]
        }).set_index("Parámetro Nutricional")
        
        st.bar_chart(df_chart)
        
        for i, ingrediente in enumerate(nombres):
            if "urea" in str(ingrediente).lower() and resultado.x[i] >= 0.0119:
                st.warning("⚠️ Nota: La urea alcanzó su límite máximo de seguridad biológica (1.2%).")
    else:
        st.error("No se encontró una solución factible con los parámetros actuales. Revisa los precios o los límites analíticos en la pestaña de Catálogo.")
