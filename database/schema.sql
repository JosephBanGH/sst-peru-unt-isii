-- =====================================================
-- SISTEMA INTEGRAL DE SEGURIDAD Y SALUD EN EL TRABAJO
-- Alineado a la Ley 29783 - Perú
-- =====================================================
--
-- INSTRUCCIONES:
-- 1. Ejecutar este archivo completo en Supabase SQL Editor
-- 2. El script incluye:
--    - Todas las tablas del sistema
--    - Vistas útiles para reportes
--    - Triggers para actualización automática
--    - Configuración para desarrollo (RLS desactivado)
--    - Configuración de storage
--    - Índices optimizados
-- 3. Para más instrucciones, ver SETUP.md
-- =====================================================

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- TABLA: usuarios
-- =====================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    nombre_completo VARCHAR(255) NOT NULL,
    cargo VARCHAR(150),
    area VARCHAR(150),
    rol VARCHAR(50) DEFAULT 'usuario' CHECK (rol IN ('admin', 'supervisor', 'usuario', 'auditor')),
    telefono VARCHAR(20),
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW(),
    auth_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE
);

-- =====================================================
-- TABLA: riesgos (Art. 26-28)
-- =====================================================
CREATE TABLE IF NOT EXISTS riesgos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    area VARCHAR(150) NOT NULL,
    proceso VARCHAR(150),
    tipo_riesgo VARCHAR(100) NOT NULL CHECK (tipo_riesgo IN (
        'Físico', 'Químico', 'Biológico', 'Ergonómico', 
        'Psicosocial', 'Mecánico', 'Eléctrico', 'Locativo'
    )),
    probabilidad INTEGER NOT NULL CHECK (probabilidad BETWEEN 1 AND 5),
    severidad INTEGER NOT NULL CHECK (severidad BETWEEN 1 AND 5),
    nivel_riesgo INTEGER GENERATED ALWAYS AS (probabilidad * severidad) STORED,
    clasificacion VARCHAR(20) GENERATED ALWAYS AS (
        CASE 
            WHEN (probabilidad * severidad) <= 4 THEN 'Bajo'
            WHEN (probabilidad * severidad) <= 12 THEN 'Medio'
            WHEN (probabilidad * severidad) <= 16 THEN 'Alto'
            ELSE 'Crítico'
        END
    ) STORED,
    medidas_control TEXT,
    responsable_id UUID REFERENCES usuarios(id),
    estado VARCHAR(50) DEFAULT 'identificado' CHECK (estado IN ('identificado', 'en_control', 'controlado', 'cerrado')),
    fecha_identificacion DATE DEFAULT CURRENT_DATE,
    fecha_revision DATE,
    creado_por UUID REFERENCES usuarios(id),
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- TABLA: checklists
-- =====================================================
CREATE TABLE IF NOT EXISTS checklists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(100) NOT NULL CHECK (tipo IN (
        'Seguridad General', 'EPP', 'Maquinaria', 'Instalaciones',
        'Orden y Limpieza', 'Ergonomía', 'Emergencias', 'Otro'
    )),
    items JSONB NOT NULL,
    activo BOOLEAN DEFAULT true,
    creado_por UUID REFERENCES usuarios(id),
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- TABLA: inspecciones
-- =====================================================
CREATE TABLE IF NOT EXISTS inspecciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo VARCHAR(50) UNIQUE NOT NULL,
    checklist_id UUID REFERENCES checklists(id),
    area VARCHAR(150) NOT NULL,
    fecha_programada DATE NOT NULL,
    fecha_realizada DATE,
    inspector_id UUID REFERENCES usuarios(id),
    estado VARCHAR(50) DEFAULT 'programada' CHECK (estado IN ('programada', 'en_proceso', 'completada', 'cancelada')),
    observaciones TEXT,
    puntaje_total DECIMAL(5,2),
    puntaje_obtenido DECIMAL(5,2),
    porcentaje_cumplimiento DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN puntaje_total > 0 THEN (puntaje_obtenido / puntaje_total) * 100 ELSE 0 END
    ) STORED,
    creado_por UUID REFERENCES usuarios(id),
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- TABLA: hallazgos
-- =====================================================
CREATE TABLE IF NOT EXISTS hallazgos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inspeccion_id UUID REFERENCES inspecciones(id) ON DELETE CASCADE,
    descripcion TEXT NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('Conforme', 'No Conforme Menor', 'No Conforme Mayor', 'Observación')),
    severidad VARCHAR(50) CHECK (severidad IN ('Baja', 'Media', 'Alta', 'Crítica')),
    ubicacion VARCHAR(255),
    evidencia_url TEXT,
    accion_correctiva TEXT,
    responsable_id UUID REFERENCES usuarios(id),
    fecha_limite DATE,
    estado VARCHAR(50) DEFAULT 'abierto' CHECK (estado IN ('abierto', 'en_proceso', 'cerrado', 'verificado')),
    fecha_cierre DATE,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- TABLA: capacitaciones (Art. 27, 35)
