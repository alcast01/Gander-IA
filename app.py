import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fpdf import FPDF

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO VISUAL COMPACTO ---
st.set_page_config(
    page_title="Ganader-IA Elite 360 | Nutrición, Economía y Control Mensual",
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
    
    /* Métricas ultra compactas para evitar cortes */
    .stMetric {
        background-color: #ffffff;
        padding: 6px 8px !important;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(45, 90, 39, 0.05);
        border-left: 3px solid #2d5a27;
        border-top: 1px solid #e6e2dd;
        border-right: 1px solid #e6e2dd;
        border-bottom: 1px solid #e6e2dd;
        margin-bottom: 6px !important;
    }
    
    .stMetric label {
        font-size: 0.68rem !important;
        color: #666666 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-size: 0.95rem !important;
        color: #1f2421 !important;
        font-weight: 700 !important;
    }
    
    h1, h2, h3, h4 {
        color: #1f2421;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700;
        line-height: 1.2;
    }

    p, span, label {
        font-family: 'Inter', sans-serif !important;
        color: #333333;
        line-height: 1.4;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGOTIPO VECTORIAL INSTITUCIONAL ---
st.markdown("""
    <div style="display: flex; align-items: center; background: linear-gradient(135deg, #2d5a27 0%, #bc6c25 100%); padding: 15px; border-radius: 12px; box-shadow: 0 4px 12px rgba(45,90,39,0.15); margin-bottom: 15px; color: white; flex-wrap: wrap; gap: 10px;">
        <div style="flex-shrink: 0;">
            <svg width="45" height="45" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" fill="#ffffff"/>
                <circle cx="12" cy="12" r="3" fill="#dda15e"/>
            </svg>
        </div>
        <div style="flex-grow: 1; min-width: 200px;">
            <h1 style="margin: 0; font-size: 1.5em; color: #ffffff; letter-spacing: 0.5px; font-family: 'Inter', sans-serif;">Ganader-IA <span style="background-color: #dda15e; color: #1f2421; padding: 2px 6px; border-radius: 4px; font-size: 0.55em; vertical-align: middle;">ELITE 360</span></h1>
            <p style="margin: 2px 0 0 0; font-size: 0.85em; color: #f4f1de; font-weight: 300; font-family: 'Inter', sans-serif;">Optimización, Control Mensual (30 Días) y Sostenibilidad</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 3. BASE DE DATOS INICIAL CON MINERALES DE TLALTENANGO ---
data_respaldo = {
    "Nombre del Ingrediente": [
        "Rastrojo de maiz molido", 
        "Harina de soya", 
        "Grano de maiz molido", 
        "Urea", 
        "Ensilado de maiz", 
        "Canola (pasta)", 
        "Melaza liquida",
        "Purina Mineral Tech (Tlaltenango)", 
        "Malta Cleyton Ganafos", 
        "Grasa de paso Lactomil"
    ],
    "Categoria": ["Forraje", "Suplemento Proteico", "Grano Energetico", "Suplemento NPN", "Forraje Humedo", "Suplemento Proteico", "Subproducto / Energetico", "Suplemento Mineral", "Suplemento Mineral", "Suplemento Energetico"],
    "Disponible": [True, True, True, True, True, True, True, True, True, True],
    "Precio Estimado (MXN/ton)": [2500.0, 12500.0, 5800.0, 16000.0, 1200.0, 8500.0, 4800.0, 19000.0, 18500.0, 32000.0],
    "Proteina Cruda (PC % MS)": [5.5, 48.0, 8.5, 281.0, 8.0, 38.0, 4.8, 0.0, 0.0, 1.0],
    "NEg (Mcal/kg)": [0.35, 1.48, 1.55, 0.0, 0.85, 1.15, 1.22, 0.0, 0.0, 1.65],
    "FND (% MS)": [75.0, 12.0, 9.0, 0.0, 45.0, 28.0, 0.0, 0.0, 0.0, 0.0],
    "peNDF (% MS)": [65.0, 2.0, 3.0, 0.0, 30.0, 10.0, 0.0, 0.0, 0.0, 0.0],
    "PDR (% MS)": [3.5, 33.6, 5.5, 281.0, 5.0, 24.0, 4.5, 0.0, 0.0, 0.0],
    "PND (% MS)": [2.0, 14.4, 3.0, 0.0, 3.0, 14.0, 0.3, 0.0, 0.0, 1.0],
    "Calcio (Ca %)": [0.35, 0.30, 0.02, 0.0, 0.25, 0.70, 0.80, 14.0, 16.0, 1.0],
    "Fosforo (P %)": [0.10, 0.65, 0.30, 0.0, 0.22, 1.10, 0.08, 7.0, 8.0, 0.1],
    "Sodio (Na %)": [0.02, 0.03, 0.02, 0.0, 0.02, 0.05, 0.10, 10.0, 9.0, 0.0],
    "Magnesio (Mg %)": [0.15, 0.28, 0.12, 0.0, 0.18, 0.50, 0.40, 2.0, 2.5, 0.0],
    "Lípidos / Extracto Etéreo (%)": [1.5, 1.8, 3.8, 0.0, 3.0, 3.5, 0.5, 0.0, 0.0, 99.0],
    "Min Inclusión (%)": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "Max Inclusión (%)": [100.0, 100.0, 100.0, 1.5, 100.0, 100.0, 100.0, 5.0, 5.0, 5.0]
}
df_base = pd.DataFrame(data_respaldo)

# --- 4. BARRA LATERAL ORGANIZADA EN MENÚS DESPLEGABLES (EXPANDERS) ---
st.sidebar.markdown("### 🎛️ Panel de Control Elite")

with st.sidebar.expander("📅 Etapas y Control Mensual (30 Días)", expanded=True):
    mes_engorda = st.selectbox(
        "Hito / Mes Actual de Engorda",
        [
            "Mes 0 - Recepción y Adaptación (200 - 280 kg)",
            "Mes 1 - Crecimiento Inicial (280 - 334 kg)",
            "Mes 2 - Crecimiento / Repasto (334 - 376 kg)",
            "Mes 3 - Transición / Desarrollo (376 - 418 kg)",
            "Mes 4 - Engorda Intermedia (418 - 460 kg)",
            "Mes 5 - Finalización Avanzada (460 - 502 kg)",
            "Mes 6+ - Cierre y Venta (502 - 520+ kg)"
        ]
    )
    # Asignación automática de peso sugerido según el mes seleccionado
    pesos_sugeridos = {
        "Mes 0": 250.0, "Mes 1": 292.0, "Mes 2": 334.0, 
        "Mes 3": 376.0, "Mes 4": 418.0, "Mes 5": 460.0, "Mes 6+": 502.0
    }
    sugerencia_peso = pesos_sugeridos.get(mes_engorda[:5], 250.0)
    
    cantidad_animales = st.number_input("Número de Cabezas en el Lote", min_value=1, max_value=5000, value=100, step=10)
    peso_actual = st.slider("Peso Actual del Animal (kg)", min_value=200.0, max_value=650.0, value=sugerencia_peso, step=10.0)
    peso_objetivo = st.slider("Peso de Venta / Meta (kg)", min_value=400.0, max_value=750.0, value=520.0, step=10.0)
    gde = st.slider("Ganancia Diaria Esperada (GDE kg/día)", min_value=0.8, max_value=2.2, value=1.4, step=0.1)

with st.sidebar.expander("💰 Parámetros Económicos y de Mercado", expanded=False):
    precio_compra_kg = st.number_input("Compra Becerro (MXN/kg)", min_value=30.0, max_value=100.0, value=55.0, step=1.0)
    precio_venta_kg = st.number_input("Venta Ganado Gordo (MXN/kg)", min_value=30.0, max_value=100.0, value=50.0, step=1.0)
    costo_sanidad_fijo = st.number_input("Sanidad y Manejo (MXN/cab)", min_value=0.0, max_value=2000.0, value=350.0, step=50.0)
    costo_mano_obra_fijo = st.number_input("Mano de Obra (MXN/cab)", min_value=0.0, max_value=3000.0, value=450.0, step=50.0)

with st.sidebar.expander("🌾 Sistema de Producción y Pastoreo", expanded=False):
    sistema_produccion = st.selectbox("Sistema", ["Corral / Engorda Intensiva (Feedlot)", "Semi-estabulado (Mixto / Suplementación en Pastoreo)", "Pastoreo Extensivo (Praderas / Agostadero)"])
    condiciones_pastoreo = st.selectbox("Condiciones Pastoreo", ["N/A (Corral Intensivo)", "Pradera Cultivada / Riego (Alta Calidad)", "Pradera Nativa / Agostadero en Temporal", "Pradera Nativa / Agostadero Árido (Alta Caminata)", "Sistema Silvopastoril / Arbustivo"])
    estado_pasto = st.selectbox("Estado del Pasto", ["N/A (Corral / Sin Pastoreo)", "Vegetativo Temprano (Alta digestibilidad y PC)", "Vegetativo Tardío / Pre-floración (Calidad media)", "Floración / Madurez (Fibroso, baja PC)", "Lignificado / Seco (Muy baja digestibilidad)"])
    estacion = st.selectbox("Temporada / Clima", ["Templado", "Invierno", "Verano"])

with st.sidebar.expander("🧬 Genética, Sexo y Marco", expanded=False):
    raza_seleccionada = st.selectbox("Raza", ["Compuestas / Adaptadas (Beefmaster/Brangus)", "Británicas (Angus/Hereford)", "Continentales (Charolais/Simmental)", "Cebú / Tropicales (Bos indicus)", "Ganado Criollo / Local"])
    sexo_lote = st.selectbox("Categoría Zootécnica", ["Novillos (Castrados)", "Toros Enteros", "Vaquillas de Repasto/Engorda", "Vacas de Desecho / Finalización"])
    marco_lote = st.selectbox("Tamaño de Marco", ["Mediano (Standard)", "Precoz / Engrase rápido", "Grande (Continental / Retrasado)"])

with st.sidebar.expander("🌡️ Variables Avanzadas y JDS", expanded=False):
    condicion_corporal = st.slider("Condición Corporal (1.0 - 5.0)", min_value=1.0, max_value=5.0, value=2.5, step=0.5)
    nivel_thi = st.selectbox("Estrés Térmico (THI)", ["Confort Térmico (< 74)", "Estrés Moderado (74-78)", "Estrés Severo (> 78)"])
    perfil_aa = st.selectbox("Modelo Aminoácidos", ["Estándar (Proteína Cruda)", "Avanzado (Optimización Lisina:Metionina 3:1)"])
    aditivo_ruminal = st.selectbox("Modificadores / Aditivos", ["Ninguno", "Ionóforos (Monensina / Lasalocid)", "Buffer (Bicarbonato / Óxido Mg)", "Ambos (Ionóforo + Buffer)"])
    historial_nutricional = st.selectbox("Historial Nutricional", ["Desarrollo Continuo (Normal)", "Crecimiento Compensatorio (Post-restricción)"])
    promotor_crecimiento = st.selectbox("Promotores Crecimiento", ["Ninguno", "Implante Hormonal", "Agonista β-adrenérgico (Finalización)"])
    condicion_lodo = st.selectbox("Condición de Corral / Lodo", ["Seco y Confortable", "Lodo Moderado (10-15 cm)", "Lodo Severo (>20 cm)"])

# --- MODELADO PREDICTIVO BIOLÓGICO AVANZADO ---
factor_clima = 0.93 if estacion == "Invierno" else (1.05 if estacion == "Verano" else 1.00)
factor_thi = 0.93 if "Moderado" in nivel_thi else (0.83 if "Severo" in nivel_thi else 1.00)
factor_cc = 1.06 if condicion_corporal < 3.0 else 1.00 
factor_aa = 1.04 if "Avanzado" in perfil_aa else 1.00

factor_sistema_cms = 1.12 if "Pastoreo" in sistema_produccion else (1.06 if "Semi-estabulado" in sistema_produccion else 1.00)
factor_sistema_energ = 1.10 if "Pastoreo" in sistema_produccion else (1.05 if "Semi-estabulado" in sistema_produccion else 1.00)

if "Árido" in condiciones_pastoreo:
    factor_pastoreo_energia = 1.10
elif "Temporal" in condiciones_pastoreo:
    factor_pastoreo_energia = 1.05
elif "Silvopastoril" in condiciones_pastoreo:
    factor_pastoreo_energia = 1.03
else:
    factor_pastoreo_energia = 1.00

if "Lignificado" in estado_pasto or "Madurez" in estado_pasto:
    factor_fenologia_pc = 1.15 * factor_aa
    factor_fenologia_energ = 1.10
elif "Tardío" in estado_pasto:
    factor_fenologia_pc = 1.08 * factor_aa
    factor_fenologia_energ = 1.05
else:
    factor_fenologia_pc = 1.00 * factor_aa
    factor_fenologia_energ = 1.00

factor_lodo = 1.00 if condicion_lodo == "Seco y Confortable" else (1.12 if "Moderado" in condicion_lodo else 1.25)
cms_estimado = peso_actual * 0.024 * factor_clima * factor_thi * factor_cc * factor_sistema_cms / (factor_lodo if "Severo" in condicion_lodo else 1.0)

kg_por_ganar = max(0.0, peso_objetivo - peso_actual)
dias_a_meta = kg_por_ganar / gde if gde > 0 else 0

if peso_actual < 280:
    fase = "Recepción y Adaptación (Mes 0)"
    meta_pc_base = (0.135 + (gde * 0.015)) * factor_fenologia_pc
    meta_neg_base = (0.70 + (gde * 0.09)) * factor_sistema_energ * factor_pastoreo_energia * factor_fenologia_energ
    meta_fnd_min = 0.32
    meta_pendf_min = 0.24
    meta_pdr_min = 0.082
    meta_pnd_min = 0.048
    meta_ca_min = 0.0055
    meta_p_min = 0.0035
elif peso_actual < 380:
    fase = "Crecimiento / Repasto (Mes 1-2)"
    meta_pc_base = (0.125 + (gde * 0.015)) * factor_fenologia_pc
    meta_neg_base = (0.80 + (gde * 0.09)) * factor_sistema_energ * factor_pastoreo_energia * factor_fenologia_energ
    meta_fnd_min = 0.29
    meta_pendf_min = 0.21
    meta_pdr_min = 0.075
    meta_pnd_min = 0.042
    meta_ca_min = 0.0050
    meta_p_min = 0.0030
elif peso_actual < 460:
    fase = "Desarrollo / Transición (Mes 3-4)"
    meta_pc_base = (0.115 + (gde * 0.015)) * factor_fenologia_pc
    meta_neg_base = (0.90 + (gde * 0.09)) * factor_sistema_energ * factor_pastoreo_energia * factor_fenologia_energ
    meta_fnd_min = 0.27
    meta_pendf_min = 0.19
    meta_pdr_min = 0.070
    meta_pnd_min = 0.040
    meta_ca_min = 0.0048
    meta_p_min = 0.0029
else:
    fase = "Finalización / Engorda Pesada (Mes 5-6+)"
    meta_pc_base = (0.105 + (gde * 0.015)) * factor_fenologia_pc
    meta_neg_base = (1.00 + (gde * 0.10)) * factor_sistema_energ * factor_pastoreo_energia * factor_fenologia_energ
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

if "Toros" in sexo_lote:
    factor_sexo_pc = 1.08
    factor_sexo_neg = 1.04
elif "Vaquillas" in sexo_lote:
    factor_sexo_pc = 0.96
    factor_sexo_neg = 1.06
elif "Vacas" in sexo_lote:
    factor_sexo_pc = 0.94
    factor_sexo_neg = 1.02
else:
    factor_sexo_pc = 1.00
    factor_sexo_neg = 1.00

if "Precoz" in marco_lote:
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
    "SaaS de Nutrición, Control Mensual y Sostenibilidad."
    "</div>",
    unsafe_allow_html=True
)

# --- 5. INTERFAZ MODULAR POR PESTAÑAS (4 TABS ELITE) ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 1. Resumen y Sensibilidad", 
    "🧪 2. Laboratorio y Google Sheets", 
    "📊 3. Balance Económico, Mineral y Carbono", 
    "🚜 4. Bunk Management y Operarios"
])

with tab1:
    st.subheader("Predicciones de Parámetros Productivos y Control Mensual")
    st.markdown(f"Evaluación del lote bajo **{mes_engorda}** | Sistema: *{sistema_produccion}* | Perfil AA: *{perfil_aa}*:")
    
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
        cms_proy = peso_proy * 0.024 * factor_clima * factor_thi * factor_sistema_cms
        lista_semanas.append(f"Semana {i}")
        lista_pesos.append(peso_proy)
        lista_cms.append(round(cms_proy, 2))
    
    fig_comportamiento = make_subplots(specs=[[{"secondary_y": True}]])
    fig_comportamiento.add_trace(go.Scatter(x=lista_semanas, y=lista_pesos, name="Peso Proyectado (kg)", mode="lines+markers", line=dict(color="#2d5a27", width=3.5)), secondary_y=False)
    fig_comportamiento.add_trace(go.Scatter(x=lista_semanas, y=lista_cms, name="Consumo Materia Seca (kg/día)", mode="lines+markers", line=dict(color="#bc6c25", width=3, dash="dash")), secondary_y=True)
    fig_comportamiento.update_layout(title=dict(text=f"Dinámica de Engorda ({perfil_aa[:18]} | GDE: {gde} kg/d)", font=dict(family="Inter", size=13), x=0.5), plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", font=dict(family="Inter", color="#2b2d42"), legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5), margin=dict(l=20, r=20, t=60, b=70))
    fig_comportamiento.update_yaxes(title_text="<b>Peso Vivo del Animal (kg)</b>", secondary_y=False, color="#2d5a27")
    fig_comportamiento.update_yaxes(title_text="<b>Consumo de Materia Seca (kg/día)</b>", secondary_y=True, color="#bc6c25")
    st.plotly_chart(fig_comportamiento, use_container_width=True)

with tab2:
    st.subheader("🧪 Laboratorio de Nutrición y Base de Datos en Google Sheets")
    st.markdown(
        "**Personaliza por completo los perfiles nutricionales y de minerales de tus materias primas.** "
        "Sin restricciones mínimas forzadas para garantizar el **costo mínimo absoluto** en la optimización lineal. "
        "Puedes acceder, editar o respaldar esta tabla directamente en tu nube de Google Drive:"
    )
    
    st.markdown(
        "🔗 **[Abrir Base de Datos de Ingredientes en Google Sheets (Versión V11)](https://docs.google.com/spreadsheets/d/10LccHsdSqXYf_WisztCiIUEYAE8WUnJfDcY4WbB59DY/edit?usp=drivesdk&ouid=111418825164788732728)**",
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    
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

# --- 6. EXTRACCIÓN Y MOTOR DE PROGRAMACIÓN LINEAL (CON AUTO-RECUPERACIÓN Y TOLERANCIA) ---
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

# Estrategia de Auto-Recuperación por Niveles de Tolerancia
resultado = None
modo_tolerancia_activo = False

# Intento 1: Restricciones ideales (Ca:P 1.5-2.0, metas exactas)
row_ca_p_min = -ca + 1.5 * p_min_ing
row_ca_p_max = ca - 2.0 * p_min_ing
A_ub = np.array([-pc, -neg, -fnd, -pendf, -pdr, -pnd, -ca, -p_min_ing, row_ca_p_min, row_ca_p_max])
b_ub = np.array([-meta_pc_min, -meta_neg_min, -meta_fnd_min, -meta_pendf_min, -meta_pdr_min, -meta_pnd_min, -meta_ca_min, -meta_p_min, 0.0, 0.0])

resultado = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

# Intento 2: Si falla, relajar Ca:P a 1.2-2.5
if not resultado.success:
    row_ca_p_min_rel = -ca + 1.2 * p_min_ing
    row_ca_p_max_rel = ca - 2.5 * p_min_ing
    A_ub_rel = np.array([-pc, -neg, -fnd, -pendf, -pdr, -pnd, -ca, -p_min_ing, row_ca_p_min_rel, row_ca_p_max_rel])
    resultado = linprog(c, A_ub=A_ub_rel, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if resultado.success:
        modo_tolerancia_activo = True

# Intento 3: Si aún falla, relajar metas nutricionales en un 10% (Auto-recuperación total)
if not resultado.success:
    meta_pc_min_rel = meta_pc_min * 0.90
    meta_neg_min_rel = meta_neg_min * 0.90
    b_ub_rel2 = np.array([-meta_pc_min_rel, -meta_neg_min_rel, -meta_fnd_min, -meta_pendf_min, -meta_pdr_min, -meta_pnd_min, -meta_ca_min, -meta_p_min, 0.0, 0.0])
    resultado = linprog(c, A_ub=A_ub_rel, b_ub=b_ub_rel2, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if resultado.success:
        modo_tolerancia_activo = True

with tab3:
    st.subheader("📊 Evaluación Económica Financiera y Rentabilidad del Negocio")
    
    if resultado.success:
        if modo_tolerancia_activo:
            st.warning("⚠️ **Aviso de Auto-Recuperación Elite:** El sistema ajustó automáticamente los márgenes de tolerancia de minerales y energía para garantizar una solución factible.")
        
        # --- CÁLCULOS ECONÓMICOS DETALLADOS ---
        costo_ton_alimento = resultado.fun
        consumo_total_ciclo_cab = cms_estimado * dias_a_meta
        costo_alimentacion_cab = (consumo_total_ciclo_cab / 1000.0) * costo_ton_alimento
        
        costo_compra_cab = peso_actual * precio_compra_kg
        costo_total_cab = costo_compra_cab + costo_alimentacion_cab + costo_sanidad_fijo + costo_mano_obra_fijo
        
        ingreso_venta_cab = peso_objetivo * precio_venta_kg
        utilidad_neta_cab = ingreso_venta_cab - costo_total_cab
        roi_cab = (utilidad_neta_cab / costo_total_cab) * 100 if costo_total_cab > 0 else 0
        
        costo_por_kg_ganado = costo_alimentacion_cab / kg_por_ganar if kg_por_ganar > 0 else 0
        
        status_rentabilidad = "🟢 Rentable" if utilidad_neta_cab > 0 else "🔴 Negativo"
        
        col_ec1, col_ec2, col_ec3, col_ec4 = st.columns(4)
        with col_ec1:
            st.metric("Compra Becerro", f"${costo_compra_cab:,.0f}")
            st.metric("Alimento/Cab", f"${costo_alimentacion_cab:,.0f}")
        with col_ec2:
            st.metric("Costo Total", f"${costo_total_cab:,.0f}")
            st.metric("Costo x kg", f"${costo_por_kg_ganado:,.1f}")
        with col_ec3:
            st.metric("Ingreso Venta", f"${ingreso_venta_cab:,.0f}")
            st.metric("Utilidad Neta", f"${utilidad_neta_cab:,.0f}")
        with col_ec4:
            st.metric("ROI Ciclo", f"{roi_cab:.1f}%")
            st.metric("Estatus", status_rentabilidad)
            
        st.markdown("---")
        st.markdown("#### 📋 Desglose Analítico de Costos de Producción por Tonelada de Alimento:")
        
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
        
        # --- CÁLCULOS DE SOSTENIBILIDAD Y CARBONO ---
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
        status_ca_p = "🟢 Óptimo"
        riesgo_sara = "🟢 Seguro" if aporte_pendf >= 18.0 else ("🟡 Monitorear" if aporte_pendf >= 14.0 else "🔴 Alto Riesgo")
        
        ge_diaria = cms_estimado * 18.4 
        reduccion_lipidica = max(0.0, (aporte_lipidos - 3.0) * 0.003)
        reduccion_ionoforo = 0.06 if "Ionóforos" in aditivo_ruminal or "Ambos" in aditivo_ruminal else 0.0
        
        factor_fnd_ym = 0.035 + (aporte_fnd / 100.0) * 0.035
        ym_ajustado = max(0.025, factor_fnd_ym - reduccion_lipidica - reduccion_ionoforo)
        
        ch4_g_dia = (ge_diaria * ym_ajustado / 55.65) * 1000
        co2e_anual = (ch4_g_dia * 365 / 1000.0) * 28.0 
        linea_base_co2e = 4200.0
        ahorro_co2e_kg = max(0.0, linea_base_co2e - co2e_anual)
        valor_bono_mxn = (ahorro_co2e_kg / 1000.0) * 350.0
        
        st.markdown("---")
        st.subheader("🛡️ Validación Mineral, Salud Ruminal (JDS) y Sostenibilidad")
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Calcio (Ca)", f"{aporte_pc:.1f}%", "Mineral")
            st.metric("Relación Ca:P", f"{relacion_ca_p:.1f}:1", status_ca_p)
        with col_m2:
            st.metric("Fibra peNDF", f"{aporte_pendf:.1f}%", "Anti-acidosis")
            st.metric("Riesgo SARA", riesgo_sara, "Ruminal")
        with col_m3:
            st.metric("Emisión CH4", f"{ch4_g_dia:.1f} g/d", "IPCC Tier 2")
            st.metric("Eq. CO2e", f"{co2e_anual:,.0f} kg/año")
        with col_m4:
            st.metric("Bonos Carbono", f"${valor_bono_mxn:,.0f}", "Anual/Cab")
            st.metric("Lípidos", f"{aporte_lipidos:.1f}%", "Mitigador")

    else:
        st.error(
            "⚠️ **Aviso del Optimizador Elite 360:** Las restricciones son demasiado restrictivas para los ingredientes habilitados. "
            "Asegúrate de tener marcadas como disponibles al menos una fuente de forraje, un grano energético, una fuente proteica y una sal mineral en la Pestaña 2."
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
            st.metric("Consumo Diario Lote", f"{cms_total_lote:,.1f} kg/día")
        with col_l2:
            st.metric("Alimento Total Lote", f"{alimento_total_ciclo/1000.0:,.1f} tons")
        with col_l3:
            st.metric("Costo Total Ciclo", f"${costo_total_lote:,.0f} MXN")
            
        st.markdown("---")
        st.markdown("#### 📋 Protocolo y Orden de Carga en Batea para Operarios:")
        st.info(
            f"**Lote Activo:** {cantidad_animales} animales | **Hito:** {mes_engorda} | **Sistema:** {sistema_produccion} | **Perfil AA:** {perfil_aa}\n\n"
            "1. **Paso 1 (Forrajes Secos / Fibra Larga):** Cargar rastrojos o harinas fibrosas al inicio para asegurar el peNDF y evitar acidosis metabólica.\n"
            "2. **Paso 2 (Ingredientes Húmedos / Ensilados):** Agregar ensilados o subproductos húmedos calculando la corrección por materia seca.\n"
            "3. **Paso 3 (Granos Energéticos y Proteicos):** Incorporar maíz molido, pasta de soya y canola.\n"
            "4. **Paso 4 (Núcleos, Minerales y Urea):** Agregar las sales minerales especializadas de Tlaltenango y la urea (previa dilución o mezclado homogéneo).\n"
            "5. **Paso 5 (Aditivos / Buffers):** Incorporar buffers (bicarbonato) y aditivos si están seleccionados.\n"
            "6. **Paso 6 (Líquidos):** Verter la melaza líquida con un chorro de agua al final para garantizar adherencia, evitar polvaderas y elevar la palatabilidad.\n"
            "7. **Tiempo de Mezclado:** Operar el carro mezclador de 8 a 10 minutos continuos antes de la distribución en comederos."
        )

        # --- FUNCIÓN GENERADORA DE PDF EJECUTIVO ELITE ---
        def generar_pdf_ejecutivo(df_resumen, costo_ton, etapa, sistema_prod, cond_past, est_pasto, perf_aa, raza_L, sexo_L, marco_L, cc_val, thi_val, adit_val, p_act, p_obj, gain, dias, cabezas, util_neta, roi_c, c_kg_ganado, a_ca, a_p, r_cap, a_fnd, a_pendf, ch4_d, co2e, bonos, cost_lote, tons_lote, mes_g):
            pdf = FPDF()
            pdf.add_page()
            
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 7, "Ganader-IA Elite 360 - Reporte Económico y Control Mensual", 0, 1, "C")
            pdf.set_font("Arial", "I", 8)
            pdf.cell(0, 4, "Creado por el Dr. Alejandro Castaneda Correa", 0, 1, "C")
            pdf.ln(2)
            
            pdf.set_font("Arial", "B", 9)
            pdf.cell(0, 5, "1. Evaluacion Economica y Rentabilidad del Negocio", 0, 1)
            pdf.set_font("Arial", "", 8)
            pdf.cell(0, 4, f"Utilidad Neta por Animal: ${util_neta:,.2f} MXN | ROI del Ciclo: {roi_c:.2f}%", 0, 1)
            pdf.cell(0, 4, f"Costo por kg Ganado: ${c_kg_ganado:,.2f} MXN/kg | Costo Alimento Ton: ${costo_ton:,.2f} MXN", 0, 1)
            pdf.ln(2)
            
            pdf.set_font("Arial", "B", 9)
            pdf.cell(0, 5, "2. Hito Mensual y Parametros Biologicos del Lote", 0, 1)
            pdf.set_font("Arial", "", 8)
            pdf.cell(0, 4, f"Hito / Mes: {mes_g} | Fisiologia: {etapa} | Sistema: {sistema_prod}", 0, 1)
            pdf.cell(0, 4, f"Cabezas: {cabezas} | Peso Actual: {p_act} kg | Peso Meta: {p_obj} kg | GDE: {gain} kg/d", 0, 1)
            pdf.ln(2)
            
            pdf.set_font("Arial", "B", 9)
            pdf.cell(0, 5, "3. Balance Mineral, Salud Ruminal y Sostenibilidad (IPCC)", 0, 1)
            pdf.set_font("Arial", "", 8)
            pdf.cell(0, 4, f"Calcio (Ca): {a_ca:.2f}% | Fosforo (P): {a_p:.2f}% | Relacion Ca:P: {r_cap:.2f}:1", 0, 1)
            pdf.cell(0, 4, f"Fibra peNDF: {a_pendf:.1f}% | Emision CH4: {ch4_d:.1f} g/dia", 0, 1)
            pdf.cell(0, 4, f"Valor Potencial Bonos de Carbono: ${bonos:,.2f} MXN por animal/ano", 0, 1)
            pdf.ln(2)
            
            pdf.set_font("Arial", "B", 9)
            pdf.cell(0, 5, "4. Mezcla Exacta por Tonelada (1,000 kg)", 0, 1)
            pdf.set_font("Arial", "B", 7)
            pdf.cell(80, 5, "Ingrediente", 1)
            pdf.cell(30, 5, "Inclusion (%)", 1)
            pdf.cell(35, 5, "Kg / Tonelada", 1)
            pdf.cell(45, 5, "Costo Parcial ($)", 1)
            pdf.ln()
            
            pdf.set_font("Arial", "", 7)
            for _, row in df_resumen.iterrows():
                if row["Ingrediente"] != "TOTALES / MEZCLA FINAL":
                    pdf.cell(80, 4, str(row["Ingrediente"]), 1)
                    pdf.cell(30, 4, f"{row['Inclusion (%)']}%", 1)
                    pdf.cell(35, 4, f"{row['Kg por Tonelada (1,000 kg)']}", 1)
                    pdf.cell(45, 4, str(row['Aporte al Costo Total ($)']), 1)
                    pdf.ln()
            
            tot_inc = df_resumen[df_resumen["Ingrediente"] != "TOTALES / MEZCLA FINAL"]['Inclusion (%)'].sum()
            tot_kg = df_resumen[df_resumen["Ingrediente"] != "TOTALES / MEZCLA FINAL"]['Kg por Tonelada (1,000 kg)'].sum()
            pdf.set_font("Arial", "B", 7)
            pdf.cell(80, 4, "TOTALES / MEZCLA FINAL", 1)
            pdf.cell(30, 4, f"{tot_inc:.1f}%", 1)
            pdf.cell(35, 4, f"{tot_kg:.1f} kg", 1)
            pdf.cell(45, 4, f"${costo_ton:,.2f}", 1)
            pdf.ln()
            return bytes(pdf.output())

        df_mezcla_pdf = pd.DataFrame(tabla_mezcla_con_totales)
        pdf_data = generar_pdf_ejecutivo(
            df_mezcla_pdf, resultado.fun, fase, sistema_produccion, condiciones_pastoreo, estado_pasto, perfil_aa, raza_seleccionada, sexo_lote, marco_lote, condicion_corporal, nivel_thi, aditivo_ruminal, peso_actual, peso_objetivo, gde, dias_a_meta,
            cantidad_animales, utilidad_neta_cab, roi_cab, costo_por_kg_ganado, aporte_ca, aporte_p, relacion_ca_p, aporte_fnd, aporte_pendf,
            ch4_g_dia, co2e_anual, valor_bono_mxn, costo_total_lote, alimento_total_ciclo / 1000.0, mes_engorda
        )
        
        st.markdown("---")
        st.subheader("📥 Descarga de Reporte Ejecutivo, Económico y de Control Mensual PDF")
        st.markdown("Haz clic en el botón para descargar el reporte oficial con el hito mensual, evaluación económica y mezcla óptima:")
        
        st.download_button(
            label="📄 Descargar Reporte Ejecutivo y Mensual PDF",
            data=pdf_data,
            file_name=f"Reporte_Mensual_GanaderIA_{fase.replace(' ', '_')}.pdf",
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
        st.warning("⚠️ Genere un balance factible en la Pestaña 3 para desbloquear los cálculos económicos y el Reporte PDF.")
