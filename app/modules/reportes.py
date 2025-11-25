"""
Módulo de Reportes y Análisis Estadístico
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.supabase_client import get_supabase_client
from config.settings import REPORTES_CONFIG


def reporte_ejecutivo():
    """Reporte ejecutivo del sistema SST"""
    st.subheader("📊 Resumen Ejecutivo")
    
    supabase = get_supabase_client()
    
    # Obtener datos
    riesgos = supabase.listar_riesgos()
    incidentes = supabase.listar_incidentes()
    capacitaciones = supabase.listar_capacitaciones()
    inspecciones = supabase.listar_inspecciones()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Riesgos", len(riesgos))
        riesgos_criticos = len([r for r in riesgos if r.get("clasificacion") in ["Alto", "Crítico"]])
        st.metric("Riesgos Críticos", riesgos_criticos)
    
    with col2:
        st.metric("Total Incidentes", len(incidentes))
        accidentes = len([i for i in incidentes if "Accidente" in i.get("tipo", "")])
        st.metric("Accidentes", accidentes)
    
    with col3:
        st.metric("Capacitaciones", len(capacitaciones))
        cap_realizadas = len([c for c in capacitaciones if c.get("estado") == "realizada"])
        st.metric("Realizadas", cap_realizadas)
    
    with col4:
        st.metric("Inspecciones", len(inspecciones))
        insp_completadas = len([i for i in inspecciones if i.get("estado") == "completada"])
        st.metric("Completadas", insp_completadas)
    
    # Gráficos de resumen
    st.markdown("### 📈 Tendencias")
    
    if incidentes:
        df_inc = pd.DataFrame(incidentes)
        df_inc["fecha"] = pd.to_datetime(df_inc["fecha_hora"]).dt.date
        inc_por_mes = df_inc.groupby(pd.to_datetime(df_inc["fecha_hora"]).dt.to_period("M")).size()
        
        fig = px.line(
            x=inc_por_mes.index.astype(str),
            y=inc_por_mes.values,
            title="Tendencia de Incidentes por Mes",
            labels={"x": "Mes", "y": "Cantidad"}
        )
        st.plotly_chart(fig, use_container_width=True)


def reporte_legal_sunafil():
    """Reporte legal para SUNAFIL"""
    st.subheader("📋 Reporte Legal SUNAFIL")
    st.markdown("**Reporte según Ley 29783 y DS 005-2012-TR**")
    
    supabase = get_supabase_client()
    
    # Filtros de fecha
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha Inicio", value=date.today() - timedelta(days=365))
    with col2:
        fecha_fin = st.date_input("Fecha Fin", value=date.today())
    
    st.markdown("### 1. Datos de la Empresa")
    st.markdown(f"**Razón Social:** {REPORTES_CONFIG['empresa']}")
    st.markdown(f"**RUC:** {REPORTES_CONFIG['ruc']}")
    st.markdown(f"**Dirección:** {REPORTES_CONFIG['direccion']}")
    st.markdown(f"**Sector:** {REPORTES_CONFIG['sector']}")
    st.markdown(f"**Actividad Económica:** {REPORTES_CONFIG['actividad_economica']}")
    
    st.markdown("### 2. Estadísticas de Seguridad")
    
    incidentes = supabase.listar_incidentes()
    
    if incidentes:
        df = pd.DataFrame(incidentes)
        df["fecha"] = pd.to_datetime(df["fecha_hora"]).dt.date
        
        # Filtrar por rango de fechas
        df_filtrado = df[(df["fecha"] >= fecha_inicio) & (df["fecha"] <= fecha_fin)]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_incidentes = len(df_filtrado)
            st.metric("Total Incidentes", total_incidentes)
        
        with col2:
            accidentes_incap = len(df_filtrado[df_filtrado["tipo"] == "Accidente Incapacitante"])
            st.metric("Accidentes Incapacitantes", accidentes_incap)
        
        with col3:
            dias_perdidos = df_filtrado["dias_descanso_medico"].sum()
            st.metric("Días Perdidos", int(dias_perdidos))
        
        # Tabla de incidentes por tipo
        st.markdown("### 3. Incidentes por Tipo")
        incidentes_tipo = df_filtrado["tipo"].value_counts().reset_index()
        incidentes_tipo.columns = ["Tipo", "Cantidad"]
        st.dataframe(incidentes_tipo, hide_index=True)
        
        # Índices de seguridad
        st.markdown("### 4. Índices de Seguridad")
        
        # Solicitar horas hombre trabajadas
        horas_hombre = st.number_input("Horas Hombre Trabajadas en el Período", min_value=1, value=100000)
        
        if horas_hombre > 0:
            # Índice de Frecuencia
            if_value = (accidentes_incap / horas_hombre) * 1000000
            st.metric("Índice de Frecuencia (IF)", f"{if_value:.2f}")
            st.caption("IF = (Nº Accidentes Incapacitantes / HH Trabajadas) × 1,000,000")
            
            # Índice de Severidad
            is_value = (dias_perdidos / horas_hombre) * 1000000
            st.metric("Índice de Severidad (IS)", f"{is_value:.2f}")
            st.caption("IS = (Días Perdidos / HH Trabajadas) × 1,000,000")
            
            # Índice de Accidentabilidad
            ia_value = (if_value * is_value) / 1000
            st.metric("Índice de Accidentabilidad (IA)", f"{ia_value:.2f}")
            st.caption("IA = (IF × IS) / 1,000")
    
    # Botones de descarga directa
    st.markdown("### 📥 Exportar Reporte")
    
    col1, col2 = st.columns(2)
    
    # Generar Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        # Hoja 1: Información General
        info_general = pd.DataFrame({
            "Campo": ["Razón Social", "RUC", "Dirección", "Sector", "Actividad Económica", "Período Desde", "Período Hasta"],
            "Valor": [
                REPORTES_CONFIG['empresa'],
                REPORTES_CONFIG['ruc'],
                REPORTES_CONFIG['direccion'],
                REPORTES_CONFIG['sector'],
                REPORTES_CONFIG['actividad_economica'],
                str(fecha_inicio),
                str(fecha_fin)
            ]
        })
        info_general.to_excel(writer, sheet_name="Información General", index=False)
        
        # Hoja 2: Estadísticas
        if incidentes:
            estadisticas = pd.DataFrame({
                "Indicador": ["Total Incidentes", "Accidentes Incapacitantes", "Días Perdidos"],
                "Valor": [total_incidentes, accidentes_incap, int(dias_perdidos)]
            })
            estadisticas.to_excel(writer, sheet_name="Estadísticas", index=False)
            
            # Hoja 3: Incidentes por Tipo
            incidentes_tipo.to_excel(writer, sheet_name="Incidentes por Tipo", index=False)
            
            # Hoja 4: Detalle de Incidentes
            df_filtrado.to_excel(writer, sheet_name="Detalle Incidentes", index=False)
    
    excel_buffer.seek(0)
    
    # Generar PDF
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("<b>REPORTE LEGAL SUNAFIL</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Subtítulo
    subtitle = Paragraph(f"Período: {fecha_inicio} al {fecha_fin}", styles['Heading2'])
    elements.append(subtitle)
    elements.append(Spacer(1, 12))
    
    # Información de la empresa
    empresa_data = [
        ['Campo', 'Valor'],
        ['Razón Social', REPORTES_CONFIG['empresa']],
        ['RUC', REPORTES_CONFIG['ruc']],
        ['Dirección', REPORTES_CONFIG['direccion']],
        ['Sector', REPORTES_CONFIG['sector']],
        ['Actividad Económica', REPORTES_CONFIG['actividad_economica']]
    ]
    
    empresa_table = Table(empresa_data, colWidths=[200, 300])
    empresa_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(empresa_table)
    elements.append(Spacer(1, 20))
    
    # Estadísticas
    if incidentes:
        stats_title = Paragraph("<b>Estadísticas de Seguridad</b>", styles['Heading2'])
        elements.append(stats_title)
        elements.append(Spacer(1, 12))
        
        stats_data = [
            ['Indicador', 'Valor'],
            ['Total Incidentes', str(total_incidentes)],
            ['Accidentes Incapacitantes', str(accidentes_incap)],
            ['Días Perdidos', str(int(dias_perdidos))]
        ]
        
        if horas_hombre > 0:
            stats_data.append(['Índice de Frecuencia (IF)', f"{if_value:.2f}"])
            stats_data.append(['Índice de Severidad (IS)', f"{is_value:.2f}"])
            stats_data.append(['Índice de Accidentabilidad (IA)', f"{ia_value:.2f}"])
        
        stats_table = Table(stats_data, colWidths=[300, 200])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 20))
        
        # Incidentes por tipo
        tipo_title = Paragraph("<b>Incidentes por Tipo</b>", styles['Heading2'])
        elements.append(tipo_title)
        elements.append(Spacer(1, 12))
        
        tipo_data = [['Tipo', 'Cantidad']]
        for _, row in incidentes_tipo.iterrows():
            tipo_data.append([str(row['Tipo']), str(row['Cantidad'])])
        
        tipo_table = Table(tipo_data, colWidths=[300, 200])
        tipo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(tipo_table)
    
    # Generar PDF
    doc.build(elements)
    pdf_buffer.seek(0)
    
    # Botones de descarga directa
    with col1:
        st.download_button(
            label="📥 Descargar Excel",
            data=excel_buffer,
            file_name=f"reporte_sunafil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        st.download_button(
            label="📄 Descargar PDF",
            data=pdf_buffer,
            file_name=f"reporte_sunafil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


def analisis_estadistico():
    """Análisis estadístico avanzado"""
    st.subheader("📊 Análisis Estadístico")
    
    supabase = get_supabase_client()
    
    # Selector de análisis
    tipo_analisis = st.selectbox("Tipo de Análisis", [
        "Análisis de Riesgos",
        "Análisis de Incidentes",
        "Análisis de Capacitaciones",
        "Análisis por Área"
    ])
    
    if tipo_analisis == "Análisis de Riesgos":
        riesgos = supabase.listar_riesgos()
        
        if riesgos:
            df = pd.DataFrame(riesgos)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribución por clasificación
                fig = px.pie(df, names="clasificacion", title="Distribución por Clasificación")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Riesgos por área
                fig = px.bar(
                    df["area"].value_counts().reset_index(),
                    x="area", y="count",
                    title="Riesgos por Área"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Mapa de calor
            pivot = pd.crosstab(df["tipo_riesgo"], df["clasificacion"])
            fig = px.imshow(
                pivot,
                title="Mapa de Calor: Tipo de Riesgo vs Clasificación",
                color_continuous_scale="RdYlGn_r"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    elif tipo_analisis == "Análisis de Incidentes":
        incidentes = supabase.listar_incidentes()
        
        if incidentes:
            df = pd.DataFrame(incidentes)
            df["fecha"] = pd.to_datetime(df["fecha_hora"]).dt.date
            df["mes"] = pd.to_datetime(df["fecha_hora"]).dt.to_period("M")
            
            # Tendencia temporal
            inc_por_mes = df.groupby("mes").size().reset_index(name="cantidad")
            fig = px.line(
                inc_por_mes,
                x="mes",
                y="cantidad",
                title="Tendencia de Incidentes por Mes"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Por tipo
                fig = px.bar(
                    df["tipo"].value_counts().reset_index(),
                    x="tipo", y="count",
                    title="Incidentes por Tipo"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Por área
                fig = px.bar(
                    df["area"].value_counts().reset_index(),
                    x="area", y="count",
                    title="Incidentes por Área"
                )
                st.plotly_chart(fig, use_container_width=True)


def exportar_excel():
    """Exportar datos a Excel"""
    st.subheader("📥 Exportar Datos a Excel")
    
    supabase = get_supabase_client()
    
    opciones = st.multiselect("Selecciona los datos a exportar", [
        "Riesgos",
        "Incidentes",
        "Capacitaciones",
        "Inspecciones",
        "EPPs"
    ])
    
    if st.button("Generar Excel"):
        if not opciones:
            st.error("Selecciona al menos una opción")
        else:
            with st.spinner("Generando archivo..."):
                # Crear archivo Excel en memoria
                excel_buffer = io.BytesIO()
                
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    if "Riesgos" in opciones:
                        riesgos = supabase.listar_riesgos()
                        if riesgos:
                            pd.DataFrame(riesgos).to_excel(writer, sheet_name="Riesgos", index=False)
                    
                    if "Incidentes" in opciones:
                        incidentes = supabase.listar_incidentes()
                        if incidentes:
                            pd.DataFrame(incidentes).to_excel(writer, sheet_name="Incidentes", index=False)
                    
                    if "Capacitaciones" in opciones:
                        capacitaciones = supabase.listar_capacitaciones()
                        if capacitaciones:
                            pd.DataFrame(capacitaciones).to_excel(writer, sheet_name="Capacitaciones", index=False)
                
                excel_buffer.seek(0)
                
                # Botón de descarga
                st.download_button(
                    label="⬇️ Descargar Excel Generado",
                    data=excel_buffer,
                    file_name=f"reporte_sst_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )


def modulo_reportes():
    """Módulo principal de reportes"""
    st.title("📊 Reportes y Análisis")
    st.markdown("**Reportes Legales y Estadísticos del Sistema SST**")
    
    tabs = st.tabs(["📊 Resumen Ejecutivo", "📋 Reporte SUNAFIL", "📈 Análisis Estadístico", "📥 Exportar Excel"])
    
    with tabs[0]:
        reporte_ejecutivo()
    
    with tabs[1]:
        reporte_legal_sunafil()
    
    with tabs[2]:
        analisis_estadistico()
    
    with tabs[3]:
        exportar_excel()


if __name__ == "__main__":
    modulo_reportes()
