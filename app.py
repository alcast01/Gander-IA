import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import plotly.express as px

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
st.markdown("##### Sistema Inteligente de Optimización y Predicción Nutricional Bovina")

# --- 2. CARGA DE LA BASE DE DATOS (CON INSUMOS REGIONALES Y DE PASO) ---
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
        "Nombre del Ingrediente": [
            "Rastrojo de maiz", 
            "Harina de soya", 
            "Grano de maiz", 
            "Urea", 
            "Ensilado de maiz", 
            "Pasta de canola", 
            "Sales Minerales (Cañón de Tlaltenango)", 
            "Grasa de paso Lactomil"
        ],
        "Categoria": ["Forraje", "Concentrado", "Concentrado", "Suplemento", "Ensilado", "Concentrado", "Suplemento", "Suplemento"],
        "Precio Estimado (MXN/ton)": [2500.0, 12500.0, 5800.0, 16000.0, 1200.0, 8500.0, 18000.0, 32000.0],
        "Proteina Cruda (PC % MS)": [4.675, 42.72, 7.31, 278.1, 2.8, 33.82, 0.0, 1.0],
        "NEg (Mcal/kg)": [0.2975, 1.3172, 1.333, 0.0, 0.2975, 1.0235, 0.0, 1.65]
    }
    df_base = pd.DataFrame(data_respaldo)

st.caption(source_status)

# --- 3. CONTROLES GENERALES Y PARÁMETROS PRODUCTIVOS EN LA BARRA LATERAL ---
st.sidebar.header("⚙️ Parámetros del Lote")
peso_actual = st.sidebar.slider("Peso Vivo Actual (kg)", min_value=200.0, max_value=450.0, value=250.0, step=10.0)
peso_objetivo = st.sidebar.slider("Peso de Venta / Meta (kg)", min_value=450.0, max_value=600.0, value=520.0, step=10.0)
gde = st.sidebar.slider("Ganancia Diaria Esperada (GDE kg/día)", min_value=1.0, max_value=2.0, value=1.4, step=0.1)
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

# --- MODELADO PREDICTIVO BIOLÓGICO (ZONA DE RESUMEN) ---
factor_clima = 0.93 if estacion == "Invierno" else (1.05 if estacion == "Verano" else 1.00)
cms_estimado = peso_actual * 0.024 * factor_clima

kg_por_ganar = max(0.0, peso_objetivo - peso_actual)
dias_a_meta = kg_por_ganar / gde if gde > 0 else 0

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

# Créditos profesionales en barra lateral
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
    "📋 1. Resumen y Predicciones", 
    "🧪 2. Catálogo y Lab", 
    "📊 3. Resultados y Gráficas"
])

with tab1:
    st.subheader("Predicciones de Parámetros Productivos y Crecimiento")
    st.markdown("Proyecciones biológicas del lote basadas en peso actual, genética y condiciones ambientales:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Etapa Fisiológica", fase)
        st.metric("Ganancia Esperada (GDE)", f"{gde} kg/día")
    with col2:
        st.metric("Consumo MS Estimado", f"{cms_estimado:.2f} kg/día")
        st.metric("Días Proyectados a Meta", f"{dias_a_meta:.0f} días")
    with col3:
        st.metric("Ganancia Total Esperada", f"{kg_por_ganar:.1f} kg")
        st.metric("Genética", raza_seleccionada.split("(")[0].strip())
    
    st.markdown("---")
    st.subheader("📈 Curva de Comportamiento y Proyección de Peso en el Tiempo")
    
    semanas = int(np.ceil(dias_a_meta / 7)) if dias_a_meta > 0 else 1
    semanas = max(semanas, 4)
    
    df_proyeccion = pd.DataFrame({
        "Semana": [f"Semana {i}" for i in range(semanas + 1)],
        "Peso Proyectado (kg)": [min(peso_objetivo, peso_actual + (i * 7 * gde)) for i in range(semanas + 1)]
    })
    
    fig_line = px.line(
        df_proyeccion, 
        x="Semana", 
        y="Peso Proyectado (kg)", 
        markers=True,
        title="Trayectoria de Engorda del Lote hacia el Peso Objetivo"
    )
    fig_line.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="#ffffff")
    st.plotly_chart(fig_line, use_container_width=True)

with tab2:
    st.subheader("Gestión de Inventario y Análisis de Laboratorio")
    st.markdown("Modifica precios o valores analíticos específicos de tus materias primas en tiempo real:")
    df_ingredientes = st.data_editor(
        df_base, 
        num_rows="dynamic", 
        use_container_width=True,
        key="editor_ingredientes"
    )

