# 🛡️ Sistema Integral de Seguridad y Salud en el Trabajo - Perú

Sistema completo de gestión de SST alineado a la **Ley 29783** y su reglamento **DS 005-2012-TR**.

## 🚀 Inicio Rápido

**Para instalar y configurar el sistema, consulta:** [SETUP.md](SETUP.md)

**Para configurar workflows de n8n, consulta:** [n8n_workflows/README_WORKFLOWS.md](n8n_workflows/README_WORKFLOWS.md)

## 📋 Características Principales

### ✅ Módulos Implementados

1. **⚠️ Gestión de Riesgos (Art. 26-28)**
   - Matriz de evaluación 5x5
   - Identificación y evaluación de riesgos
   - Dashboard interactivo
   - Exportación a Excel
   - Notificaciones automáticas para riesgos críticos

2. **🔍 Inspecciones**
   - Creación de checklists personalizados
   - Programación de inspecciones
   - Registro de hallazgos con evidencias
   - Control de acciones correctivas

3. **📚 Capacitaciones (Art. 27, 35)**
   - Registro de capacitaciones
   - Control de asistencia
   - Recordatorios automáticos
   - Gestión de evidencias y certificados

4. **🚨 Incidentes y Accidentes (Art. 82-88)**
   - Registro detallado de incidentes
   - Análisis de causa raíz
   - Acciones correctivas
   - Notificaciones inmediatas (Email + Slack)
   - Estadísticas e índices de seguridad

5. **🦺 Gestión de EPP**
   - Catálogo de EPP
   - Control de asignaciones
   - Alertas de vencimiento
   - Control de stock

6. **📁 Gestión Documental (Art. 28, 32)**
   - Versionado de documentos
   - Control de vigencias
   - Alertas de revisión
   - Almacenamiento seguro en Supabase Storage

7. **📊 Reportes y Análisis**
   - Resumen ejecutivo
   - Reporte legal SUNAFIL
   - Análisis estadístico
   - Índices de frecuencia y severidad
   - Exportación Excel/PDF

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.8 o superior
- Cuenta de Supabase (gratuita)
- n8n instalado (local o cloud)
- ngrok (para exponer n8n localmente)

### Paso 1: Clonar o Descargar el Proyecto

```bash
cd "C:\Users\Jonathan Rojas\Sistema Integral de Seguridad y Salud en el Trabajo\sst-peru"
```

### Paso 2: Crear Entorno Virtual

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Paso 3: Instalar Dependencias

```powershell
pip install -r requirements.txt
```

### Paso 4: Configurar Variables de Entorno

1. Copiar el archivo de ejemplo:
```powershell
copy .env.example .env
```

2. Editar `.env` con tus credenciales:

```env
# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_anon_key
SUPABASE_SERVICE_KEY=tu_service_key

# n8n (con ngrok)
N8N_WEBHOOK_URL=https://joellen-prebronze-undespondently.ngrok-free.dev/webhook

# Aplicación
APP_NAME=Sistema SST Perú
APP_VERSION=1.0.0
ENVIRONMENT=development
```

### Paso 5: Configurar Base de Datos en Supabase

