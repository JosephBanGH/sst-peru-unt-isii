"""
Sistema Integral de Seguridad y Salud en el Trabajo
Ley 29783 - Perú
"""


import streamlit as st
import sys
import os

# Configurar path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT, APP_NAME, APP_VERSION
from auth import (
    requerir_autenticacion,
    mostrar_info_usuario,
    obtener_usuario_actual,
    es_admin,
    es_supervisor
)

# Importar módulos
from modules import (
    riesgos,
    inspecciones,
    capacitaciones,
    incidentes,
    epp,
    documental,
    reportes
)


# Configuración de la página
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)


def aplicar_estilos():
    """Aplica estilos CSS personalizados"""
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            padding: 1rem 0;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
        .stButton>button {
            width: 100%;
        }
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
    </style>
    """, unsafe_allow_html=True)


def mostrar_dashboard_principal():
    """Dashboard principal del sistema"""
    st.markdown('<div class="main-header">🛡️ Sistema Integral SST</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Sistema de Gestión de Seguridad y Salud en el Trabajo - Ley 29783</div>', 
                unsafe_allow_html=True)
    
    usuario = obtener_usuario_actual()
    
    st.markdown(f"### Bienvenido, {usuario['nombre_completo']} 👋")
    
    # Información del sistema
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **📋 Sistema:** {APP_NAME}  
        **🔢 Versión:** {APP_VERSION}  
        **👤 Rol:** {usuario.get('rol', 'usuario').title()}
        """)
    
    with col2:
        st.info(f"""
        **🏢 Área:** {usuario.get('area', 'N/A')}  
        **💼 Cargo:** {usuario.get('cargo', 'N/A')}  
        **📧 Email:** {usuario.get('email')}
        """)
    
    with col3:
        st.info("""
        **📚 Módulos Disponibles:**  
        - Gestión de Riesgos  
        - Inspecciones  
        - Capacitaciones  
        - Incidentes  
        - EPP  
        - Documental  
        - Reportes
        """)
    
    st.markdown("---")
    
    # Accesos rápidos
    st.markdown("### 🚀 Accesos Rápidos")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⚠️ Registrar Riesgo", width='stretch'):
            st.session_state.pagina_actual = "riesgos"
            st.rerun()
    
    with col2:
        if st.button("🚨 Reportar Incidente", width='stretch'):
            st.session_state.pagina_actual = "incidentes"
            st.rerun()
    
    with col3:
        if st.button("📚 Nueva Capacitación", width='stretch'):
            st.session_state.pagina_actual = "capacitaciones"
            st.rerun()
    
    with col4:
        if st.button("🔍 Nueva Inspección", width='stretch'):
            st.session_state.pagina_actual = "inspecciones"
            st.rerun()
    
    st.markdown("---")
    
    # Información legal
    st.markdown("### 📖 Marco Legal")
    
    with st.expander("Ley 29783 - Ley de Seguridad y Salud en el Trabajo"):
        st.markdown("""
        **Objeto de la Ley:**  
        Promover una cultura de prevención de riesgos laborales en el país, sobre la base de la 
        observancia del deber de prevención de los empleadores, el rol de fiscalización y control 
        del Estado y la participación de los trabajadores y sus organizaciones sindicales.
        
        **Principios Fundamentales:**
        - Principio de prevención
        - Principio de responsabilidad
        - Principio de cooperación
        - Principio de información y capacitación
        - Principio de gestión integral
        - Principio de atención integral de la salud
        - Principio de consulta y participación
        - Principio de primacía de la realidad
        - Principio de protección
        """)
    
    with st.expander("DS 005-2012-TR - Reglamento de la Ley 29783"):
        st.markdown("""
        **Aspectos Clave del Reglamento:**
        - Sistema de Gestión de SST
        - Comité de SST
        - Identificación de Peligros y Evaluación de Riesgos (IPERC)
        - Capacitación en SST
        - Investigación de Accidentes
        - Auditorías del Sistema de Gestión
        - Estadísticas de Seguridad
        - Registros Obligatorios
        """)
    
    st.markdown("---")
    
    # Pie de página
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p>Sistema Integral de Seguridad y Salud en el Trabajo v1.0.0</p>
        <p>Desarrollado conforme a la Ley 29783 y DS 005-2012-TR</p>
        <p>© 2024 - Todos los derechos reservados</p>
    </div>
    """, unsafe_allow_html=True)


def menu_navegacion():
    """Menú de navegación lateral"""
    with st.sidebar:
        st.image("https://placehold.co/200x80/1f77b4/ffffff?text=SST+PERU", width='stretch')
        
        st.markdown("---")
        st.markdown("### 📋 Navegación")
        
        # Menú principal
        paginas = {
            "🏠 Inicio": "inicio",
            "⚠️ Gestión de Riesgos": "riesgos",
            "🔍 Inspecciones": "inspecciones",
            "📚 Capacitaciones": "capacitaciones",
            "🚨 Incidentes y Accidentes": "incidentes",
            "🦺 Gestión de EPP": "epp",
            "📁 Gestión Documental": "documental",
            "📊 Reportes y Análisis": "reportes"
        }
        
        # Inicializar página actual
        if "pagina_actual" not in st.session_state:
            st.session_state.pagina_actual = "inicio"
        
        # Botones de navegación
        for nombre, clave in paginas.items():
            if st.button(nombre, width='stretch', key=f"nav_{clave}"):
                st.session_state.pagina_actual = clave
                st.rerun()
        
        st.markdown("---")
        
        # Información del usuario
        mostrar_info_usuario()
        
        st.markdown("---")
        
        # Información del sistema
        st.markdown("### ℹ️ Información")
        st.caption(f"Versión: {APP_VERSION}")
        st.caption("Ley 29783 - Perú")


def main():
    """Función principal de la aplicación"""
    # Requerir autenticación
    requerir_autenticacion()
    
    # Aplicar estilos
    aplicar_estilos()
    
    # Mostrar menú de navegación
    menu_navegacion()
    
    # Obtener página actual
    pagina = st.session_state.get("pagina_actual", "inicio")
    
    # Renderizar página correspondiente
    if pagina == "inicio":
        mostrar_dashboard_principal()
    elif pagina == "riesgos":
        riesgos.modulo_riesgos()
    elif pagina == "inspecciones":
        inspecciones.modulo_inspecciones()
    elif pagina == "capacitaciones":
        capacitaciones.modulo_capacitaciones()
    elif pagina == "incidentes":
        incidentes.modulo_incidentes()
    elif pagina == "epp":
        epp.modulo_epp()
    elif pagina == "documental":
        documental.modulo_documental()
    elif pagina == "reportes":
        reportes.modulo_reportes()


if __name__ == "__main__":
    main()
