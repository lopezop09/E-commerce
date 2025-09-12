import flet as ft

# --- OBSERVER ---
class Observer:
    def actualizar(self, mensaje):
        pass

class ProductSubject:
    def __init__(self):
        self._observadores = []

    def agregar(self, observador):
        self._observadores.append(observador)

    def notificar(self, mensaje):
        for observador in self._observadores:
            observador.actualizar(mensaje)

# --- DECORATOR ---
class Producto:
    def __init__(self, nombre, precio):
        self.nombre = nombre
        self.precio = precio

    def get_precio(self):
        return self.precio

    def get_descripcion(self):
        return self.nombre

class ProductoDecorador(Producto):
    def __init__(self, producto):
        self._producto = producto

    def get_precio(self):
        return self._producto.get_precio()

    def get_descripcion(self):
        return self._producto.get_descripcion()

class DescuentoDecorador(ProductoDecorador):
    def __init__(self, producto, descuento):
        super().__init__(producto)
        self.descuento = descuento

    def get_precio(self):
        return self._producto.get_precio() * (1 - self.descuento)

    def get_descripcion(self):
        return f"{self._producto.get_descripcion()} (Descuento {int(self.descuento*100)}%)"

class EnvioDecorador(ProductoDecorador):
    def get_precio(self):
        return self._producto.get_precio() + 20000

    def get_descripcion(self):
        return f"{self._producto.get_descripcion()} + envío extra"

# --- FLET APP ---
def main(page: ft.Page):
    page.title = "Detalle de Producto"
    page.bgcolor = "#f9f9f9"
    page.window_width = 500
    page.window_height = 500

    producto = Producto("Nombre del producto", 60000)  
    subject = ProductSubject()

    # Elementos UI
    image_box = ft.Container(
        content=ft.Text("IMAGEN", color="gray", weight="bold", size=12),
        width=140,
        height=140,
        alignment=ft.alignment.center,
        border=ft.border.all(1, "black"),
        bgcolor="white",
    )

    nombre_texto = ft.Text(producto.get_descripcion(), size=20, weight="bold", color="white")
    precio_texto = ft.Text(f"${producto.get_precio():,.0f}", size=18, color="green")

    descuento_checkbox = ft.Checkbox(label="Aplicar cupón 20% descuento")
    envio_checkbox = ft.Checkbox(label="Aplicar envío ultra rápido (+20.000$)")

    mensajes = ft.Column([], spacing=5, scroll="auto")

    # --- Funciones ---
    def actualizar_precio(e):
        nonlocal producto
        producto_modificado = producto
        if descuento_checkbox.value:
            producto_modificado = DescuentoDecorador(producto_modificado, 0.2)
        if envio_checkbox.value:
            producto_modificado = EnvioDecorador(producto_modificado)

        nombre_texto.value = producto_modificado.get_descripcion()
        precio_texto.value = f"${producto_modificado.get_precio():,.0f}"
        page.update()

    def al_carrito(e):
        mensaje = f"'{producto.get_descripcion()}' añadido al carrito"
        mensajes.controls.append(ft.Text(mensaje, color="blue"))
        page.update()

    # --- Layout ---
    page.add(
        ft.Column(
            [
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                image_box,
                                nombre_texto,
                                precio_texto,
                                ft.Divider(),
                                descuento_checkbox,
                                envio_checkbox,
                                ft.Row(
                                    [
                                        ft.ElevatedButton("Actualizar precio", on_click=actualizar_precio, bgcolor="blue", color="white"),
                                        ft.ElevatedButton("Añadir al carrito", on_click=al_carrito, bgcolor="black", color="white"),
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
                mensajes
            ],
            horizontal_alignment="center",
            spacing=15,
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
