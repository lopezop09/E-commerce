import flet as ft

class VistaCarrito:
    def __init__(self, pagina, usuario, carrito, controlador_carrito):
        self.pagina = pagina
        self.usuario = usuario
        self.carrito = carrito
        self.controlador = controlador_carrito
        self.crear_controles()

    def crear_controles(self):
        barra_superior = ft.Row(
            controls=[
                ft.ElevatedButton("⬅️ Volver", on_click=self.volver),
                ft.Container(expand=True),
                ft.Text("🛒 Carrito de Compras", size=20, weight="bold")
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        if not self.carrito:
            self.contenido = ft.Column([
                barra_superior,
                ft.Text("Tu carrito está vacío", size=18, color="gray"),
                ft.ElevatedButton("Seguir comprando", on_click=self.volver)
            ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        else:
            productos_carrito = []
            total = 0
            
            for producto_id, item in self.carrito.items():
                subtotal = item['precio_final'] * item['cantidad']
                total += subtotal
                
                productos_carrito.append(
                    ft.Row([
                        ft.Text(f"{item['descripcion_final']}", size=16, weight="bold", width=200),
                        ft.Text(f"${item['precio_final']:,.2f}", width=100),
                        ft.Row([
                            ft.IconButton(ft.Icons.REMOVE, on_click=lambda e, id=producto_id: self.actualizar_cantidad(id, -1)),
                            ft.Text(f"{item['cantidad']}", width=30, text_align=ft.TextAlign.CENTER),
                            ft.IconButton(ft.Icons.ADD, on_click=lambda e, id=producto_id: self.actualizar_cantidad(id, 1)),
                        ]),
                        ft.Text(f"${subtotal:,.2f}", width=100, color="green", weight="bold"),
                        ft.IconButton(ft.Icons.DELETE, icon_color="red", 
                                    on_click=lambda e, id=producto_id: self.eliminar_producto(id))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            
            productos_carrito.append(ft.Divider())
            productos_carrito.append(
                ft.Row([
                    ft.Text("TOTAL:", size=18, weight="bold"),
                    ft.Text(f"${total:,.2f}", size=18, color="green", weight="bold")
                ], alignment=ft.MainAxisAlignment.END)
            )
            
            botones_accion = ft.Row([
                ft.ElevatedButton(
                    "Finalizar Compra", 
                    on_click=lambda e: self.procesar_pago(total), 
                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
                    width=200
                ),
                ft.ElevatedButton(
                    "Seguir Comprando", 
                    on_click=self.volver,
                    width=200
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
            
            productos_carrito.append(botones_accion)
            
            self.contenido = ft.Column([
                barra_superior,
                *productos_carrito
            ], spacing=15)

    def mostrar(self):
        self.pagina.clean()
        self.pagina.add(self.contenido)
    
    def actualizar_cantidad(self, producto_id, cambio):
        if producto_id in self.carrito:
            self.carrito[producto_id]['cantidad'] += cambio
            
            if self.carrito[producto_id]['cantidad'] <= 0:
                del self.carrito[producto_id]
        
        self.controlador.actualizar_carrito(self.carrito)
    
    def eliminar_producto(self, producto_id):
        if producto_id in self.carrito:
            del self.carrito[producto_id]
        
        self.controlador.actualizar_carrito(self.carrito)
    
    def procesar_pago(self, total):
        self.controlador.mostrar_pasarela_pago(self.carrito, total)
    
    def volver(self, e):
        self.controlador.volver_principal(self.carrito)