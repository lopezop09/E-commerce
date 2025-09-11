import flet as ft

def main(page: ft.Page):
    page.title = "Pasarela de Pago"
    page.bgcolor = "white"
    page.window_width = 650
    page.window_height = 400

    # --- LEFT PANEL: Detalles del pedido ---
    detalles = [
        ("Comercio:", "Tienda Online"),
        ("Terminal:", "335255568-1"),
        ("Pedido:", "00005189416"),
        ("Fecha:", "DD/MM/AAAA 00:00"),
        ("Descripción producto:", "Pedido 5189"),
    ]

    left_panel = ft.Container(
        content=ft.Column([
            ft.Text("Importe:", size=16, weight=ft.FontWeight.BOLD, color="black"),
            ft.Text("50,000 $", size=20, weight=ft.FontWeight.BOLD, color="blue"),
            *[ft.Text(f"{k} {v}", size=12, color="black") for k, v in detalles]
        ], spacing=5, alignment="start"),
        bgcolor="#E6F2FF",
        padding=15,
        border=ft.border.all(1, "black"),
        width=280
    )

    # --- RIGHT PANEL: Formulario de pago ---
    num_tarjeta = ft.TextField(label="Nº Tarjeta", width=230)
    expiracion = ft.TextField(label="Caducidad (MM/AA)", width=150)
    cvv = ft.TextField(label="Cód. Seguridad", width=100, password=True)

    def cancelar_pago(e):
        num_tarjeta.value = ""
        expiracion.value = ""
        cvv.value = ""
        page.dialog = ft.AlertDialog(
            title=ft.Text("Cancelado"),
            content=ft.Text("El pago fue cancelado")
        )
        page.dialog.open = True
        page.update()

    def completar_pago(e):
        if not num_tarjeta.value or not expiracion.value or not cvv.value:
            page.dialog = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text("Por favor, completa todos los campos")
            )
        else:
            page.dialog = ft.AlertDialog(
                title=ft.Text("Pago Exitoso"),
                content=ft.Text(f"Pago realizado con tarjeta terminada en {num_tarjeta.value[-4:]}")
            )
        page.dialog.open = True
        page.update()

    right_panel = ft.Container(
        content=ft.Column([
            ft.Text("PAGAR CON TARJETA", size=14, weight=ft.FontWeight.BOLD, color="black"),
            num_tarjeta,
            expiracion,
            cvv,
            ft.Row([
                ft.ElevatedButton("CANCELAR", bgcolor="gray", color="white", on_click=cancelar_pago),
                ft.ElevatedButton("PAGAR", bgcolor="blue", color="white", on_click=completar_pago),
            ], spacing=10)
        ], spacing=10, alignment="start"),
        bgcolor="white",
        padding=15,
        border=ft.border.all(1, "black"),
        width=280
    )

    # --- LAYOUT with centered content and spacing ---
    page.add(
        ft.Row(
            [left_panel, right_panel],
            alignment="center",   # centers the row in window
            spacing=20,           # adds space between the two panels
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
