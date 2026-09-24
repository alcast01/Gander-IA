import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import linprog
import plotly.express as px
from fpdf import FPDF

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO VISUAL (CAMPO Y GANADERÍA) ---
st.set_page_config(
    page_title="Ganader-IA Pro | Nutrición Bovina Inteligente",
    page_icon="🐄",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Importación de tipografía moderna y uniforme (Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        color: #2b2d42;
    }
    
    .main {
        background-color: #fcfbf9; /* Fondo arena cálida / campo */
    }
    
    /* Contenedores de tarjetas métricas ejecutivas */
    .stMetric {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(45, 90, 39, 0.08);
        border-left: 5px solid #2d5a27; /* Verde pastura */
        border-top: 1px solid #e6e2dd;
        border-right: 1px solid #e6e2dd;
        border-bottom: 1px solid #e6e2dd;
        transition: transform 0.2s ease;
    }
    .stMetric:hover {
        transform: translateY(-2px);
    }
    
    /* Encabezados y títulos uniformes */
    h1, h2, h3, h4 {
        color: #1f2421;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700;
    }

    p, span, label {
        font-family: 'Inter', sans-serif !important;
        color: #333333;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. SISTEMA DE SEGURIDAD Y CONTROL DE ACCESOS (MEMBRESÍAS / LICENCIAS) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        st.markdown("<h2 style='text-align: center; color: #2d5a27;'>🔐 Ganader-IA Pro</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Sistema Inteligente de Optimización y Nutrición Bovina</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.info("Introduce tu clave de licencia comercial o membresía institucional para acceder:")
        licencia_input = st.text_input("Clave de Acceso / Licencia", type="password", placeholder="Ingresa tu clave...")
        
        if st.button("🚀 Entrar al Sistema", use_container_width=True):
            admin_pwd = st.secrets.get("ADMIN_PASSWORD", "demo")
            if licencia_input == admin_pwd or licencia_input == "GANADERIA-PRO-2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Licencia inválida o membresía expirada.")
                
        st.markdown("<div style='text-align: center; margin-top: 15px;'><small>🔑 <i>Usa la clave <b>demo</b> para pruebas académicas y profesionales.</i></small></div>", unsafe_allow_html=True)
    st.stop()

# --- 3. LOGOTIPO VECTORIAL DE VANGUARDIA (PALETA CAMPO Y GANADERÍA) ---
st.markdown("""
    <div style="display: flex; align-items: center; background: linear-gradient(135deg, #2d5a27 0%, #bc6c25 100%); padding: 25px; border-radius: 16px; box-shadow: 0 6px 20px rgba(45,90,39,0.15); margin-bottom: 25px; color: white;">
        <div style="flex-shrink: 0; margin-right: 20px;">
            <svg width="70" height="70" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" fill="#ffffff"/>
                <circle cx="12" cy="12" r="3" fill="#dda15e"/>
            </svg>
        </div>
        <div>
            <h1 style="margin: 0; font-size: 2.2em; color: #ffffff; letter-spacing: 0.5px; font-family: 'Inter', sans-serif;">Ganader-IA <span style="background-color: #dda15e; color: #1f2421; padding: 2px 8px; border-radius: 6px; font-size: 0.6em; vertical-align: middle;">PRO</span></h1>
            <p style="margin: 5px 0 0 0; font-size: 1.05em; color: #f4f1de; font-weight: 300; font-family: 'Inter', sans-serif;">Plataforma de Precisión Zootécnica y Optimización de Raciones</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 4. CARGA DE LA BASE DE DATOS DESDE GOOGLE SHEETS (V4) ---
sheet_url = "https://docs.google.com/spreadsheets/d/1yCuTmDi1wEzdeMHoAbuxMewwo0Pe1neyjntMgAhMzhA/export?format=csv"

@st.cache_data(ttl=10)
def cargar_datos(url):
    return pd.read_csv(url)

try:
    df_base = cargar_datos(sheet_url)
    source_status = "☁️ Conectado a Google Sheets (Base V4 en Vivo)"
except Exception:
    source_status = "⚠️ Usando base de datos local de emergencia"
    data_respaldo = {
        "Nombre del Ingrediente": [
            "Rastrojo de maiz molido", 
            "Harina de soya", 
            "Grano de maiz molido", 
            "Urea", 
            "Ensilado de maiz", 
            "Canola (pasta)", 
            "Melaza liquida",
            "Sales Minerales (Cañón de Tlaltenango)", 
            "Grasa de paso Lactomil"
        ],
        "Categoria": ["Forraje", "Suplemento Proteico", "Grano Energetico", "Suplemento NPN", "Forraje Humedo", "Suplemento Proteico", "Subproducto / Energetico", "Suplemento Mineral", "Suplemento Energetico"],
        "Precio Estimado (MXN/ton)": [2500.0, 12500.0, 5800.0, 16000.0, 1200.0, 8500.0, 4800.0, 18000.0, 32000.0],
        "Proteina Cruda (PC % MS)": [5.5, 48.0, 8.5, 281.0, 8.0, 38.0, 4.8, 0.0, 1.0],
        "NEg (Mcal/kg)": [0.35, 1.48, 1.55, 0.0, 0.85, 1.15, 1.22, 0.0, 1.65]
    }
    df_base = pd.DataFrame(data_respaldo)

st.caption(source_status)

# --- 5. CONTROLES GENERALES Y PARÁMETROS PRODUCTIVOS EN LA BARRA LATERAL ---
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

# --- MODELADO PREDICTIVO BIOLÓGICO ---
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

# Botón para cerrar sesión en barra lateral
st.sidebar.markdown("---")
if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()

# Créditos profesionales institucionales
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='text-align: center; color: #555; font-size: 0.85em; padding: 5px; font-family: Inter, sans-serif;'>"
    "<b>Ganader-IA Pro</b><br>"
    "Creado por el <b>Dr. Alejandro Castañeda Correa</b>.<br><br>"
    "Diseñado para Nutriólogos, Técnicos, Estudiantes Universitarios y Ganaderos."
    "</div>",
    unsafe_allow_html=True
)

# --- 6. INTERFAZ MODULAR POR PESTAÑAS (3 TABS) ---
tab1, tab2, tab3 = st.tabs([
    "📋 1. Resumen y Predicciones", 
    "🧪 2. Catálogo y Lab", 
    "📊 3. Resultados y Reporte PDF"
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
    fig_line.update_traces(line_color="#2d5a27", marker=dict(size=8, color="#bc6c25"))
    fig_line.update_layout(
        plot_bgcolor="#ffffff", 
        paper_bgcolor="#ffffff", 
        font=dict(family="Inter", color="#2b2d42")
    )
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

# --- 7. EXTRACCIÓN Y MOTOR DE PROGRAMACIÓN LINEAL ---
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
    if "urea" in nombre:
        bounds.append((0.0, 0.015))    # Urea: 0% a 1.5% máx
    elif "mineral" in nombre or "sal" in nombre:
        bounds.append((0.01, 0.03))   # Minerales: Mínimo 1% y máximo 3%
    elif "grasa" in nombre or "lactomil" in nombre:
        bounds.append((0.01, 0.03))   # Grasa de paso: Mínimo 1% y máximo 3%
    elif "melaza" in nombre:
        bounds.append((0.02, 0.06))   # Melaza: Mínimo 2% y máximo 6%
    else:
        bounds.append((0.0, 1.0))      # Resto de forrajes y concentrados (0% al 100%)

A_eq = np.ones((1, len(c)))
b_eq = np.array([1.0])
A_ub = np.array([-pc, -neg])
b_ub = np.array([-meta_pc_min, -meta_neg_min])

resultado = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

with tab3:
    st.subheader("Reporte Financiero, Mezcla y Descarga de PDF")
    
    if resultado.success:
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric(label="Costo Óptimo por Tonelada", value=f"${resultado.fun:,.2f} MXN")
        with col_res2:
            st.metric(label="Estado del Proceso", value="Factible (Máxima Eficiencia) 🟢")
        
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
                    "Inclusión (%)": round(porcentaje, 1),
                    "Kg por Tonelada (1,000 kg)": round(kilos, 2),
                    "Costo Unitario ($/ton)": f"${c[i]:,.2f}",
                    "Aporte al Costo Total ($)": f"${costo_parcial:,.2f}"
                })
                
                cat_ing = str(df_ingredientes.iloc[i].get("Categoria", "Otros"))
                categorias_pie[cat_ing] = categorias_pie.get(cat_ing, 0) + porcentaje
        
        df_mezcla_final = pd.DataFrame(tabla_mezcla)
        st.dataframe(df_mezcla_final, use_container_width=True, hide_index=True)
        
        # --- FUNCIÓN GENERADORA DE PDF EJECUTIVO ---
        def generar_pdf_ejecutivo(df_resumen, costo_ton, etapa, raza_L, p_act, p_obj, gain, dias):
            pdf = FPDF()
            pdf.add_page()
            
            # Encabezado
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Ganader-IA Pro - Reporte Ejecutivo de Nutricion", 0, 1, "C")
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 6, "Creado por el Dr. Alejandro Castaneda Correa", 0, 1, "C")
            pdf.ln(5)
            
            # Datos del Lote
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, "1. Parametros y Predicciones del Lote", 0, 1)
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, f"Fisiologia: {etapa} | Genetica: {raza_L}", 0, 1)
            pdf.cell(0, 6, f"Peso Actual: {p_act} kg | Peso Meta: {p_obj} kg | GDE Esperada: {gain} kg/dia", 0, 1)
            pdf.cell(0, 6, f"Dias Proyectados a Venta: {dias:.0f} dias", 0, 1)
            pdf.ln(4)
            
            # Corrida Financiera
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, "2. Corrida Financiera", 0, 1)
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, f"Costo Optimo por Tonelada de Alimento: ${costo_ton:,.2f} MXN", 0, 1)
            pdf.ln(4)
            
            # Tabla de ingredientes
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, "3. Orden Exacta de Ingredientes por Tonelada (1,000 kg)", 0, 1)
            pdf.set_font("Arial", "B", 9)
            pdf.cell(80, 7, "Ingrediente", 1)
            pdf.cell(30, 7, "Inclusion (%)", 1)
            pdf.cell(35, 7, "Kg / Tonelada", 1)
            pdf.cell(45, 7, "Costo Parcial ($)", 1)
            pdf.ln()
            
            pdf.set_font("Arial", "", 9)
            for _, row in df_resumen.iterrows():
                pdf.cell(80, 6, str(row["Ingrediente"]), 1)
                pdf.cell(30, 6, f"{row['Inclusión (%)']}%", 1)
                pdf.cell(35, 6, f"{row['Kg por Tonelada (1,000 kg)']}", 1)
                pdf.cell(45, 6, str(row['Aporte al Costo Total ($)']), 1)
                pdf.ln()
                
            pdf.ln(5)
            # Instrucciones para operarios
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, "4. Instrucciones de Mezclado para los Operarios del Corral", 0, 1)
            pdf.set_font("Arial", "", 9)
            pdf.multi_cell(0, 5, 
                "1. Orden de carga en la batea: Agregar primero los forrajes secos y ensilados.\n"
                "2. Incorporar los granos energeticos, concentrados proteicos y subproductos.\n"
                "3. Agregar con precision los aditivos especiales (Sales Minerales, Grasa de paso Lactomil y Urea).\n"
                "4. Verter la melaza liquida al final junto con el agua de batea para asegurar palatabilidad y evitar polvos.\n"
                "5. Tiempo de mezcla recomendado: 8 a 10 minutos posteriores a la adicion del ultimo ingrediente."
            )
            return bytes(pdf.output())

        pdf_data = generar_pdf_ejecutivo(df_mezcla_final, resultado.fun, fase, raza_seleccionada, peso_actual, peso_objetivo, gde, dias_a_meta)
        
        st.markdown("---")
        st.subheader("📥 Descarga de Reporte Ejecutivo PDF")
        st.markdown("Haz clic en el siguiente botón para generar y descargar el reporte oficial con la receta de batea y corrida financiera:")
        
        st.download_button(
            label="📄 Descargar Reporte Ejecutivo PDF (Operarios y Corrida Financiera)",
            data=pdf_data,
            file_name=f"Reporte_GanaderIA_{fase.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        # --- GRÁFICAS DE PASTEL Y BARRAS (PALETA CAMPO) ---
        st.markdown("---")
        st.subheader("🥧 Composición Porcentual de la Dieta por Categoría")
        df_pie = pd.DataFrame(list(categorias_pie.items()), columns=["Categoría", "Porcentaje"])
        
        colores_campo = ['#2d5a27', '#bc6c25', '#dda15e', '#606c38', '#283618', '#e76f51']
        fig_pie = px.pie(
            df_pie, 
            names="Categoría", 
            values="Porcentaje", 
            hole=0.4, 
            title="Distribución de Insumos en la Mezcla",
            color_discrete_sequence=colores_campo
        )
        fig_pie.update_layout(font=dict(family="Inter", color="#2b2d42"))
        st.plotly_chart(fig_pie, use_container_width=True)
                
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
        
    else:
        st.error(
            "⚠️ **Aviso del Optimizador:** Con los precios actuales o metas extremas introducidas, no se encontró una solución matemática 100% factible. "
            "Sin embargo, **las predicciones de parámetros productivos y consumo en la Pestaña 1 siguen vigentes y operativas**. "
            "Revisa los precios o valores analíticos en la pestaña **Catálogo y Lab**."
        )
