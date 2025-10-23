import flet as ft
from modelos import Observador, DecoradorDescuento, DecoradorEnvio

class VistaDetalleProducto(Observador):
    def __init__(self, pagina, producto, controlador_producto):
        self.pagina = pagina
        self.producto_base = producto
        self.producto_actual = producto
        self.controlador = controlador_producto
        self.crear_interfaz()

    def crear_interfaz(self):
        caja_imagen = ft.Container(
            content=ft.Text(self.producto_base.imagen, size=40),
            width=140,
            height=140,
            alignment=ft.alignment.center,
            border=ft.border.all(1, "black"),
            bgcolor="white",
        )

        self.texto_nombre = ft.Text(self.producto_actual.obtener_descripcion(), size=20, weight="bold")
        self.texto_precio = ft.Text(f"${self.producto_actual.obtener_precio():,.2f}", size=18, color="green")
        
        self.checkbox_descuento = ft.Checkbox(label="Aplicar cupón 20% descuento", on_change=self.actualizar_precio)
        self.checkbox_envio = ft.Checkbox(label="Aplicar envío ultra rápido", on_change=self.actualizar_precio)

        self.mensajes = ft.Column([], spacing=5, scroll="auto")

        barra_superior = ft.Row(
            controls=[
                ft.ElevatedButton("⬅️ Volver", on_click=self.volver),
                ft.Container(expand=True),
                ft.Text("Detalle del Producto", size=20, weight="bold")
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        contenido = ft.Column(
            [
                barra_superior,
                ft.Divider(),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Row([caja_imagen], alignment="center"),
                                self.texto_nombre,
                                self.texto_precio,
                                ft.Text(self.producto_base.descripcion, size=12, color="gray"),
                                ft.Divider(),
                                self.checkbox_descuento,
                                self.checkbox_envio,
                                ft.Row(
                                    [
                                        ft.ElevatedButton("Añadir al carrito", on_click=self.agregar_al_carrito, bgcolor="blue", color="white"),
                                    ],
                                    alignment="center",
                                    spacing=20,
                                )
                            ],
                            horizontal_alignment="center",
                            spacing=10,
                        ),
                        padding=20,
                    ),
                ),
                ft.Text("Eventos:", size=16, weight="bold"),
                self.mensajes
            ],
            horizontal_alignment="center",
            spacing=15,
            expand=True
        )

        self.pagina.clean()
        self.pagina.add(contenido)
    
    def actualizar_precio(self, e=None):
        self.producto_actual = self.producto_base
        
        if self.checkbox_descuento.value:
            self.producto_actual = DecoradorDescuento(self.producto_actual, 0.2)
        if self.checkbox_envio.value:
            self.producto_actual = DecoradorEnvio(self.producto_actual)

        self.texto_nombre.value = self.producto_actual.obtener_descripcion()
        self.texto_precio.value = f"${self.producto_actual.obtener_precio():,.2f}"
        self.pagina.update()
    
    def agregar_al_carrito(self, e):
        producto_dict = self.producto_base.to_dict()
        producto_dict['precio_final'] = self.producto_actual.obtener_precio()
        producto_dict['descripcion_final'] = self.producto_actual.obtener_descripcion()
        
        self.controlador.agregar_al_carrito(producto_dict)
    
    def actualizar(self, mensaje):
        self.mensajes.controls.append(ft.Text(mensaje, color="blue"))
        self.pagina.update()
    
    def volver(self, e):
        self.controlador.volver_principal()