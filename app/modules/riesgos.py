"""
Módulo de Gestión de Riesgos (Art. 26-28 Ley 29783)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.supabase_client import get_supabase_client
from utils.n8n_client import get_n8n_client
from config.settings import TIPOS_RIESGO
from auth import obtener_usuario_actual


def generar_codigo_riesgo() -> str:
    """Genera un código único para el riesgo"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"RIESGO-{timestamp}"


def calcular_nivel_riesgo(probabilidad: int, severidad: int) -> tuple:
    """
    Calcula el nivel y clasificación del riesgo
    
    Returns:
        tuple: (nivel, clasificacion, color)
    """
    nivel = probabilidad * severidad
    
    if nivel <= 4:
        return nivel, "Bajo", "green"
    elif nivel <= 12:
        return nivel, "Medio", "yellow"
    elif nivel <= 16:
        return nivel, "Alto", "orange"
    else:
        return nivel, "Crítico", "red"


def mostrar_matriz_riesgo():
    """Muestra la matriz de riesgos 5x5"""
    st.subheader("📊 Matriz de Evaluación de Riesgos 5x5")
    
    # Crear matriz
    matriz = []
    for severidad in range(5, 0, -1):
        fila = []
        for probabilidad in range(1, 6):
            nivel = probabilidad * severidad
            if nivel <= 4:
                color = "🟢"
                clasificacion = "Bajo"
            elif nivel <= 12:
                color = "🟡"
                clasificacion = "Medio"
            elif nivel <= 16:
                color = "🟠"
                clasificacion = "Alto"
            else:
                color = "🔴"
                clasificacion = "Crítico"
            fila.append(f"{color} {nivel}")
        matriz.append(fila)
    
    df_matriz = pd.DataFrame(
        matriz,
        columns=["Prob 1", "Prob 2", "Prob 3", "Prob 4", "Prob 5"],
        index=["Sev 5", "Sev 4", "Sev 3", "Sev 2", "Sev 1"]
    )
    
    st.dataframe(df_matriz, width=800)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Probabilidad:**
        - 1: Muy Improbable
        - 2: Improbable
        - 3: Posible
        - 4: Probable
        - 5: Muy Probable
        """)
    
    with col2:
        st.markdown("""
        **Severidad:**
        - 1: Insignificante
        - 2: Menor
        - 3: Moderado
        - 4: Mayor
        - 5: Catastrófico
        """)


def formulario_registro_riesgo():
    """Formulario para registrar un nuevo riesgo"""
    st.subheader("➕ Registrar Nuevo Riesgo")
    
    supabase = get_supabase_client()
    n8n = get_n8n_client()
    usuario = obtener_usuario_actual()
    
    # Obtener lista de usuarios para asignar responsable
    usuarios = supabase.listar_usuarios()
    usuarios_dict = {u["nombre_completo"]: u["id"] for u in usuarios}
    
    with st.form("form_riesgo"):
        col1, col2 = st.columns(2)
        
        with col1:
            descripcion = st.text_area("Descripción del Riesgo *", height=100)
            area = st.text_input("Área *")
            proceso = st.text_input("Proceso")
            tipo_riesgo = st.selectbox("Tipo de Riesgo *", TIPOS_RIESGO)
        
        with col2:
            probabilidad = st.select_slider(
                "Probabilidad (1-5) *",
                options=[1, 2, 3, 4, 5],
                value=3
            )
            severidad = st.select_slider(
                "Severidad (1-5) *",
                options=[1, 2, 3, 4, 5],
                value=3
            )
            
            # Calcular nivel automáticamente
            nivel, clasificacion, color = calcular_nivel_riesgo(probabilidad, severidad)
            st.metric("Nivel de Riesgo", f"{nivel} - {clasificacion}")
            
            responsable_nombre = st.selectbox("Responsable", list(usuarios_dict.keys()))
            estado = st.selectbox("Estado", ["identificado", "en_control", "controlado", "cerrado"])
        
        medidas_control = st.text_area("Medidas de Control", height=100)
        fecha_revision = st.date_input("Fecha de Revisión", value=None)
        
        submitted = st.form_submit_button("💾 Registrar Riesgo", type="primary")
        
        if submitted:
            if not all([descripcion, area, tipo_riesgo]):
                st.error("Por favor completa todos los campos obligatorios (*)")
            else:
                datos_riesgo = {
                    "codigo": generar_codigo_riesgo(),
                    "descripcion": descripcion,
                    "area": area,
                    "proceso": proceso,
                    "tipo_riesgo": tipo_riesgo,
                    "probabilidad": probabilidad,
                    "severidad": severidad,
                    "medidas_control": medidas_control,
                    "responsable_id": usuarios_dict.get(responsable_nombre),
                    "estado": estado,
                    "fecha_revision": fecha_revision.isoformat() if fecha_revision else None,
                    "creado_por": usuario["id"]
                }
                
                riesgo_creado = supabase.crear_riesgo(datos_riesgo)
                
                if riesgo_creado:
                    st.success(f"✅ Riesgo registrado: {riesgo_creado['codigo']}")
                    
                    # Notificar si es riesgo crítico
                    if clasificacion in ["Alto", "Crítico"]:
                        riesgo_notif = {**riesgo_creado, "responsable": responsable_nombre}
                        n8n.notificar_riesgo_critico(riesgo_notif)
                        st.info("🔔 Notificación enviada por riesgo crítico")
                    
                    st.rerun()


def listar_riesgos():
    """Lista y filtra riesgos registrados"""
    st.subheader("📋 Listado de Riesgos")
    
    supabase = get_supabase_client()
    
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filtro_area = st.text_input("🔍 Filtrar por Área")
    with col2:
        filtro_clasificacion = st.selectbox("Clasificación", ["Todos", "Bajo", "Medio", "Alto", "Crítico"])
    with col3:
        filtro_estado = st.selectbox("Estado", ["Todos", "identificado", "en_control", "controlado", "cerrado"])
    with col4:
        filtro_tipo = st.selectbox("Tipo", ["Todos"] + TIPOS_RIESGO)
    
    # Construir filtros
    filtros = {}
    if filtro_area:
        filtros["area"] = filtro_area
    if filtro_clasificacion != "Todos":
        filtros["clasificacion"] = filtro_clasificacion
    if filtro_estado != "Todos":
        filtros["estado"] = filtro_estado
    
    riesgos = supabase.listar_riesgos(filtros)
    
    if filtro_tipo != "Todos":
        riesgos = [r for r in riesgos if r.get("tipo_riesgo") == filtro_tipo]
    
    if riesgos:
        st.info(f"Total de riesgos: {len(riesgos)}")
        
        # Convertir a DataFrame
        df = pd.DataFrame(riesgos)
        
        # Seleccionar columnas a mostrar
        columnas_mostrar = [
            "codigo", "descripcion", "area", "tipo_riesgo",
            "probabilidad", "severidad", "nivel_riesgo", "clasificacion",
            "estado", "fecha_identificacion"
        ]
        
        df_mostrar = df[columnas_mostrar].copy()
        df_mostrar.columns = [
            "Código", "Descripción", "Área", "Tipo",
            "Prob", "Sev", "Nivel", "Clasificación",
            "Estado", "Fecha"
        ]
        
        st.dataframe(df_mostrar, hide_index=True)
        
        # Exportar a Excel
        if st.button("📥 Exportar a Excel"):
            excel_file = f"riesgos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df_mostrar.to_excel(excel_file, index=False)
            st.success(f"Archivo exportado: {excel_file}")
    else:
        st.warning("No se encontraron riesgos con los filtros aplicados")


def dashboard_riesgos():
    """Dashboard con gráficos de riesgos"""
    st.subheader("📊 Dashboard de Riesgos")
    
    supabase = get_supabase_client()
    riesgos = supabase.listar_riesgos()
    
    if not riesgos:
        st.warning("No hay riesgos registrados")
        return
    
    df = pd.DataFrame(riesgos)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(df)
        st.metric("Total Riesgos", total)
    
    with col2:
        criticos = len(df[df["clasificacion"] == "Crítico"])
        st.metric("Riesgos Críticos", criticos, delta=None if criticos == 0 else "⚠️")
    
    with col3:
        altos = len(df[df["clasificacion"] == "Alto"])
        st.metric("Riesgos Altos", altos)
    
    with col4:
        controlados = len(df[df["estado"] == "controlado"])
        porcentaje = (controlados / total * 100) if total > 0 else 0
        st.metric("% Controlados", f"{porcentaje:.1f}%")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución por clasificación
        fig_clasificacion = px.pie(
            df,
            names="clasificacion",
            title="Distribución por Clasificación",
            color="clasificacion",
            color_discrete_map={
                "Bajo": "green",
                "Medio": "yellow",
                "Alto": "orange",
                "Crítico": "red"
            }
        )
        st.plotly_chart(fig_clasificacion, width='stretch')
    
    with col2:
        # Distribución por tipo de riesgo
        fig_tipo = px.bar(
            df["tipo_riesgo"].value_counts().reset_index(),
            x="tipo_riesgo",
            y="count",
            title="Riesgos por Tipo",
            labels={"tipo_riesgo": "Tipo de Riesgo", "count": "Cantidad"}
        )
        st.plotly_chart(fig_tipo, width='stretch')
    
    # Mapa de calor por área y clasificación
    pivot_area = pd.crosstab(df["area"], df["clasificacion"])
    fig_heatmap = px.imshow(
        pivot_area,
        title="Mapa de Calor: Riesgos por Área y Clasificación",
        labels=dict(x="Clasificación", y="Área", color="Cantidad"),
        color_continuous_scale="RdYlGn_r"
    )
    st.plotly_chart(fig_heatmap, width='stretch')


def modulo_riesgos():
    """Módulo principal de gestión de riesgos"""
    st.title("⚠️ Gestión de Riesgos")
    st.markdown("**Identificación y Evaluación de Riesgos - Art. 26-28 Ley 29783**")
    
    tabs = st.tabs(["📊 Dashboard", "📋 Listado", "➕ Registrar", "📐 Matriz 5x5"])
    
    with tabs[0]:
        dashboard_riesgos()
    
    with tabs[1]:
        listar_riesgos()
    
    with tabs[2]:
        formulario_registro_riesgo()
    
    with tabs[3]:
        mostrar_matriz_riesgo()


if __name__ == "__main__":
    modulo_riesgos()
