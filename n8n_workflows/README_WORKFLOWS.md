# 🔄 Workflows de n8n - Sistema SST Perú

## 📋 Descripción General

Este directorio contiene 4 workflows de n8n que automatizan procesos críticos del Sistema SST.

## 🔗 URLs de Webhooks

Todos los webhooks usan la URL base configurada en `.env`:
```
https://joellen-prebronze-undespondently.ngrok-free.dev/webhook
```

### Endpoints Disponibles

1. **Incidente Registrado**
   - URL: `/incidente-registrado`
   - Método: POST
   - Trigger: Manual desde la aplicación

2. **Alerta EPP Vencimiento**
   - URL: `/alerta-epp-vencimiento`
   - Método: POST
   - Trigger: Manual + Cron diario (8:00 AM)

3. **Recordatorio Capacitación**
   - URL: `/recordatorio-capacitacion`
   - Método: POST
   - Trigger: Manual + Cron semanal (Lunes 9:00 AM)

4. **Documento Revisión**
   - URL: `/documento-revision`
   - Método: POST
   - Trigger: Manual + Cron mensual (Día 1, 10:00 AM)

## 📥 Importación de Workflows

### Paso a Paso

1. **Abrir n8n**
   ```
   Local: http://localhost:5678
   Cloud: https://app.n8n.cloud
   ```

2. **Importar cada workflow**
   - Clic en "Workflows" (menú superior)
   - Clic en "Import from File"
   - Seleccionar archivo JSON
   - Clic en "Import"

3. **Activar workflow**
   - Abrir el workflow importado
   - Clic en el toggle "Active" (esquina superior derecha)

## ⚙️ Configuración de Nodos

### 1️⃣ Workflow: Incidente Registrado

#### Nodos a Configurar:

**A. Email Send**
- **Credentials**: Crear credencial SMTP
  - Host: smtp.gmail.com (o tu servidor)
  - Port: 587
  - User: tu-email@empresa.com
  - Password: tu-contraseña-app
- **From Email**: sst@empresa.com
- **To Email**: supervisor@empresa.com, seguridad@empresa.com

**B. Slack**
- **Credentials**: Crear credencial Slack
  - Webhook URL: Tu Slack Webhook URL
  - O usar OAuth2
- **Channel**: #seguridad-sst

**C. HTTP Request (Crear Acción Correctiva)**
- **URL**: Actualizar con tu URL de API si es diferente
- **Authentication**: Si requiere

#### Payload de Ejemplo:
```json
{
  "evento": "incidente_registrado",
  "incidente_id": "uuid",
  "codigo": "INC-20240101120000",
  "tipo": "Accidente Leve",
  "area": "Producción",
  "descripcion": "Descripción del incidente",
  "fecha_hora": "2024-01-01T12:00:00",
  "afectado_nombre": "Juan Pérez",
  "requiere_investigacion": true,
  "reportado_por": "uuid"
}
```

---

### 2️⃣ Workflow: Alerta EPP Vencimiento

#### Nodos a Configurar:

**A. Cron Trigger**
- **Expression**: `0 8 * * *` (Diario a las 8:00 AM)
- Puedes cambiar la hora según necesites

**B. HTTP Request (Obtener Vencimientos)**
- **URL**: `https://tu-url/api/epp/vencimientos`
- Debe retornar array de EPPs próximos a vencer

**C. Email Send**
- Configurar SMTP (igual que workflow anterior)
- **To Email**: `={{$json.email}}` (dinámico por trabajador)

**D. Slack**
- **Channel**: #almacen-epp

#### Payload de Ejemplo:
```json
{
  "evento": "alerta_epp_vencimiento",
  "asignacion_id": "uuid",
  "epp_nombre": "Casco de Seguridad",
  "epp_tipo": "Protección Cabeza",
  "usuario": "María López",
  "email": "maria.lopez@empresa.com",
  "area": "Mantenimiento",
  "fecha_vencimiento": "2024-02-15",
  "dias_restantes": 15
}
```

---

### 3️⃣ Workflow: Recordatorio Capacitación

#### Nodos a Configurar:

**A. Cron Trigger**
- **Expression**: `0 9 * * 1` (Lunes a las 9:00 AM)

**B. HTTP Request (Obtener Capacitaciones)**
- **URL**: `https://tu-url/api/capacitaciones/proximas`
- Debe retornar capacitaciones de los próximos 7 días

**C. Split Asistentes**
- Divide el array de asistentes para enviar email individual

**D. Email Send**
- **To Email**: `={{$json.email}}` (dinámico)

**E. Slack**
- **Channel**: #capacitaciones-sst

#### Payload de Ejemplo:
```json
{
  "evento": "recordatorio_capacitacion",
  "capacitacion_id": "uuid",
  "codigo": "CAP-20240101120000",
  "titulo": "Uso Correcto de EPP",
  "tipo": "Uso de EPP",
  "fecha_programada": "2024-01-15T14:00:00",
  "instructor": "Ing. Carlos Mendoza",
  "lugar": "Sala de Capacitación",
  "duracion_horas": 2,
  "modalidad": "Presencial",
  "asistentes": [
    {
      "nombre": "Juan Pérez",
      "email": "juan.perez@empresa.com"
    },
    {
      "nombre": "María López",
      "email": "maria.lopez@empresa.com"
    }
  ]
}
```

