import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fpdf import FPDF

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO VISUAL (CAMPO Y GANADERÍA) ---
st.set_page_config(
    page_title="Ganader-IA Pro | Nutrición de Precisión, Bonos de Carbono y Bunk Management",
    page_icon="🐄",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        color: #2b2d42;
    }
    
    .main {
        background-color: #fcfbf9;
    }
    
    .stMetric {
        background-color: #ffffff;
        padding: 20px 16px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(45, 90, 39, 0.08);
        border-left: 5px solid #2d5a27;
        border-top: 1px solid #e6e2dd;
        border-right: 1px solid #e6e2dd;
        border-bottom: 1px solid #e6e2dd;
        margin-bottom: 12px;
    }
    
    h1, h2, h3, h4 {
        color: #1f2421;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700;
        line-height: 1.3;
    }

    p, span, label {
        font-family: 'Inter', sans-serif !important;
        color: #333333;
        line-height: 1.5;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGOTIPO VECTORIAL INSTITUCIONAL ---
st.markdown("""
    <div style="display: flex; align-items: center; background: linear-gradient(135deg, #2d5a27 0%, #bc6c25 100%); padding: 25px; border-radius: 16px; box-shadow: 0 6px 20px rgba(45,90,39,0.15); margin-bottom: 25px; color: white; flex-wrap: wrap; gap: 15px;">
        <div style="flex-shrink: 0;">
            <svg width="70" height="70" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" fill="#ffffff"/>
                <circle cx="12" cy="12" r="3" fill="#dda15e"/>
            </svg>
        </div>
        <div style="flex-grow: 1; min-width: 250px;">
            <h1 style="margin: 0; font-size: 2.2em; color: #ffffff; letter-spacing: 0.5px; font-family: 'Inter', sans-serif;">Ganader-IA <span style="background-color: #dda15e; color: #1f2421; padding: 2px 8px; border-radius: 6px; font-size: 0.6em; vertical-align: middle;">ELITE 360</span></h1>
            <p style="margin: 6px 0 0 0; font-size: 1.05em; color: #f4f1de; font-weight: 300; font-family: 'Inter', sans-serif;">Nutrición de Precisión, Bonos de Carbono y Gestión Inteligente de Corrales</p>
            <p style="margin: 6px 0 0 0; font-size: 0.85em; color: #ffe8d6; font-style: italic; font-weight: 400; font-family: 'Inter', sans-serif;">✨ Tecnología e Innovación en tus manos</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 3. BASE DE DATOS INICIAL CON MINERALES Y NUTRIENTES EDITABLES ---
data_respaldo = {
    "Nombre del Ingrediente": [
        "Rastrojo de maiz molido", 
        "Harina de soya", 
        "Grano de maiz molido", 
        "Urea", 
        "Ensilado de maiz", 
        "Canola (pasta)", 
        "Melaza liquida",
        "Sales Minerales (Especializadas)", 
        "Grasa de paso Lactomil"
    ],
    "Categoria": ["Forraje", "Suplemento Proteico", "Grano Energetico", "Suplemento NPN", "Forraje Humedo", "Suplemento Proteico", "Subproducto / Energetico", "Suplemento Mineral", "Suplemento Energetico"],
    "Disponible": [True, True, True, True, False, True, True, True, True],
    "Precio Estimado (MXN/ton)": [2500.0, 12500.0, 5800.0, 16000.0, 1200.0, 8500.0, 4800.0, 18000.0, 32000.0],
    "Proteina Cruda (PC % MS)": [5.5, 48.0, 8.5, 281.0, 8.0, 38.0, 4.8, 0.0, 1.0],
    "NEg (Mcal/kg)": [0.35, 1.48, 1.55, 0.0, 0.85, 1.15, 1.22, 0.0, 1.65],
    "FND (% MS)": [75.0, 12.0, 9.0, 0.0, 45.0, 28.0, 0.0, 0.0, 0.0],
    "peNDF (% MS)": [65.0, 2.0, 3.0, 0.0, 30.0, 10.0, 0.0, 0.0, 0.0],
    "PDR (% MS)": [3.5, 33.6, 5.5, 281.0, 5.0, 24.0, 4.5, 0.0, 0.0],
    "PND (% MS)": [2.0, 14.4, 3.0, 0.0, 3.0, 14.0, 0.3, 0.0, 1.0],
    "Calcio (Ca %)": [0.35, 0.30, 0.02, 0.0, 0.25, 0.70, 0.80, 18.0, 1.0],
    "Fosforo (P %)": [0.10, 0.65, 0.30, 0.0, 0.22, 1.10, 0.08, 10.0, 0.1],
    "Sodio (Na %)": [0.02, 0.03, 0.02, 0.0, 0.02, 0.05, 0.10, 10.0, 0.0],
    "Magnesio (Mg %)": [0.15, 0.28, 0.12, 0.0, 0.18, 0.50, 0.40, 2.0, 0.0],
    "Lípidos / Extracto Etéreo (%)": [1.5, 1.8, 3.8, 0.0, 3.0, 3.5, 0.5, 0.0, 99.0],
    "Min Inclusión (%)": [20.0, 5.0, 10.0, 0.0, 0.0, 0.0, 2.0, 1.0, 0.0],
    "Max Inclusión (%)": [60.0, 35.0, 50.0, 1.5, 0.0, 30.0, 6.0, 3.0, 3.0]
}
df_base = pd.DataFrame(data_respaldo)

# --- 4. CONTROLES GENERALES Y VARIABLES AVANZADAS EN LA BARRA LATERAL ---
st.sidebar.header("⚙️ Parámetros del Lote y Población")
cantidad_animales = st.sidebar.number_input("Número de Cabezas en el Lote", min_value=1, max_value=5000, value=100, step=10)
peso_actual = st.sidebar.slider("Peso Vivo Actual (kg)", min_value=200.0, max_value=450.0, value=250.0, step=10.0)
peso_objetivo = st.sidebar.slider("Peso de Venta / Meta (kg)", min_value=450.0, max_value=600.0, value=520.0, step=10.0)
gde = st.sidebar.slider("Ganancia Diaria Esperada (GDE kg/día)", min_value=1.0, max_value=2.0, value=1.4, step=0.1)
estacion = st.sidebar.selectbox("Temporada / Clima", ["Templado", "Invierno", "Verano"])

st.sidebar.markdown("---")
st.sidebar.header("🧬 Genética, Sexo y Manejo")
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
sexo_lote = st.sidebar.selectbox("Tipo Sexual", ["Novillos (Castrados)", "Toros Enteros", "Vaquillas"])
marco_lote = st.sidebar.selectbox("Tamaño de Marco", ["Mediano (Standard)", "Pequeño (Precoz / Engrase rápido)", "Grande (Continental / Retrasado)"])
historial_nutricional = st.sidebar.selectbox("Historial Nutricional", ["Desarrollo Continuo (Normal)", "Crecimiento Compensatorio (Post-restricción)"])
promotor_crecimiento = st.sidebar.selectbox("Promotores de Crecimiento", ["Ninguno", "Implante Hormonal", "Agonista β-adrenérgico (Finalización)"])
condicion_lodo = st.sidebar.selectbox("Condición de Corral / Lodo", ["Seco y Confortable", "Lodo Moderado (10-15 cm)", "Lodo Severo (>20 cm)"])

# --- MODELADO PREDICTIVO BIOLÓGICO AVANZADO ---
factor_clima = 0.93 if estacion == "Invierno" else (1.05 if estacion == "Verano" else 1.00)

factor_lodo = 1.00 if condicion_lodo == "Seco y Confortable" else (1.12 if "Moderado" in condicion_lodo else 1.25)
cms_estimado = peso_actual * 0.024 * factor_clima / (factor_lodo if "Severo" in condicion_lodo else 1.0)

kg_por_ganar = max(0.0, peso_objetivo - peso_actual)
dias_a_meta = kg_por_ganar / gde if gde > 0 else 0

if peso_actual < 300:
    fase = "Crecimiento (Becerro Ligero)"
    meta_pc_base = 0.130 + (gde * 0.015)
    meta_neg_base = 0.75 + (gde * 0.09)
    meta_fnd_min = 0.30
    meta_pendf_min = 0.22
    meta_pdr_min = 0.080
    meta_pnd_min = 0.045
    meta_ca_min = 0.0055
    meta_p_min = 0.0035
elif peso_actual < 380:
    fase = "Desarrollo / Transición"
    meta_pc_base = 0.120 + (gde * 0.015)
    meta_neg_base = 0.85 + (gde * 0.09)
    meta_fnd_min = 0.28
    meta_pendf_min = 0.20
    meta_pdr_min = 0.072
    meta_pnd_min = 0.040
    meta_ca_min = 0.0050
    meta_p_min = 0.0030
else:
    fase = "Finalización (Engorda Pesada)"
    meta_pc_base = 0.105 + (gde * 0.015)
    meta_neg_base = 1.00 + (gde * 0.10)
    meta_fnd_min = 0.25
    meta_pendf_min = 0.18
    meta_pdr_min = 0.065
    meta_pnd_min = 0.038
    meta_ca_min = 0.0045
    meta_p_min = 0.0028

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

if sexo_lote == "Toros Enteros":
    factor_sexo_pc = 1.08
    factor_sexo_neg = 1.04
elif sexo_lote == "Vaquillas":
    factor_sexo_pc = 0.96
    factor_sexo_neg = 1.06
else:
    factor_sexo_pc = 1.00
    factor_sexo_neg = 1.00

if "Pequeño" in marco_lote:
    factor_marco = 1.05
elif "Grande" in marco_lote:
    factor_marco = 0.95
else:
    factor_marco = 1.00

factor_promotor = 1.08 if promotor_crecimiento == "Implante Hormonal" else (1.15 if "Agonista" in promotor_crecimiento else 1.00)
factor_compensatorio = 0.93 if "Compensatorio" in historial_nutricional else 1.00

meta_pc_min = meta_pc_base * factor_pc * factor_sexo_pc * factor_promotor
meta_neg_min = meta_neg_base * factor_neg * factor_sexo_neg * factor_marco * factor_lodo * factor_compensatorio

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='text-align: center; color: #555; font-size: 0.85em; padding: 5px; font-family: Inter, sans-serif;'>"
    "<b>Ganader-IA Elite 360</b><br>"
    "Creado por el <b>Dr. Alejandro Castañeda Correa</b>.<br><br>"
    "SaaS de Nutrición y Sostenibilidad."
    "</div>",
    unsafe_allow_html=True
)

# --- 5. INTERFAZ MODULAR POR PESTAÑAS (4 TABS ELITE) ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 1. Resumen y Sensibilidad", 
    "🧪 2. Laboratorio y Perfiles", 
    "📊 3. Balance Mineral y Bonos de Carbono", 
    "🚜 4. Bunk Management y Operarios"
])

with tab1:
    st.subheader("Predicciones de Parámetros Productivos y Análisis de Sensibilidad")
    st.markdown("Proyecciones biológicas del lote y simulación de impacto financiero ante volatilidad de precios en materias primas:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Etapa Fisiológica", fase)
        st.metric("Ganancia Esperada (GDE)", f"{gde} kg/día")
    with col2:
        st.metric("Consumo MS por Cabeza", f"{cms_estimado:.2f} kg/día")
        st.metric("Días Proyectados a Meta", f"{dias_a_meta:.0f} días")
    with col3:
        st.metric("Cabezas en el Lote", f"{cantidad_animales} animales")
        st.metric("Ganancia Total Esperada", f"{kg_por_ganar:.1f} kg/cab")
    
    st.markdown("---")
    st.subheader("📈 Gráfica de Comportamiento: Peso y Consumo de Materia Seca en el Tiempo")
    
    semanas = int(np.ceil(dias_a_meta / 7)) if dias_a_meta > 0 else 1
    semanas = max(semanas, 4)
    
    lista_semanas = []
    lista_pesos = []
    lista_cms = []
    
    for i in range(semanas + 1):
        dias_transcurridos = i * 7
        peso_proy = min(peso_objetivo, peso_actual + (dias_transcurridos * gde))
        cms_proy = peso_proy * 0.024 * factor_clima
        lista_semanas.append(f"Semana {i}")
        lista_pesos.append(peso_proy)
        lista_cms.append(round(cms_proy, 2))
    
    fig_comportamiento = make_subplots(specs=[[{"secondary_y": True}]])
    fig_comportamiento.add_trace(go.Scatter(x=lista_semanas, y=lista_pesos, name="Peso Proyectado (kg)", mode="lines+markers", line=dict(color="#2d5a27", width=3.5)), secondary_y=False)
    fig_comportamiento.add_trace(go.Scatter(x=lista_semanas, y=lista_cms, name="Consumo Materia Seca (kg/día)", mode="lines+markers", line=dict(color="#bc6c25", width=3, dash="dash")), secondary_y=True)
    fig_comportamiento.update_layout(title=dict(text=f"Dinámica de Engorda (GDE: {gde} kg/d | Clima: {estacion})", font=dict(family="Inter", size=13), x=0.5), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", font=dict(family="Inter", color="#2b2d42"), legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5), margin=dict(l=20, r=20, t=60, b=70))
    fig_comportamiento.update_yaxes(title_text="<b>Peso Vivo del Animal (kg)</b>", secondary_y=False, color="#2d5a27")
    fig_comportamiento.update_yaxes(title_text="<b>Consumo de Materia Seca (kg/día)</b>", secondary_y=True, color="#bc6c25")
    st.plotly_chart(fig_comportamiento, use_container_width=True)

with tab2:
    st.subheader("🧪 Laboratorio de Nutrición Editable y Control Regional")
    st.markdown(
        "**Personaliza por completo los perfiles nutricionales y de minerales de tus materias primas.** "
        "Selecciona cuáles insumos están disponibles en tu rancho (`✓`), ajusta sus límites de inclusión, "
        "y edita directamente en la tabla los valores según los análisis de tu laboratorio local:"
    )
    
    df_ingredientes = st.data_editor(
        df_base, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "Disponible": st.column_config.CheckboxColumn("¿Disponible en tu Rancho?", default=True),
            "Min Inclusión (%)": st.column_config.NumberColumn("Min (%)", min_value=0.0, max_value=100.0, step=0.5),
            "Max Inclusión (%)": st.column_config.NumberColumn("Max (%)", min_value=0.0, max_value=100.0, step=0.5),
        },
        key="editor_ingredientes"
    )

# --- 6. EXTRACCIÓN Y MOTOR DE PROGRAMACIÓN LINEAL (CON BALANCE AUTOMÁTICO Ca:P) ---
try:
    nombres = df_ingredientes["Nombre del Ingrediente"].astype(str).values
    c = df_ingredientes["Precio Estimado (MXN/ton)"].astype(float).values
    pc = df_ingredientes["Proteina Cruda (PC % MS)"].astype(float).values / 100.0  
    neg = df_ingredientes["NEg (Mcal/kg)"].astype(float).values
    fnd = df_ingredientes["FND (% MS)"].astype(float).values / 100.0
    pendf = df_ingredientes["peNDF (% MS)"].astype(float).values / 100.0
    pdr = df_ingredientes["PDR (% MS)"].astype(float).values / 100.0
    pnd = df_ingredientes["PND (% MS)"].astype(float).values / 100.0
    ca = df_ingredientes["Calcio (Ca %)"].astype(float).values / 100.0
    p_min_ing = df_ingredientes["Fosforo (P %)"].astype(float).values / 100.0
    na = df_ingredientes["Sodio (Na %)"].astype(float).values / 100.0
    mg = df_ingredientes["Magnesio (Mg %)"].astype(float).values / 100.0
    lipidos = df_ingredientes["Lípidos / Extracto Etéreo (%)"].astype(float).values / 100.0
    
    disponibles = df_ingredientes["Disponible"].astype(bool).values
except KeyError as err:
    st.error(f"Falta una columna clave en la tabla: {err}.")
    st.stop()

bounds = []
for idx, row in df_ingredientes.iterrows():
    if not row["Disponible"]:
        bounds.append((0.0, 0.0))
    else:
        min_lim = max(0.0, float(row["Min Inclusión (%)"]) / 100.0)
        max_lim = min(1.0, float(row["Max Inclusión (%)"]) / 100.0)
        bounds.append((min_lim, max_lim))

A_eq = np.ones((1, len(c)))
b_eq = np.array([1.0])

# Restricciones Ca:P automáticas (1.5:1 a 2.0:1)
row_ca_p_min = -ca + 1.5 * p_min_ing
row_ca_p_max = ca - 2.0 * p_min_ing

A_ub = np.array([-pc, -neg, -fnd, -pendf, -pdr, -pnd, -ca, -p_min_ing, row_ca_p_min, row_ca_p_max])
b_ub = np.array([-meta_pc_min, -meta_neg_min, -meta_fnd_min, -meta_pendf_min, -meta_pdr_min, -meta_pnd_min, -meta_ca_min, -meta_p_min, 0.0, 0.0])

resultado = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

with tab3:
    st.subheader("Reporte Financiero, Balance Mineral y Monetización de Bonos de Carbono")
    
    if resultado.success:
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric(label="Costo Óptimo por Tonelada", value=f"${resultado.fun:,.2f} MXN")
        with col_res2:
            st.metric(label="Estado del Proceso", value="Factible (Elite 360) 🟢")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📋 Tabla de Ingredientes y Mezcla Exacta por Tonelada:")
        
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
                    "Inclusion (%)": round(porcentaje, 1),
                    "Kg por Tonelada (1,000 kg)": round(kilos, 2),
                    "Costo Unitario ($/ton)": f"${c[i]:,.2f}",
                    "Aporte al Costo Total ($)": f"${costo_parcial:,.2f}"
                })
                cat_ing = str(df_ingredientes.iloc[i].get("Categoria", "Otros"))
                categorias_pie[cat_ing] = categorias_pie.get(cat_ing, 0) + porcentaje
        
        total_porcentaje = sum([row["Inclusion (%)"] for row in tabla_mezcla])
        total_kilos = sum([row["Kg por Tonelada (1,000 kg)"] for row in tabla_mezcla])
        total_costo = resultado.fun

        tabla_mezcla_con_totales = tabla_mezcla.copy()
        tabla_mezcla_con_totales.append({
            "Ingrediente": "TOTALES / MEZCLA FINAL",
            "Inclusion (%)": round(total_porcentaje, 1),
            "Kg por Tonelada (1,000 kg)": round(total_kilos, 1),
            "Costo Unitario ($/ton)": "-",
            "Aporte al Costo Total ($)": f"${total_costo:,.2f}"
        })

        df_mezcla_final = pd.DataFrame(tabla_mezcla_con_totales)
        st.dataframe(df_mezcla_final, use_container_width=True, hide_index=True)
        
        # --- CÁLCULOS AVANZADOS Y BONOS DE CARBONO ---
        aporte_pc = np.sum(resultado.x * pc) * 100
        aporte_neg = np.sum(resultado.x * neg)
        aporte_fnd = np.sum(resultado.x * fnd) * 100
        aporte_pendf = np.sum(resultado.x * pendf) * 100
        aporte_pdr = np.sum(resultado.x * pdr) * 100
        aporte_pnd = np.sum(resultado.x * pnd) * 100
        aporte_ca = np.sum(resultado.x * ca) * 100
        aporte_p = np.sum(resultado.x * p_min_ing) * 100
        aporte_na = np.sum(resultado.x * na) * 100
        aporte_mg = np.sum(resultado.x * mg) * 100
        aporte_lipidos = np.sum(resultado.x * lipidos) * 100
        
        relacion_ca_p = (aporte_ca / aporte_p) if aporte_p > 0 else 0
        status_ca_p = "🟢 Óptimo Automático (1.5 - 2.0:1)"
        
        ge_diaria = cms_estimado * 18.4 
        reduccion_lipidica = max(0.0, (aporte_lipidos - 3.0) * 0.003)
        factor_fnd_ym = 0.035 + (aporte_fnd / 100.0) * 0.035
        ym_ajustado = max(0.030, factor_fnd_ym - reduccion_lipidica)
        
        ch4_g_dia = (ge_diaria * ym_ajustado / 55.65) * 1000
        ch4_g_kg_ganancia = ch4_g_dia / gde if gde > 0 else 0
        co2e_anual = (ch4_g_dia * 365 / 1000.0) * 28.0 
        
        linea_base_co2e = 4200.0
        ahorro_co2e_kg = max(0.0, linea_base_co2e - co2e_anual)
        valor_bono_mxn = (ahorro_co2e_kg / 1000.0) * 350.0
        
        st.markdown("---")
        st.subheader("🛡️ Validación Mineral, Salud Ruminal y Monetización Verde")
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Calcio (Ca)", f"{aporte_ca:.2f}%", "Mineral Mayor")
            st.metric("Relación Ca:P", f"{relacion_ca_p:.2f}:1", status_ca_p)
        with col_m2:
            st.metric("Fósforo (P)", f"{aporte_p:.2f}%", "Mineral Mayor")
            st.metric("Fibra peNDF", f"{aporte_pendf:.1f}%", "Anti-acidosis")
        with col_m3:
            st.metric("Emisión $CH_4$", f"{ch4_g_dia:.1f} g/día", "IPCC Tier 2")
            st.metric("Equivalente $CO_2e$", f"{co2e_anual:,.1f} kg/año")
        with col_m4:
            st.metric("Valor Bonos Carbono", f"${valor_bono_mxn:,.2f} MXN", "Potencial Anual/Cab")
            st.metric("Lípidos Totales", f"{aporte_lipidos:.1f}%", "Mitigador")

    else:
        st.error(
            "⚠️ **Aviso del Optimizador Elite 360:** Con los ingredientes seleccionados o restricciones muy cerradas, no se encontró una solución matemática factible "
            "que cumpla simultáneamente con energía, proteína, fibra y la proporción automática Ca:P de 1.5 a 2.0. "
            "Asegúrate de tener activa una fuente mineral especializada en la Pestaña 2."
        )

with tab4:
    st.subheader("🚜 Bunk Management y Gestión Logística de Alimento")
    st.markdown("Control total de inventarios, requerimientos de toneladas totales para el lote y guía de mezcla para el personal del corral:")
    
    if resultado.success:
        cms_total_lote = cms_estimado * cantidad_animales
        alimento_total_ciclo = cms_total_lote * dias_a_meta
        costo_total_lote = (alimento_total_ciclo / 1000.0) * resultado.fun
        
        col_l1, col_l2, col_l3 = st.columns(3)
        with col_l1:
            st.metric("Consumo Diario del Lote", f"{cms_total_lote:,.1f} kg MS/día")
        with col_l2:
            st.metric("Alimento Total Requerido", f"{alimento_total_ciclo:,.1f} kg ({alimento_total_ciclo/1000.0:,.1f} tons)")
        with col_l3:
            st.metric("Costo Total de Alimentación", f"${costo_total_lote:,.2f} MXN")
            
        st.markdown("---")
        st.markdown("#### 📋 Protocolo y Orden de Carga en Batea para Operarios:")
        st.info(
            f"**Lote Activo:** {cantidad_animales} animales | **Duración Estimada:** {dias_a_meta:.0f} días\n\n"
            "1. **Paso 1 (Forrajes Secos / Fibra Larga):** Cargar rastrojos o harinas fibrosas al inicio para asegurar el peNDF y evitar acidosis metabólica.\n"
            "2. **Paso 2 (Ingredientes Húmedos / Ensilados):** Agregar ensilados o subproductos húmedos calculando la corrección por materia seca.\n"
            "3. **Paso 3 (Granos Energéticos y Proteicos):** Incorporar maíz molido, pasta de soya y canola.\n"
            "4. **Paso 4 (Núcleos, Minerales y Urea):** Agregar las sales minerales especializadas y la urea (previa dilución o mezclado homogéneo para evitar toxicidad).\n"
            "5. **Paso 5 (Líquidos):** Verter la melaza líquida con un chorro de agua al final para garantizar adherencia, evitar polvaderas y elevar la palatabilidad.\n"
            "6. **Tiempo de Mezclado:** Operar el carro mezclador de 8 a 10 minutos continuos antes de la distribución en comederos."
        )

        # --- FUNCIÓN GENERADORA DE PDF EJECUTIVO ELITE ---
        def generar_pdf_ejecutivo(df_resumen, costo_ton, etapa, raza_L, sexo_L, marco_L, p_act, p_obj, gain, dias, cabezas, a_ca, a_p, r_cap, a_fnd, a_pendf, ch4_d, co2e, bonos, cost_lote, tons_lote):
            pdf = FPDF()
            pdf.add_page()
            
            pdf.set_font("Arial", "B", 15)
            pdf.cell(0, 8, "Ganader-IA Elite 360 - Reporte Ejecutivo y Bonos de Carbono", 0, 1, "C")
            pdf.set_font("Arial", "I", 9)
            pdf.cell(0, 5, "Creado por el Dr. Alejandro Castaneda Correa", 0, 1, "C")
            pdf.ln(3)
            
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "1. Parametros Biologicos y Poblacionales del Lote", 0, 1)
            pdf.set_font("Arial", "", 9)
            pdf.cell(0, 5, f"Fisiologia: {etapa} | Cabezas: {cabezas} | Genetica: {raza_L} | Sexo: {sexo_L}", 0, 1)
            pdf.cell(0, 5, f"Peso Actual: {p_act} kg | Peso Meta: {p_obj} kg | GDE: {gain} kg/dia | Dias: {dias:.0f}", 0, 1)
            pdf.ln(3)
            
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "2. Corrida Financiera y Logistica de Alimento", 0, 1)
            pdf.set_font("Arial", "", 9)
            pdf.cell(0, 5, f"Costo Optimo por Tonelada: ${costo_ton:,.2f} MXN | Alimento Total Lote: {tons_lote:,.1f} tons", 0, 1)
            pdf.cell(0, 5, f"Costo Total de Alimentacion del Ciclo: ${cost_lote:,.2f} MXN", 0, 1)
            pdf.ln(3)
            
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "3. Balance Mineral, Salud Ruminal y Sostenibilidad (IPCC)", 0, 1)
            pdf.set_font("Arial", "", 9)
            pdf.cell(0, 5, f"Calcio (Ca): {a_ca:.2f}% | Fosforo (P): {a_p:.2f}% | Relacion Ca:P: {r_cap:.2f}:1 (Ideal 1.5 - 2.0)", 0, 1)
            pdf.cell(0, 5, f"Fibra FND: {a_fnd:.1f}% | peNDF (Anti-acidosis): {a_pendf:.1f}%", 0, 1)
            pdf.cell(0, 5, f"Emision Metano (CH4): {ch4_d:.1f} g/dia | CO2e Anual: {co2e:,.1f} kg/ano", 0, 1)
            pdf.cell(0, 5, f"Valor Potencial Bonos de Carbono: ${bonos:,.2f} MXN por animal/ano", 0, 1)
            pdf.ln(3)
            
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "4. Mezcla Exacta por Tonelada (1,000 kg)", 0, 1)
            pdf.set_font("Arial", "B", 8)
            pdf.cell(80, 6, "Ingrediente", 1)
            pdf.cell(30, 6, "Inclusion (%)", 1)
            pdf.cell(35, 6, "Kg / Tonelada", 1)
            pdf.cell(45, 6, "Costo Parcial ($)", 1)
            pdf.ln()
            
            pdf.set_font("Arial", "", 8)
            for _, row in df_resumen.iterrows():
                if row["Ingrediente"] != "TOTALES / MEZCLA FINAL":
                    pdf.cell(80, 5, str(row["Ingrediente"]), 1)
                    pdf.cell(30, 5, f"{row['Inclusion (%)']}%", 1)
                    pdf.cell(35, 5, f"{row['Kg por Tonelada (1,000 kg)']}", 1)
                    pdf.cell(45, 5, str(row['Aporte al Costo Total ($)']), 1)
                    pdf.ln()
            
            tot_inc = df_resumen[df_resumen["Ingrediente"] != "TOTALES / MEZCLA FINAL"]['Inclusion (%)'].sum()
            tot_kg = df_resumen[df_resumen["Ingrediente"] != "TOTALES / MEZCLA FINAL"]['Kg por Tonelada (1,000 kg)'].sum()
            pdf.set_font("Arial", "B", 8)
            pdf.cell(80, 5, "TOTALES / MEZCLA FINAL", 1)
            pdf.cell(30, 5, f"{tot_inc:.1f}%", 1)
            pdf.cell(35, 5, f"{tot_kg:.1f} kg", 1)
            pdf.cell(45, 5, f"${costo_ton:,.2f}", 1)
            pdf.ln()
                
            pdf.ln(3)
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "5. Protocolo de Mezclado para Operarios", 0, 1)
            pdf.set_font("Arial", "", 8)
            pdf.multi_cell(0, 4, 
                "1. Orden en batea: Forrajes secos (rastrojo) para asegurar peNDF y evitar acidosis.\n"
                "2. Incorporar ensilados y subproductos humedos.\n"
                "3. Anadir granos energeticos y fuentes de proteina (soya/canola).\n"
                "4. Agregar aditivos y minerales especializados (Sales y Urea con cuidado).\n"
                "5. Anadir melaza liquida al final con agua y mezclar de 8 a 10 minutos."
            )
            return bytes(pdf.output())

        df_mezcla_pdf = pd.DataFrame(tabla_mezcla_con_totales)
        pdf_data = generar_pdf_ejecutivo(
            df_mezcla_pdf, resultado.fun, fase, raza_seleccionada, sexo_lote, marco_lote, peso_actual, peso_objetivo, gde, dias_a_meta,
            cantidad_animales, aporte_ca, aporte_p, relacion_ca_p, aporte_fnd, aporte_pendf,
            ch4_g_dia, co2e_anual, valor_bono_mxn, costo_total_lote, alimento_total_ciclo / 1000.0
        )
        
        st.markdown("---")
        st.subheader("📥 Descarga de Reporte Ejecutivo PDF Elite 360")
        st.markdown("Haz clic en el botón para descargar el reporte oficial con bonos de carbono, logística de lote, balance mineral y protocolo de carga:")
        
        st.download_button(
            label="📄 Descargar Reporte Ejecutivo PDF (Elite, Carbono & Bunk Management)",
            data=pdf_data,
            file_name=f"Reporte_GanaderIA_Elite_{fase.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        st.markdown("---")
        st.subheader("🥧 Composición Porcentual de la Dieta por Categoría")
        df_pie = pd.DataFrame(list(categorias_pie.items()), columns=["Categoría", "Porcentaje"])
        colores_campo = ['#2d5a27', '#bc6c25', '#dda15e', '#606c38', '#283618', '#e76f51']
        fig_pie = px.pie(df_pie, names="Categoría", values="Porcentaje", hole=0.4, title="Distribución de Insumos Seleccionados en la Mezcla", color_discrete_sequence=colores_campo)
        fig_pie.update_layout(font=dict(family="Inter", color="#2b2d42"))
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("⚠️ Genere un balance factible en la Pestaña 3 para desbloquear los cálculos de Bunk Management y el Reporte PDF.")
