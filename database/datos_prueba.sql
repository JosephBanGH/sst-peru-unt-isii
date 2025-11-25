-- =====================================================
-- DATOS DE PRUEBA PARA EL SISTEMA SST
-- Ejecutar después de schema.sql y schema_part2.sql
-- =====================================================

-- NOTA: Estos son datos de ejemplo para testing
-- NO usar en producción con datos reales

-- =====================================================
-- USUARIOS DE PRUEBA
-- =====================================================
-- Los usuarios se crean desde la aplicación con Supabase Auth
-- Aquí solo insertamos datos complementarios si ya existen en auth.users

-- =====================================================
-- RIESGOS DE EJEMPLO
-- =====================================================

INSERT INTO riesgos (codigo, descripcion, area, proceso, tipo_riesgo, probabilidad, severidad, medidas_control, estado, fecha_identificacion) VALUES
('RIESGO-001', 'Caída de altura en trabajos de mantenimiento en techos', 'Mantenimiento', 'Mantenimiento de Techos', 'Mecánico', 4, 5, 'Uso obligatorio de arnés de seguridad, líneas de vida, inspección previa del área', 'identificado', CURRENT_DATE),
('RIESGO-002', 'Exposición a ruido en área de producción', 'Producción', 'Operación de Maquinaria', 'Físico', 5, 3, 'Uso de protectores auditivos, rotación de personal, mantenimiento preventivo de equipos', 'en_control', CURRENT_DATE - INTERVAL '10 days'),
('RIESGO-003', 'Contacto con sustancias químicas corrosivas', 'Almacén', 'Manipulación de Químicos', 'Químico', 3, 4, 'Uso de guantes químicos, lentes de seguridad, delantal, capacitación en MSDS', 'controlado', CURRENT_DATE - INTERVAL '20 days'),
('RIESGO-004', 'Sobreesfuerzo en levantamiento manual de cargas', 'Logística', 'Carga y Descarga', 'Ergonómico', 4, 3, 'Capacitación en técnicas de levantamiento, uso de ayudas mecánicas, límite de peso', 'identificado', CURRENT_DATE - INTERVAL '5 days'),
('RIESGO-005', 'Estrés laboral por alta carga de trabajo', 'Administración', 'Gestión Administrativa', 'Psicosocial', 3, 2, 'Pausas activas, redistribución de carga laboral, apoyo psicológico', 'en_control', CURRENT_DATE - INTERVAL '15 days');

-- =====================================================
-- CHECKLISTS DE EJEMPLO
-- =====================================================

INSERT INTO checklists (nombre, descripcion, tipo, items, activo) VALUES
('Inspección de Seguridad General', 'Checklist para inspección general de seguridad en áreas de trabajo', 'Seguridad General', 
'[
  {"pregunta": "¿Las salidas de emergencia están señalizadas y libres de obstáculos?", "tipo_respuesta": "si_no", "es_critico": true},
  {"pregunta": "¿Los extintores están en su lugar y con carga vigente?", "tipo_respuesta": "si_no", "es_critico": true},
  {"pregunta": "¿El área de trabajo está limpia y ordenada?", "tipo_respuesta": "si_no", "es_critico": false},
  {"pregunta": "¿Las herramientas están en buen estado?", "tipo_respuesta": "si_no", "es_critico": false},
  {"pregunta": "¿Se observa uso correcto de EPP?", "tipo_respuesta": "si_no", "es_critico": true}
]'::jsonb, true),

('Inspección de EPP', 'Verificación del estado y uso de equipos de protección personal', 'EPP',
'[
  {"pregunta": "¿El casco está en buen estado sin grietas?", "tipo_respuesta": "si_no", "es_critico": true},
  {"pregunta": "¿Los lentes de seguridad están limpios y sin rayones?", "tipo_respuesta": "si_no", "es_critico": true},
  {"pregunta": "¿Los guantes son apropiados para la tarea?", "tipo_respuesta": "si_no", "es_critico": true},
  {"pregunta": "¿El calzado de seguridad tiene puntera de acero?", "tipo_respuesta": "si_no", "es_critico": true}
]'::jsonb, true),

