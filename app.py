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
    page_title="Ganader-IA Pro | Nutrición, Minerales y Sostenibilidad NASEM",
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
            <h1 style="margin: 0; font-size: 2.2em; color: #ffffff; letter-spacing: 0.5px; font-family: 'Inter', sans-serif;">Ganader-IA <span style="background-color: #dda15e; color: #1f2421; padding: 2px 8px; border-radius: 6px; font-size: 0.6em; vertical-align: middle;">PRO MINERAL</span></h1>
            <p style="margin: 6px 0 0 0; font-size: 1.05em; color: #f4f1de; font-weight: 300; font-family: 'Inter', sans-serif;">Nutrición de Precisión, Minerales Mayores y Salud Ruminal</p>
            <p style="margin: 6px 0 0 0; font-size: 0.85em; color: #ffe8d6; font-style: italic; font-weight: 400; font-family: 'Inter', sans-serif;">✨ Tecnología e Innovación en tus manos</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 3. BASE DE DATOS INICIAL CON MINERALES MAYORES Y PERFILES EDITABLES ---
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

# --- 4. CONTROLES GENERALES Y PARÁMETROS PRODUCTIVOS EN LA BARRA LATERAL ---
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

# --- MODELADO PREDICTIVO BIOLÓGICO NASEM ---
factor_clima = 0.93 if estacion == "Invierno" else (1.05 if estacion == "Verano" else 1.00)
cms_estimado = peso_actual * 0.024 * factor_clima

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

meta_pc_min = meta_pc_base * factor_pc
meta_neg_min = meta_neg_base * factor_neg

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='text-align: center; color: #555; font-size: 0.85em; padding: 5px; font-family: Inter, sans-serif;'>"
    "<b>Ganader-IA Pro MINERAL</b><br>"
    "Creado por el <b>Dr. Alejandro Castañeda Correa</b>.<br><br>"
    "Balance Mineral y Nutrición de Precisión."
    "</div>",
    unsafe_allow_html=True
)

# --- 5. INTERFAZ MODULAR POR PESTAÑAS (3 TABS) ---
tab1, tab2, tab3 = st.tabs([
    "📋 1. Resumen y Predicciones", 
    "🧪 2. Laboratorio y Selección Regional", 
    "📊 3. Resultados, Minerales y Reporte PDF"
])

with tab1:
    st.subheader("Predicciones de Parámetros Productivos y Crecimiento")
    st.markdown("Proyecciones biológicas del lote basadas en peso actual, genética y condiciones ambientales:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Etapa Fisiológica", fase)
        st.metric("Ganancia Esperada (GDE)", f"{gde} kg/día")
    with col2:
        st.metric("Consumo MS Inicial", f"{cms_estimado:.2f} kg/día")
        st.metric("Días Proyectados a Meta", f"{dias_a_meta:.0f} días")
    with col3:
        st.metric("Ganancia Total Esperada", f"{kg_por_ganar:.1f} kg")
        st.metric("Genética", raza_seleccionada.split("(")[0].strip())
    
    st.markdown("---")
    st.subheader("📈 Gráfica de Comportamiento: Peso y Consumo de Materia Seca en el Tiempo")
    st.markdown(f"Evolución semanal del lote desde el **Peso Inicial ({peso_actual} kg)** hasta el **Peso Final ({peso_objetivo} kg)** considerando una GDE constante de **{gde} kg/día**:")
    
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

    fig_comportamiento.add_trace(
        go.Scatter(
            x=lista_semanas,
            y=lista_pesos,
            name="Peso Proyectado (kg)",
            mode="lines+markers",
            line=dict(color="#2d5a27", width=3.5),
            marker=dict(size=8, color="#2d5a27")
        ),
        secondary_y=False,
    )

    fig_comportamiento.add_trace(
        go.Scatter(
            x=lista_semanas,
            y=lista_cms,
            name="Consumo Materia Seca (kg/día)",
            mode="lines+markers",
            line=dict(color="#bc6c25", width=3, dash="dash"),
            marker=dict(size=8, color="#bc6c25")
        ),
        secondary_y=True,
    )

    fig_comportamiento.update_layout(
        title=dict(
            text=f"Dinámica de Engorda (GDE: {gde} kg/d | Clima: {estacion})", 
            font=dict(family="Inter", size=14),
            x=0.5,
            xanchor="center"
        ),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(family="Inter", color="#2b2d42"),
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.25, 
            xanchor="center", 
            x=0.5
        ),
        margin=dict(l=20, r=20, t=60, b=70)
    )

    fig_comportamiento.update_yaxes(title_text="<b>Peso Vivo del Animal (kg)</b>", secondary_y=False, color="#2d5a27")
    fig_comportamiento.update_yaxes(title_text="<b>Consumo de Materia Seca (kg/día)</b>", secondary_y=True, color="#bc6c25")

    st.plotly_chart(fig_comportamiento, use_container_width=True)

