import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. CONFIGURACION DE PAGINA
# ==========================================
st.set_page_config(page_title="Mi Ferreteria - Web", layout="wide")

# ==========================================
# 2. VARIABLES DE SESION (ESTADO)
# ==========================================
if 'logeado' not in st.session_state:
    st.session_state['logeado'] = False
if 'carrito' not in st.session_state:
    st.session_state['carrito'] = []
if 'total_actual' not in st.session_state:
    st.session_state['total_actual'] = 0.0

# ==========================================
# 3. PANTALLA DE LOGIN (CENTRADA)
# ==========================================
if not st.session_state['logeado']:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #FF7300; font-size: 3rem;'>Mi Ferreteria</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #000000; font-size: 1.2rem;'>Panel de Administracion Web</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        with st.container(border=True):
            usuario = st.text_input("Usuario", value="admin", placeholder="Ingresa tu usuario")
            password = st.text_input("Contrasena", value="123", type="password", placeholder="Ingresa tu contrasena")
            
            if st.button("Iniciar Sesion", use_container_width=True, type="primary"):
                if usuario == "admin" and password == "123":
                    st.session_state['logeado'] = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. (Usa admin / 123)")

# ==========================================
# 4. APLICACION PRINCIPAL (ENRUTADOR Y VISTAS)
# ==========================================
else:
    # --- SIDEBAR (MENU LATERAL) ---
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #FF7300;'>Mi Ferreteria</h2>", unsafe_allow_html=True)
        st.markdown("---")
        opcion = st.sidebar.selectbox(
            "Navegacion",
            ["Inicio", "Caja y Ventas", "Inventario", "Compras", "Proveedores", "Seguridad", "Configuracion", "Reportes"]
        )
        st.markdown("---")
        if st.button("Cerrar Sesion", use_container_width=True):
            st.session_state['logeado'] = False
            st.rerun()
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #000000;'>Desarrollado por<br><b>Brandon Sanchez</b><br>CEO de BizPilot</p>", unsafe_allow_html=True)

    # --- VISTA 1: INICIO (DASHBOARD) ---
    if opcion == "Inicio":
        st.title("Resumen Operativo")
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Ventas del dia", "$28,560.00", "12.5% Hoy")
        kpi2.metric("Ganancias del mes", "$152,430.00", "8.3% Este mes")
        kpi3.metric("Productos por agotarse", "18", "-3 vs ayer", delta_color="inverse")
        kpi4.metric("Alertas pendientes", "7", "Requiere atencion", delta_color="off")
        
        st.markdown("---")
        
        st.subheader("Ventas de la Semana")
        df_ventas = pd.DataFrame({
            "Ventas ($)": [12000, 15000, 11000, 18000, 25000, 28560]
        }, index=['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'])
        st.bar_chart(df_ventas, color="#FF7300")
        
        st.markdown("---")
        
        st.subheader("Alertas Recientes")
        col_alerta1, col_alerta2 = st.columns(2)
        with col_alerta1:
            st.selectbox(
                "Inventario Critico (18 productos)", 
                ["Selecciona para ver...", "- Cemento Holcim 50kg (Quedan 3)", "- Pintura Comex 19L (Quedan 2)", "- Broca para concreto (Quedan 5)"]
            )
        with col_alerta2:
            st.selectbox(
                "Tareas y Pagos (3 pendientes)", 
                ["Selecciona para ver...", "- Pago a Truper ($4,850) - Vence Hoy", "- Pedido programado IUSA", "- Verificar respaldo de sistema"]
            )

    # --- VISTA 2: CAJA Y VENTAS (TPV) ---
    elif opcion == "Caja y Ventas":
        st.title("Terminal Punto de Venta (TPV)")
        
        col_busqueda, col_precio, col_btn = st.columns([3, 1, 1])
        with col_busqueda:
            prod_input = st.text_input("Producto o Codigo de Barras")
        with col_precio:
            precio_input = st.number_input("Precio ($)", min_value=0.0, step=1.0)
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True) 
            if st.button("Agregar al Carrito", use_container_width=True, type="primary"):
                if prod_input and precio_input > 0:
                    st.session_state['carrito'].append({
                        "Cant.": 1, "Producto": prod_input, 
                        "Precio Unit.": f"${precio_input:,.2f}", 
                        "Subtotal": f"${precio_input:,.2f}"
                    })
                    st.session_state['total_actual'] += precio_input
                    st.rerun()

        if st.session_state['carrito']:
            df_carrito = pd.DataFrame(st.session_state['carrito'])
            st.dataframe(df_carrito, use_container_width=True, hide_index=True)
        else:
            st.info("El carrito esta vacio.")

        st.markdown(f"<h2 style='text-align: right; color: #000000;'>Total a Cobrar: ${st.session_state['total_actual']:,.2f}</h2>", unsafe_allow_html=True)
        
        if st.button("Procesar Cobro", type="primary"):
            if st.session_state['total_actual'] > 0:
                st.success(f"Cobro exitoso por ${st.session_state['total_actual']:,.2f}. Imprimiendo ticket...")
                st.session_state['carrito'] = []
                st.session_state['total_actual'] = 0.0
            else:
                st.warning("Agrega productos antes de cobrar.")

    # --- VISTA 3: INVENTARIO ---
    elif opcion == "Inventario":
        st.title("Inventario y Existencias")
        
        col1, col2 = st.columns([3, 1])
        col1.text_input("Buscar por SKU o Nombre...")
        col2.markdown("<br>", unsafe_allow_html=True)
        col2.button("Nuevo Producto", type="primary", use_container_width=True)

        datos_inv = [
            {"SKU": "CM-50", "Producto": "Cemento Holcim 50kg", "Categoria": "Construccion", "Stock": 3, "Estado": "Critico"}, 
            {"SKU": "PT-19", "Producto": "Pintura Comex 19L Blanca", "Categoria": "Pinturas", "Stock": 2, "Estado": "Critico"},
            {"SKU": "PVC-12", "Producto": "Tubo PVC 1/2\"", "Categoria": "Plomeria", "Stock": 45, "Estado": "Optimo"}, 
            {"SKU": "TR-01", "Producto": "Tornillo Pija 1\"", "Categoria": "Ferreteria", "Stock": 500, "Estado": "Optimo"},
            {"SKU": "MT-05", "Producto": "Martillo Truper 16oz", "Categoria": "Herramientas", "Stock": 12, "Estado": "Optimo"}
        ]
        
        df_inv = pd.DataFrame(datos_inv)
        st.dataframe(df_inv, use_container_width=True, hide_index=True)

    # --- VISTA 4: COMPRAS ---
    elif opcion == "Compras":
        st.title("Gestion de Compras")
        st.button("Generar Orden de Compra", type="primary")
        
        datos_compras = [
            {"Orden #": "OC-1045", "Fecha": "2026-07-20", "Proveedor": "Truper S.A. de C.V.", "Monto": "$12,500.00", "Estado": "Recibido"},
            {"Orden #": "OC-1046", "Fecha": "2026-07-21", "Proveedor": "Cemex Mexico", "Monto": "$8,400.00", "Estado": "En Transito"},
            {"Orden #": "OC-1047", "Fecha": "2026-07-22", "Proveedor": "Pinturas Comex", "Monto": "$3,200.00", "Estado": "Pendiente"}
        ]
        st.dataframe(pd.DataFrame(datos_compras), use_container_width=True, hide_index=True)

    # --- VISTA 5: PROVEEDORES ---
    elif opcion == "Proveedores":
        st.title("Directorio de Proveedores")
        datos_prov = [
            {"ID": "PRV-01", "Empresa": "Truper S.A. de C.V.", "Contacto": "Carlos Slim H.", "Telefono": "555-123-4567"},
            {"ID": "PRV-02", "Empresa": "Cemex Mexico", "Contacto": "Ana Garcia", "Telefono": "555-987-6543"},
            {"ID": "PRV-03", "Empresa": "Pinturas Comex", "Contacto": "Luis Perez", "Telefono": "555-456-7890"}
        ]
        st.dataframe(pd.DataFrame(datos_prov), use_container_width=True, hide_index=True)

    # --- VISTA 6: SEGURIDAD ---
    elif opcion == "Seguridad":
        st.title("Seguridad y Respaldos")
        
        with st.container(border=True):
            st.subheader("Copia de Seguridad (Backup)")
            st.write("Ultimo respaldo exitoso: Hoy 02:00 AM. Se recomienda respaldar al cierre de caja.")
            if st.button("Generar Respaldo de Base de Datos Ahora", type="primary"):
                st.success("Respaldo generado correctamente y cifrado en el servidor.")
                
        st.subheader("Gestion de Usuarios del Sistema")
        datos_usr = [
            {"Usuario": "admin", "Rol": "Administrador Total", "Ultimo Acceso": "Hace 5 min"},
            {"Usuario": "cajero_01", "Rol": "Cajero", "Ultimo Acceso": "Ayer 18:30"},
            {"Usuario": "almacen", "Rol": "Inventario", "Ultimo Acceso": "Hoy 08:00"}
        ]
        st.dataframe(pd.DataFrame(datos_usr), use_container_width=True, hide_index=True)

    # --- VISTA 7: CONFIGURACION ---
    elif opcion == "Configuracion":
        st.title("Configuracion del Sistema")
        
        with st.container(border=True):
            st.subheader("Datos del Ticket y Recibo")
            st.text_input("Nombre Comercial:", value="Ferreteria El Tuerca")
            st.text_input("RFC:", value="XAXX010101000")
            st.text_input("Direccion:", value="Av. Principal 123, Colonia Centro")
            st.text_input("Telefono:", value="555-000-1111")
            st.text_input("Impresora por Defecto:", value="EPSON TM-T20III Receipt")
            
            if st.button("Guardar Configuracion", type="primary"):
                st.success("Configuracion actualizada para futuros tickets.")

    # --- VISTA 8: REPORTES ---
    elif opcion == "Reportes":
        st.title("Generador de Reportes Analiticos")
        
        st.write("Genera y descarga la informacion operativa de la sucursal.")
        
        df_csv = pd.DataFrame({"Fecha": [datetime.now().strftime("%Y-%m-%d")], "Total Ventas": [28560], "Productos": [150]})
        csv_buffer = df_csv.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="Descargar Reporte de Ventas (CSV)",
            data=csv_buffer,
            file_name="Ventas_Ferreteria.csv",
            mime="text/csv",
            type="primary"
        )
        
        txt_content = f"--- RESUMEN DE INVENTARIO ---\nFecha: {datetime.now().strftime('%Y-%m-%d')}\nProductos Criticos:\n- Cemento Holcim 50kg (Stock: 3)\n- Pintura Comex 19L (Stock: 2)\n"
        
        st.download_button(
            label="Descargar Resumen de Inventario (TXT)",
            data=txt_content,
            file_name="Inventario.txt",
            mime="text/plain"
        )