"""
Cliente de Supabase para el Sistema SST
"""
from supabase import create_client, Client
from typing import Optional, Dict, List, Any
import streamlit as st
from datetime import datetime
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY, STORAGE_BUCKETS


class SupabaseClient:
    """Cliente para interactuar con Supabase"""
    
    def __init__(self):
        """Inicializa el cliente de Supabase"""
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            raise ValueError("Las credenciales de Supabase no están configuradas")
        
        # Usar SERVICE_KEY para bypass de RLS
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # ==================== USUARIOS ====================
    
    def obtener_usuario_por_email(self, email: str) -> Optional[Dict]:
        """Obtiene un usuario por su email"""
        try:
            response = self.client.table("usuarios").select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error al obtener usuario: {str(e)}")
            return None
    
    def crear_usuario(self, datos: Dict) -> Optional[Dict]:
        """Crea un nuevo usuario"""
        try:
            response = self.client.table("usuarios").insert(datos).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error al crear usuario: {str(e)}")
            return None
    
    def listar_usuarios(self, activos_solo: bool = True) -> List[Dict]:
        """Lista todos los usuarios"""
        try:
            query = self.client.table("usuarios").select("*")
            if activos_solo:
                query = query.eq("activo", True)
            response = query.execute()
            return response.data
        except Exception as e:
            st.error(f"Error al listar usuarios: {str(e)}")
            return []
    
    # ==================== RIESGOS ====================
    
    def crear_riesgo(self, datos: Dict) -> Optional[Dict]:
        """Crea un nuevo riesgo"""
        try:
            response = self.client.table("riesgos").insert(datos).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error al crear riesgo: {str(e)}")
            return None
    
    def listar_riesgos(self, filtros: Optional[Dict] = None) -> List[Dict]:
        """Lista riesgos con filtros opcionales"""
        try:
            query = self.client.table("riesgos").select("*, responsable:responsable_id(nombre_completo), creador:creado_por(nombre_completo)")
            
            if filtros:
                if "area" in filtros:
                    query = query.eq("area", filtros["area"])
                if "clasificacion" in filtros:
                    query = query.eq("clasificacion", filtros["clasificacion"])
                if "estado" in filtros:
                    query = query.eq("estado", filtros["estado"])
            
            response = query.order("fecha_creacion", desc=True).execute()
            return response.data
        except Exception as e:
            st.error(f"Error al listar riesgos: {str(e)}")
            return []
    
    def actualizar_riesgo(self, riesgo_id: str, datos: Dict) -> bool:
        """Actualiza un riesgo"""
        try:
            self.client.table("riesgos").update(datos).eq("id", riesgo_id).execute()
            return True
        except Exception as e:
            st.error(f"Error al actualizar riesgo: {str(e)}")
            return False
    
    # ==================== INSPECCIONES ====================
    
    def crear_checklist(self, datos: Dict) -> Optional[Dict]:
        """Crea un nuevo checklist"""
        try:
            response = self.client.table("checklists").insert(datos).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error al crear checklist: {str(e)}")
            return None
    
    def listar_checklists(self, activos_solo: bool = True) -> List[Dict]:
        """Lista checklists"""
        try:
            query = self.client.table("checklists").select("*")
            if activos_solo:
                query = query.eq("activo", True)
            response = query.execute()
            return response.data
        except Exception as e:
            st.error(f"Error al listar checklists: {str(e)}")
            return []
    
    def crear_inspeccion(self, datos: Dict) -> Optional[Dict]:
        """Crea una nueva inspección"""
        try:
            response = self.client.table("inspecciones").insert(datos).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error al crear inspección: {str(e)}")
            return None
    
    def listar_inspecciones(self, filtros: Optional[Dict] = None) -> List[Dict]:
        """Lista inspecciones"""
        try:
            query = self.client.table("inspecciones").select("*, checklist:checklist_id(nombre), inspector:inspector_id(nombre_completo)")
            
            if filtros:
                if "estado" in filtros:
                    query = query.eq("estado", filtros["estado"])
                if "area" in filtros:
                    query = query.eq("area", filtros["area"])
            
            response = query.order("fecha_programada", desc=True).execute()
            return response.data
        except Exception as e:
            st.error(f"Error al listar inspecciones: {str(e)}")
            return []
    
    # ==================== CAPACITACIONES ====================
    
    def crear_capacitacion(self, datos: Dict) -> Optional[Dict]:
        """Crea una nueva capacitación"""
        try:
            response = self.client.table("capacitaciones").insert(datos).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error al crear capacitación: {str(e)}")
            return None
    
    def listar_capacitaciones(self, filtros: Optional[Dict] = None) -> List[Dict]:
        """Lista capacitaciones"""
        try:
            query = self.client.table("capacitaciones").select("*")
            
            if filtros:
                if "estado" in filtros:
                    query = query.eq("estado", filtros["estado"])
                if "tipo" in filtros:
                    query = query.eq("tipo", filtros["tipo"])
            
            response = query.order("fecha_programada", desc=True).execute()
            return response.data
        except Exception as e:
            st.error(f"Error al listar capacitaciones: {str(e)}")
            return []
    
    def registrar_asistente(self, datos: Dict) -> bool:
        """Registra un asistente a una capacitación"""
        try:
            self.client.table("asistentes_capacitacion").insert(datos).execute()
            return True
        except Exception as e:
            st.error(f"Error al registrar asistente: {str(e)}")
            return False
    
    # ==================== INCIDENTES ====================
    
    def crear_incidente(self, datos: Dict) -> Optional[Dict]:
        """Crea un nuevo incidente"""
        try:
            response = self.client.table("incidentes").insert(datos).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error al crear incidente: {str(e)}")
            return None
    
    def listar_incidentes(self, filtros: Optional[Dict] = None) -> List[Dict]:
        """Lista incidentes"""
        try:
            query = self.client.table("incidentes").select("*, reportador:reportado_por(nombre_completo)")
            
            if filtros:
                if "tipo" in filtros:
                    query = query.eq("tipo", filtros["tipo"])
                if "estado" in filtros:
                    query = query.eq("estado", filtros["estado"])
                if "area" in filtros:
                    query = query.eq("area", filtros["area"])
            
            response = query.order("fecha_hora", desc=True).execute()
            return response.data
        except Exception as e:
            st.error(f"Error al listar incidentes: {str(e)}")
            return []
    
    def crear_accion_correctiva(self, datos: Dict) -> Optional[Dict]:
        """Crea una acción correctiva"""
        try:
            response = self.client.table("acciones_correctivas").insert(datos).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error al crear acción correctiva: {str(e)}")
            return None
    
    # ==================== EPP ====================
    
    def crear_epp(self, datos: Dict) -> Optional[Dict]:
        """Crea un nuevo EPP en el catálogo"""
        try:
            response = self.client.table("epp_catalogo").insert(datos).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error al crear EPP: {str(e)}")
            return None
    
    def listar_epp(self, activos_solo: bool = True) -> List[Dict]:
        """Lista EPPs del catálogo"""
        try:
            query = self.client.table("epp_catalogo").select("*")
            if activos_solo:
                query = query.eq("activo", True)
            response = query.execute()
            return response.data
        except Exception as e:
            st.error(f"Error al listar EPP: {str(e)}")
            return []
    
    def asignar_epp(self, datos: Dict) -> Optional[Dict]:
        """Asigna un EPP a un usuario"""
        try:
            response = self.client.table("epp_asignaciones").insert(datos).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error al asignar EPP: {str(e)}")
            return None
    
    def obtener_epp_vencimientos(self) -> List[Dict]:
        """Obtiene EPPs próximos a vencer"""
        try:
            response = self.client.table("v_epp_vencimientos").select("*").execute()
            return response.data
        except Exception as e:
            st.error(f"Error al obtener vencimientos: {str(e)}")
            return []
    
    # ==================== DOCUMENTOS ====================
    
    def crear_documento(self, datos: Dict) -> Optional[Dict]:
        """Crea un nuevo documento"""
        try:
            response = self.client.table("documentos").insert(datos).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error al crear documento: {str(e)}")
            return None
    
    def listar_documentos(self, filtros: Optional[Dict] = None) -> List[Dict]:
        """Lista documentos"""
        try:
            query = self.client.table("documentos").select("*")
            
            if filtros:
                if "tipo" in filtros:
                    query = query.eq("tipo", filtros["tipo"])
                if "estado" in filtros:
                    query = query.eq("estado", filtros["estado"])
            
            response = query.order("fecha_creacion", desc=True).execute()
            return response.data
        except Exception as e:
            st.error(f"Error al listar documentos: {str(e)}")
            return []
    
    # ==================== STORAGE ====================
    
    def subir_archivo(self, bucket: str, ruta: str, archivo) -> Optional[str]:
        """Sube un archivo a Supabase Storage"""
        try:
            response = self.client.storage.from_(bucket).upload(ruta, archivo)
            if response:
                url_publica = self.client.storage.from_(bucket).get_public_url(ruta)
                return url_publica
            return None
        except Exception as e:
            st.error(f"Error al subir archivo: {str(e)}")
            return None
    
    def eliminar_archivo(self, bucket: str, ruta: str) -> bool:
        """Elimina un archivo de Supabase Storage"""
        try:
            self.client.storage.from_(bucket).remove([ruta])
            return True
        except Exception as e:
            st.error(f"Error al eliminar archivo: {str(e)}")
            return False


# Instancia global del cliente (sin caché temporal para forzar SERVICE_KEY)
_client_instance = None

def get_supabase_client():
    """Retorna una instancia del cliente de Supabase con SERVICE_KEY"""
    global _client_instance
    if _client_instance is None:
        _client_instance = SupabaseClient()
    return _client_instance
