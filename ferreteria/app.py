import sys
import os
import pandas as pd
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QStackedWidget, QFrame, QGridLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog,
                             QFormLayout)
from PyQt6.QtCore import Qt

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# ==========================================
# 1. ESTILOS GLOBALES (QSS)
# ==========================================
ESTILO_GLOBAL = """
    QMainWindow { background-color: #F3F4F6; }
    #sidebar { background-color: #FF7300; border-right: 1px solid #E5E7EB; }
    #sidebar QPushButton {
        background-color: transparent; color: white; text-align: left;
        padding: 12px 20px; font-size: 14px; font-weight: bold; border: none;
    }
    #sidebar QPushButton:hover { background-color: #E66600; }
    #sidebar QPushButton:checked { background-color: #CC5A00; border-left: 4px solid white; }
    QPushButton.btn-primario {
        background-color: #FF7300; color: white; border-radius: 6px; padding: 10px; font-weight: bold;
    }
    QPushButton.btn-primario:hover { background-color: #E66600; }
    QPushButton.btn-secundario {
        background-color: #E5E7EB; color: #374151; border-radius: 6px; padding: 10px; font-weight: bold;
    }
    QPushButton.btn-secundario:hover { background-color: #D1D5DB; }
    QFrame.tarjeta { background-color: white; border-radius: 8px; border: 1px solid #E5E7EB; }
    QTableWidget { background-color: white; border: 1px solid #E5E7EB; border-radius: 8px; color: black; }
    QHeaderView::section {
        background-color: #F9FAFB; border: none; border-bottom: 1px solid #E5E7EB;
        padding: 8px; font-weight: bold; color: #374151;
    }
    QLineEdit {
        padding: 8px; border: 1px solid #D1D5DB; border-radius: 4px; color: black; background-color: #FFFFFF;
    }
    QLineEdit:focus { border: 1px solid #FF7300; }
"""