('Inspección de Orden y Limpieza', 'Evaluación de orden y limpieza en áreas de trabajo', 'Orden y Limpieza',
'[
  {"pregunta": "¿Los pasillos están libres de obstáculos?", "tipo_respuesta": "si_no", "es_critico": false},
  {"pregunta": "¿Los residuos están en contenedores apropiados?", "tipo_respuesta": "si_no", "es_critico": false},
  {"pregunta": "¿Las áreas de almacenamiento están organizadas?", "tipo_respuesta": "si_no", "es_critico": false},
  {"pregunta": "¿Los derrames están limpios?", "tipo_respuesta": "si_no", "es_critico": true}
]'::jsonb, true);

-- =====================================================
-- CATÁLOGO DE EPP
-- =====================================================

INSERT INTO epp_catalogo (codigo, nombre, descripcion, tipo, marca, modelo, certificacion, vida_util_meses, stock_minimo, stock_actual, costo_unitario, proveedor, activo) VALUES
('EPP-001', 'Casco de Seguridad Blanco', 'Casco de seguridad industrial clase E', 'Protección Cabeza', '3M', 'H-700', 'ANSI Z89.1', 24, 20, 45, 35.00, 'Distribuidora SST SAC', true),
('EPP-002', 'Lentes de Seguridad Claros', 'Lentes de policarbonato antiempañante', 'Protección Ojos/Cara', 'Steelpro', 'LUNA', 'ANSI Z87.1', 12, 30, 60, 15.00, 'Distribuidora SST SAC', true),
('EPP-003', 'Guantes de Cuero', 'Guantes de cuero para trabajos pesados', 'Protección Manos', 'Promart', 'GL-500', 'EN 388', 6, 50, 80, 12.00, 'Ferretería Industrial', true),
('EPP-004', 'Botas de Seguridad Punta de Acero', 'Botas dieléctricas con puntera de acero', 'Protección Pies', 'Caterpillar', 'CAT-2000', 'ASTM F2413', 18, 15, 25, 180.00, 'Calzado Industrial SAC', true),
('EPP-005', 'Protector Auditivo Tipo Copa', 'Protector auditivo de reducción 30dB', 'Protección Auditiva', '3M', 'PELTOR X5A', 'ANSI S3.19', 36, 25, 40, 85.00, 'Distribuidora SST SAC', true),
('EPP-006', 'Respirador Media Cara', 'Respirador reutilizable para vapores orgánicos', 'Protección Respiratoria', '3M', '6200', 'NIOSH', 12, 10, 15, 120.00, 'Distribuidora SST SAC', true),
('EPP-007', 'Arnés de Seguridad', 'Arnés de cuerpo completo para trabajos en altura', 'Protección Caídas', 'Miller', 'E650', 'ANSI Z359.11', 60, 8, 12, 350.00, 'Equipos de Altura SAC', true),
('EPP-008', 'Chaleco Reflectivo', 'Chaleco alta visibilidad clase 2', 'Protección Cuerpo', 'Safetop', 'CH-100', 'ANSI 107', 12, 40, 70, 25.00, 'Uniformes Industriales', true);

-- =====================================================
-- CAPACITACIONES DE EJEMPLO
-- =====================================================

INSERT INTO capacitaciones (codigo, titulo, descripcion, tipo, modalidad, instructor, fecha_programada, duracion_horas, lugar, estado) VALUES
('CAP-001', 'Inducción en Seguridad y Salud en el Trabajo', 'Capacitación obligatoria para personal nuevo sobre políticas y procedimientos de SST', 'Inducción', 'Presencial', 'Ing. Carlos Mendoza', CURRENT_TIMESTAMP + INTERVAL '7 days', 4, 'Sala de Capacitación - Planta', 'programada'),
('CAP-002', 'Uso Correcto de EPP', 'Entrenamiento práctico sobre selección, uso y mantenimiento de equipos de protección personal', 'Uso de EPP', 'Presencial', 'Tec. María Rodríguez', CURRENT_TIMESTAMP + INTERVAL '14 days', 2, 'Área de Producción', 'programada'),
('CAP-003', 'Primeros Auxilios Básicos', 'Curso de primeros auxilios y RCP para brigadistas', 'Primeros Auxilios', 'Híbrida', 'Dr. Juan Pérez', CURRENT_TIMESTAMP + INTERVAL '21 days', 8, 'Auditorio Principal', 'programada'),
('CAP-004', 'Prevención de Riesgos Ergonómicos', 'Técnicas de levantamiento seguro y prevención de lesiones musculoesqueléticas', 'Ergonomía', 'Virtual', 'Lic. Ana Torres', CURRENT_TIMESTAMP - INTERVAL '10 days', 3, 'Plataforma Zoom', 'realizada'),
('CAP-005', 'Plan de Evacuación y Emergencias', 'Procedimientos de evacuación y respuesta ante emergencias', 'Evacuación', 'Presencial', 'Ing. Roberto Silva', CURRENT_TIMESTAMP - INTERVAL '5 days', 2, 'Instalaciones de la Empresa', 'realizada');

