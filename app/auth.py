"""
Sistema de Autenticación con Supabase
"""
import streamlit as st
from typing import Optional, Dict
from utils.supabase_client import get_supabase_client


def inicializar_sesion():
    """Inicializa las variables de sesión"""
    if "usuario_autenticado" not in st.session_state:
        st.session_state.usuario_autenticado = False
    if "usuario_datos" not in st.session_state:
        st.session_state.usuario_datos = None
    if "usuario_email" not in st.session_state:
        st.session_state.usuario_email = None


def login(email: str, password: str) -> bool:
    """
    Realiza el login del usuario
    
    Args:
        email: Email del usuario
        password: Contraseña del usuario
        
    Returns:
        bool: True si el login fue exitoso
    """
    try:
        supabase = get_supabase_client()
        
        # Autenticar con Supabase Auth
        response = supabase.client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Obtener datos adicionales del usuario
            usuario = supabase.obtener_usuario_por_email(email)
            
            if usuario and usuario.get("activo", False):
                st.session_state.usuario_autenticado = True
                st.session_state.usuario_datos = usuario
                st.session_state.usuario_email = email
                return True
            else:
                st.error("Usuario inactivo o no encontrado en el sistema")
                return False
        else:
            st.error("Credenciales incorrectas")
            return False
            
    except Exception as e:
        st.error(f"Error al iniciar sesión: {str(e)}")
        return False


def logout():
    """Cierra la sesión del usuario"""
    try:
        supabase = get_supabase_client()
        supabase.client.auth.sign_out()
    except:
        pass
    
    st.session_state.usuario_autenticado = False
    st.session_state.usuario_datos = None
    st.session_state.usuario_email = None
    st.rerun()


def registrar_usuario(email: str, password: str, nombre_completo: str, 
                      cargo: str = "", area: str = "", telefono: str = "") -> bool:
    """
    Registra un nuevo usuario en el sistema
    
    Args:
        email: Email del usuario
        password: Contraseña
        nombre_completo: Nombre completo
        cargo: Cargo del usuario
        area: Área de trabajo
        telefono: Teléfono
        
    Returns:
        bool: True si el registro fue exitoso
    """
    try:
        supabase = get_supabase_client()
        
        # Crear usuario en Supabase Auth
        response = supabase.client.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Crear registro en tabla usuarios
            datos_usuario = {
                "email": email,
                "nombre_completo": nombre_completo,
                "cargo": cargo,
                "area": area,
                "telefono": telefono,
                "rol": "usuario",
                "activo": True,
                "auth_user_id": response.user.id
            }
            
            usuario_creado = supabase.crear_usuario(datos_usuario)
            
            if usuario_creado:
                st.success("Usuario registrado exitosamente. Por favor inicia sesión.")
                return True
            else:
                st.error("Error al crear el perfil del usuario")
                return False
        else:
            st.error("Error al registrar usuario")
            return False
            
    except Exception as e:
        st.error(f"Error al registrar usuario: {str(e)}")
        return False


def verificar_autenticacion() -> bool:
    """
    Verifica si el usuario está autenticado
    
    Returns:
        bool: True si está autenticado
    """
    inicializar_sesion()
    return st.session_state.usuario_autenticado


def obtener_usuario_actual() -> Optional[Dict]:
    """
    Obtiene los datos del usuario actual
    
    Returns:
        Dict con los datos del usuario o None
    """
    if verificar_autenticacion():
        return st.session_state.usuario_datos
    return None


def es_admin() -> bool:
    """
    Verifica si el usuario actual es administrador
    
    Returns:
        bool: True si es admin
    """
    usuario = obtener_usuario_actual()
    if usuario:
        return usuario.get("rol") == "admin"
    return False


def es_supervisor() -> bool:
    """
    Verifica si el usuario actual es supervisor o admin
    
    Returns:
        bool: True si es supervisor o admin
    """
    usuario = obtener_usuario_actual()
    if usuario:
        return usuario.get("rol") in ["admin", "supervisor"]
    return False


def mostrar_formulario_login():
    """Muestra el formulario de login"""
    st.title("🛡️ Sistema SST Perú")
    st.subheader("Iniciar Sesión")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="usuario@empresa.com")
        password = st.text_input("Contraseña", type="password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
        
        with col2:
            registrar = st.form_submit_button("Registrarse", use_container_width=True)
        
        if submit:
            if email and password:
                if login(email, password):
                    st.success("¡Bienvenido!")
                    st.rerun()
            else:
                st.error("Por favor completa todos los campos")
        
        if registrar:
            st.session_state.mostrar_registro = True
            st.rerun()


def mostrar_formulario_registro():
    """Muestra el formulario de registro"""
    st.title("🛡️ Sistema SST Perú")
    st.subheader("Registro de Usuario")
    
    with st.form("registro_form"):
        email = st.text_input("Email", placeholder="usuario@empresa.com")
        password = st.text_input("Contraseña", type="password")
        password_confirm = st.text_input("Confirmar Contraseña", type="password")
        nombre_completo = st.text_input("Nombre Completo")
        
        col1, col2 = st.columns(2)
        with col1:
            cargo = st.text_input("Cargo")
            area = st.text_input("Área")
        with col2:
            telefono = st.text_input("Teléfono")
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit = st.form_submit_button("Registrar", use_container_width=True)
        
        with col2:
            volver = st.form_submit_button("Volver al Login", use_container_width=True)
        
        if submit:
            if not all([email, password, password_confirm, nombre_completo]):
                st.error("Por favor completa los campos obligatorios")
            elif password != password_confirm:
                st.error("Las contraseñas no coinciden")
            elif len(password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres")
            else:
                if registrar_usuario(email, password, nombre_completo, cargo, area, telefono):
                    st.session_state.mostrar_registro = False
                    st.rerun()
        
        if volver:
            st.session_state.mostrar_registro = False
            st.rerun()


def mostrar_info_usuario():
    """Muestra información del usuario en el sidebar"""
    usuario = obtener_usuario_actual()
    
    if usuario:
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 Usuario")
            st.markdown(f"**{usuario.get('nombre_completo')}**")
            st.markdown(f"📧 {usuario.get('email')}")
            if usuario.get('cargo'):
                st.markdown(f"💼 {usuario.get('cargo')}")
            if usuario.get('area'):
                st.markdown(f"🏢 {usuario.get('area')}")
            st.markdown(f"🔐 Rol: {usuario.get('rol', 'usuario').title()}")
            
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                logout()


def requerir_autenticacion():
    """
    Decorator para requerir autenticación en una página
    Redirige al login si el usuario no está autenticado
    """
    if not verificar_autenticacion():
        if "mostrar_registro" not in st.session_state:
            st.session_state.mostrar_registro = False
        
        if st.session_state.mostrar_registro:
            mostrar_formulario_registro()
        else:
            mostrar_formulario_login()
        
        st.stop()