# ==========================================
# COMPONENTE DE GRÁFICA (Canvas de Matplotlib)
# ==========================================
class LienzoGrafica(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

# ==========================================
# 2. PANTALLA DE LOGIN
# ==========================================
class VistaLogin(QWidget):
    def __init__(self, al_autenticar):
        super().__init__()
        self.al_autenticar = al_autenticar
        self.configurar_ui()

    def configurar_ui(self):
        layout_principal = QVBoxLayout()
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        tarjeta.setFixedWidth(400)
        tarjeta.setStyleSheet("background-color: white; border-radius: 10px; padding: 30px; border: 1px solid #ccc;")
        layout_tarjeta = QVBoxLayout(tarjeta)

        titulo = QLabel("Mi Ferreteria")
        titulo.setStyleSheet("color: #FF7300; font-size: 28px; font-weight: bold;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitulo = QLabel("Panel de Administracion")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet("color: gray; margin-bottom: 20px; font-size: 14px;")

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Usuario")
        self.input_usuario.setText("admin") # Pre-llenado para la demo
        
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Contrasena")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setText("123") # Pre-llenado para la demo
        self.input_password.returnPressed.connect(self.validar_credenciales)

        btn_entrar = QPushButton("Iniciar Sesion")
        btn_entrar.setProperty("class", "btn-primario")
        btn_entrar.setStyleSheet("font-size: 16px; padding: 12px; margin-top: 10px;")
        btn_entrar.clicked.connect(self.validar_credenciales)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: red; font-size: 12px;")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout_tarjeta.addWidget(titulo)
        layout_tarjeta.addWidget(subtitulo)
        layout_tarjeta.addWidget(self.input_usuario)
        layout_tarjeta.addWidget(self.input_password)
        layout_tarjeta.addWidget(btn_entrar)
        layout_tarjeta.addWidget(self.lbl_error)

        layout_principal.addWidget(tarjeta)
        self.setLayout(layout_principal)

    def validar_credenciales(self):
        if self.input_usuario.text() == "admin" and self.input_password.text() == "123":
            self.lbl_error.setText("")
            self.al_autenticar() 
        else:
            self.lbl_error.setText("Credenciales incorrectas. (Usa admin / 123)")

# ==========================================
# 3. PANTALLAS DE LA APLICACIÓN
# ==========================================
class VistaInicio(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # KPIs
        grid_kpi = QGridLayout()
        kpis = [
            ("Ventas del dia", "$28,560.00", "12.5% Hoy"),
            ("Ganancias del mes", "$152,430.00", "8.3% Este mes"),
            ("Productos por agotarse", "18", "Revisar inventario"),
            ("Alertas pendientes", "7", "Requiere atencion")
        ]

        for i, (titulo, valor, subtitulo) in enumerate(kpis):
            tarjeta = QFrame()
            tarjeta.setProperty("class", "tarjeta")
            t_layout = QVBoxLayout(tarjeta)
            lbl_t = QLabel(titulo)
            lbl_t.setStyleSheet("color: gray; font-size: 12px;")
            lbl_v = QLabel(valor)
            lbl_v.setStyleSheet("font-size: 20px; font-weight: bold; color: black;")
            lbl_s = QLabel(subtitulo)
            lbl_s.setStyleSheet("color: #FF7300; font-size: 11px;")
            t_layout.addWidget(lbl_t)
            t_layout.addWidget(lbl_v)
            t_layout.addWidget(lbl_s)
            grid_kpi.addWidget(tarjeta, 0, i)
        layout.addLayout(grid_kpi)

        cuerpo = QHBoxLayout()
        
        # Gráfica
        frame_grafica = QFrame()
        frame_grafica.setProperty("class", "tarjeta")
        layout_grafica = QVBoxLayout(frame_grafica)
        layout_grafica.addWidget(QLabel("<b>Ventas de la Semana</b>"))
        
        lienzo = LienzoGrafica(self, width=5, height=3)
        dias = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab']
        ventas = [12000, 15000, 11000, 18000, 25000, 28560]
        lienzo.axes.bar(dias, ventas, color='#FF7300')
        lienzo.axes.set_ylabel('Pesos ($)')
        layout_grafica.addWidget(lienzo)
        cuerpo.addWidget(frame_grafica, stretch=2)

        # Alertas
        frame_alertas = QFrame()
        frame_alertas.setProperty("class", "tarjeta")
        layout_alertas = QVBoxLayout(frame_alertas)
        layout_alertas.addWidget(QLabel("<b>Alertas Recientes</b>"))
        alertas = [
            "18 productos por agotarse (Hoy)",
            "3 pagos pendientes ($4,850) (Hoy)",
            "Respaldo completado (Ayer)",
            "Pedido programado: Truper (Ayer)"
        ]
        for a in alertas:
            lbl = QLabel(f"• {a}")
            lbl.setStyleSheet("padding: 10px; border-bottom: 1px solid #eee; color: #333;")
            layout_alertas.addWidget(lbl)
        layout_alertas.addStretch()
        cuerpo.addWidget(frame_alertas, stretch=1)

        layout.addLayout(cuerpo)

class VistaCajaVentas(QWidget):
    def __init__(self):
        super().__init__()
        self.total_actual = 0.0
        layout = QVBoxLayout(self)
        
        lbl_titulo = QLabel("Terminal Punto de Venta (TPV)")
        lbl_titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #FF7300;")
        layout.addWidget(lbl_titulo)

        caja_busqueda = QHBoxLayout()
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Nombre del producto o Codigo de Barras")
        
        self.input_precio = QLineEdit()
        self.input_precio.setPlaceholderText("Precio (ej. 50)")
        self.input_precio.setFixedWidth(150)
        
        btn_agregar = QPushButton("Agregar al Carrito")
        btn_agregar.setProperty("class", "btn-primario")
        btn_agregar.clicked.connect(self.agregar_al_carrito)
        
        caja_busqueda.addWidget(self.input_busqueda)
        caja_busqueda.addWidget(self.input_precio)
        caja_busqueda.addWidget(btn_agregar)
        layout.addLayout(caja_busqueda)

        self.tabla = QTableWidget(0, 4)
        self.tabla.setHorizontalHeaderLabels(["Cant.", "Producto", "Precio Unit.", "Subtotal"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla)

        self.lbl_total = QLabel("Total a Cobrar: $0.00")
        self.lbl_total.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.lbl_total)

        btn_cobrar = QPushButton("Procesar Cobro")
        btn_cobrar.setProperty("class", "btn-primario")
        btn_cobrar.setStyleSheet("font-size: 16px; padding: 15px;")
        btn_cobrar.clicked.connect(self.cobrar)
        layout.addWidget(btn_cobrar)

    def agregar_al_carrito(self):
        prod = self.input_busqueda.text()
        precio_str = self.input_precio.text()
        
        if prod and precio_str:
            try:
                precio = float(precio_str)
                fila = self.tabla.rowCount()
                self.tabla.insertRow(fila)
                self.tabla.setItem(fila, 0, QTableWidgetItem("1"))
                self.tabla.setItem(fila, 1, QTableWidgetItem(prod))
                self.tabla.setItem(fila, 2, QTableWidgetItem(f"${precio:.2f}"))
                self.tabla.setItem(fila, 3, QTableWidgetItem(f"${precio:.2f}"))
                
                self.total_actual += precio
                self.lbl_total.setText(f"Total a Cobrar: ${self.total_actual:,.2f}")
                
                self.input_busqueda.clear()
                self.input_precio.clear()
            except ValueError:
                QMessageBox.warning(self, "Error", "El precio debe ser un numero.")

    def cobrar(self):
        if self.total_actual > 0:
            QMessageBox.information(self, "Cobro Exitoso", f"Se cobro un total de ${self.total_actual:,.2f}\nImprimiendo ticket...")
            self.tabla.setRowCount(0)
            self.total_actual = 0.0
            self.lbl_total.setText("Total a Cobrar: $0.00")
        else:
            QMessageBox.warning(self, "Carrito Vacio", "Agrega productos antes de cobrar.")

class VistaInventario(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        lbl_titulo = QLabel("Inventario y Existencias")
        lbl_titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #FF7300;")
        layout.addWidget(lbl_titulo)

        caja_herramientas = QHBoxLayout()
        input_buscar = QLineEdit()
        input_buscar.setPlaceholderText("Buscar por SKU o Nombre...")
        btn_nuevo = QPushButton("Nuevo Producto")
        btn_nuevo.setProperty("class", "btn-primario")
        caja_herramientas.addWidget(input_buscar)
        caja_herramientas.addWidget(btn_nuevo)
        layout.addLayout(caja_herramientas)

        tabla = QTableWidget(8, 5)
        tabla.setHorizontalHeaderLabels(["SKU", "Producto", "Categoria", "Stock", "Estado"])
        tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        datos = [
            ("CM-50", "Cemento Holcim 50kg", "Construccion", "3", "Critico"), 
            ("PT-19", "Pintura Comex 19L Blanca", "Pinturas", "2", "Critico"),
            ("PVC-12", "Tubo PVC 1/2\"", "Plomeria", "45", "Optimo"), 
            ("TR-01", "Tornillo Pija 1\"", "Ferreteria", "500", "Optimo"),
            ("MT-05", "Martillo Truper 16oz", "Herramientas", "12", "Optimo"),
            ("CB-12", "Cable THW Cal. 12", "Electrico", "100", "Optimo"),
            ("FO-01", "Foco LED 10W Philips", "Electrico", "8", "Bajo"),
            ("BR-38", "Broca para concreto 3/8\"", "Herramientas", "5", "Critico")
        ]
        
        for f, fila in enumerate(datos):
            for c, val in enumerate(fila):
                item = QTableWidgetItem(val)
                if val == "Critico":
                    item.setForeground(Qt.GlobalColor.red)
                elif val == "Bajo":
                    item.setForeground(Qt.GlobalColor.darkYellow)
                tabla.setItem(f, c, item)
        layout.addWidget(tabla)

class VistaCompras(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        lbl_titulo = QLabel("Gestion de Compras")
        lbl_titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #FF7300;")
        layout.addWidget(lbl_titulo)

        btn_nuevo = QPushButton("Generar Orden de Compra")
        btn_nuevo.setProperty("class", "btn-primario")
        btn_nuevo.setFixedWidth(250)
        layout.addWidget(btn_nuevo)

        tabla = QTableWidget(4, 5)
        tabla.setHorizontalHeaderLabels(["Orden #", "Fecha", "Proveedor", "Monto Total", "Estado"])
        tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        datos = [
            ("OC-1045", "2026-07-20", "Truper S.A. de C.V.", "$12,500.00", "Recibido"),
            ("OC-1046", "2026-07-21", "Cemex Mexico", "$8,400.00", "En Transito"),
            ("OC-1047", "2026-07-22", "Pinturas Comex", "$3,200.00", "Pendiente"),
            ("OC-1048", "2026-07-22", "IUSA Material Electrico", "$5,150.00", "Borrador")
        ]

        for f, fila in enumerate(datos):
            for c, val in enumerate(fila):
                tabla.setItem(f, c, QTableWidgetItem(val))
        layout.addWidget(tabla)

class VistaProveedores(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        lbl_titulo = QLabel("Directorio de Proveedores")
        lbl_titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #FF7300;")
        layout.addWidget(lbl_titulo)

        tabla = QTableWidget(5, 4)
        tabla.setHorizontalHeaderLabels(["ID", "Empresa", "Contacto Comercial", "Telefono"])
        tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        datos = [
            ("PRV-01", "Truper S.A. de C.V.", "Carlos Slim H.", "555-123-4567"),
            ("PRV-02", "Cemex Mexico", "Ana Garcia", "555-987-6543"),
            ("PRV-03", "Pinturas Comex", "Luis Perez", "555-456-7890"),
            ("PRV-04", "IUSA Material Electrico", "Maria Lopez", "555-321-0987"),
            ("PRV-05", "Urrea Herramientas", "Jorge Ramos", "555-654-3210")
        ]

        for f, fila in enumerate(datos):
            for c, val in enumerate(fila):
                tabla.setItem(f, c, QTableWidgetItem(val))
        layout.addWidget(tabla)

class VistaSeguridad(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        lbl_titulo = QLabel("Seguridad y Respaldos")
        lbl_titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #FF7300;")
        layout.addWidget(lbl_titulo)

        frame_respaldo = QFrame()
        frame_respaldo.setProperty("class", "tarjeta")
        l_respaldo = QVBoxLayout(frame_respaldo)
        l_respaldo.addWidget(QLabel("<b>Copia de Seguridad (Backup)</b>"))
        l_respaldo.addWidget(QLabel("Ultimo respaldo exitoso: Hoy 02:00 AM. Se recomienda respaldar al cierre de caja."))
        
        btn_respaldo = QPushButton("Generar Respaldo de Base de Datos Ahora")
        btn_respaldo.setProperty("class", "btn-primario")
        btn_respaldo.clicked.connect(lambda: QMessageBox.information(self, "Respaldo", "Respaldo generado correctamente y cifrado en el disco local."))
        l_respaldo.addWidget(btn_respaldo)
        layout.addWidget(frame_respaldo)

        lbl_usuarios = QLabel("Gestion de Usuarios del Sistema")
        lbl_usuarios.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 15px;")
        layout.addWidget(lbl_usuarios)

        tabla = QTableWidget(3, 3)
        tabla.setHorizontalHeaderLabels(["Usuario", "Rol", "Ultimo Acceso"])
        tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        datos = [("admin", "Administrador Total", "Hace 5 min"), ("cajero_01", "Cajero", "Ayer 18:30"), ("almacen", "Inventario", "Hoy 08:00")]
        for f, fila in enumerate(datos):
            for c, val in enumerate(fila):
                tabla.setItem(f, c, QTableWidgetItem(val))
        layout.addWidget(tabla)

class VistaConfiguracion(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        lbl_titulo = QLabel("Configuracion del Sistema")
        lbl_titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #FF7300;")
        layout.addWidget(lbl_titulo)

        form_frame = QFrame()
        form_frame.setProperty("class", "tarjeta")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        form_layout.addRow(QLabel("<b>Datos del Ticket y Recibo</b>"))
        
        inp_nombre = QLineEdit("Ferreteria El Tuerca")
        form_layout.addRow("Nombre Comercial:", inp_nombre)
        
        inp_rfc = QLineEdit("XAXX010101000")
        form_layout.addRow("RFC:", inp_rfc)
        
        inp_dir = QLineEdit("Av. Principal 123, Colonia Centro")
        form_layout.addRow("Direccion:", inp_dir)
        
        inp_tel = QLineEdit("555-000-1111")
        form_layout.addRow("Telefono:", inp_tel)
        
        inp_impresora = QLineEdit("EPSON TM-T20III Receipt")
        form_layout.addRow("Impresora por Defecto:", inp_impresora)

        btn_guardar = QPushButton("Guardar Configuracion")
        btn_guardar.setProperty("class", "btn-primario")
        btn_guardar.clicked.connect(lambda: QMessageBox.information(self, "Guardado", "Configuracion actualizada para futuros tickets."))
        form_layout.addRow("", btn_guardar)

        layout.addWidget(form_frame)
        layout.addStretch()

class VistaReportes(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        lbl_titulo = QLabel("Generador de Reportes Analiticos")
        lbl_titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #FF7300;")
        layout.addWidget(lbl_titulo)

        btn_excel = QPushButton("Descargar Reporte de Ventas (Excel/CSV)")
        btn_excel.setProperty("class", "btn-primario")
        btn_excel.setMinimumHeight(60)
        btn_excel.clicked.connect(self.descargar_excel)
        layout.addWidget(btn_excel)

        btn_pdf = QPushButton("Descargar Resumen de Inventario (Documento TXT)")
        btn_pdf.setProperty("class", "btn-secundario")
        btn_pdf.setMinimumHeight(60)
        btn_pdf.clicked.connect(self.descargar_doc)
        layout.addWidget(btn_pdf)
        
        layout.addStretch()

    def descargar_excel(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Reporte", "Ventas_Ferreteria.csv", "CSV Files (*.csv)")
        if ruta:
            df = pd.DataFrame({"Fecha": [datetime.now().strftime("%Y-%m-%d")], "Total Ventas": [28560], "Productos": [150]})
            df.to_csv(ruta, index=False)
            QMessageBox.information(self, "Exito", f"Reporte guardado en:\n{ruta}")

    def descargar_doc(self):
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Resumen", "Inventario.txt", "Text Files (*.txt)")
        if ruta:
            with open(ruta, 'w', encoding='utf-8') as f:
                f.write(f"--- RESUMEN DE INVENTARIO ---\nFecha: {datetime.now().strftime('%Y-%m-%d')}\n")
                f.write("Productos Criticos:\n- Cemento Holcim 50kg (Stock: 3)\n- Pintura Comex 19L (Stock: 2)\n")
            QMessageBox.information(self, "Exito", f"Documento guardado en:\n{ruta}")

# ==========================================
# 4. VENTANA PRINCIPAL Y ENRUTADOR
# ==========================================
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mi Ferreteria - Sistema de Gestion")
        self.resize(1100, 700)

        self.stack_principal = QStackedWidget()
        self.setCentralWidget(self.stack_principal)

        self.vista_login = VistaLogin(self.iniciar_sesion)
        self.vista_app = self.crear_interfaz_app()

        self.stack_principal.addWidget(self.vista_login)
        self.stack_principal.addWidget(self.vista_app)

    def iniciar_sesion(self):
        self.stack_principal.setCurrentIndex(1)

    def cerrar_sesion(self):
        self.stack_principal.setCurrentIndex(0)

    def crear_interfaz_app(self):
        widget_app = QWidget()
        layout_app = QHBoxLayout(widget_app)
        layout_app.setContentsMargins(0, 0, 0, 0)
        layout_app.setSpacing(0)

        # SIDEBAR
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        layout_sidebar = QVBoxLayout(sidebar)
        
        lbl_logo = QLabel("Mi\nFerreteria")
        lbl_logo.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin: 20px 0;")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_sidebar.addWidget(lbl_logo)

        opciones = ["Inicio", "Caja y Ventas", "Inventario", "Compras", "Proveedores", "Seguridad", "Configuracion", "Reportes"]
        self.botones_menu = []
        
        for i, op in enumerate(opciones):
            btn = QPushButton(op)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self.cambiar_pantalla(idx))
            self.botones_menu.append(btn)
            layout_sidebar.addWidget(btn)

        layout_sidebar.addStretch()
        
        btn_salir = QPushButton("Cerrar Sesion")
        btn_salir.clicked.connect(self.cerrar_sesion)
        layout_sidebar.addWidget(btn_salir)

        # ÁREA PRINCIPAL
        self.stack_contenido = QStackedWidget()
        self.stack_contenido.addWidget(VistaInicio())       # 0
        self.stack_contenido.addWidget(VistaCajaVentas())   # 1
        self.stack_contenido.addWidget(VistaInventario())   # 2
        self.stack_contenido.addWidget(VistaCompras())      # 3
        self.stack_contenido.addWidget(VistaProveedores())  # 4
        self.stack_contenido.addWidget(VistaSeguridad())    # 5
        self.stack_contenido.addWidget(VistaConfiguracion())# 6
        self.stack_contenido.addWidget(VistaReportes())     # 7

        layout_app.addWidget(sidebar)
        layout_app.addWidget(self.stack_contenido)

        self.botones_menu[0].setChecked(True)
        return widget_app

    def cambiar_pantalla(self, indice):
        for btn in self.botones_menu:
            btn.setChecked(False)
        self.botones_menu[indice].setChecked(True)
        self.stack_contenido.setCurrentIndex(indice)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(ESTILO_GLOBAL)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())