# --- 5. EXTRACCIÓN Y MOTOR DE PROGRAMACIÓN LINEAL (CON LÍMITES FISIOLÓGICOS) ---
try:
    nombres = df_ingredientes["Nombre del Ingrediente"].astype(str).values
    c = df_ingredientes["Precio Estimado (MXN/ton)"].astype(float).values
    pc = df_ingredientes["Proteina Cruda (PC % MS)"].astype(float).values / 100.0  
    neg = df_ingredientes["NEg (Mcal/kg)"].astype(float).values
except KeyError as err:
    st.error(f"Falta una columna clave en la tabla: {err}.")
    st.stop()

# LÍMITES INTELIGENTES: Control estricto en aditivos/suplementos y grasa restringida al 3%
bounds = []
for idx, row in df_ingredientes.iterrows():
    nombre = str(row["Nombre del Ingrediente"]).lower()
    if "urea" in nombre:
        bounds.append((0.0, 0.015))  # Tope biológico estricto para urea (1.5%)
    elif "mineral" in nombre or "sal" in nombre:
        bounds.append((0.0, 0.03))   # Tope máximo seguro para sales minerales (3%)
    elif "grasa" in nombre or "lactomil" in nombre:
        bounds.append((0.0, 0.03))   # Tope máximo estricto para grasa de paso (3%)
    else:
        bounds.append((0.0, 1.0))    # Flexibilidad completa para forrajes y concentrados (0% al 100%)

A_eq = np.ones((1, len(c)))
b_eq = np.array([1.0])
A_ub = np.array([-pc, -neg])
b_ub = np.array([-meta_pc_min, -meta_neg_min])

resultado = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

with tab3:
    st.subheader("Reporte Financiero y Nutricional Optimizado")
    
    if resultado.success:
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric(label="Costo Óptimo por Tonelada", value=f"${resultado.fun:,.2f} MXN")
        with col_res2:
            st.metric(label="Estado del Proceso", value="Factible (Máxima Eficiencia) 🟢")
        
        st.markdown("#### 📋 Tabla de Ingredientes y Mezcla Exacta por Tonelada:")
        st.markdown("Utiliza esta tabla para la carga precisa en la batea o mezcladora:")
        
        tabla_mezcla = []
        categorias_pie = {}
        
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
                
                cat_ing = str(df_ingredientes.iloc[i].get("Categoria", "Otros"))
                categorias_pie[cat_ing] = categorias_pie.get(cat_ing, 0) + porcentaje
        
        df_mezcla_final = pd.DataFrame(tabla_mezcla)
        st.dataframe(df_mezcla_final, use_container_width=True, hide_index=True)
        
        # --- GRÁFICA DE PASTEL DE LA COMPOSICIÓN DE LA DIETA ---
        st.markdown("---")
        st.subheader("🥧 Composición Porcentual de la Dieta por Categoría de Ingrediente")
        df_pie = pd.DataFrame(list(categorias_pie.items()), columns=["Categoría", "Porcentaje"])
        fig_pie = px.pie(df_pie, names="Categoría", values="Porcentaje", hole=0.4, title="Distribución de Insumos en la Mezcla")
        st.plotly_chart(fig_pie, use_container_width=True)
                
        # --- VISUALIZACIÓN AVANZADA DE DATOS (GRÁFICA DE BARRAS) ---
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
            ing_lower = str(ingrediente).lower()
            if "urea" in ing_lower and resultado.x[i] >= 0.014:
                st.warning("⚠️ Nota: La urea alcanzó su límite máximo de seguridad biológica (1.5%).")
            elif ("mineral" in ing_lower or "sal" in ing_lower) and resultado.x[i] >= 0.029:
                st.warning("⚠️ Nota: Las sales minerales alcanzaron su límite máximo recomendado (3%).")
            elif ("grasa" in ing_lower or "lactomil" in ing_lower) and resultado.x[i] >= 0.029:
                st.warning("⚠️ Nota: La grasa de paso alcanzó su límite máximo restringido (3%).")
    else:
        st.error(
            "⚠️ **Aviso del Optimizador:** Con los precios actuales o metas extremas introducidas, no se encontró una solución matemática 100% factible. "
            "Sin embargo, **las predicciones de parámetros productivos y consumo en la Pestaña 1 siguen vigentes y operativas**. "
            "Revisa los precios o valores analíticos en la pestaña **Catálogo y Lab**."
        )
