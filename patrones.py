import flet as ft

# --- OBSERVER ---
class Observer:
    def actualizar(self, message):
        pass

class ProductSubject:
    def __init__(self):
        self._observers = []

    def agregar(self, observer):
        self._observers.append(observer)

    def notify(self, message):
        for observer in self._observers:
            observer.actualizar(message)

# --- DECORATOR ---
class Product:
    def __init__(self, name, precio):
        self.name = name
        self.precio = precio

    def get_precio(self):
        return self.precio

    def get_descripcion(self):
        return self.name

class ProductDecorator(Product):
    def __init__(self, product):
        self._product = product

    def get_precio(self):
        return self._product.get_precio()

    def get_descripcion(self):
        return self._product.get_descripcion()

class DescuentoDecorator(ProductDecorator):
    def __init__(self, product, descuento):
        super().__init__(product)
        self.descuento = descuento

    def get_precio(self):
        return self._product.get_precio() * (1 - self.descuento)

    def get_descripcion(self):
        return f"{self._product.get_descripcion()} (Descuento {int(self.descuento*100)}%)"

class EnvioDecorator(ProductDecorator):
    def get_precio(self):
        return self._product.get_precio() + 20000

    def get_descripcion(self):
        return f"{self._product.get_descripcion()} + envío extra"

# --- FLET APP ---
def main(page: ft.Page):
    page.title = "Detalle de Producto"
    page.bgcolor = "#f9f9f9"
    page.window_width = 500
    page.window_height = 500

    product = Product("Nombre del producto", 60000) #color=ft.colors.WHITE
    subject = ProductSubject()

    # UI Elements
    image_box = ft.Container(
        content=ft.Text("IMAGEN", color="gray", weight="bold", size=12),
        width=140,
        height=140,
        alignment=ft.alignment.center,
        border=ft.border.all(1, "black"),
        bgcolor="white",
    )

    name_text = ft.Text(product.get_descripcion(), size=20, weight="bold", color="white")
    precio_text = ft.Text(f"${product.get_precio():,.0f}", size=18, color="green")

    descuento_checkbox = ft.Checkbox(label="Aplicar cupón 20% descuento")
    envio_checkbox = ft.Checkbox(label="Aplicar envío ultra rápido (+20.000$)")

    mensajes = ft.Column([], spacing=5, scroll="auto")

    # --- Functions ---
    def actualizar_precio(e):
        nonlocal product
        decorated_product = product
        if descuento_checkbox.value:
            decorated_product = DescuentoDecorator(decorated_product, 0.2)
        if envio_checkbox.value:
            decorated_product = EnvioDecorator(decorated_product)

        name_text.value = decorated_product.get_descripcion()
        precio_text.value = f"${decorated_product.get_precio():,.0f}"
        page.update()

    def al_carrito(e):
        mensaje = f"'{product.get_descripcion()}' añadido al carrito"
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
                                name_text,
                                precio_text,
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