-- =====================================================
CREATE TABLE IF NOT EXISTS capacitaciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo VARCHAR(50) UNIQUE NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(100) NOT NULL CHECK (tipo IN (
        'Inducción', 'Específica del Puesto', 'Uso de EPP', 
        'Prevención de Riesgos', 'Primeros Auxilios', 'Evacuación',
        'Ergonomía', 'Manejo de Sustancias', 'Otro'
    )),
    modalidad VARCHAR(50) CHECK (modalidad IN ('Presencial', 'Virtual', 'Híbrida')),
    instructor VARCHAR(255),
    fecha_programada TIMESTAMP NOT NULL,
    fecha_realizada TIMESTAMP,
    duracion_horas DECIMAL(5,2),
    lugar VARCHAR(255),
    estado VARCHAR(50) DEFAULT 'programada' CHECK (estado IN ('programada', 'realizada', 'cancelada', 'reprogramada')),
    material_url TEXT,
    evidencia_url TEXT,
    evaluacion_realizada BOOLEAN DEFAULT false,
    puntaje_promedio DECIMAL(5,2),
    observaciones TEXT,
    creado_por UUID REFERENCES usuarios(id),
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- TABLA: asistentes_capacitacion
-- =====================================================
CREATE TABLE IF NOT EXISTS asistentes_capacitacion (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    capacitacion_id UUID REFERENCES capacitaciones(id) ON DELETE CASCADE,
    usuario_id UUID REFERENCES usuarios(id),
    asistio BOOLEAN DEFAULT false,
    puntaje_evaluacion DECIMAL(5,2),
    certificado_url TEXT,
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- TABLA: incidentes (Art. 82-88)
-- =====================================================
CREATE TABLE IF NOT EXISTS incidentes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo VARCHAR(50) UNIQUE NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('Incidente', 'Accidente Leve', 'Accidente Incapacitante', 'Accidente Mortal', 'Enfermedad Ocupacional')),
    fecha_hora TIMESTAMP NOT NULL,
    area VARCHAR(150) NOT NULL,
    ubicacion_especifica VARCHAR(255),
    descripcion TEXT NOT NULL,
    afectado_nombre VARCHAR(255),
    afectado_dni VARCHAR(20),
    afectado_cargo VARCHAR(150),
    parte_cuerpo_afectada VARCHAR(150),
    naturaleza_lesion VARCHAR(150),
    dias_descanso_medico INTEGER DEFAULT 0,
    testigos TEXT,
    causas_inmediatas TEXT,
    causas_basicas TEXT,
    analisis_causa_raiz TEXT,
    medidas_inmediatas TEXT,
    requiere_investigacion BOOLEAN DEFAULT false,
    investigador_id UUID REFERENCES usuarios(id),
    fecha_investigacion DATE,
    evidencias_url TEXT[],
    estado VARCHAR(50) DEFAULT 'reportado' CHECK (estado IN ('reportado', 'en_investigacion', 'investigado', 'cerrado')),
    notificado_sunafil BOOLEAN DEFAULT false,
    fecha_notificacion_sunafil DATE,
    reportado_por UUID REFERENCES usuarios(id),
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- TABLA: acciones_correctivas
-- =====================================================
CREATE TABLE IF NOT EXISTS acciones_correctivas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incidente_id UUID REFERENCES incidentes(id) ON DELETE CASCADE,
    descripcion TEXT NOT NULL,
    tipo VARCHAR(50) CHECK (tipo IN ('Correctiva', 'Preventiva', 'Mejora')),
    responsable_id UUID REFERENCES usuarios(id),
    fecha_compromiso DATE NOT NULL,
    fecha_implementacion DATE,
    estado VARCHAR(50) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'en_proceso', 'completada', 'verificada', 'vencida')),
    evidencia_implementacion_url TEXT,
    verificado_por UUID REFERENCES usuarios(id),
    fecha_verificacion DATE,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- TABLA: epp_catalogo