1. Crear un proyecto en [Supabase](https://supabase.com)
2. Ir al SQL Editor
3. Ejecutar el contenido de `database/schema.sql`
4. Ejecutar el contenido de `database/schema_part2.sql`
5. Crear los buckets de Storage:
   - `evidencias-sst`
   - `documentos-sst`
   - `capacitaciones-sst`
   - `incidentes-sst`

### Paso 6: Configurar n8n

#### Opción A: n8n Local con Docker

```powershell
docker run -it --rm --name n8n -p 5678:5678 -v C:\n8n-data:/home/node/.n8n n8nio/n8n
```

#### Opción B: n8n Cloud

Usar directamente [n8n.cloud](https://n8n.cloud)

#### Configurar ngrok (para n8n local)

```powershell
ngrok http 5678
```

Copiar la URL generada (ej: `https://joellen-prebronze-undespondently.ngrok-free.dev`) y actualizar el `.env`

#### Importar Workflows

1. Abrir n8n en `http://localhost:5678` o tu instancia cloud
2. Ir a Workflows → Import from File
3. Importar cada archivo JSON de la carpeta `n8n_workflows/`:
   - `incidente_registrado.json`
   - `alerta_epp_vencimiento.json`
   - `recordatorio_capacitacion.json`
   - `documento_revision.json`
4. Activar cada workflow
5. Configurar credenciales de Email y Slack en cada nodo

### Paso 7: Ejecutar la Aplicación

```powershell
streamlit run app/main.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

## 👤 Primer Uso

### Crear Usuario Administrador

1. En la pantalla de login, hacer clic en "Registrarse"
2. Completar el formulario:
   - Email: admin@empresa.com
   - Contraseña: (mínimo 6 caracteres)
   - Nombre completo
   - Cargo: Administrador SST
   - Área: Seguridad

3. Iniciar sesión con las credenciales creadas

4. **Importante**: Actualizar el rol a 'admin' directamente en Supabase:
   - Ir a Table Editor → usuarios
   - Buscar tu usuario
   - Cambiar el campo `rol` de 'usuario' a 'admin'

## 📁 Estructura del Proyecto

```
sst-peru/
├── app/
│   ├── main.py                 # Aplicación principal
│   ├── auth.py                 # Sistema de autenticación
│   ├── modules/                # Módulos funcionales
│   │   ├── riesgos.py
│   │   ├── inspecciones.py
│   │   ├── capacitaciones.py
│   │   ├── incidentes.py
│   │   ├── epp.py
│   │   ├── documental.py
│   │   └── reportes.py
│   ├── utils/                  # Utilidades
│   │   ├── supabase_client.py
│   │   └── n8n_client.py
│   └── config/                 # Configuración
│       └── settings.py
├── database/
│   ├── schema.sql              # Schema principal
│   └── schema_part2.sql        # Schema complementario
├── n8n_workflows/              # Workflows de automatización
│   ├── incidente_registrado.json
│   ├── alerta_epp_vencimiento.json
│   ├── recordatorio_capacitacion.json
│   └── documento_revision.json
├── requirements.txt            # Dependencias Python
├── .env.example               # Ejemplo de variables de entorno
├── .gitignore
└── README.md
```

## 🔧 Configuración Avanzada

### Personalizar Información de la Empresa

Editar `app/config/settings.py`:

```python
REPORTES_CONFIG = {
    "empresa": "Tu Empresa S.A.C.",
    "ruc": "20XXXXXXXXX",
    "direccion": "Tu dirección",
    "sector": "Tu sector",
    "actividad_economica": "Tu actividad"
}
```

### Configurar Email en n8n

En cada workflow que usa el nodo "Email Send":
1. Configurar SMTP credentials
2. Actualizar emails de destino según tu organización

### Configurar Slack en n8n

1. Crear un Slack App en tu workspace
2. Obtener el Webhook URL
3. Configurar en los nodos de Slack de cada workflow

## 📊 Uso del Sistema

### Flujo Típico de Trabajo

1. **Identificar Riesgos**
   - Ir a "Gestión de Riesgos"
   - Registrar nuevos riesgos con matriz 5x5
   - Asignar responsables

2. **Programar Inspecciones**
   - Crear checklists personalizados
   - Programar inspecciones por área
   - Registrar hallazgos

3. **Gestionar Capacitaciones**
   - Programar capacitaciones obligatorias
   - Registrar asistentes
   - Sistema envía recordatorios automáticos

4. **Reportar Incidentes**
   - Registro inmediato de incidentes
   - Sistema notifica automáticamente
   - Crear acciones correctivas
   - Seguimiento hasta cierre

5. **Controlar EPP**
   - Mantener catálogo actualizado
   - Asignar EPP a trabajadores
   - Sistema alerta vencimientos

6. **Generar Reportes**
   - Reportes ejecutivos
   - Reportes legales SUNAFIL
   - Análisis estadísticos
   - Exportar a Excel/PDF

## 🔐 Seguridad

- Autenticación con Supabase Auth
- Row Level Security (RLS) en todas las tablas
- Almacenamiento seguro de archivos
- Roles de usuario (admin, supervisor, usuario, auditor)

## 📱 Responsive Design

El sistema es completamente responsive y funciona en:
- 💻 Desktop
- 📱 Tablets
- 📱 Móviles

## 🆘 Solución de Problemas

### Error: "Las credenciales de Supabase no están configuradas"

- Verificar que el archivo `.env` existe
- Verificar que las variables SUPABASE_URL y SUPABASE_KEY están correctas

### Error: "No se pudo conectar con n8n"

- Verificar que n8n está ejecutándose
- Verificar que ngrok está activo
- Verificar la URL en N8N_WEBHOOK_URL

### Error al subir archivos

- Verificar que los buckets de Storage existen en Supabase
- Verificar permisos de los buckets (deben ser públicos para lectura)

### Error de autenticación

- Verificar que el usuario existe en la tabla `usuarios`
- Verificar que el campo `activo` es `true`
- Verificar que `auth_user_id` coincide con el ID de Supabase Auth

## 📚 Documentación Legal

Este sistema implementa los siguientes artículos de la Ley 29783:

- **Art. 26-28**: Identificación de Peligros y Evaluación de Riesgos (IPERC)
- **Art. 27, 35**: Capacitación en SST
- **Art. 28, 32**: Documentación del Sistema de Gestión
- **Art. 29, 61-72**: Comité de SST
- **Art. 42**: Auditorías
- **Art. 49, 101**: Exámenes Médicos Ocupacionales
- **Art. 82-88**: Investigación de Accidentes e Incidentes

## 🤝 Soporte

Para soporte técnico o consultas:
- Email: soporte@sistema-sst.com
- Documentación: [Wiki del proyecto]

## 📄 Licencia

Copyright © 2024 - Sistema SST Perú

## 🔄 Actualizaciones

### Versión 1.0.0 (2024)
- ✅ Sistema completo funcional
- ✅ 7 módulos implementados
- ✅ 4 workflows de n8n
- ✅ Integración completa Supabase
- ✅ Autenticación y seguridad
- ✅ Responsive design
- ✅ Exportación Excel/PDF

## 🎯 Roadmap

- [ ] App móvil nativa
- [ ] Integración con WhatsApp
- [ ] Firma digital de documentos
- [ ] Dashboard gerencial avanzado
- [ ] Integración con ERP
- [ ] API REST pública

---

**Desarrollado conforme a la Ley 29783 - Ley de Seguridad y Salud en el Trabajo del Perú** 🇵🇪
password qwerty