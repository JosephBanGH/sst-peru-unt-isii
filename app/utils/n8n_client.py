"""
Cliente de n8n para automatizaciones del Sistema SST
"""
import requests
import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import N8N_WEBHOOKS


class N8NClient:
    """Cliente para interactuar con webhooks de n8n"""
    
    def __init__(self):
        """Inicializa el cliente de n8n"""
        self.webhooks = N8N_WEBHOOKS
        self.timeout = 10  # segundos
    
    def _enviar_webhook(self, url: str, datos: Dict[str, Any]) -> bool:
        """Envía datos a un webhook de n8n"""
        try:
            # Agregar timestamp
            datos["timestamp"] = datetime.now().isoformat()
            
            response = requests.post(
                url,
                json=datos,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                return True
            else:
                st.warning(f"Webhook respondió con código {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            st.warning("Timeout al enviar webhook - el flujo puede ejecutarse en segundo plano")
            return False
        except requests.exceptions.ConnectionError:
            st.warning("No se pudo conectar con n8n - verifica que esté ejecutándose")
            return False
        except Exception as e:
            st.error(f"Error al enviar webhook: {str(e)}")
            return False
    
    def notificar_incidente_registrado(self, incidente: Dict[str, Any]) -> bool:
        """
        Notifica que se ha registrado un nuevo incidente
        
        Args:
            incidente: Datos del incidente registrado
            
        Returns:
            bool: True si se envió correctamente
        """
        url = self.webhooks["incidente_registrado"]
        payload = {
            "evento": "incidente_registrado",
            "incidente_id": incidente.get("id"),
            "codigo": incidente.get("codigo"),
            "tipo": incidente.get("tipo"),
            "area": incidente.get("area"),
            "descripcion": incidente.get("descripcion"),
            "fecha_hora": incidente.get("fecha_hora"),
            "afectado_nombre": incidente.get("afectado_nombre"),
            "requiere_investigacion": incidente.get("requiere_investigacion", False),
            "reportado_por": incidente.get("reportado_por")
        }
        return self._enviar_webhook(url, payload)
    
    def notificar_alerta_epp_vencimiento(self, epp_asignacion: Dict[str, Any]) -> bool:
        """
        Notifica que un EPP está próximo a vencer
        
        Args:
            epp_asignacion: Datos de la asignación de EPP
            
        Returns:
            bool: True si se envió correctamente
        """
        url = self.webhooks["alerta_epp"]
        
        payload = {
            "evento": "alerta_epp_vencimiento",
            "asignacion_id": epp_asignacion.get("id"),
            "epp_nombre": epp_asignacion.get("epp_nombre"),
            "epp_tipo": epp_asignacion.get("epp_tipo"),
            "usuario": epp_asignacion.get("usuario"),
            "email": epp_asignacion.get("email"),
            "area": epp_asignacion.get("area"),
            "fecha_vencimiento": epp_asignacion.get("fecha_vencimiento"),
            "dias_restantes": epp_asignacion.get("dias_restantes")
        }
        
        return self._enviar_webhook(url, payload)
    
    def notificar_recordatorio_capacitacion(self, capacitacion: Dict[str, Any], asistentes: list) -> bool:
        """
        Envía recordatorio de capacitación programada
        
        Args:
            capacitacion: Datos de la capacitación
            asistentes: Lista de asistentes registrados
            
        Returns:
            bool: True si se envió correctamente
        """
        url = self.webhooks["recordatorio_capacitacion"]
        
        payload = {
            "evento": "recordatorio_capacitacion",
            "capacitacion_id": capacitacion.get("id"),
            "codigo": capacitacion.get("codigo"),
            "titulo": capacitacion.get("titulo"),
            "tipo": capacitacion.get("tipo"),
            "fecha_programada": capacitacion.get("fecha_programada"),
            "instructor": capacitacion.get("instructor"),
            "lugar": capacitacion.get("lugar"),
            "duracion_horas": capacitacion.get("duracion_horas"),
            "modalidad": capacitacion.get("modalidad"),
            "asistentes": asistentes
        }
        
        return self._enviar_webhook(url, payload)
    
    def notificar_documento_revision(self, documento: Dict[str, Any]) -> bool:
        """
        Notifica que un documento requiere revisión
        
        Args:
            documento: Datos del documento
            
        Returns:
            bool: True si se envió correctamente
        """
        url = self.webhooks["documento_revision"]
        
        payload = {
            "evento": "documento_revision",
            "documento_id": documento.get("id"),
            "codigo": documento.get("codigo"),
            "titulo": documento.get("titulo"),
            "tipo": documento.get("tipo"),
            "version": documento.get("version"),
            "fecha_revision": documento.get("fecha_revision"),
            "dias_hasta_revision": documento.get("dias_hasta_revision"),
            "elaborado_por": documento.get("elaborado_por")
        }
        
        return self._enviar_webhook(url, payload)
    
    def notificar_riesgo_critico(self, riesgo: Dict[str, Any]) -> bool:
        """
        Notifica la identificación de un riesgo crítico
        
        Args:
            riesgo: Datos del riesgo
            
        Returns:
            bool: True si se envió correctamente
        """
        url = self.webhooks["riesgo_critico"]  # Webhook dedicado para riesgos
        
        payload = {
            "evento": "riesgo_critico_identificado",
            "riesgo_id": riesgo.get("id"),
            "codigo": riesgo.get("codigo"),
            "descripcion": riesgo.get("descripcion"),
            "area": riesgo.get("area"),
            "proceso": riesgo.get("proceso"),
            "tipo_riesgo": riesgo.get("tipo_riesgo"),
            "nivel_riesgo": riesgo.get("nivel_riesgo"),
            "clasificacion": riesgo.get("clasificacion"),
            "probabilidad": riesgo.get("probabilidad"),
            "severidad": riesgo.get("severidad"),
            "responsable": riesgo.get("responsable"),
            "medidas_control": riesgo.get("medidas_control"),
            "fecha_identificacion": riesgo.get("fecha_identificacion")
        }
        
        return self._enviar_webhook(url, payload)
    
    def notificar_accion_correctiva_vencida(self, accion: Dict[str, Any]) -> bool:
        """
        Notifica que una acción correctiva está vencida
        
        Args:
            accion: Datos de la acción correctiva
            
        Returns:
            bool: True si se envió correctamente
        """
        url = self.webhooks["incidente_registrado"]  # Reutilizamos este webhook
        
        payload = {
            "evento": "accion_correctiva_vencida",
            "accion_id": accion.get("id"),
            "descripcion": accion.get("descripcion"),
            "tipo": accion.get("tipo"),
            "fecha_compromiso": accion.get("fecha_compromiso"),
            "dias_vencidos": accion.get("dias_vencidos"),
            "responsable": accion.get("responsable"),
            "incidente_codigo": accion.get("incidente_codigo")
        }
        
        return self._enviar_webhook(url, payload)
    
    def test_conexion(self) -> Dict[str, bool]:
        """
        Prueba la conexión con todos los webhooks configurados
        
        Returns:
            Dict con el estado de cada webhook
        """
        resultados = {}
        
        for nombre, url in self.webhooks.items():
            try:
                response = requests.post(
                    url,
                    json={"test": True, "timestamp": datetime.now().isoformat()},
                    timeout=5
                )
                resultados[nombre] = response.status_code in [200, 201]
            except:
                resultados[nombre] = False
        
        return resultados


# Instancia global del cliente (sin caché temporal)
_n8n_client_instance = None

def get_n8n_client():
    """Retorna una instancia del cliente de n8n"""
    global _n8n_client_instance
    if _n8n_client_instance is None:
        _n8n_client_instance = N8NClient()
    return _n8n_client_instance
