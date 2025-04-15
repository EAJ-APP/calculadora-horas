import streamlit as st
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(page_title="🕒 Calculadora de Horas", page_icon="⏱️")
st.title("⏱️ Calculadora de Horas Laborales")

# Sidebar para ajustes
with st.sidebar:
    st.header("Configuración")
    horas_por_dia = st.number_input("Horas por día laboral", value=8.0, min_value=0.5, step=0.5)
    incluir_finde = st.checkbox("Incluir fines de semana", value=False)

# Selección de modo
modo = st.radio("Modo de cálculo:", 
                ("📅 Rango de fechas", "➕ Suma manual de tiempos"))

if modo == "📅 Rango de fechas":
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha de inicio", value=datetime(2025, 8, 30))
    with col2:
        fecha_fin = st.date_input("Fecha de fin", value=datetime(2025, 10, 4))
    
    vacaciones = st.number_input("Días de vacaciones a descontar", min_value=0, value=0)
    
    if st.button("🔄 Calcular", type="primary"):
        if fecha_inicio > fecha_fin:
            st.error("⚠️ La fecha de inicio debe ser anterior a la de fin")
        else:
            delta = fecha_fin - fecha_inicio
            dias_totales = delta.days + 1  # Incluye el día inicial
            
            if not incluir_finde:
                # Calcula días laborales excluyendo fines de semana
                dias_laborales = 0
                for i in range(dias_totales):
                    dia = fecha_inicio + timedelta(days=i)
                    if dia.weekday() < 5:  # 0-4 = Lunes-Viernes
                        dias_laborales += 1
            else:
                dias_laborales = dias_totales
            
            dias_laborales -= vacaciones
            horas_totales = dias_laborales * horas_por_dia
            
            st.success(f"""
            **Total calculado:**  
            - Días laborales: {dias_laborales}  
            - Horas totales: {horas_totales:.2f}h  
            """)

else:
    st.subheader("Suma manual")
    col1, col2 = st.columns(2)
    with col1:
        dias = st.number_input("Días", min_value=0, value=0)
    with col2:
        minutos = st.number_input("Minutos", min_value=0, value=0)
    
    if st.button("🔢 Sumar", type="primary"):
        total_horas = dias * horas_por_dia + minutos / 60
        st.success(f"""
        **Total sumado:**  
        - Horas: {total_horas:.2f}h  
        - Equivalente a ~{int(total_horas / horas_por_dia)} días laborales
        """)
