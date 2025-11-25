# 🚀 Guía de Instalación - Sistema SST Perú

## 📋 Requisitos Previos

- Python 3.10 o superior
- Cuenta en Supabase (https://supabase.com)
- Cuenta en n8n Cloud o instalación local de n8n (opcional para notificaciones)

---

## 1️⃣ Configuración de Supabase

### A. Crear Proyecto en Supabase

1. Ir a https://supabase.com y crear un nuevo proyecto
2. Anotar las siguientes credenciales:
   - `Project URL`
   - `anon/public key`
   - `service_role key` (desde Project Settings → API)

### B. Crear Base de Datos

1. En Supabase, ir a **SQL Editor**
2. Abrir y ejecutar: `database/schema.sql`
   - Este archivo contiene:
     - ✅ Todas las tablas del sistema
     - ✅ Vistas útiles
     - ✅ Triggers automáticos
     - ✅ Índices optimizados
     - ✅ Configuración para desarrollo (RLS desactivado)

### C. Configurar Storage

1. Ir a **Storage** en Supabase
2. Crear los siguientes buckets:
   - `documentos`
   - `incidentes`
   - `capacitaciones`
   - `inspecciones`

**Nota:** El script SQL ya configura los buckets como públicos para desarrollo.

### D. Crear Usuario Admin

1. Ir a **Authentication** → **Users**
2. Clic en **Add user**
3. Configurar:
   - Email: `admin@sst.com` (o el que prefieras)
   - Password: `Admin123456` (o el que prefieras)
   - Confirmar email automáticamente

4. Ejecutar en SQL Editor:
```sql
-- Insertar usuario en tabla usuarios
INSERT INTO usuarios (
    auth_user_id, 
    email, 
    nombre_completo, 
    cargo, 
    area, 
    rol
)
VALUES (
    'PEGAR_AQUI_EL_UUID_DEL_AUTH_USER',
    'admin@sst.com',
    'Administrador Sistema',
    'Administrador SST',
    'Seguridad y Salud',
    'admin'
);
```

**Alternativa:** Usar el script `crear_usuario_completo.py` (requiere configuración previa del .env)

---

## 2️⃣ Configuración del Proyecto Python

### A. Clonar/Copiar el Proyecto

```bash
cd "C:\ruta\donde\quieras\el\proyecto"
```

### B. Crear Entorno Virtual

```bash
python -m venv venv
```

### C. Activar Entorno Virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### D. Instalar Dependencias

```bash
pip install -r requirements.txt
```

---

## 3️⃣ Configuración de Variables de Entorno

### Copiar .env.example a .env

```bash
copy .env.example .env
```

### Editar .env con tus credenciales

```env
# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_anon_key_aqui
SUPABASE_SERVICE_KEY=tu_service_role_key_aqui

# n8n (opcional)
N8N_WEBHOOK_URL=https://tu-instancia-n8n.app.n8n.cloud/webhook
N8N_WEBHOOK_INCIDENTE=incidente-registrado
N8N_WEBHOOK_RIESGO_CRITICO=riesgo-critico
N8N_API_KEY=tu_n8n_api_key (opcional)

# Configuración de la Empresa
EMPRESA_NOMBRE=Tu Empresa S.A.C.
EMPRESA_RUC=20123456789
EMPRESA_DIRECCION=Av. Ejemplo 123, Lima
EMPRESA_SECTOR=Industrial
EMPRESA_ACTIVIDAD=Manufactura
```

---

## 4️⃣ Ejecutar la Aplicación

### Opción 1: Usar script de inicio (Windows)

```bash
.\ejecutar.bat
```

### Opción 2: Comando directo

```bash
streamlit run app/main.py
```

La aplicación se abrirá en: http://localhost:8501

---

## 5️⃣ Primer Login

1. Abrir http://localhost:8501
2. Iniciar sesión con:
   - Email: `admin@sst.com` (o el que configuraste)
   - Password: `Admin123456` (o el que configuraste)

---

## 6️⃣ Configuración de n8n (Opcional)

### A. Importar Workflows

1. Ir a tu instancia de n8n
2. Importar los archivos de `n8n_workflows/`:
   - `incidente_registrado.json`
   - `riesgo_critico_identificado.json`

### B. Configurar Credenciales

En cada workflow, configurar:
- **Email (SMTP):** Para envío de notificaciones por correo
- **Slack:** Webhook URL para canal de Slack (opcional)
- **Supabase:** Credenciales para crear acciones correctivas

### C. Activar Workflows

1. Activar ambos workflows en n8n
2. Copiar las URLs de webhook generadas
3. Actualizar `.env` con las URLs correctas

---

## 7️⃣ Verificación Final

### Checklist de Verificación

- [ ] Base de datos creada en Supabase
- [ ] Buckets de storage configurados
- [ ] Usuario admin creado
- [ ] Variables de entorno configuradas
- [ ] Aplicación ejecutándose correctamente
- [ ] Login funcional
- [ ] Módulos principales funcionando:
  - [ ] Gestión de Riesgos
  - [ ] Incidentes y Accidentes
  - [ ] Capacitaciones
  - [ ] Gestión de EPP
  - [ ] Gestión Documental
  - [ ] Reportes (Excel y PDF)

---

## 📚 Estructura del Proyecto

```
sst-peru/
├── app/
│   ├── main.py              # Aplicación principal
│   ├── auth.py              # Autenticación
│   ├── config/
│   │   └── settings.py      # Configuración general
│   ├── modules/             # Módulos funcionales
│   │   ├── riesgos.py
│   │   ├── incidentes.py
│   │   ├── capacitaciones.py
│   │   ├── epp.py
│   │   ├── documental.py
│   │   ├── inspecciones.py
│   │   └── reportes.py
│   └── utils/               # Utilidades
│       ├── supabase_client.py
│       └── n8n_client.py
├── database/
│   ├── schema.sql           # ⭐ Schema completo
│   └── datos_prueba.sql     # Datos de ejemplo
├── n8n_workflows/           # Workflows para notificaciones
│   └── README_WORKFLOWS.md  # Instrucciones n8n
├── .env                     # Variables de entorno (no incluido)
├── .env.example             # Plantilla de variables
├── requirements.txt         # Dependencias Python
├── README.md                # Documentación principal
└── SETUP.md                 # ⭐ Esta guía
```

---

## 🔧 Scripts Útiles

### Reiniciar Aplicación Completa

```bash
.\reiniciar_completo.bat
```

Este script:
- Limpia cache de Python
- Limpia cache de Streamlit
- Reinicia la aplicación

### Crear Usuario Completo

```bash
python crear_usuario_completo.py
```

Crea un usuario tanto en Supabase Auth como en la tabla usuarios.

---

## ❓ Solución de Problemas

### Error: "Row Level Security policy violation"

**Causa:** RLS no está desactivado en las tablas.

**Solución:** Ejecutar en SQL Editor:
```sql
ALTER TABLE nombre_tabla DISABLE ROW LEVEL SECURITY;
```

O ejecutar completo: `database/schema.sql`

### Error: "Storage bucket not found"

**Causa:** Buckets de storage no creados.

**Solución:** Crear manualmente desde Supabase Dashboard → Storage.

### Error: "Error al subir archivo: 403"

**Causa:** Buckets no son públicos o faltan políticas.

**Solución:** Ejecutar desde la sección de storage del `schema.sql`.

### Error: "Module not found"

**Causa:** Dependencias no instaladas.

**Solución:**
```bash
pip install -r requirements.txt
```

---

## 📞 Soporte

Para dudas o problemas:
1. Revisar `README.md` para documentación general
2. Revisar `n8n_workflows/README_WORKFLOWS.md` para configuración de notificaciones
3. Verificar logs en la consola de Streamlit

---

## 🔒 Notas de Seguridad

⚠️ **IMPORTANTE:** La configuración actual está optimizada para **DESARROLLO**.

**Para PRODUCCIÓN:**
1. Activar RLS en todas las tablas
2. Configurar políticas específicas por rol
3. Hacer buckets privados
4. Usar variables de entorno seguras
5. Configurar autenticación robusta

---

## ✅ ¡Listo!

Tu Sistema Integral de Seguridad y Salud en el Trabajo está configurado y listo para usar. 🎉
