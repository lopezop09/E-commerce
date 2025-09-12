import flet as ft

class TarjetaProducto(ft.Container):
    def __init__(self, nombre, precio, precio_anterior=None, descuento=None):
        super().__init__()
        self.content = ft.Column(
            [
                # Imagen placeholder
                ft.Container(
                    content=ft.Text("IMAGEN", color="gray"),
                    width=150,
                    height=100,
                    alignment=ft.alignment.center,
                    border=ft.border.all(1, "black"),
                ),
                # Nombre del producto
                ft.Text(nombre, weight="bold", color="black"),
                # Precio y descuento
                ft.Row(
                    [
                        # Precio principal
                        ft.Text(
                            f"COP ${precio:,.0f}".replace(",", "."),
                            weight="bold",
                            color="black"
                        ),
                        # Precio anterior (si existe)
                        ft.Text(
                            f"COP ${precio_anterior:,.0f}".replace(",", ".") if precio_anterior else "",
                            color="gray",
                            weight="w400",
                            size=12,
                            style=ft.TextThemeStyle.BODY_SMALL,
                        ),
                        # Descuento (si existe)
                        ft.Text(
                            f"-{descuento}%" if descuento else "",
                            color="red",
                            size=12,
                            weight="bold",
                        ),
                    ]
                ),
            ],
            horizontal_alignment="center",
            spacing=5,
        )
        self.padding = 10
        self.border = ft.border.all(0.5, "lightgray")
        self.border_radius = 15
        self.width = 200


def main(page: ft.Page):
    page.title = "E-commerce"
    page.scroll = "auto"
    page.padding = 20
    page.bgcolor = "white"

    # Título principal
    encabezado = ft.Text("E-commerce", size=30, weight="bold", color="black")

    # Sección nuevos productos
    nuevos_titulo = ft.Text("NUEVOS PRODUCTOS", size=20, weight="bold", color="black")
    nuevos_row = ft.Row(
        [
            TarjetaProducto("Producto 1", 120000),
            TarjetaProducto("Producto 2", 240000, 260000, 20),
            TarjetaProducto("Producto 3", 180000),
            TarjetaProducto("Producto 4", 130000, 160000, 20),
        ],
        alignment="spaceAround",
        wrap=True,
    )
    expandir_nuevos = ft.ElevatedButton("Expandir")

    # Sección más vendidos
    mas_titulo = ft.Text("MÁS VENDIDOS", size=20, weight="bold", color="black")
    mas_row = ft.Row(
        [
            TarjetaProducto("Producto A", 212000, 232000, 20),
            TarjetaProducto("Producto B", 145000),
            TarjetaProducto("Producto C", 80000),
            TarjetaProducto("Producto D", 210000),
        ],
        alignment="spaceAround",
        wrap=True,
    )
    expandir_mas = ft.ElevatedButton("Expandir")

    # Layout final
    page.add(
        encabezado,
        ft.Divider(),
        nuevos_titulo,
        nuevos_row,
        expandir_nuevos,
        ft.Divider(),
        mas_titulo,
        mas_row,
        expandir_mas,
    )

ft.app(target=main)
