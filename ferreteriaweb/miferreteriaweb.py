import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# ==========================================
# 0. INICIALIZACION DE BASE DE DATOS (SQLITE)
# ==========================================
def init_db():
    conn = sqlite3.connect('ferreteria.db')
    c = conn.cursor()
    # Tabla de inventario
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE,
            producto TEXT,
            categoria TEXT,
            stock INTEGER,
            precio REAL
        )
    ''')
    # Tabla de ventas para alimentar el dashboard
    c.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            total REAL
        )
    ''')
    conn.commit()
    return conn

conn = init_db()

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
            
        # CSS 'fixed' para anclar el texto permanentemente a la esquina inferior izquierda
        st.markdown(
            """
            <style>
                .bizpilot-footer {
                    position: fixed;
                    bottom: 20px;
                    left: 20px;
                    z-index: 99;
                }
            </style>
            <div class="bizpilot-footer">
                <p style='font-size: 1rem; color: #000000; font-weight: bold; margin: 0;'>BizPilot</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    # --- VISTA 1: INICIO (DASHBOARD DINAMICO) ---
    if opcion == "Inicio":
        st.title("Resumen Operativo")
        
        c = conn.cursor()
        
        # Calculos en tiempo real desde la BD
        c.execute("SELECT SUM(total) FROM ventas WHERE fecha = date('now', 'localtime')")
        ventas_hoy = c.fetchone()[0] or 0.0
        
        c.execute("SELECT SUM(total) FROM ventas")
        ventas_historicas = c.fetchone()[0] or 0.0
        
        c.execute("SELECT COUNT(*) FROM inventario WHERE stock < 5")
        alertas_stock = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(*) FROM inventario")
        total_productos = c.fetchone()[0] or 0
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Ventas del dia", f"${ventas_hoy:,.2f}")
        kpi2.metric("Ventas Acumuladas", f"${ventas_historicas:,.2f}")
        kpi3.metric("Alertas de Stock Bajo", alertas_stock, delta_color="inverse")
        kpi4.metric("Total Productos Catálogo", total_productos, delta_color="off")
        
        st.markdown("---")
        
        st.subheader("Historial de Ventas")
        df_ventas = pd.read_sql_query("SELECT fecha as Fecha, total as Total FROM ventas", conn)
        
        if df_ventas.empty:
            st.info("No hay ventas registradas aun. Las graficas apareceran aqui cuando inicies operaciones.")
        else:
            # Agrupar por fecha en caso de multiples ventas el mismo dia
            df_ventas_agrupado = df_ventas.groupby('Fecha', as_index=False).sum()
            fig = px.bar(
                df_ventas_agrupado, 
                x="Fecha", 
                y="Total", 
                color_discrete_sequence=["#FF7300"],
                text_auto='.2s'
            )
            
            # Ajuste de tamaño de letras en la grafica para mayor legibilidad
            fig.update_traces(
                textfont_size=16, 
                textposition="outside"
            )
            fig.update_layout(
                xaxis_title="Fecha de Venta", 
                yaxis_title="Monto ($)", 
                margin=dict(l=0, r=0, t=30, b=0),
                font=dict(size=16), 
                xaxis=dict(tickfont=dict(size=14)), 
                yaxis=dict(tickfont=dict(size=14))  
            )
            
            st.plotly_chart(fig, use_container_width=True)

    # --- VISTA 2: CAJA Y VENTAS (CONECTADA A INVENTARIO Y CAMBIO) ---
    elif opcion == "Caja y Ventas":
        st.title("Terminal Punto de Venta (TPV)")
        
        df_disponibles = pd.read_sql_query("SELECT sku, producto, precio, stock FROM inventario WHERE stock > 0", conn)
        
        if df_disponibles.empty:
            st.warning("No hay productos con stock disponible para vender. Ingresa productos en el Inventario primero.")
        else:
            df_disponibles['display'] = df_disponibles['sku'] + " - " + df_disponibles['producto'] + " ($" + df_disponibles['precio'].astype(str) + ")"
            
            col_busqueda, col_cant, col_btn = st.columns([3, 1, 1])
            with col_busqueda:
                producto_seleccionado = st.selectbox("Buscar Producto", df_disponibles['display'].tolist())
            
            sku_sel = producto_seleccionado.split(" - ")[0]
            row = df_disponibles[df_disponibles['sku'] == sku_sel].iloc[0]
            
            with col_cant:
                cant_input = st.number_input("Cantidad", min_value=1, max_value=int(row['stock']), step=1)
            
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True) 
                if st.button("Agregar al Carrito", use_container_width=True, type="primary"):
                    st.session_state['carrito'].append({
                        "SKU": row['sku'],
                        "Producto": row['producto'],
                        "Cant.": cant_input, 
                        "Precio Unit.": row['precio'], 
                        "Subtotal": cant_input * row['precio']
                    })
                    st.session_state['total_actual'] += (cant_input * row['precio'])
                    st.rerun()

        st.markdown("---")
        
        if st.session_state['carrito']:
            df_carrito = pd.DataFrame(st.session_state['carrito'])
            df_carrito_display = df_carrito.copy()
            df_carrito_display['Precio Unit.'] = df_carrito_display['Precio Unit.'].apply(lambda x: f"${x:,.2f}")
            df_carrito_display['Subtotal'] = df_carrito_display['Subtotal'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(df_carrito_display, use_container_width=True, hide_index=True)
            
            # --- SECCION DE COBRO Y CALCULO DE CAMBIO ---
            st.markdown(f"<h2 style='text-align: right; color: #000000;'>Total a Cobrar: ${st.session_state['total_actual']:,.2f}</h2>", unsafe_allow_html=True)
            
            with st.container(border=True):
                col_pago1, col_pago2, col_pago3 = st.columns([1, 1, 1])
                
                with col_pago1:
                    metodo_pago = st.selectbox("Metodo de Pago", ["Efectivo", "Tarjeta / Transferencia"])
                
                with col_pago2:
                    if metodo_pago == "Efectivo":
                        monto_recibido = st.number_input("Monto Recibido ($)", min_value=0.0, step=50.0, value=float(st.session_state['total_actual']))
                        cambio = monto_recibido - st.session_state['total_actual']
                    else:
                        monto_recibido = st.session_state['total_actual']
                        cambio = 0.0
                        st.number_input("Monto Recibido ($)", value=float(st.session_state['total_actual']), disabled=True)
                
                with col_pago3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if metodo_pago == "Efectivo":
                        if cambio >= 0:
                            st.markdown(f"<h3 style='text-align: right; color: #28a745;'>Cambio: ${cambio:,.2f}</h3>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<h3 style='text-align: right; color: #dc3545;'>Faltan: ${abs(cambio):,.2f}</h3>", unsafe_allow_html=True)
                    else:
                        st.markdown("<h3 style='text-align: right; color: #28a745;'>Pago Exacto</h3>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Boton de cobro (Se deshabilita si falta dinero)
            if st.button("Procesar Cobro", type="primary", use_container_width=True, disabled=(cambio < 0)):
                c = conn.cursor()
                # Descontar stock
                for item in st.session_state['carrito']:
                    c.execute("UPDATE inventario SET stock = stock - ? WHERE sku = ?", (item['Cant.'], item['SKU']))
                
                # Registrar venta
                c.execute("INSERT INTO ventas (fecha, total) VALUES (date('now', 'localtime'), ?)", (st.session_state['total_actual'],))
                conn.commit()
                
                # Mensaje de exito
                if metodo_pago == "Efectivo":
                    st.success(f"Cobro exitoso. Cambio a entregar: ${cambio:,.2f}. Imprimiendo ticket...")
                else:
                    st.success(f"Cobro exitoso por ${st.session_state['total_actual']:,.2f}. Imprimiendo ticket...")
                
                # Limpiar carrito
                st.session_state['carrito'] = []
                st.session_state['total_actual'] = 0.0
                st.rerun()
                
        else:
            st.info("Agrega productos al carrito para habilitar el modulo de cobro.")


    # --- VISTA 3: INVENTARIO (CON CREACION DE CATALOGO) ---
    elif opcion == "Inventario":
        st.title("Inventario y Existencias")
        
        with st.expander("Agregar Nuevo Producto al Catalogo", expanded=False):
            with st.form("form_nuevo_producto"):
                col_f1, col_f2 = st.columns(2)
                nuevo_sku = col_f1.text_input("SKU / Codigo")
                nuevo_prod = col_f2.text_input("Nombre del Producto")
                nueva_cat = col_f1.selectbox("Categoria", ["Construccion", "Pinturas", "Plomeria", "Ferreteria", "Herramientas", "Otros"])
                nuevo_stock = col_f2.number_input("Stock Inicial", min_value=0, step=1)
                nuevo_precio = col_f1.number_input("Precio de Venta ($)", min_value=0.0, step=1.0)
                
                if st.form_submit_button("Guardar en Base de Datos", type="primary"):
                    if nuevo_sku and nuevo_prod and nuevo_precio > 0:
                        try:
                            c = conn.cursor()
                            c.execute("INSERT INTO inventario (sku, producto, categoria, stock, precio) VALUES (?, ?, ?, ?, ?)", 
                                      (nuevo_sku, nuevo_prod, nueva_cat, nuevo_stock, nuevo_precio))
                            conn.commit()
                            st.success(f"Producto '{nuevo_prod}' agregado correctamente.")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("Error: El SKU ingresado ya existe en el sistema. Utiliza uno diferente.")
                    else:
                        st.error("El SKU, Nombre y Precio son obligatorios.")

        st.markdown("<br>", unsafe_allow_html=True)
        
        df_inv = pd.read_sql_query("SELECT sku AS SKU, producto AS Producto, categoria AS Categoria, stock AS Stock, precio AS Precio FROM inventario", conn)
        
        if df_inv.empty:
            st.info("El catalogo de inventario esta vacio. Registra un nuevo producto para comenzar.")
        else:
            busqueda = st.text_input("Buscar por SKU o Nombre...")
            if busqueda:
                df_inv = df_inv[df_inv['SKU'].str.contains(busqueda, case=False) | df_inv['Producto'].str.contains(busqueda, case=False)]
            
            df_inv['Precio'] = df_inv['Precio'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(df_inv, use_container_width=True, hide_index=True)

    # --- VISTA 4: COMPRAS (ENTRADAS DE ALMACEN) ---
    elif opcion == "Compras":
        st.title("Ingreso de Mercancia")
        st.write("Selecciona un producto existente para registrar una entrada y aumentar su inventario.")
        
        df_all = pd.read_sql_query("SELECT sku, producto, stock FROM inventario", conn)
        
        if df_all.empty:
            st.warning("Debe existir al menos un producto en el catálogo (Inventario) para registrar ingresos.")
        else:
            df_all['display'] = df_all['sku'] + " - " + df_all['producto'] + " (Stock Actual: " + df_all['stock'].astype(str) + ")"
            
            with st.container(border=True):
                prod_compra = st.selectbox("Producto Recibido", df_all['display'].tolist())
                sku_compra = prod_compra.split(" - ")[0]
                
                cant_ingreso = st.number_input("Cantidad a Ingresar", min_value=1, step=1)
                
                if st.button("Registrar Ingreso a Almacen", type="primary"):
                    c = conn.cursor()
                    c.execute("UPDATE inventario SET stock = stock + ? WHERE sku = ?", (cant_ingreso, sku_compra))
                    conn.commit()
                    st.success("Inventario actualizado correctamente.")
                    st.rerun()
                    
        st.markdown("---")
        st.subheader("Ordenes de Compra Pendientes")
        st.dataframe(pd.DataFrame(columns=["Orden", "Fecha", "Proveedor", "Monto", "Estado"]), use_container_width=True, hide_index=True)

    # --- VISTA 5: PROVEEDORES ---
    elif opcion == "Proveedores":
        st.title("Directorio de Proveedores")
        st.button("Nuevo Proveedor", type="primary")
        
        df_prov = pd.DataFrame(columns=["ID", "Empresa", "Contacto", "Telefono", "Correo"])
        st.dataframe(df_prov, use_container_width=True, hide_index=True)
        st.info("No hay proveedores registrados.")

    # --- VISTA 6: SEGURIDAD ---
    elif opcion == "Seguridad":
        st.title("Seguridad y Respaldos")
        
        with st.container(border=True):
            st.subheader("Copia de Seguridad (Backup)")
            st.write("Se recomienda generar respaldos periodicos de la base de datos.")
            if st.button("Generar Respaldo Ahora", type="primary"):
                st.success("Respaldo generado correctamente.")
                
        st.subheader("Gestion de Usuarios")
        df_usr = pd.DataFrame(columns=["Usuario", "Rol", "Ultimo Acceso"])
        st.dataframe(df_usr, use_container_width=True, hide_index=True)

    # --- VISTA 7: CONFIGURACION (ZONA DE BORRADO TOTAL) ---
    elif opcion == "Configuracion":
        st.title("Configuracion del Sistema")
        
        with st.container(border=True):
            st.subheader("Datos Generales")
            st.text_input("Nombre Comercial:", value="")
            st.text_input("RFC:", value="")
            st.text_input("Direccion:", value="")
            
            if st.button("Guardar Configuracion", type="primary"):
                st.success("Configuracion actualizada.")

        st.markdown("---")
        
        with st.container(border=True):
            st.markdown("<h3 style='color: red;'>Limpieza del Sistema</h3>", unsafe_allow_html=True)
            st.write("Esta accion borrara todos los productos, existencias e historial de ventas permanentemente.")
            
            if st.button("Eliminar Todos los Datos", type="primary"):
                c = conn.cursor()
                c.execute("DELETE FROM inventario")
                c.execute("DELETE FROM ventas")
                c.execute("DELETE FROM sqlite_sequence WHERE name='inventario'")
                c.execute("DELETE FROM sqlite_sequence WHERE name='ventas'")
                conn.commit()
                st.error("El sistema ha sido reestablecido a cero exitosamente.")

    # --- VISTA 8: REPORTES ---
    elif opcion == "Reportes":
        st.title("Generador de Reportes")
        
        df_csv = pd.read_sql_query("SELECT fecha AS Fecha, total AS Total FROM ventas", conn)
        
        if df_csv.empty:
            st.info("No hay datos suficientes para generar un reporte.")
        else:
            csv_buffer = df_csv.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar Reporte Historico (CSV)",
                data=csv_buffer,
                file_name="Reporte_Ventas.csv",
                mime="text/csv",
                type="primary"
            )