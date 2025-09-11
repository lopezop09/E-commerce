import flet as ft

class ProductCard(ft.Container):
    def __init__(self, name, price, old_price=None, discount=None):
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
                ft.Text(name, weight="bold", color="black"),
                # Precio y descuento
                ft.Row(
                    [
                        ft.Text(f"${price:,}", weight="bold", color="black"),
                        ft.Text(
                            f"${old_price:,}" if old_price else "",
                            color="gray",
                            weight="w400",
                            size=12,
                            style=ft.TextThemeStyle.BODY_SMALL,
                        ),
                        ft.Text(
                            f"-{discount}%" if discount else "",
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
        self.border_radius = 10
        self.width = 180


def main(page: ft.Page):
    page.title = "E-commerce"
    page.scroll = "auto"
    page.padding = 20
    page.bgcolor = "white"

    # Título principal
    header = ft.Text("E-commerce", size=30, weight="bold", color="black")

    # Sección nuevos productos
    nuevos_title = ft.Text("NUEVOS PRODUCTOS", size=20, weight="bold", color="black")
    nuevos_row = ft.Row(
        [
            ProductCard("Producto 1", 120),
            ProductCard("Producto 2", 240, 260, 20),
            ProductCard("Producto 3", 180),
            ProductCard("Producto 4", 130, 160, 20),
        ],
        alignment="spaceAround",
        wrap=True,
    )
    expand_nuevos = ft.ElevatedButton("Expandir")

    # Sección más vendidos
    mas_title = ft.Text("MÁS VENDIDOS", size=20, weight="bold", color="black")
    mas_row = ft.Row(
        [
            ProductCard("Producto A", 212, 232, 20),
            ProductCard("Producto B", 145),
            ProductCard("Producto C", 80),
            ProductCard("Producto D", 210),
        ],
        alignment="spaceAround",
        wrap=True,
    )
    expand_mas = ft.ElevatedButton("Expandir")

    # Layout final
    page.add(
        header,
        ft.Divider(),
        nuevos_title,
        nuevos_row,
        expand_nuevos,
        ft.Divider(),
        mas_title,
        mas_row,
        expand_mas,
    )


ft.app(target=main)
