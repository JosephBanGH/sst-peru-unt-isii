"""
Módulo de Gestión de Capacitaciones (Art. 27, 35 Ley 29783)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.supabase_client import get_supabase_client
from utils.n8n_client import get_n8n_client
from config.settings import TIPOS_CAPACITACION, STORAGE_BUCKETS
from auth import obtener_usuario_actual


def generar_codigo_capacitacion() -> str:
    """Genera un código único para la capacitación"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"CAP-{timestamp}"


def formulario_registro_capacitacion():
    """Formulario para registrar una nueva capacitación"""
    st.subheader("➕ Registrar Nueva Capacitación")
    
    supabase = get_supabase_client()
    n8n = get_n8n_client()
    usuario = obtener_usuario_actual()
    
    with st.form("form_capacitacion"):
        col1, col2 = st.columns(2)
        
        with col1:
            titulo = st.text_input("Título de la Capacitación *")
            tipo = st.selectbox("Tipo *", TIPOS_CAPACITACION)
            modalidad = st.selectbox("Modalidad", ["Presencial", "Virtual", "Híbrida"])
            instructor = st.text_input("Instructor *")
        
        with col2:
            fecha_cap = st.date_input("Fecha Programada *", value=date.today())
            hora_cap = st.time_input("Hora Programada *", value=datetime.now().time())
            duracion_horas = st.number_input("Duración (horas)", min_value=0.5, value=2.0, step=0.5)
            lugar = st.text_input("Lugar")
        
        descripcion = st.text_area("Descripción")
        
        # Selección de participantes
        usuarios = supabase.listar_usuarios()
        participantes_seleccionados = st.multiselect(
            "Participantes",
            options=[u["nombre_completo"] for u in usuarios]
        )
        
        # Archivos
        material = st.file_uploader("Material de Capacitación", type=["pdf", "ppt", "pptx"])
        
        submitted = st.form_submit_button("💾 Registrar Capacitación", type="primary")
        
        if submitted:
            if not all([titulo, tipo, instructor, fecha_cap, hora_cap]):
                st.error("Por favor completa todos los campos obligatorios (*)")
            else:
                # Combinar fecha y hora
                fecha_programada = datetime.combine(fecha_cap, hora_cap)
                # Subir material si existe
                material_url = None
                if material:
                    ruta = f"capacitaciones/{datetime.now().strftime('%Y%m')}/{material.name}"
                    material_url = supabase.subir_archivo(
                        STORAGE_BUCKETS["capacitaciones"],
                        ruta,
                        material.getvalue()
                    )
                
                datos_capacitacion = {
                    "codigo": generar_codigo_capacitacion(),
                    "titulo": titulo,
                    "descripcion": descripcion,
                    "tipo": tipo,
                    "modalidad": modalidad,
                    "instructor": instructor,
                    "fecha_programada": fecha_programada.isoformat(),
                    "duracion_horas": duracion_horas,
                    "lugar": lugar,
                    "estado": "programada",
                    "material_url": material_url,
                    "creado_por": usuario["id"]
                }
                
                capacitacion_creada = supabase.crear_capacitacion(datos_capacitacion)
                
                if capacitacion_creada:
                    # Registrar participantes
                    usuarios_dict = {u["nombre_completo"]: u["id"] for u in usuarios}
                    asistentes_data = []
                    
                    for participante in participantes_seleccionados:
                        datos_asistente = {
                            "capacitacion_id": capacitacion_creada["id"],
                            "usuario_id": usuarios_dict[participante],
                            "asistio": False
                        }
                        supabase.registrar_asistente(datos_asistente)
                        asistentes_data.append({
                            "nombre": participante,
                            "email": next((u["email"] for u in usuarios if u["nombre_completo"] == participante), "")
                        })
                    
                    st.success(f"✅ Capacitación registrada: {capacitacion_creada['codigo']}")
                    
                    # Enviar recordatorio
                    if asistentes_data:
                        n8n.notificar_recordatorio_capacitacion(capacitacion_creada, asistentes_data)
                        st.info("🔔 Recordatorios enviados a los participantes")
                    
                    st.rerun()