with tab2:
    st.subheader("🧪 Laboratorio de Nutrición Editable y Control Regional")
    st.markdown(
        "**Personaliza por completo los perfiles nutricionales y de minerales de tus materias primas.** "
        "Selecciona cuáles insumos están disponibles en tu rancho (`✓`), ajusta sus límites de inclusión, "
        "y edita directamente en la tabla los valores de **Proteína, Energía, FND, peNDF, PDR, PND, Calcio, Fósforo, Sodio, Magnesio y Lípidos** "
        "según los análisis de tu laboratorio local:"
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

# --- 6. EXTRACCIÓN Y MOTOR DE PROGRAMACIÓN LINEAL ---
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

A_ub = np.array([
    -pc,
    -neg,
    -fnd,
    -pendf,
    -pdr,
    -pnd,
    -ca,
    -p_min_ing
])
b_ub = np.array([
    -meta_pc_min,
    -meta_neg_min,
    -meta_fnd_min,
    -meta_pendf_min,
    -meta_pdr_min,
    -meta_pnd_min,
    -meta_ca_min,
    -meta_p_min
])

resultado = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

with tab3:
    st.subheader("Reporte Financiero, Balance Mineral y Mitigación de Metano")
    
    if resultado.success:
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric(label="Costo Óptimo por Tonelada", value=f"${resultado.fun:,.2f} MXN")
        with col_res2:
            st.metric(label="Estado del Proceso", value="Factible (Balance Óptimo) 🟢")
        
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
        
        df_mezcla_final = pd.DataFrame(tabla_mezcla)
        st.dataframe(df_mezcla_final, use_container_width=True, hide_index=True)
        
        # --- CÁLCULOS AVANZADOS NASEM, MINERALES Y METANO ---
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
        status_ca_p = "🟢 Óptimo (1.5 - 2.0:1)" if (1.4 <= relacion_ca_p <= 2.1) else "⚠️ Revisar Relación"
        
        # Estimación de Metano IPCC Tier 2
        ge_diaria = cms_estimado * 18.4 
        reduccion_lipidica = max(0.0, (aporte_lipidos - 3.0) * 0.003)
        factor_fnd_ym = 0.035 + (aporte_fnd / 100.0) * 0.035
        ym_ajustado = max(0.030, factor_fnd_ym - reduccion_lipidica)
        
        ch4_g_dia = (ge_diaria * ym_ajustado / 55.65) * 1000
        ch4_g_kg_ganancia = ch4_g_dia / gde if gde > 0 else 0
        co2e_anual = (ch4_g_dia * 365 / 1000.0) * 28.0 
        
        st.markdown("---")
        st.subheader("🛡️ Validación de Minerales Mayores, Relación Ca:P y Salud Ruminal")
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Calcio (Ca)", f"{aporte_ca:.2f}%", "Mineral Mayor")
            st.metric("Fibra FND", f"{aporte_fnd:.1f}%")
        with col_m2:
            st.metric("Fósforo (P)", f"{aporte_p:.2f}%", "Mineral Mayor")
            st.metric("Fibra peNDF", f"{aporte_pendf:.1f}%", "Anti-acidosis")
        with col_m3:
            st.metric("Relación Ca:P", f"{relacion_ca_p:.2f}:1", status_ca_p)
            st.metric("Lípidos Totales", f"{aporte_lipidos:.1f}%")
        with col_m4:
            st.metric("Sodio (Na)", f"{aporte_na:.2f}%")
            st.metric("Magnesio (Mg)", f"{aporte_mg:.2f}%")

        # --- FUNCIÓN GENERADORA DE PDF EJECUTIVO CON MINERALES ---
        def generar_pdf_ejecutivo(df_resumen, costo_ton, etapa, raza_L, p_act, p_obj, gain, dias, a_pc, a_neg, a_ca, a_p, a_na, a_mg, r_cap, a_fnd, a_pendf, ch4_d, co2e):
            pdf = FPDF()
            pdf.add_page()
            
            # Encabezado
            pdf.set_font("Arial", "B", 15)
            pdf.cell(0, 8, "Ganader-IA Pro MINERAL - Reporte Ejecutivo Nutricional", 0, 1, "C")
            pdf.set_font("Arial", "I", 9)
            pdf.cell(0, 5, "Creado por el Dr. Alejandro Castaneda Correa", 0, 1, "C")
            pdf.ln(3)
            
            # Datos del Lote
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "1. Parametros Biologicos y Predicciones del Lote", 0, 1)
            pdf.set_font("Arial", "", 9)
            pdf.cell(0, 5, f"Fisiologia: {etapa} | Genetica: {raza_L}", 0, 1)
            pdf.cell(0, 5, f"Peso Actual: {p_act} kg | Peso Meta: {p_obj} kg | GDE: {gain} kg/dia | Dias: {dias:.0f}", 0, 1)
            pdf.ln(3)
            
            # Corrida Financiera
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "2. Corrida Financiera y Costo Optimo", 0, 1)
            pdf.set_font("Arial", "", 9)
            pdf.cell(0, 5, f"Costo Optimo por Tonelada de Alimento: ${costo_ton:,.2f} MXN", 0, 1)
            pdf.ln(3)
            
            # Balance Mineral y Salud Ruminal
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "3. Balance de Minerales Mayores y Salud Ruminal (NASEM)", 0, 1)
            pdf.set_font("Arial", "", 9)
            pdf.cell(0, 5, f"Calcio (Ca): {a_ca:.2f}% | Fosforo (P): {a_p:.2f}% | Relacion Ca:P: {r_cap:.2f}:1 (Ideal 1.5 - 2.0)", 0, 1)
            pdf.cell(0, 5, f"Sodio (Na): {a_na:.2f}% | Magnesio (Mg): {a_mg:.2f}%", 0, 1)
            pdf.cell(0, 5, f"Fibra FND: {a_fnd:.1f}% | Fibra peNDF (Anti-acidosis): {a_pendf:.1f}%", 0, 1)
            pdf.cell(0, 5, f"Emision Metano (CH4): {ch4_d:.1f} g/dia | CO2e Anual: {co2e:,.1f} kg/ano", 0, 1)
            pdf.ln(3)
            
            # Tabla de ingredientes
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
                pdf.cell(80, 5, str(row["Ingrediente"]), 1)
                pdf.cell(30, 5, f"{row['Inclusion (%)']}%", 1)
                pdf.cell(35, 5, f"{row['Kg por Tonelada (1,000 kg)']}", 1)
                pdf.cell(45, 5, str(row['Aporte al Costo Total ($)']), 1)
                pdf.ln()
                
            pdf.ln(3)
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, "5. Protocolo de Mezclado para Operarios", 0, 1)
            pdf.set_font("Arial", "", 8)
            pdf.multi_cell(0, 4, 
                "1. Orden en batea: Forrajes secos (rastrojo) para asegurar peNDF y evitar acidosis.\n"
                "2. Incorporar granos energeticos y fuentes de proteina (soya/canola).\n"
                "3. Agregar aditivos y minerales especializados (Sales y Urea con cuidado).\n"
                "4. Anadir melaza liquida al final con agua para adherencia y palatabilidad.\n"
                "5. Tiempo de mezcla recomendado: 8 a 10 minutos."
            )
            return bytes(pdf.output())

        pdf_data = generar_pdf_ejecutivo(
            df_mezcla_final, resultado.fun, fase, raza_seleccionada, peso_actual, peso_objetivo, gde, dias_a_meta,
            aporte_pc, aporte_neg, aporte_ca, aporte_p, aporte_na, aporte_mg, relacion_ca_p, aporte_fnd, aporte_pendf,
            ch4_g_dia, co2e_anual
        )
        
        st.markdown("---")
        st.subheader("📥 Descarga de Reporte Ejecutivo PDF MINERAL")
        st.markdown("Haz clic en el botón para descargar el reporte oficial con el balance mineral, corrida financiera y protocolo de carga:")
        
        st.download_button(
            label="📄 Descargar Reporte Ejecutivo PDF (Minerales, Sostenibilidad & Operarios)",
            data=pdf_data,
            file_name=f"Reporte_GanaderIA_Mineral_{fase.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        st.markdown("---")
        st.subheader("🥧 Composición Porcentual de la Dieta por Categoría")
        df_pie = pd.DataFrame(list(categorias_pie.items()), columns=["Categoría", "Porcentaje"])
        
        colores_campo = ['#2d5a27', '#bc6c25', '#dda15e', '#606c38', '#283618', '#e76f51']
        fig_pie = px.pie(
            df_pie, 
            names="Categoría", 
            values="Porcentaje", 
            hole=0.4, 
            title="Distribución de Insumos Seleccionados en la Mezcla",
            color_discrete_sequence=colores_campo
        )
        fig_pie.update_layout(font=dict(family="Inter", color="#2b2d42"))
        st.plotly_chart(fig_pie, use_container_width=True)
                
    else:
        st.error(
            "⚠️ **Aviso del Optimizador MINERAL:** Con los ingredientes seleccionados y los límites estrictos de minerales (Ca, P) o fibra, "
            "no se encontró una solución matemática factible. Te sugerimos activar una fuente mineral especializada o ajustar los rangos de inclusión en la Pestaña 2."
        )
