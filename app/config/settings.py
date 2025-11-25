"""
Configuración del Sistema SST Perú
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Configuración de n8n
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")

# Configuración de la aplicación
APP_NAME = os.getenv("APP_NAME", "Sistema SST Perú")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Configuración de Streamlit
PAGE_TITLE = "Sistema Integral SST - Ley 29783"
PAGE_ICON = "🛡️"
LAYOUT = "wide"

# Buckets de Supabase Storage
STORAGE_BUCKETS = {
    "evidencias": "evidencias-sst",
    "documentos": "documentos-sst",
    "capacitaciones": "capacitaciones-sst",
    "incidentes": "incidentes-sst"
}

# Webhooks de n8n
N8N_WEBHOOKS = {
    "incidente_registrado": f"{N8N_WEBHOOK_URL}/incidente-registrado",
    "alerta_epp": f"{N8N_WEBHOOK_URL}/alerta-epp-vencimiento",
    "recordatorio_capacitacion": f"{N8N_WEBHOOK_URL}/recordatorio-capacitacion",
    "documento_revision": f"{N8N_WEBHOOK_URL}/documento-revision",
    "riesgo_critico": f"{N8N_WEBHOOK_URL}/riesgo-critico"
}

# Configuración de reportes
REPORTES_CONFIG = {
    "empresa": "Mi Empresa S.A.C.",
    "ruc": "20XXXXXXXXX",
    "direccion": "Av. Principal 123, Lima, Perú",
    "sector": "Industrial",
    "actividad_economica": "Manufactura"
}

# Tipos de riesgo según Ley 29783
TIPOS_RIESGO = [
    'Físico',
    'Químico',
    'Biológico',
    'Ergonómico',
    'Psicosocial',
    'Mecánico',
    'Eléctrico',
    'Locativo'
]

# Tipos de incidente
TIPOS_INCIDENTE = [
    'Incidente',
    'Accidente Leve',
    'Accidente Incapacitante',
    'Accidente Mortal',
    'Enfermedad Ocupacional'
]

# Tipos de EPP
TIPOS_EPP = [
    'Protección Cabeza',
    'Protección Ojos/Cara',
    'Protección Auditiva',
    'Protección Respiratoria',
    'Protección Manos',
    'Protección Pies',
    'Protección Cuerpo',
    'Protección Caídas',
    'Otro'
]

# Tipos de capacitación
TIPOS_CAPACITACION = [
    'Inducción',
    'Específica del Puesto',
    'Uso de EPP',
    'Prevención de Riesgos',
    'Primeros Auxilios',
    'Evacuación',
    'Ergonomía',
    'Manejo de Sustancias',
    'Otro'
]

# Validación de configuración
def validar_configuracion():
    """Valida que las variables de entorno estén configuradas"""
    errores = []
    
    if not SUPABASE_URL:
        errores.append("SUPABASE_URL no está configurada")
    if not SUPABASE_KEY:
        errores.append("SUPABASE_KEY no está configurada")
    if not N8N_WEBHOOK_URL:
        errores.append("N8N_WEBHOOK_URL no está configurada")
    
    return errores

def obtener_info_sistema():
    """Retorna información del sistema"""
    return {
        "nombre": APP_NAME,
        "version": APP_VERSION,
        "ambiente": ENVIRONMENT,
        "supabase_configurado": bool(SUPABASE_URL and SUPABASE_KEY),
        "n8n_configurado": bool(N8N_WEBHOOK_URL)
    }
