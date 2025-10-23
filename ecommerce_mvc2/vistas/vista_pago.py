import flet as ft
import webbrowser
import mercadopago

class VistaPasarelaPago:
    def __init__(self, pagina, usuario, carrito, total, controlador_pago):
        self.pagina = pagina
        self.usuario = usuario
        self.carrito = carrito
        self.total = total
        self.controlador = controlador_pago
        self.crear_pasarela()

    def crear_pasarela(self):
        # Panel izquierdo: Detalles del pedido
        panel_izquierdo = ft.Container(
            content=ft.Column([
                ft.Text("Importe:", size=16, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text(f"${self.total:,.2f}", size=20, weight=ft.FontWeight.BOLD, color="#4fc3f7"),
                ft.Text(f"ID: {self.controlador.obtener_id_pedido()}", size=12, color="white"),
                ft.Text(f"Fecha: {self.controlador.obtener_fecha_actual()}", size=12, color="white"),
                ft.Text("Método de pago: MercadoPago", size=12, color="white"),
                ft.Text("Estado del pago: Pendiente", size=12, color="white"),
                ft.Divider(color="#333333"),
                ft.Text("Productos:", size=14, weight=ft.FontWeight.BOLD, color="white"),
                *[ft.Text(f"- {item['descripcion_final']} x{item['cantidad']}", size=12, color="white") 
                  for item in self.carrito.values()]
            ], spacing=5, alignment="start"),
            bgcolor="#2d2d2d",
            padding=15,
            border=ft.border.all(1, "#444444"),
            border_radius=10,
            width=280
        )

        # Panel derecho: Información de pago
        panel_derecho = ft.Container(
            content=ft.Column([
                ft.Text("PAGO CON MERCADOPAGO", size=16, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=10),
                ft.Icon(ft.Icons.PAYMENT, size=50, color="#00B2FF"),
                ft.Container(height=10),
                ft.Text("Serás redirigido a MercadoPago para completar tu pago de forma segura.", 
                       size=14, color="white", text_align=ft.TextAlign.CENTER),
                ft.Container(height=20),
                ft.Text("Ventajas de MercadoPago:", size=12, weight=ft.FontWeight.BOLD, color="#4fc3f7"),
                ft.Text("• Pago 100% seguro", size=11, color="white"),
                ft.Text("• Múltiples métodos de pago", size=11, color="white"),
                ft.Text("• Protección al comprador", size=11, color="white"),
                ft.Text("• Procesamiento instantáneo", size=11, color="white"),
                ft.Container(height=20),
                ft.Row([
                    ft.ElevatedButton("CANCELAR", 
                                    bgcolor="#d32f2f", 
                                    color="white", 
                                    on_click=self.cancelar_pago,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))),
                    ft.ElevatedButton("PAGAR CON MERCADOPAGO", 
                                    bgcolor="#00B2FF", 
                                    color="white", 
                                    on_click=self.completar_pago,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))),
                ], spacing=10)
            ], spacing=10, alignment="start"),
            bgcolor="#2d2d2d",
            padding=20,
            border=ft.border.all(1, "#444444"),
            border_radius=10,
            width=320
        )

        # Barra superior
        barra_superior = ft.Row([
            ft.ElevatedButton("⬅️ Volver al carrito", 
                            on_click=self.cancelar_pago,
                            style=ft.ButtonStyle(
                                bgcolor="#333333",
                                color="white",
                                shape=ft.RoundedRectangleBorder(radius=5)
                            )),
            ft.Container(expand=True),
            ft.Text("Pasarela de Pago - MercadoPago", size=20, weight="bold", color="white")
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Layout principal
        self.contenido = ft.Column([
            barra_superior,
            ft.Divider(color="#333333"),
            ft.Row(
                [panel_izquierdo, panel_derecho],
                alignment="center",
                spacing=20,
            )
        ], spacing=20)

    def mostrar(self):
        self.pagina.clean()
        self.pagina.add(self.contenido)
    
    def cancelar_pago(self, e):
        self.controlador.cancelar_pago()
    
    def completar_pago(self, e):
        self.controlador.procesar_pago_mercadopago()
    
    def mostrar_redireccion(self, url_pago):
        contenido = ft.Column([
            ft.Icon(ft.Icons.AUTORENEW, size=60, color="#00B2FF"),
            ft.Text("Redirigiendo a MercadoPago...", size=24, weight="bold", color="white"),
            ft.Container(height=20),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("✅ Pedido creado exitosamente", size=18, weight="bold", color="green"),
                        ft.Text(f"ID del pedido: {self.controlador.obtener_id_pedido()}", size=16),
                        ft.Text(f"Total: ${self.total:,.2f}", size=16),
                        ft.Text(f"Cliente: {self.usuario['email']}", size=14),
                        ft.Container(height=20),
                        ft.Text("Haz clic en el botón para completar el pago:", size=14),
                        ft.ElevatedButton(
                            "🎯 Ir a MercadoPago para Pagar",
                            on_click=lambda e: webbrowser.open(url_pago),
                            style=ft.ButtonStyle(
                                bgcolor="#00B2FF",
                                color=ft.Colors.WHITE,
                                padding=20
                            )
                        ),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "Volver al Inicio",
                            on_click=lambda e: self.controlador.finalizar_compra(),
                            style=ft.ButtonStyle(
                                bgcolor="#333333",
                                color="white"
                            )
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=30
                ),
                width=500
            )
        ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.pagina.clean()
        self.pagina.add(contenido)

    def mostrar_error(self, mensaje):
        snack_bar = ft.SnackBar(
            content=ft.Text(mensaje),
            bgcolor=ft.Colors.RED,
            duration=5000
        )
        self.pagina.snack_bar = snack_bar
        snack_bar.open = True
        self.pagina.update()