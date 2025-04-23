import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from fpdf import FPDF
import base64
from streamlit.components.v1 import html

# Configuración de la página
st.set_page_config(
    page_title="🕒 Calculadora de Horas Laborales V2",
    page_icon="⏱️",
    layout="wide"
)

# Inicialización del estado de sesión
if 'historial' not in st.session_state:
    st.session_state.historial = []

# Título y descripción
st.title("⏱️ Calculadora de Horas Laborales V2")
st.markdown("""
Calcula horas trabajadas, personaliza tu semana laboral y exporta resultados.
""")

# Sidebar para configuración avanzada
with st.sidebar:
    st.header("🔧 Configuración")
    
    # Horas por día básico
    horas_por_dia = st.number_input(
        "Horas por día laboral (predeterminado)",
        value=8.0,
        min_value=0.5,
        step=0.5
    )
    
    # Semana laboral personalizada
    st.subheader("📅 Semana Personalizada")
    dias_semana = st.multiselect(
        "Selecciona tus días laborales",
        ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
        default=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    )
    
    horario_personalizado = st.checkbox("Usar horario personalizado por día")
    if horario_personalizado:
        hora_inicio = st.time_input("Hora de inicio", value=datetime.strptime("08:00", "%H:%M").time())
        hora_fin = st.time_input("Hora de fin", value=datetime.strptime("17:00", "%H:%M").time())
        horas_por_dia_personal = (hora_fin.hour - hora_inicio.hour) + (hora_fin.minute - hora_inicio.minute)/60
    else:
        horas_por_dia_personal = horas_por_dia

# Función para guardar en el historial
def guardar_historial(tipo, resultado):
    registro = {
        "tipo": tipo,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "resultado": resultado
    }
    st.session_state.historial.append(registro)
    
    # Persistencia en localStorage (JavaScript)
    html(f"""
    <script>
    localStorage.setItem('historial', JSON.stringify({st.session_state.historial}));
    </script>
    """, height=0)

# Pestañas para diferentes funcionalidades
tab1, tab2, tab3 = st.tabs(["📅 Calcular por fechas", "➕ Sumar manualmente", "📊 Historial"])

with tab1:
    st.subheader("Cálculo por rango de fechas")
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha de inicio", value=datetime(2025, 8, 30))
    with col2:
        fecha_fin = st.date_input("Fecha de fin", value=datetime(2025, 10, 4))
    
    vacaciones = st.number_input("Días de vacaciones a descontar", min_value=0, value=0)
    
    if st.button("🔄 Calcular", key="calcular_fechas"):
        if fecha_inicio > fecha_fin:
            st.error("⚠️ La fecha de inicio debe ser anterior a la de fin")
        else:
            delta = fecha_fin - fecha_inicio
            dias_totales = delta.days + 1  # Incluye el día inicial
            
            # Mapeo de días en inglés a español (clave para que funcione)
            dias_ingles_a_espanol = {
                "Monday": "Lunes",
                "Tuesday": "Martes",
                "Wednesday": "Miércoles",
                "Thursday": "Jueves",
                "Friday": "Viernes",
                "Saturday": "Sábado",
                "Sunday": "Domingo"
            }
            
            # Calcula días laborales según configuración
            dias_laborales = 0
            for i in range(dias_totales):
                dia = fecha_inicio + timedelta(days=i)
                nombre_dia_ingles = dia.strftime("%A")
                nombre_dia_espanol = dias_ingles_a_espanol.get(nombre_dia_ingles, "")
                if nombre_dia_espanol in dias_semana:  # Ahora compara con los nombres en español
                    dias_laborales += 1
            
            dias_laborales -= vacaciones
            horas_totales = dias_laborales * horas_por_dia_personal
            
            resultado = f"""
            **Total calculado:**  
            - Días laborales: {dias_laborales}  
            - Horas totales: {horas_totales:.2f}h  
            """
            st.success(resultado)
            guardar_historial("Rango de fechas", resultado)

with tab2:
    st.subheader("Suma manual de tiempos")
    col1, col2 = st.columns(2)
    with col1:
        dias = st.number_input("Días", min_value=0, value=0)
    with col2:
        minutos = st.number_input("Minutos", min_value=0, value=0)
    
    if st.button("🔢 Sumar", key="sumar_manual"):
        total_horas = dias * horas_por_dia_personal + minutos / 60
        resultado = f"""
        **Total sumado:**  
        - Horas: {total_horas:.2f}h  
        - Equivalente a ~{int(total_horas / horas_por_dia_personal)} días laborales
        """
        st.success(resultado)
        guardar_historial("Suma manual", resultado)

with tab3:
    st.subheader("📝 Historial de cálculos")
    
    # Mostrar historial
    if st.session_state.historial:
        df = pd.DataFrame(st.session_state.historial)
        st.dataframe(df, use_container_width=True)
        
        # Botones de exportación
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Exportar a Excel"):
                excel_file = df.to_excel("historial.xlsx", index=False)
                with open("historial.xlsx", "rb") as f:
                    st.download_button(
                        "⬇️ Descargar Excel",
                        f,
                        file_name="historial_calculos.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        with col2:
            if st.button("📤 Exportar a PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Historial de Cálculos", ln=True, align="C")
                for _, row in df.iterrows():
                    pdf.cell(200, 10, txt=f"{row['tipo']} ({row['fecha']}): {row['resultado']}", ln=True)
                pdf.output("historial.pdf")
                with open("historial.pdf", "rb") as f:
                    st.download_button(
                        "⬇️ Descargar PDF",
                        f,
                        file_name="historial_calculos.pdf",
                        mime="application/pdf"
                    )
    else:
        st.info("Aún no hay cálculos en el historial.")

# Cargar historial desde localStorage al iniciar
html("""
<script>
if (localStorage.getItem('historial')) {
    const historial = JSON.parse(localStorage.getItem('historial'));
    window.parent.postMessage({
        type: 'streamlit:setComponentValue',
        value: historial
    }, '*');
}
</script>
""", height=0)