-- =====================================================
CREATE TABLE IF NOT EXISTS epp_catalogo (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(100) NOT NULL CHECK (tipo IN (
        'Protección Cabeza', 'Protección Ojos/Cara', 'Protección Auditiva',
        'Protección Respiratoria', 'Protección Manos', 'Protección Pies',
        'Protección Cuerpo', 'Protección Caídas', 'Otro'
    )),
    marca VARCHAR(100),
    modelo VARCHAR(100),
    certificacion VARCHAR(150),
    vida_util_meses INTEGER,
    stock_minimo INTEGER DEFAULT 0,
    stock_actual INTEGER DEFAULT 0,
    costo_unitario DECIMAL(10,2),
    proveedor VARCHAR(255),
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- TABLA: epp_asignaciones
-- =====================================================
CREATE TABLE IF NOT EXISTS epp_asignaciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    epp_id UUID REFERENCES epp_catalogo(id),
    usuario_id UUID REFERENCES usuarios(id),
    cantidad INTEGER NOT NULL DEFAULT 1,
    fecha_asignacion DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_vencimiento DATE NOT NULL,
    estado VARCHAR(50) DEFAULT 'activo' CHECK (estado IN ('activo', 'vencido', 'reemplazado', 'devuelto')),
    observaciones TEXT,
    entregado_por UUID REFERENCES usuarios(id),
    acta_entrega_url TEXT,
    fecha_devolucion DATE,
    motivo_devolucion TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- TABLA: documentos (Art. 28, 32)
-- =====================================================
CREATE TABLE IF NOT EXISTS documentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo VARCHAR(50) UNIQUE NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    tipo VARCHAR(100) NOT NULL CHECK (tipo IN (
        'Política SST', 'Procedimiento', 'Instructivo', 'Registro',
        'Plan', 'Programa', 'Reglamento', 'Manual', 'Formato', 'Otro'
    )),
    categoria VARCHAR(100),
    descripcion TEXT,
    version VARCHAR(20) NOT NULL DEFAULT '1.0',
    archivo_url TEXT NOT NULL,
    fecha_emision DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_vigencia DATE,
    fecha_revision DATE,
    estado VARCHAR(50) DEFAULT 'vigente' CHECK (estado IN ('borrador', 'vigente', 'obsoleto', 'archivado')),
    elaborado_por UUID REFERENCES usuarios(id),
    revisado_por UUID REFERENCES usuarios(id),
    aprobado_por UUID REFERENCES usuarios(id),
    fecha_aprobacion DATE,
    requiere_revision BOOLEAN DEFAULT false,
    dias_antes_alerta INTEGER DEFAULT 30,
    observaciones TEXT,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- TABLA: historial_versiones
-- =====================================================
CREATE TABLE IF NOT EXISTS historial_versiones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    documento_id UUID REFERENCES documentos(id) ON DELETE CASCADE,
    version VARCHAR(20) NOT NULL,
    archivo_url TEXT NOT NULL,
    cambios_realizados TEXT,
    modificado_por UUID REFERENCES usuarios(id),
    fecha_modificacion TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- VISTAS ÚTILES
-- =====================================================

CREATE OR REPLACE VIEW v_epp_vencimientos AS
SELECT 
    ea.id,
    ea.fecha_vencimiento,
    ea.fecha_vencimiento - CURRENT_DATE as dias_restantes,
    ec.nombre as epp_nombre,
    ec.tipo as epp_tipo,
    u.nombre_completo as usuario,
    u.email,
    u.area,
    ea.estado
FROM epp_asignaciones ea
JOIN epp_catalogo ec ON ea.epp_id = ec.id
JOIN usuarios u ON ea.usuario_id = u.id
WHERE ea.estado = 'activo' 
  AND ea.fecha_vencimiento <= CURRENT_DATE + INTERVAL '30 days'
ORDER BY ea.fecha_vencimiento;

CREATE OR REPLACE VIEW v_riesgos_criticos AS
SELECT 
    r.id,
    r.codigo,
    r.descripcion,
    r.area,
    r.tipo_riesgo,
    r.probabilidad,
    r.severidad,
    r.nivel_riesgo,
    r.clasificacion,
    r.estado,
    u.nombre_completo as responsable,
    r.fecha_identificacion
FROM riesgos r
LEFT JOIN usuarios u ON r.responsable_id = u.id
WHERE r.clasificacion IN ('Alto', 'Crítico')
  AND r.estado NOT IN ('cerrado')
ORDER BY r.nivel_riesgo DESC;

CREATE OR REPLACE VIEW v_capacitaciones_proximas AS
SELECT 
    c.id,
    c.codigo,
    c.titulo,
    c.tipo,
    c.fecha_programada,
    c.duracion_horas,
    c.instructor,
    c.estado,
    COUNT(ac.id) as total_inscritos
FROM capacitaciones c
LEFT JOIN asistentes_capacitacion ac ON c.id = ac.capacitacion_id
WHERE c.estado = 'programada'
  AND c.fecha_programada >= NOW()
  AND c.fecha_programada <= NOW() + INTERVAL '30 days'
GROUP BY c.id, c.codigo, c.titulo, c.tipo, c.fecha_programada, c.duracion_horas, c.instructor, c.estado
ORDER BY c.fecha_programada;

-- =====================================================
-- TRIGGERS
-- =====================================================

CREATE OR REPLACE FUNCTION actualizar_fecha_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_usuarios
    BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_actualizacion();

CREATE TRIGGER trigger_actualizar_riesgos
    BEFORE UPDATE ON riesgos
    FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_actualizacion();

CREATE TRIGGER trigger_actualizar_capacitaciones
    BEFORE UPDATE ON capacitaciones
    FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_actualizacion();

CREATE TRIGGER trigger_actualizar_incidentes
    BEFORE UPDATE ON incidentes
    FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_actualizacion();

CREATE TRIGGER trigger_actualizar_documentos
    BEFORE UPDATE ON documentos
    FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_actualizacion();

CREATE TRIGGER trigger_actualizar_epp_catalogo
    BEFORE UPDATE ON epp_catalogo
    FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_actualizacion();

-- =====================================================
-- CONFIGURACIÓN PARA DESARROLLO
-- =====================================================
-- NOTA: Para desarrollo se recomienda desactivar RLS
-- En producción, configurar políticas adecuadas

-- Desactivar RLS en todas las tablas (SOLO DESARROLLO)
ALTER TABLE usuarios DISABLE ROW LEVEL SECURITY;
ALTER TABLE riesgos DISABLE ROW LEVEL SECURITY;
ALTER TABLE capacitaciones DISABLE ROW LEVEL SECURITY;
ALTER TABLE asistentes_capacitacion DISABLE ROW LEVEL SECURITY;
ALTER TABLE incidentes DISABLE ROW LEVEL SECURITY;
ALTER TABLE acciones_correctivas DISABLE ROW LEVEL SECURITY;
ALTER TABLE epp_catalogo DISABLE ROW LEVEL SECURITY;
ALTER TABLE epp_asignaciones DISABLE ROW LEVEL SECURITY;
ALTER TABLE documentos DISABLE ROW LEVEL SECURITY;
ALTER TABLE historial_versiones DISABLE ROW LEVEL SECURITY;
ALTER TABLE checklists DISABLE ROW LEVEL SECURITY;
ALTER TABLE inspecciones DISABLE ROW LEVEL SECURITY;
ALTER TABLE hallazgos DISABLE ROW LEVEL SECURITY;

-- Configurar buckets de storage como públicos (SOLO DESARROLLO)
-- Ejecutar desde el panel de Supabase o usar SQL:
UPDATE storage.buckets 
SET public = true 
WHERE name IN ('documentos', 'incidentes', 'capacitaciones', 'inspecciones');

-- Políticas para storage (permitir todas las operaciones)
CREATE POLICY IF NOT EXISTS "Allow all inserts" 
ON storage.objects 
FOR INSERT 
TO public
WITH CHECK (true);

CREATE POLICY IF NOT EXISTS "Allow all selects" 
ON storage.objects 
FOR SELECT 
TO public
USING (true);

CREATE POLICY IF NOT EXISTS "Allow all updates" 
ON storage.objects 
FOR UPDATE 
TO public
USING (true)
WITH CHECK (true);

CREATE POLICY IF NOT EXISTS "Allow all deletes" 
ON storage.objects 
FOR DELETE 
TO public
USING (true);

-- =====================================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_riesgos_area ON riesgos(area);
CREATE INDEX IF NOT EXISTS idx_riesgos_clasificacion ON riesgos(clasificacion);
CREATE INDEX IF NOT EXISTS idx_riesgos_estado ON riesgos(estado);

CREATE INDEX IF NOT EXISTS idx_incidentes_tipo ON incidentes(tipo);
CREATE INDEX IF NOT EXISTS idx_incidentes_area ON incidentes(area);
CREATE INDEX IF NOT EXISTS idx_incidentes_fecha ON incidentes(fecha_hora);
CREATE INDEX IF NOT EXISTS idx_incidentes_estado ON incidentes(estado);

CREATE INDEX IF NOT EXISTS idx_capacitaciones_fecha ON capacitaciones(fecha_programada);
CREATE INDEX IF NOT EXISTS idx_capacitaciones_estado ON capacitaciones(estado);

CREATE INDEX IF NOT EXISTS idx_epp_asignaciones_vencimiento ON epp_asignaciones(fecha_vencimiento);
CREATE INDEX IF NOT EXISTS idx_epp_asignaciones_estado ON epp_asignaciones(estado);

CREATE INDEX IF NOT EXISTS idx_documentos_tipo ON documentos(tipo);
CREATE INDEX IF NOT EXISTS idx_documentos_estado ON documentos(estado);

-- =====================================================
-- FIN DEL SCHEMA
-- =====================================================
-- Para instrucciones de uso, consulta README.md
-- Para workflows de n8n, consulta n8n_workflows/README_WORKFLOWS.md
