import flet as ft

class VistaPanelAdministrador:
    def __init__(self, pagina, usuario, controlador_admin):
        self.pagina = pagina
        self.usuario = usuario
        self.controlador = controlador_admin
        self.crear_panel()

    def crear_panel(self):
        # Barra superior
        barra_superior = ft.Row(
            controls=[
                ft.ElevatedButton("⬅️ Volver al Inicio", on_click=self.volver),
                ft.Container(expand=True),
                ft.Text("PANEL ADMINISTRADOR", size=24, weight="bold", color=ft.Colors.ORANGE),
                ft.Container(expand=True),
                ft.Text(f"Admin: {self.usuario['nombre']}", size=14, color="gray")
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Sección: Gestión de Usuarios
        self.campo_email_usuario = ft.TextField(
            label="Email del usuario",
            hint_text="ejemplo@correo.com",
            width=300,
            prefix_icon=ft.Icons.EMAIL
        )
        
        self.mensaje_gestion_usuarios = ft.Text("", color=ft.Colors.BLUE, size=12)
        
        seccion_usuarios = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.BLUE),
                        ft.Text(" Gestión de Usuarios", size=18, weight="bold"),
                    ]),
                    ft.Divider(),
                    ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Ingresa el email del usuario:", size=12, weight="bold"),
                                self.campo_email_usuario,
                                self.mensaje_gestion_usuarios
                            ], spacing=8),
                            padding=ft.padding.only(bottom=10)
                        ),
                        ft.Row([
                            self.crear_boton("🔍 Ver Estado", "Ver información del usuario", 
                                           lambda e: self.controlador.ver_estado_usuario(self.campo_email_usuario.value),
                                           color=ft.Colors.BLUE, compacto=True),
                            self.crear_boton("Desbloquear", "Desbloquear cuenta", 
                                           lambda e: self.controlador.desbloquear_usuario(self.campo_email_usuario.value),
                                           color=ft.Colors.GREEN, compacto=True),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([
                            self.crear_boton("Bloquear", "Bloquear cuenta", 
                                           lambda e: self.controlador.bloquear_usuario(self.campo_email_usuario.value),
                                           color=ft.Colors.ORANGE, compacto=True),
                            self.crear_boton("Eliminar", "Eliminar cuenta", 
                                           lambda e: self.controlador.eliminar_usuario(self.campo_email_usuario.value),
                                           color=ft.Colors.RED, compacto=True),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                    ], spacing=8)
                ], spacing=12),
                padding=20,
                width=400
            ),
            elevation=5
        )

        # Otras secciones (simplificadas para el ejemplo)
        seccion_marcas_categorias = self.crear_seccion_general("Marcas y Categorías", [
            ("🏷️ Gestionar Marcas", "Administrar marcas de productos", self.controlador.gestionar_marcas),
            ("📂 Gestionar Categorías", "Administrar categorías de productos", self.controlador.gestionar_categorias)
        ])

        seccion_inventario = self.crear_seccion_general("Gestión de Inventario", [
            ("📊 Ver Inventario", "Ver stock completo de productos", self.controlador.ver_inventario_completo),
            ("⚠️ Stock Bajo", "Productos con stock bajo", self.controlador.ver_stock_bajo),
            ("✏️ Actualizar Stock", "Modificar cantidades de productos", self.controlador.actualizar_stock_producto)
        ])

        # Layout principal
        self.contenido = ft.Column(
            controls=[
                barra_superior,
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Bienvenido al Panel de administración", size=22, weight="bold"),
                        ft.Text("Gestiona todas las operaciones de la plataforma desde un solo lugar", 
                               size=14, color="gray", text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.only(bottom=20)
                ),
                ft.Row([seccion_usuarios, seccion_marcas_categorias], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                ft.Container(height=15),
                ft.Row([seccion_inventario], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(
                    content=ft.Column([
                        ft.Divider(),
                        ft.Text("Panel de Administrador - Versión 1.0", size=12, color="gray", text_align=ft.TextAlign.CENTER),
                    ], spacing=5),
                    margin=ft.margin.only(top=20)
                )
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        )

    def crear_seccion_general(self, titulo, botones):
        contenido_botones = []
        for texto, descripcion, on_click in botones:
            contenido_botones.append(self.crear_boton(texto, descripcion, on_click))
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CATEGORY, color=ft.Colors.PURPLE),
                        ft.Text(f" {titulo}", size=18, weight="bold"),
                    ]),
                    ft.Divider(),
                    ft.Column(contenido_botones, spacing=8)
                ], spacing=12),
                padding=20,
                width=350
            ),
            elevation=5
        )

    def crear_boton(self, texto, descripcion, on_click_func, color=None, compacto=False):
        color_boton = color if color else ft.Colors.BLUE
        ancho = 140 if compacto else 300
        
        return ft.Container(
            content=ft.Column([
                ft.ElevatedButton(
                    text=texto,
                    on_click=on_click_func,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=color_boton,
                        padding=ft.padding.symmetric(horizontal=15, vertical=10)
                    ),
                    width=ancho
                ),
                ft.Text(descripcion, size=11, color="gray", text_align=ft.TextAlign.CENTER)
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=5)
        )

    def mostrar(self):
        self.pagina.clean()
        self.pagina.add(self.contenido)

    def volver(self, e):
        self.controlador.volver_principal()

    def mostrar_mensaje_gestion_usuarios(self, mensaje, color):
        self.mensaje_gestion_usuarios.value = mensaje
        self.mensaje_gestion_usuarios.color = color
        self.pagina.update()

    def mostrar_mensaje_global(self, texto):
        self.pagina.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            duration=3000,
        )
        self.pagina.snack_bar.open = True
        self.pagina.update()