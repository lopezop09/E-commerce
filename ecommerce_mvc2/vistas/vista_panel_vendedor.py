import flet as ft
from datetime import datetime

class VistaPanelVendedor:
    def __init__(self, pagina, usuario, controlador_vendedor):
        self.pagina = pagina
        self.usuario = usuario
        self.controlador = controlador_vendedor
        self.crear_panel()

    def crear_panel(self):
        # Barra superior
        barra_superior = ft.Row(
            controls=[
                ft.ElevatedButton("⬅️ Volver al Inicio", on_click=self.volver),
                ft.Container(expand=True),
                ft.Text("PANEL VENDEDOR", size=24, weight="bold", color=ft.Colors.GREEN),
                ft.Container(expand=True),
                ft.Text(f"Vendedor: {self.usuario['nombre_tienda']}", size=14, color="gray")
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Sección: Notificaciones de Compras
        self.notificaciones_container = ft.Column([], scroll=ft.ScrollMode.ADAPTIVE)
        self.cargar_notificaciones()

        seccion_notificaciones = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.NOTIFICATIONS, color=ft.Colors.ORANGE),
                        ft.Text(" Notificaciones de Compras", size=18, weight="bold"),
                    ]),
                    ft.Divider(),
                    ft.Text("Productos comprados por clientes:", size=14, weight="bold"),
                    self.notificaciones_container
                ], spacing=12),
                padding=20,
                width=400
            ),
            elevation=5
        )

        # Sección: Gestión de Productos
        seccion_productos = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INVENTORY, color=ft.Colors.BLUE),
                        ft.Text(" Gestión de Productos", size=18, weight="bold"),
                    ]),
                    ft.Divider(),
                    self.crear_boton("📦 Publicar Producto", "Agregar nuevo producto al catálogo", 
                                   self.controlador.mostrar_publicar_producto),
                    self.crear_boton("✏️ Editar Productos", "Modificar productos existentes", 
                                   self.controlador.mostrar_editar_productos),
                    self.crear_boton("🗑️ Eliminar Productos", "Eliminar productos del catálogo", 
                                   self.controlador.mostrar_eliminar_productos),
                ], spacing=12),
                padding=20,
                width=350
            ),
            elevation=5
        )

        # Sección: Control de Envíos
        seccion_envios = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.LOCAL_SHIPPING, color=ft.Colors.PURPLE),
                        ft.Text(" Control de Envíos", size=18, weight="bold"),
                    ]),
                    ft.Divider(),
                    self.crear_boton("🚚 Gestionar Envíos", "Marcar productos como enviados", 
                                   self.controlador.mostrar_gestion_envios),
                    self.crear_boton("📊 Estadísticas", "Ver estadísticas de ventas", 
                                   self.controlador.mostrar_estadisticas),
                ], spacing=12),
                padding=20,
                width=350
            ),
            elevation=5
        )

        # Layout principal
        self.contenido = ft.Column(
            controls=[
                barra_superior,
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"Bienvenido, {self.usuario['nombre']}", size=22, weight="bold"),
                        ft.Text(f"Tienda: {self.usuario['nombre_tienda']}", size=16, color="green"),
                        ft.Text("Gestiona tus productos y ventas desde aquí", 
                               size=14, color="gray", text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.only(bottom=20)
                ),
                ft.Row([seccion_notificaciones, seccion_productos], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ft.Container(height=15),
                ft.Row([seccion_envios], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(
                    content=ft.Column([
                        ft.Divider(),
                        ft.Text("Panel de Vendedor - Versión 1.0", size=12, color="gray", text_align=ft.TextAlign.CENTER),
                    ], spacing=5),
                    margin=ft.margin.only(top=20)
                )
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ADAPTIVE
        )

    def crear_boton(self, texto, descripcion, on_click_func, color=None):
        color_boton = color if color else ft.Colors.BLUE
        
        return ft.Container(
            content=ft.Column([
                ft.ElevatedButton(
                    text=texto,
                    on_click=on_click_func,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=color_boton,
                        padding=ft.padding.symmetric(horizontal=15, vertical=12)
                    ),
                    width=300
                ),
                ft.Text(descripcion, size=11, color="gray", text_align=ft.TextAlign.CENTER)
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=5)
        )

    def cargar_notificaciones(self):
        # Cargar notificaciones de compras
        notificaciones = self.controlador.obtener_notificaciones_compras()
        
        if not notificaciones:
            self.notificaciones_container.controls.append(
                ft.Text("No hay compras recientes", size=12, color="gray", text_align=ft.TextAlign.CENTER)
            )
            return
        
        for notif in notificaciones:
            notif_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.SHOPPING_CART, color=ft.Colors.GREEN, size=20),
                            ft.Text(f"Pedido #{notif['pedido_id']}", size=14, weight="bold"),
                        ]),
                        ft.Text(f"Producto: {notif['producto_nombre']}", size=12),
                        ft.Text(f"Cantidad: {notif['cantidad']} - ${notif['subtotal']:,.2f}", size=12),
                        ft.Text(f"Cliente: {notif['cliente_email']}", size=11, color="gray"),
                        ft.Text(f"Fecha: {notif['fecha_pedido']}", size=10, color="gray"),
                        ft.Row([
                            ft.ElevatedButton(
                                "Marcar como Enviado",
                                on_click=lambda e, pid=notif['pedido_id']: self.controlador.marcar_como_enviado(pid),
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor=ft.Colors.GREEN,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5)
                                ),
                                height=30
                            )
                        ]) if not notif.get('enviado', False) else ft.Text("✅ Enviado", size=12, color="green")
                    ], spacing=5),
                    padding=10
                )
            )
            self.notificaciones_container.controls.append(notif_card)

    def mostrar(self):
        self.pagina.clean()
        self.pagina.add(self.contenido)

    def volver(self, e):
        self.controlador.volver_principal()

    def actualizar_notificaciones(self):
        self.notificaciones_container.controls.clear()
        self.cargar_notificaciones()
        self.pagina.update()

    def mostrar_mensaje(self, texto):
        self.pagina.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            duration=3000,
        )
        self.pagina.snack_bar.open = True
        self.pagina.update()