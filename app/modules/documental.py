"""
Módulo de Gestión Documental (Art. 28, 32 Ley 29783)
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.supabase_client import get_supabase_client
from utils.n8n_client import get_n8n_client
from config.settings import STORAGE_BUCKETS
from auth import obtener_usuario_actual


def generar_codigo_documento() -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"DOC-{timestamp}"


def formulario_registro_documento():
    """Formulario para registrar documento"""
    st.subheader("➕ Registrar Nuevo Documento")
    
    supabase = get_supabase_client()
    usuario = obtener_usuario_actual()
    usuarios = supabase.listar_usuarios()
    usuarios_dict = {u["nombre_completo"]: u["id"] for u in usuarios}
    
    with st.form("form_documento"):
        col1, col2 = st.columns(2)
        
        with col1:
            titulo = st.text_input("Título del Documento *")
            tipo = st.selectbox("Tipo *", [
                'Política SST', 'Procedimiento', 'Instructivo', 'Registro',
                'Plan', 'Programa', 'Reglamento', 'Manual', 'Formato', 'Otro'
            ])
            categoria = st.text_input("Categoría")
            version = st.text_input("Versión", value="1.0")
        
        with col2:
            fecha_emision = st.date_input("Fecha de Emisión *", value=date.today())
            fecha_vigencia = st.date_input("Fecha de Vigencia", value=None)
            requiere_revision = st.checkbox("Requiere Revisión Periódica")
            if requiere_revision:
                dias_antes_alerta = st.number_input("Días antes de alerta", value=30)
                fecha_revision = st.date_input("Fecha de Revisión", value=date.today() + timedelta(days=365))
        
        descripcion = st.text_area("Descripción")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            elaborado_por = st.selectbox("Elaborado por", list(usuarios_dict.keys()))
        with col2:
            revisado_por = st.selectbox("Revisado por", [""] + list(usuarios_dict.keys()))
        with col3:
            aprobado_por = st.selectbox("Aprobado por", [""] + list(usuarios_dict.keys()))
        
        archivo = st.file_uploader("Archivo del Documento *", type=["pdf", "docx", "xlsx"])
        
        submitted = st.form_submit_button("💾 Registrar Documento")
        
        if submitted:
            if not all([titulo, tipo, fecha_emision, archivo]):
                st.error("Completa todos los campos obligatorios")
            else:
                # Subir archivo
                ruta = f"documentos/{datetime.now().strftime('%Y%m')}/{archivo.name}"
                archivo_url = supabase.subir_archivo(
                    STORAGE_BUCKETS["documentos"],
                    ruta,
                    archivo.getvalue()
                )
                
                if archivo_url:
                    datos = {
                        "codigo": generar_codigo_documento(),
                        "titulo": titulo,
                        "tipo": tipo,
                        "categoria": categoria,
                        "descripcion": descripcion,
                        "version": version,
                        "archivo_url": archivo_url,
                        "fecha_emision": fecha_emision.isoformat(),
                        "fecha_vigencia": fecha_vigencia.isoformat() if fecha_vigencia else None,
                        "fecha_revision": fecha_revision.isoformat() if requiere_revision else None,
                        "estado": "vigente",
                        "elaborado_por": usuarios_dict[elaborado_por],
                        "revisado_por": usuarios_dict.get(revisado_por) if revisado_por else None,
                        "aprobado_por": usuarios_dict.get(aprobado_por) if aprobado_por else None,
                        "requiere_revision": requiere_revision,
                        "dias_antes_alerta": dias_antes_alerta if requiere_revision else 30
                    }
                    
                    if supabase.crear_documento(datos):
                        st.success("✅ Documento registrado")
                        st.rerun()


def listar_documentos():
    """Lista documentos"""
    st.subheader("📋 Listado de Documentos")
    
    supabase = get_supabase_client()
    
    col1, col2 = st.columns(2)
    with col1:
        filtro_tipo = st.selectbox("Tipo", ["Todos", 'Política SST', 'Procedimiento', 'Instructivo', 'Registro',
                                             'Plan', 'Programa', 'Reglamento', 'Manual', 'Formato', 'Otro'])
    with col2:
        filtro_estado = st.selectbox("Estado", ["Todos", "vigente", "obsoleto", "borrador", "archivado"])
    
    filtros = {}
    if filtro_tipo != "Todos":
        filtros["tipo"] = filtro_tipo
    if filtro_estado != "Todos":
        filtros["estado"] = filtro_estado
    
    documentos = supabase.listar_documentos(filtros)
    
    if documentos:
        st.info(f"Total: {len(documentos)}")
        
        for doc in documentos:
            with st.expander(f"📄 {doc['codigo']} - {doc['titulo']} (v{doc['version']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Tipo:** {doc['tipo']}")
                    st.markdown(f"**Estado:** {doc['estado']}")
                    st.markdown(f"**Fecha Emisión:** {doc['fecha_emision']}")
                
                with col2:
                    if doc.get('categoria'):
                        st.markdown(f"**Categoría:** {doc['categoria']}")
                    if doc.get('fecha_revision'):
                        st.markdown(f"**Fecha Revisión:** {doc['fecha_revision']}")
                
                if doc.get('descripcion'):
                    st.markdown(f"**Descripción:** {doc['descripcion']}")
                
                st.markdown(f"[📥 Descargar Documento]({doc['archivo_url']})")
    else:
        st.warning("No hay documentos registrados")


def documentos_por_revisar():
    """Muestra documentos próximos a revisión"""
    st.subheader("⏰ Documentos Próximos a Revisión")
    
    supabase = get_supabase_client()
    n8n = get_n8n_client()
    
    # Aquí se usaría la vista v_documentos_revision
    # Por simplicidad, filtramos manualmente
    documentos = supabase.listar_documentos({"estado": "vigente"})
    
    docs_revision = []
    for doc in documentos:
        if doc.get("requiere_revision") and doc.get("fecha_revision"):
            fecha_rev = datetime.fromisoformat(doc["fecha_revision"]).date()
            dias_restantes = (fecha_rev - date.today()).days
            if dias_restantes <= 30:
                doc["dias_hasta_revision"] = dias_restantes
                docs_revision.append(doc)
    
    if docs_revision:
        st.warning(f"⚠️ {len(docs_revision)} documentos requieren revisión")
        
        df = pd.DataFrame(docs_revision)
        st.dataframe(df[["codigo", "titulo", "tipo", "fecha_revision", "dias_hasta_revision"]], 
                    use_container_width=True, hide_index=True)
        
        if st.button("📧 Enviar Alertas de Revisión"):
            for doc in docs_revision:
                n8n.notificar_documento_revision(doc)
            st.success("✅ Alertas enviadas")
    else:
        st.success("✅ No hay documentos próximos a revisión")


def modulo_documental():
    """Módulo principal de gestión documental"""
    st.title("📁 Gestión Documental")
    st.markdown("**Control de Documentos del Sistema SST - Art. 28, 32 Ley 29783**")
    
    tabs = st.tabs(["📋 Documentos", "⏰ Por Revisar", "➕ Registrar"])
    
    with tabs[0]:
        listar_documentos()
    
    with tabs[1]:
        documentos_por_revisar()
    
    with tabs[2]:
        formulario_registro_documento()


if __name__ == "__main__":
    modulo_documental()
