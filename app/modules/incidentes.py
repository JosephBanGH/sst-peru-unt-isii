"""
Módulo de Gestión de Incidentes y Accidentes (Art. 82-88 Ley 29783)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.supabase_client import get_supabase_client
from utils.n8n_client import get_n8n_client
from config.settings import TIPOS_INCIDENTE, STORAGE_BUCKETS
from auth import obtener_usuario_actual


def generar_codigo_incidente() -> str:
    """Genera un código único para el incidente"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"INC-{timestamp}"


def formulario_registro_incidente():
    """Formulario para registrar un nuevo incidente"""
    st.subheader("➕ Registrar Nuevo Incidente/Accidente")
    
    supabase = get_supabase_client()
    n8n = get_n8n_client()
    usuario = obtener_usuario_actual()
    
    # Si no hay usuario en sesión, obtener el primer usuario admin de la BD
    if not usuario:
        usuarios = supabase.listar_usuarios()
        usuario = usuarios[0] if usuarios else {"id": None}
    
    with st.form("form_incidente"):
        st.markdown("### 📝 Información General")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tipo = st.selectbox("Tipo de Incidente *", TIPOS_INCIDENTE)
            fecha_incidente = st.date_input("Fecha del Incidente *", value=date.today())
            hora_incidente = st.time_input("Hora del Incidente *", value=datetime.now().time())
            area = st.text_input("Área *")
            ubicacion_especifica = st.text_input("Ubicación Específica")
        
        with col2:
            requiere_investigacion = st.checkbox("Requiere Investigación Formal")
            notificado_sunafil = st.checkbox("Notificado a SUNAFIL")
            if notificado_sunafil:
                fecha_notificacion = st.date_input("Fecha de Notificación SUNAFIL")
        
        descripcion = st.text_area("Descripción Detallada del Incidente *", height=150)
        
        st.markdown("### 👤 Información del Afectado")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            afectado_nombre = st.text_input("Nombre Completo")
            afectado_dni = st.text_input("DNI")
        
        with col2:
            afectado_cargo = st.text_input("Cargo")
            parte_cuerpo = st.text_input("Parte del Cuerpo Afectada")
        
        with col3:
            naturaleza_lesion = st.text_input("Naturaleza de la Lesión")
            dias_descanso = st.number_input("Días de Descanso Médico", min_value=0, value=0)
        
        st.markdown("### 🔍 Análisis de Causas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            testigos = st.text_area("Testigos", height=80)
            causas_inmediatas = st.text_area("Causas Inmediatas", height=80)
            medidas_inmediatas = st.text_area("Medidas Inmediatas Tomadas", height=80)
        
        with col2:
            causas_basicas = st.text_area("Causas Básicas", height=80)
            analisis_causa_raiz = st.text_area("Análisis de Causa Raíz", height=80)
        
        st.markdown("### 📎 Evidencias")
        evidencias = st.file_uploader(
            "Subir Evidencias (fotos, videos, documentos)",
            accept_multiple_files=True,
            type=["jpg", "jpeg", "png", "pdf", "mp4", "avi"]
        )
        
        submitted = st.form_submit_button("💾 Registrar Incidente", type="primary")
        
        if submitted:
            if not all([tipo, fecha_incidente, hora_incidente, area, descripcion]):
                st.error("Por favor completa todos los campos obligatorios (*)")
            else:
                # Combinar fecha y hora
                fecha_hora = datetime.combine(fecha_incidente, hora_incidente)
                # Subir evidencias si existen
                evidencias_urls = []
                if evidencias:
                    with st.spinner("Subiendo evidencias..."):
                        for evidencia in evidencias:
                            ruta = f"incidentes/{datetime.now().strftime('%Y%m')}/{evidencia.name}"
                            url = supabase.subir_archivo(
                                STORAGE_BUCKETS["incidentes"],
                                ruta,
                                evidencia.getvalue()
                            )
                            if url:
                                evidencias_urls.append(url)
                
                datos_incidente = {
                    "codigo": generar_codigo_incidente(),
                    "tipo": tipo,
                    "fecha_hora": fecha_hora.isoformat(),
                    "area": area,
                    "ubicacion_especifica": ubicacion_especifica,
                    "descripcion": descripcion,
                    "afectado_nombre": afectado_nombre,
                    "afectado_dni": afectado_dni,
                    "afectado_cargo": afectado_cargo,
                    "parte_cuerpo_afectada": parte_cuerpo,
                    "naturaleza_lesion": naturaleza_lesion,
                    "dias_descanso_medico": dias_descanso,
                    "testigos": testigos,
                    "causas_inmediatas": causas_inmediatas,
                    "causas_basicas": causas_basicas,
                    "analisis_causa_raiz": analisis_causa_raiz,
                    "medidas_inmediatas": medidas_inmediatas,
                    "requiere_investigacion": requiere_investigacion,
                    "evidencias_url": evidencias_urls if evidencias_urls else None,
                    "notificado_sunafil": notificado_sunafil,
                    "fecha_notificacion_sunafil": fecha_notificacion.isoformat() if notificado_sunafil else None,
                    "reportado_por": usuario["id"],
                    "estado": "reportado"
                }
                
                incidente_creado = supabase.crear_incidente(datos_incidente)
                
                if incidente_creado:
                    st.success(f"✅ Incidente registrado: {incidente_creado['codigo']}")
                    
                    # Enviar notificación a n8n
                    with st.spinner("Enviando notificaciones..."):
                        n8n.notificar_incidente_registrado(incidente_creado)
                    
                    st.info("🔔 Notificaciones enviadas (Email + Slack)")
                    st.rerun()


def formulario_accion_correctiva(incidente_id: str):
    """Formulario para registrar acciones correctivas"""
    st.subheader("➕ Registrar Acción Correctiva")
    
    supabase = get_supabase_client()
    usuarios = supabase.listar_usuarios()
    usuarios_dict = {u["nombre_completo"]: u["id"] for u in usuarios}
    
    with st.form("form_accion_correctiva"):
        descripcion = st.text_area("Descripción de la Acción *", height=100)
        tipo = st.selectbox("Tipo", ["Correctiva", "Preventiva", "Mejora"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            responsable_nombre = st.selectbox("Responsable *", list(usuarios_dict.keys()))
            fecha_compromiso = st.date_input("Fecha Compromiso *")
        
        with col2:
            estado = st.selectbox("Estado", ["pendiente", "en_proceso", "completada", "verificada"])
            fecha_implementacion = st.date_input("Fecha Implementación", value=None)
        
        observaciones = st.text_area("Observaciones")
        evidencia = st.file_uploader("Evidencia de Implementación", type=["pdf", "jpg", "png"])
        
        submitted = st.form_submit_button("💾 Registrar Acción", type="primary")
        
        if submitted:
            if not all([descripcion, responsable_nombre, fecha_compromiso]):
                st.error("Por favor completa todos los campos obligatorios (*)")
            else:
                # Subir evidencia si existe
                evidencia_url = None
                if evidencia:
                    ruta = f"acciones_correctivas/{datetime.now().strftime('%Y%m')}/{evidencia.name}"
                    evidencia_url = supabase.subir_archivo(
                        STORAGE_BUCKETS["incidentes"],
                        ruta,
                        evidencia.getvalue()
                    )
                
                datos_accion = {
                    "incidente_id": incidente_id,
                    "descripcion": descripcion,
                    "tipo": tipo,
                    "responsable_id": usuarios_dict[responsable_nombre],
                    "fecha_compromiso": fecha_compromiso.isoformat(),
                    "fecha_implementacion": fecha_implementacion.isoformat() if fecha_implementacion else None,
                    "estado": estado,
                    "evidencia_implementacion_url": evidencia_url,
                    "observaciones": observaciones
                }
                
                accion_creada = supabase.crear_accion_correctiva(datos_accion)
                
                if accion_creada:
                    st.success("✅ Acción correctiva registrada")
                    st.rerun()


def listar_incidentes():
    """Lista y filtra incidentes registrados"""
    st.subheader("📋 Listado de Incidentes")
    
    supabase = get_supabase_client()
    
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filtro_tipo = st.selectbox("Tipo", ["Todos"] + TIPOS_INCIDENTE)
    with col2:
        filtro_estado = st.selectbox("Estado", ["Todos", "reportado", "en_investigacion", "investigado", "cerrado"])
    with col3:
        filtro_area = st.text_input("🔍 Área")
    with col4:
        filtro_fecha_desde = st.date_input("Desde", value=None)
    
    # Construir filtros
    filtros = {}
    if filtro_tipo != "Todos":
        filtros["tipo"] = filtro_tipo
    if filtro_estado != "Todos":
        filtros["estado"] = filtro_estado
    if filtro_area:
        filtros["area"] = filtro_area
    
    incidentes = supabase.listar_incidentes(filtros)
    
    if incidentes:
        st.info(f"Total de incidentes: {len(incidentes)}")
        
        # Mostrar incidentes
        for inc in incidentes:
            with st.expander(f"🔴 {inc['codigo']} - {inc['tipo']} - {inc['area']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Fecha:** {inc['fecha_hora']}")
                    st.markdown(f"**Área:** {inc['area']}")
                    st.markdown(f"**Ubicación:** {inc.get('ubicacion_especifica', 'N/A')}")
                    st.markdown(f"**Estado:** {inc['estado']}")
                
                with col2:
                    if inc.get('afectado_nombre'):
                        st.markdown(f"**Afectado:** {inc['afectado_nombre']}")
                        st.markdown(f"**Cargo:** {inc.get('afectado_cargo', 'N/A')}")
                        st.markdown(f"**Días descanso:** {inc.get('dias_descanso_medico', 0)}")
                
                st.markdown(f"**Descripción:** {inc['descripcion']}")
                
                if inc.get('medidas_inmediatas'):
                    st.markdown(f"**Medidas Inmediatas:** {inc['medidas_inmediatas']}")
                
                # Botón para agregar acción correctiva
                if st.button(f"➕ Agregar Acción Correctiva", key=f"btn_accion_{inc['id']}"):
                    st.session_state[f"mostrar_form_accion_{inc['id']}"] = True
                
                if st.session_state.get(f"mostrar_form_accion_{inc['id']}", False):
                    formulario_accion_correctiva(inc['id'])
    else:
        st.warning("No se encontraron incidentes")


def dashboard_incidentes():
    """Dashboard con estadísticas de incidentes"""
    st.subheader("📊 Dashboard de Incidentes")
    
    supabase = get_supabase_client()
    incidentes = supabase.listar_incidentes()
    
    if not incidentes:
        st.warning("No hay incidentes registrados")
        return
    
    df = pd.DataFrame(incidentes)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(df)
        st.metric("Total Incidentes", total)
    
    with col2:
        accidentes = len(df[df["tipo"].str.contains("Accidente")])
        st.metric("Accidentes", accidentes)
    
    with col3:
        dias_perdidos = df["dias_descanso_medico"].sum()
        st.metric("Días Perdidos", int(dias_perdidos))
    
    with col4:
        investigacion = len(df[df["requiere_investigacion"] == True])
        st.metric("En Investigación", investigacion)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución por tipo
        fig_tipo = px.pie(
            df,
            names="tipo",
            title="Distribución por Tipo de Incidente"
        )
        st.plotly_chart(fig_tipo, width='stretch')
    
    with col2:
        # Incidentes por área
        fig_area = px.bar(
            df["area"].value_counts().reset_index(),
            x="area",
            y="count",
            title="Incidentes por Área",
            labels={"area": "Área", "count": "Cantidad"}
        )
        st.plotly_chart(fig_area, width='stretch')
    
    # Tendencia temporal
    df["fecha"] = pd.to_datetime(df["fecha_hora"]).dt.date
    incidentes_por_fecha = df.groupby("fecha").size().reset_index(name="cantidad")
    
    fig_tendencia = px.line(
        incidentes_por_fecha,
        x="fecha",
        y="cantidad",
        title="Tendencia de Incidentes en el Tiempo",
        labels={"fecha": "Fecha", "cantidad": "Cantidad de Incidentes"}
    )
    st.plotly_chart(fig_tendencia, width='stretch')


def modulo_incidentes():
    """Módulo principal de gestión de incidentes"""
    st.title("🚨 Gestión de Incidentes y Accidentes")
    st.markdown("**Registro e Investigación de Incidentes - Art. 82-88 Ley 29783**")
    
    tabs = st.tabs(["📊 Dashboard", "📋 Listado", "➕ Registrar"])
    
    with tabs[0]:
        dashboard_incidentes()
    
    with tabs[1]:
        listar_incidentes()
    
    with tabs[2]:
        formulario_registro_incidente()


if __name__ == "__main__":
    modulo_incidentes()