---

### 4️⃣ Workflow: Documento Revisión

#### Nodos a Configurar:

**A. Cron Trigger**
- **Expression**: `0 10 1 * *` (Día 1 de cada mes a las 10:00 AM)

**B. HTTP Request (Obtener Documentos)**
- **URL**: `https://tu-url/api/documentos/revision`
- Retorna documentos que requieren revisión en 30 días

**C. Email Send**
- **To Email**: calidad@empresa.com, sst@empresa.com

**D. Slack**
- **Channel**: #documentos-sst

#### Payload de Ejemplo:
```json
{
  "evento": "documento_revision",
  "documento_id": "uuid",
  "codigo": "DOC-001",
  "titulo": "Política de SST",
  "tipo": "Política SST",
  "version": "2.0",
  "fecha_revision": "2024-02-01",
  "dias_hasta_revision": 15,
  "elaborado_por": "Ing. Roberto Silva"
}
```

---

## 🧪 Testing de Workflows

### Método 1: Test Manual en n8n

1. Abrir workflow en n8n
2. Clic en "Execute Workflow" (botón play)
3. Usar datos de prueba en el nodo Webhook
4. Verificar ejecución de cada nodo

### Método 2: Test desde la Aplicación

1. Ejecutar acción en la app (ej: registrar incidente)
2. Verificar que se envió el webhook
3. Revisar ejecución en n8n → Executions
4. Verificar recepción de emails/mensajes Slack

### Método 3: Test con cURL

```bash
curl -X POST https://joellen-prebronze-undespondently.ngrok-free.dev/webhook/incidente-registrado \
  -H "Content-Type: application/json" \
  -d '{
    "evento": "incidente_registrado",
    "codigo": "TEST-001",
    "tipo": "Incidente",
    "area": "Pruebas",
    "descripcion": "Test de webhook"
  }'
```

---

## 🔧 Troubleshooting

### ❌ Webhook no responde

**Causas posibles:**
- n8n no está ejecutándose
- ngrok no está activo
- URL incorrecta en `.env`
- Workflow no está activado

**Solución:**
```bash
# Verificar n8n
curl http://localhost:5678

# Verificar ngrok
curl https://tu-url.ngrok-free.dev

# Revisar logs de n8n
docker logs n8n  # Si usas Docker
```

### ❌ Emails no se envían

**Causas posibles:**
- Credenciales SMTP incorrectas
- Puerto bloqueado por firewall
- Gmail requiere "App Password"

**Solución:**
- Usar App Password de Gmail
- Verificar configuración SMTP
- Probar con otro proveedor (SendGrid, Mailgun)

### ❌ Slack no notifica

**Causas posibles:**
- Webhook URL incorrecta
- Canal no existe
- Permisos insuficientes

**Solución:**
- Regenerar Webhook en Slack
- Verificar nombre del canal (incluir #)
- Verificar permisos del bot

---

## 📊 Monitoreo de Workflows

### En n8n

1. **Executions**: Ver historial de ejecuciones
2. **Logs**: Revisar logs de cada nodo
3. **Errors**: Filtrar solo ejecuciones con error

### Métricas Recomendadas

- Tasa de éxito de webhooks
- Tiempo promedio de ejecución
- Emails enviados vs fallidos
- Alertas procesadas diariamente

---

## 🔐 Seguridad

### Recomendaciones

1. **No exponer webhooks públicamente sin autenticación**
2. **Usar HTTPS siempre (ngrok lo provee)**
3. **Validar payloads en cada webhook**
4. **Rotar credenciales periódicamente**
5. **Limitar rate de requests**

### Agregar Autenticación

En el nodo Webhook, agregar:
- Header Auth
- Basic Auth
- Bearer Token

---

## 📝 Personalización

### Agregar Nuevo Workflow

1. Crear nuevo workflow en n8n
2. Agregar nodo Webhook
3. Configurar lógica de negocio
4. Exportar como JSON
5. Guardar en esta carpeta
6. Actualizar este README

### Modificar Plantillas de Email

En cada nodo "Email Send", editar el campo "Text":
- Usar variables: `={{$json.campo}}`
- Agregar formato HTML si necesitas
- Personalizar asunto y remitente

---

## 🎯 Próximos Workflows Sugeridos

- [ ] Alerta de acciones correctivas vencidas
- [ ] Recordatorio de exámenes médicos
- [ ] Notificación de auditorías programadas
- [ ] Reporte semanal de indicadores
- [ ] Alerta de documentos obsoletos
- [ ] Notificación de riesgos críticos nuevos

---

**¿Necesitas ayuda?** Revisa la [documentación oficial de n8n](https://docs.n8n.io)
