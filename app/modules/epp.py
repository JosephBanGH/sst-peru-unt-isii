"""
Módulo de Gestión de Equipos de Protección Personal (EPP)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.supabase_client import get_supabase_client
from utils.n8n_client import get_n8n_client
from config.settings import TIPOS_EPP
from auth import obtener_usuario_actual


def generar_codigo_epp() -> str:
    """Genera un código único para el EPP"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"EPP-{timestamp}"


def formulario_registro_epp():
    """Formulario para registrar un nuevo EPP en el catálogo"""
    st.subheader("➕ Registrar Nuevo EPP en Catálogo")
    
    supabase = get_supabase_client()
    
    with st.form("form_epp"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre del EPP *")
            tipo = st.selectbox("Tipo de EPP *", TIPOS_EPP)
            marca = st.text_input("Marca")
            modelo = st.text_input("Modelo")
            certificacion = st.text_input("Certificación/Norma Técnica")
        
        with col2:
            vida_util_meses = st.number_input("Vida Útil (meses) *", min_value=1, value=12)
            stock_minimo = st.number_input("Stock Mínimo", min_value=0, value=10)
            stock_actual = st.number_input("Stock Actual", min_value=0, value=0)
            costo_unitario = st.number_input("Costo Unitario (S/)", min_value=0.0, value=0.0, step=0.01)
            proveedor = st.text_input("Proveedor")
        
        descripcion = st.text_area("Descripción")
        
        submitted = st.form_submit_button("💾 Registrar EPP", width='stretch')
        
        if submitted:
            if not all([nombre, tipo, vida_util_meses]):
                st.error("Por favor completa todos los campos obligatorios (*)")
            else:
                datos_epp = {
                    "codigo": generar_codigo_epp(),
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "tipo": tipo,
                    "marca": marca,
                    "modelo": modelo,
                    "certificacion": certificacion,
                    "vida_util_meses": vida_util_meses,
                    "stock_minimo": stock_minimo,
                    "stock_actual": stock_actual,
                    "costo_unitario": costo_unitario,
                    "proveedor": proveedor,
                    "activo": True
                }
                
                epp_creado = supabase.crear_epp(datos_epp)
                
                if epp_creado:
                    st.success(f"✅ EPP registrado: {epp_creado['codigo']}")
                    st.rerun()


def formulario_asignacion_epp():
    """Formulario para asignar EPP a un trabajador"""
    st.subheader("➕ Asignar EPP a Trabajador")
    
    supabase = get_supabase_client()
    usuario_actual = obtener_usuario_actual()
    
    # Obtener listas
    epps = supabase.listar_epp()
    usuarios = supabase.listar_usuarios()
    
    if not epps:
        st.warning("No hay EPPs registrados en el catálogo")
        return
    
    if not usuarios:
        st.warning("No hay usuarios registrados")
        return
    
    epps_dict = {f"{e['nombre']} ({e['codigo']})": e for e in epps}
    usuarios_dict = {u["nombre_completo"]: u for u in usuarios}
    
    with st.form("form_asignacion"):
        col1, col2 = st.columns(2)
        
        with col1:
            epp_seleccionado = st.selectbox("EPP a Asignar *", list(epps_dict.keys()))
            usuario_seleccionado = st.selectbox("Trabajador *", list(usuarios_dict.keys()))
            cantidad = st.number_input("Cantidad *", min_value=1, value=1)
        
        with col2:
            fecha_asignacion = st.date_input("Fecha de Asignación *", value=date.today())
            
            # Calcular fecha de vencimiento automáticamente
            epp_data = epps_dict[epp_seleccionado]
            vida_util_meses = epp_data.get("vida_util_meses", 12)
            fecha_vencimiento_sugerida = fecha_asignacion + timedelta(days=vida_util_meses * 30)
            
            fecha_vencimiento = st.date_input(
                "Fecha de Vencimiento *",
                value=fecha_vencimiento_sugerida
            )
        
        observaciones = st.text_area("Observaciones")
        
        submitted = st.form_submit_button("💾 Asignar EPP", width='stretch')
        
        if submitted:
            # Verificar stock disponible
            if epp_data["stock_actual"] < cantidad:
                st.error(f"Stock insuficiente. Disponible: {epp_data['stock_actual']}")
            else:
                datos_asignacion = {
                    "epp_id": epp_data["id"],
                    "usuario_id": usuarios_dict[usuario_seleccionado]["id"],
                    "cantidad": cantidad,
                    "fecha_asignacion": fecha_asignacion.isoformat(),
                    "fecha_vencimiento": fecha_vencimiento.isoformat(),
                    "estado": "activo",
                    "observaciones": observaciones,
                    "entregado_por": usuario_actual["id"]
                }
                
                asignacion_creada = supabase.asignar_epp(datos_asignacion)
                
                if asignacion_creada:
                    st.success("✅ EPP asignado correctamente")
                    st.info(f"Stock actualizado: {epp_data['stock_actual']} → {epp_data['stock_actual'] - cantidad}")
                    st.rerun()


def listar_catalogo_epp():
    """Lista el catálogo de EPPs"""
    st.subheader("📋 Catálogo de EPPs")
    
    supabase = get_supabase_client()
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filtro_tipo = st.selectbox("Tipo", ["Todos"] + TIPOS_EPP)
    with col2:
        filtro_stock_bajo = st.checkbox("Solo con stock bajo")
    with col3:
        filtro_activos = st.checkbox("Solo activos", value=True)
    
    epps = supabase.listar_epp(activos_solo=filtro_activos)
    
    if filtro_tipo != "Todos":
        epps = [e for e in epps if e.get("tipo") == filtro_tipo]
    
    if filtro_stock_bajo:
        epps = [e for e in epps if e.get("stock_actual", 0) <= e.get("stock_minimo", 0)]
    
    if epps:
        st.info(f"Total de EPPs: {len(epps)}")
        
        df = pd.DataFrame(epps)
        
        # Agregar indicador de stock
        df["estado_stock"] = df.apply(
            lambda row: "🔴 Bajo" if row["stock_actual"] <= row["stock_minimo"] 
            else "🟢 OK",
            axis=1
        )
        
        columnas_mostrar = [
            "codigo", "nombre", "tipo", "marca", "modelo",
            "stock_actual", "stock_minimo", "estado_stock",
            "vida_util_meses", "costo_unitario"
        ]
        
        df_mostrar = df[columnas_mostrar].copy()
        df_mostrar.columns = [
            "Código", "Nombre", "Tipo", "Marca", "Modelo",
            "Stock", "Stock Mín", "Estado", "Vida Útil (m)", "Costo (S/)"
        ]
        
        st.dataframe(df_mostrar, width='stretch', hide_index=True)
        
        # Alertas de stock bajo
        stock_bajo = df[df["stock_actual"] <= df["stock_minimo"]]
        if not stock_bajo.empty:
            st.warning(f"⚠️ {len(stock_bajo)} EPPs con stock bajo o agotado")
            with st.expander("Ver detalles"):
                st.dataframe(stock_bajo[["nombre", "stock_actual", "stock_minimo"]], hide_index=True)
    else:
        st.warning("No se encontraron EPPs")


def listar_epp_vencimientos():
    """Lista EPPs próximos a vencer"""
    st.subheader("⏰ EPPs Próximos a Vencer (30 días)")
    
    supabase = get_supabase_client()
    n8n = get_n8n_client()
    
    vencimientos = supabase.obtener_epp_vencimientos()
    
    if vencimientos:
        st.warning(f"⚠️ {len(vencimientos)} EPPs próximos a vencer")
        
        df = pd.DataFrame(vencimientos)
        
        # Colorear según días restantes
        def color_dias(dias):
            if dias < 0:
                return "🔴 Vencido"
            elif dias <= 7:
                return "🟠 Urgente"
            elif dias <= 15:
                return "🟡 Pronto"
            else:
                return "🟢 Próximo"
        
        df["alerta"] = df["dias_restantes"].apply(color_dias)
        
        columnas_mostrar = [
            "usuario", "area", "epp_nombre", "epp_tipo",
            "fecha_vencimiento", "dias_restantes", "alerta"
        ]
        
        df_mostrar = df[columnas_mostrar].copy()
        df_mostrar.columns = [
            "Trabajador", "Área", "EPP", "Tipo",
            "Fecha Venc.", "Días Rest.", "Estado"
        ]
        
        st.dataframe(df_mostrar, width='stretch', hide_index=True)
        
        # Botón para enviar alertas
        if st.button("📧 Enviar Alertas de Vencimiento"):
            with st.spinner("Enviando alertas..."):
                for _, row in df.iterrows():
                    n8n.notificar_alerta_epp_vencimiento(row.to_dict())
                st.success("✅ Alertas enviadas correctamente")
    else:
        st.success("✅ No hay EPPs próximos a vencer")


def dashboard_epp():
    """Dashboard de EPPs"""
    st.subheader("📊 Dashboard de EPPs")
    
    supabase = get_supabase_client()
    epps = supabase.listar_epp()
    
    if not epps:
        st.warning("No hay EPPs registrados")
        return
    
    df = pd.DataFrame(epps)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_epps = len(df)
        st.metric("Total EPPs", total_epps)
    
    with col2:
        stock_total = df["stock_actual"].sum()
        st.metric("Stock Total", int(stock_total))
    
    with col3:
        stock_bajo = len(df[df["stock_actual"] <= df["stock_minimo"]])
        st.metric("Stock Bajo", stock_bajo, delta="⚠️" if stock_bajo > 0 else None)
    
    with col4:
        valor_inventario = (df["stock_actual"] * df["costo_unitario"]).sum()
        st.metric("Valor Inventario", f"S/ {valor_inventario:,.2f}")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución por tipo
        fig_tipo = px.pie(
            df,
            names="tipo",
            title="Distribución por Tipo de EPP"
        )
        st.plotly_chart(fig_tipo, width='stretch')
    
    with col2:
        # Stock por tipo
        stock_por_tipo = df.groupby("tipo")["stock_actual"].sum().reset_index()
        fig_stock = px.bar(
            stock_por_tipo,
            x="tipo",
            y="stock_actual",
            title="Stock por Tipo de EPP",
            labels={"tipo": "Tipo", "stock_actual": "Stock"}
        )
        st.plotly_chart(fig_stock, width='stretch')


def modulo_epp():
    """Módulo principal de gestión de EPP"""
    st.title("🦺 Gestión de Equipos de Protección Personal (EPP)")
    st.markdown("**Control de EPPs y Asignaciones**")
    
    tabs = st.tabs(["📊 Dashboard", "📋 Catálogo", "⏰ Vencimientos", "➕ Registrar EPP", "➕ Asignar EPP"])
    
    with tabs[0]:
        dashboard_epp()
    
    with tabs[1]:
        listar_catalogo_epp()
    
    with tabs[2]:
        listar_epp_vencimientos()
    
    with tabs[3]:
        formulario_registro_epp()
    
    with tabs[4]:
        formulario_asignacion_epp()


if __name__ == "__main__":
    modulo_epp()