-- =====================================================
-- DOCUMENTOS DE EJEMPLO
-- =====================================================

INSERT INTO documentos (codigo, titulo, tipo, categoria, descripcion, version, archivo_url, fecha_emision, estado, requiere_revision, dias_antes_alerta) VALUES
('DOC-001', 'Política de Seguridad y Salud en el Trabajo', 'Política SST', 'Política', 'Política general de SST de la organización', '2.0', 'https://ejemplo.com/politica-sst.pdf', CURRENT_DATE - INTERVAL '180 days', 'vigente', true, 30),
('DOC-002', 'Procedimiento de Investigación de Accidentes', 'Procedimiento', 'Incidentes', 'Procedimiento para investigación de accidentes e incidentes', '1.5', 'https://ejemplo.com/proc-investigacion.pdf', CURRENT_DATE - INTERVAL '90 days', 'vigente', true, 30),
('DOC-003', 'Matriz IPERC - Área de Producción', 'Registro', 'IPERC', 'Identificación de peligros y evaluación de riesgos en producción', '3.0', 'https://ejemplo.com/iperc-produccion.xlsx', CURRENT_DATE - INTERVAL '60 days', 'vigente', true, 30),
('DOC-004', 'Reglamento Interno de Seguridad y Salud', 'Reglamento', 'Normativa', 'Reglamento interno de SST según Ley 29783', '1.0', 'https://ejemplo.com/reglamento-sst.pdf', CURRENT_DATE - INTERVAL '365 days', 'vigente', true, 60),
('DOC-005', 'Plan Anual de Seguridad y Salud 2024', 'Plan', 'Planificación', 'Plan anual de actividades de SST', '1.0', 'https://ejemplo.com/plan-anual-2024.pdf', CURRENT_DATE - INTERVAL '30 days', 'vigente', true, 30);

-- =====================================================
-- NOTAS IMPORTANTES
-- =====================================================

-- 1. Los IDs de usuario (creado_por, responsable_id, etc.) deben actualizarse
--    con los IDs reales de los usuarios creados en tu sistema

-- 2. Las URLs de archivos son ejemplos. En producción, estos serán URLs
--    de Supabase Storage

-- 3. Para insertar incidentes de prueba, primero necesitas usuarios registrados

-- 4. Las asignaciones de EPP requieren usuarios existentes

-- 5. Ajusta las fechas según tus necesidades de testing

-- =====================================================
-- CONSULTAS ÚTILES PARA VERIFICAR DATOS
-- =====================================================

-- Ver resumen de riesgos por clasificación
-- SELECT clasificacion, COUNT(*) as total FROM riesgos GROUP BY clasificacion;

-- Ver EPP con stock bajo
-- SELECT nombre, stock_actual, stock_minimo FROM epp_catalogo WHERE stock_actual <= stock_minimo;

-- Ver capacitaciones próximas
-- SELECT codigo, titulo, fecha_programada, estado FROM capacitaciones WHERE fecha_programada >= CURRENT_DATE ORDER BY fecha_programada;

-- Ver documentos próximos a revisión
-- SELECT codigo, titulo, fecha_revision FROM documentos WHERE requiere_revision = true AND fecha_revision <= CURRENT_DATE + INTERVAL '30 days';
