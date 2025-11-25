"""
Módulo de Gestión de Inspecciones
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.supabase_client import get_supabase_client
from auth import obtener_usuario_actual


def generar_codigo_inspeccion() -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"INSP-{timestamp}"


def formulario_checklist():
    """Formulario para crear checklist"""
    st.subheader("➕ Crear Checklist")
    
    supabase = get_supabase_client()
    usuario = obtener_usuario_actual()
    
    with st.form("form_checklist"):
        nombre = st.text_input("Nombre del Checklist *")
        tipo = st.selectbox("Tipo", [
            'Seguridad General', 'EPP', 'Maquinaria', 'Instalaciones',
            'Orden y Limpieza', 'Ergonomía', 'Emergencias', 'Otro'
        ])
        descripcion = st.text_area("Descripción")
        
        st.markdown("### Items del Checklist")
        num_items = st.number_input("Número de items", min_value=1, max_value=50, value=5)
        
        items = []
        for i in range(num_items):
            col1, col2 = st.columns([3, 1])
            with col1:
                pregunta = st.text_input(f"Item {i+1}", key=f"item_{i}")
            with col2:
                critico = st.checkbox("Crítico", key=f"critico_{i}")
            
            if pregunta:
                items.append({
                    "pregunta": pregunta,
                    "tipo_respuesta": "si_no",
                    "es_critico": critico
                })
        
        submitted = st.form_submit_button("💾 Crear Checklist")
        
        if submitted:
            if not all([nombre, tipo]) or not items:
                st.error("Completa todos los campos obligatorios")
            else:
                datos = {
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "tipo": tipo,
                    "items": json.dumps(items),
                    "activo": True,
                    "creado_por": usuario["id"]
                }
                
                if supabase.crear_checklist(datos):
                    st.success("✅ Checklist creado")
                    st.rerun()


def formulario_inspeccion():
    """Formulario para registrar inspección"""
    st.subheader("➕ Registrar Inspección")
    
    supabase = get_supabase_client()
    usuario = obtener_usuario_actual()
    
    checklists = supabase.listar_checklists()
    if not checklists:
        st.warning("No hay checklists disponibles. Crea uno primero.")
        return
    
    usuarios = supabase.listar_usuarios()
    
    with st.form("form_inspeccion"):
        col1, col2 = st.columns(2)
        
        with col1:
            checklist_dict = {c["nombre"]: c for c in checklists}
            checklist_sel = st.selectbox("Checklist *", list(checklist_dict.keys()))
            area = st.text_input("Área *")
            fecha_programada = st.date_input("Fecha Programada *")
        
        with col2:
            usuarios_dict = {u["nombre_completo"]: u["id"] for u in usuarios}
            inspector = st.selectbox("Inspector *", list(usuarios_dict.keys()))
            estado = st.selectbox("Estado", ["programada", "en_proceso", "completada"])
        
        observaciones = st.text_area("Observaciones")
        
        submitted = st.form_submit_button("💾 Registrar Inspección")
        
        if submitted:
            if not all([checklist_sel, area, fecha_programada]):
                st.error("Completa todos los campos obligatorios")
            else:
                datos = {
                    "codigo": generar_codigo_inspeccion(),
                    "checklist_id": checklist_dict[checklist_sel]["id"],
                    "area": area,
                    "fecha_programada": fecha_programada.isoformat(),
                    "inspector_id": usuarios_dict[inspector],
                    "estado": estado,
                    "observaciones": observaciones,
                    "creado_por": usuario["id"]
                }
                
                if supabase.crear_inspeccion(datos):
                    st.success("✅ Inspección registrada")
                    st.rerun()


def listar_inspecciones():
    """Lista inspecciones"""
    st.subheader("📋 Listado de Inspecciones")
    
    supabase = get_supabase_client()
    
    filtro_estado = st.selectbox("Estado", ["Todos", "programada", "en_proceso", "completada", "cancelada"])
    
    filtros = {}
    if filtro_estado != "Todos":
        filtros["estado"] = filtro_estado
    
    inspecciones = supabase.listar_inspecciones(filtros)
    
    if inspecciones:
        st.info(f"Total: {len(inspecciones)}")
        
        df = pd.DataFrame(inspecciones)
        st.dataframe(df[["codigo", "area", "fecha_programada", "estado"]], width='stretch', hide_index=True)
    else:
        st.warning("No hay inspecciones registradas")


def modulo_inspecciones():
    """Módulo principal de inspecciones"""
    st.title("🔍 Gestión de Inspecciones")
    
    tabs = st.tabs(["📋 Inspecciones", "➕ Nueva Inspección", "📝 Crear Checklist"])
    
    with tabs[0]:
        listar_inspecciones()
    
    with tabs[1]:
        formulario_inspeccion()
    
    with tabs[2]:
        formulario_checklist()


if __name__ == "__main__":
    modulo_inspecciones()
