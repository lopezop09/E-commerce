import flet as ft

class ControladorPrincipal:
    def __init__(self, pagina):
        self.pagina = pagina
        # Importación diferida para evitar circular imports
        from modelos.base_de_datos import BaseDatos
        self.base_datos = BaseDatos()
        self.usuario_actual = None
        self.carrito_actual = {}
        
        # Inicializar controladores (importación diferida)
        from .controlador_productos import ControladorProductos
        from .controlador_carrito import ControladorCarrito
        from .controlador_pagos import ControladorPagos
        from .controlador_admin import ControladorAdmin
        from .controlador_vendedor import ControladorVendedor
        
        self.controlador_productos = ControladorProductos(pagina, self)
        self.controlador_carrito = ControladorCarrito(pagina, self)
        self.controlador_pagos = ControladorPagos(pagina, self)
        self.controlador_admin = ControladorAdmin(pagina, self)
        self.controlador_vendedor = ControladorVendedor(pagina, self)
        
        # Inicializar vista principal (importación diferida)
        from vistas.vista_principal import VistaPrincipal
        self.vista_principal = VistaPrincipal(pagina, self)

    def mostrar_principal(self, usuario, carrito=None):
        print(f"🔍 DEBUG: Mostrando principal para usuario {usuario['email']}")
        self.usuario_actual = usuario
        if carrito:
            self.carrito_actual = carrito
        
        productos, categorias, marcas = self.base_datos.cargar_productos()
        print(f"🔍 DEBUG: {len(productos)} productos cargados para vista principal")
        
        self.vista_principal.mostrar(usuario, productos, self.carrito_actual)

    def mostrar_detalle_producto(self, producto):
        self.controlador_productos.mostrar_detalle(producto, self.carrito_actual)

    def mostrar_carrito(self, carrito):
        self.controlador_carrito.mostrar_carrito(self.usuario_actual, carrito)

    def mostrar_panel_administrador(self):
        self.controlador_admin.mostrar_panel(self.usuario_actual)

    def mostrar_panel_vendedor(self):
        self.controlador_vendedor.mostrar_panel(self.usuario_actual)

    def mostrar_devolucion_rapida(self):
        """Método directo para mostrar devolución rápida - VERSIÓN COMPLETA"""
        print("🔍 DEBUG: mostrar_devolucion_rapida() ejecutándose")
        
        # Crear interfaz simple directamente aquí para probar
        campo_pedido = ft.TextField(
            label="ID del Pedido a devolver", 
            width=300,
            hint_text="Ej: ABC123"
        )
        
        campo_monto = ft.TextField(
            label="Monto a devolver", 
            width=200, 
            prefix_text="$",
            hint_text="0.00"
        )
        
        campo_motivo = ft.TextField(
            label="Motivo de la devolución", 
            width=400, 
            multiline=True,
            max_lines=3,
            hint_text="Describe brevemente el motivo..."
        )
        
        mensaje = ft.Text("", color=ft.Colors.BLUE, size=12)
        
        def procesar_devolucion(e):
            # Validaciones
            if not campo_pedido.value or not campo_pedido.value.strip():
                mensaje.value = "❌ Ingresa el ID del pedido"
                mensaje.color = ft.Colors.RED
                self.pagina.update()
                return
                
            if not campo_monto.value:
                mensaje.value = "❌ Ingresa el monto a devolver"
                mensaje.color = ft.Colors.RED
                self.pagina.update()
                return
            
            try:
                # Procesar devolución
                monto = float(campo_monto.value)
                pedido_id = campo_pedido.value.strip()
                motivo = campo_motivo.value or "Devolución solicitada"
                
                # Simular procesamiento con MercadoPago
                print(f"🔄 Procesando devolución para pedido {pedido_id}")
                print(f"💰 Monto: ${monto:,.2f}")
                print(f"📝 Motivo: {motivo}")
                
                # Simular éxito
                mensaje.value = f"✅ Reembolso de ${monto:,.2f} procesado exitosamente para pedido {pedido_id}"
                mensaje.color = ft.Colors.GREEN
                
                # Limpiar campos
                campo_pedido.value = ""
                campo_monto.value = ""
                campo_motivo.value = ""
                
            except ValueError:
                mensaje.value = "❌ El monto debe ser un número válido"
                mensaje.color = ft.Colors.RED
            except Exception as e:
                mensaje.value = f"❌ Error: {str(e)}"
                mensaje.color = ft.Colors.RED
                
            self.pagina.update()
        
        def volver(e):
            usuario_actual = self.get_usuario_actual()
            carrito_actual = self.get_carrito_actual()
            self.mostrar_principal(usuario_actual, carrito_actual)
        
        # Interfaz simple
        contenido = ft.Column([
            ft.Row([
                ft.ElevatedButton("⬅️ Volver al Inicio", on_click=volver),
                ft.Container(expand=True),
                ft.Text("DEVOLUCIÓN RÁPIDA", size=24, weight="bold", color=ft.Colors.PURPLE),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Devoluciones", size=18, weight="bold"),
                        ft.Text("Procesar reembolso", size=14, color="gray"),
                        ft.Divider(),
                        
                        ft.Row([campo_pedido], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([campo_monto], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([campo_motivo], alignment=ft.MainAxisAlignment.CENTER),
                        
                        ft.Container(height=20),
                        
                        ft.Row([
                            ft.ElevatedButton(
                                "PROCESAR DEVOLUCIÓN",
                                on_click=procesar_devolucion,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.PURPLE,
                                    color=ft.Colors.WHITE,
                                    padding=20
                                )
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        
                        ft.Container(height=10),
                        mensaje,
                        
                        ft.Container(height=20),
                        ft.Text("💡 Información importante:", size=12, weight="bold", color="blue"),
                        ft.Text("• El reembolso se procesará a través de MercadoPago y puede tomar de 5 a 10 dias habiles", size=11, color="gray"),
                        ft.Text("• El dinero será devuelto al método de pago original", size=11, color="gray"),
                        ft.Text("• El proceso puede tomar de 5 a 10 días hábiles", size=11, color="gray"),
                    ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=30,
                    width=500
                )
            )
        ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.pagina.clean()
        self.pagina.add(contenido)

    def buscar_productos(self, query):
        productos, categorias, marcas = self.base_datos.cargar_productos()
        
        if not query:
            self.vista_principal.mostrar(self.usuario_actual, productos, self.carrito_actual)
            return

        query = query.lower()
        resultados = []
        
        for producto in productos:
            if (query in producto['nombre'].lower() or 
                query in producto['marca'].lower() or 
                query in producto['categoria'].lower()):
                resultados.append(producto)
        
        # Actualizar vista con resultados
        self.vista_principal.mostrar(self.usuario_actual, resultados, self.carrito_actual)

    def cerrar_sesion(self):
        from controladores.controlador_auth import ControladorAuth
        controlador_auth = ControladorAuth(self.pagina)
        controlador_auth.set_controlador_principal(self)
        controlador_auth.mostrar_login()

    def actualizar_carrito(self, carrito):
        self.carrito_actual = carrito
        self.vista_principal.actualizar_contador_carrito()

    def get_usuario_actual(self):
        return self.usuario_actual

    def get_carrito_actual(self):
        return self.carrito_actual