def listar_capacitaciones():
    """Lista capacitaciones registradas"""
    st.subheader("📋 Listado de Capacitaciones")
    
    supabase = get_supabase_client()
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_estado = st.selectbox("Estado", ["Todos", "programada", "realizada", "cancelada", "reprogramada"])
    with col2:
        filtro_tipo = st.selectbox("Tipo", ["Todos"] + TIPOS_CAPACITACION)
    with col3:
        filtro_modalidad = st.selectbox("Modalidad", ["Todos", "Presencial", "Virtual", "Híbrida"])
    
    filtros = {}
    if filtro_estado != "Todos":
        filtros["estado"] = filtro_estado
    if filtro_tipo != "Todos":
        filtros["tipo"] = filtro_tipo
    
    capacitaciones = supabase.listar_capacitaciones(filtros)
    
    if filtro_modalidad != "Todos":
        capacitaciones = [c for c in capacitaciones if c.get("modalidad") == filtro_modalidad]
    
    if capacitaciones:
        st.info(f"Total de capacitaciones: {len(capacitaciones)}")
        
        for cap in capacitaciones:
            with st.expander(f"📚 {cap['codigo']} - {cap['titulo']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Tipo:** {cap['tipo']}")
                    st.markdown(f"**Instructor:** {cap['instructor']}")
                    st.markdown(f"**Fecha:** {cap['fecha_programada']}")
                    st.markdown(f"**Duración:** {cap.get('duracion_horas', 0)} horas")
                
                with col2:
                    st.markdown(f"**Modalidad:** {cap.get('modalidad', 'N/A')}")
                    st.markdown(f"**Lugar:** {cap.get('lugar', 'N/A')}")
                    st.markdown(f"**Estado:** {cap['estado']}")
                
                if cap.get('descripcion'):
                    st.markdown(f"**Descripción:** {cap['descripcion']}")
                
                if cap.get('material_url'):
                    st.markdown(f"[📎 Descargar Material]({cap['material_url']})")
    else:
        st.warning("No se encontraron capacitaciones")


def dashboard_capacitaciones():
    """Dashboard de capacitaciones"""
    st.subheader("📊 Dashboard de Capacitaciones")
    
    supabase = get_supabase_client()
    capacitaciones = supabase.listar_capacitaciones()
    
    if not capacitaciones:
        st.warning("No hay capacitaciones registradas")
        return
    
    df = pd.DataFrame(capacitaciones)
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(df)
        st.metric("Total Capacitaciones", total)
    
    with col2:
        realizadas = len(df[df["estado"] == "realizada"])
        st.metric("Realizadas", realizadas)
    
    with col3:
        programadas = len(df[df["estado"] == "programada"])
        st.metric("Programadas", programadas)
    
    with col4:
        horas_totales = df["duracion_horas"].sum()
        st.metric("Horas Totales", f"{horas_totales:.1f}")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        fig_tipo = px.pie(df, names="tipo", title="Capacitaciones por Tipo")
        st.plotly_chart(fig_tipo, use_container_width=True)
    
    with col2:
        fig_estado = px.bar(
            df["estado"].value_counts().reset_index(),
            x="estado", y="count",
            title="Capacitaciones por Estado",
            labels={"estado": "Estado", "count": "Cantidad"}
        )
        st.plotly_chart(fig_estado, use_container_width=True)


def modulo_capacitaciones():
    """Módulo principal de gestión de capacitaciones"""
    st.title("📚 Gestión de Capacitaciones")
    st.markdown("**Capacitación y Entrenamiento - Art. 27, 35 Ley 29783**")
    
    tabs = st.tabs(["📊 Dashboard", "📋 Listado", "➕ Registrar"])
    
    with tabs[0]:
        dashboard_capacitaciones()
    
    with tabs[1]:
        listar_capacitaciones()
    
    with tabs[2]:
        formulario_registro_capacitacion()


if __name__ == "__main__":
    modulo_capacitaciones()
