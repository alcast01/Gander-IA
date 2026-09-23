import streamlit as st
import numpy as np
from scipy.optimize import linprog

st.set_page_config(page_title="NutriZacatecas Móvil", page_icon="🐄", layout="centered")

st.title("🐄 NutriZacatecas App")
st.markdown("### Optimizador de Raciones de Mínimo Costo")

st.sidebar.header("Parámetros del Lote")
peso_actual = st.sidebar.slider("Peso Vivo Actual (kg)", min_value=200.0, max_value=450.0, value=250.0, step=10.0)
gde = st.sidebar.slider("Ganancia Diaria Esperada (kg/día)", min_value=1.0, max_value=2.0, value=1.4, step=0.1)
estacion = st.sidebar.selectbox("Temporada / Clima", ["Templado", "Invierno", "Verano"])

st.info(f"Evaluando lote de **{peso_actual} kg** en temporada de **{estacion.lower()}**.")

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

nombres = ["Rastrojo de maiz", "Harina de soya", "Grano de maiz", "Urea", "Ensilado de maiz", "Pasta de canola"]
c = np.array([2500.0, 12500.0, 5800.0, 16000.0, 1200.0, 8500.0])
pc = np.array([0.04675, 0.4272, 0.0731, 2.781, 0.028, 0.3382])
neg = np.array([0.2975, 1.3172, 1.333, 0.0, 0.2975, 1.0235])

A_eq = np.ones((1, len(c)))
b_eq = np.array([1.0])
A_ub = np.array([-pc, -neg])
b_ub = np.array([-meta_pc_min, -meta_neg_min])

bounds = [
    (0.0, 0.40), (0.0, 0.25), (0.0, 0.70),
    (0.0, 0.012), (0.20, 0.60), (0.0, 0.25)
]

resultado = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

if resultado.success:
    st.success("¡Dieta optimizada con éxito!")
    st.metric(label="Costo Óptimo por Tonelada", value=f"${resultado.fun:,.2f} MXN")
    
    st.markdown("#### 📋 Mezcla exacta para la batea (por tonelada):")
    for i, ingrediente in enumerate(nombres):
        porcentaje = resultado.x[i] * 100
        kilos = resultado.x[i] * 1000
        if porcentaje > 0.01:
            st.write(f"- **{ingrediente}:** {porcentaje:.1f}% `({kilos:.1f} kg)`")
            st.progress(float(resultado.x[i]))
            
    if resultado.x[3] >= 0.0119:
        st.warning("⚠️ Nota: La urea alcanzó su límite máximo de seguridad biológica (1.2%).")
else:
    st.error("No se encontró una combinación factible con los parámetros actuales.")
