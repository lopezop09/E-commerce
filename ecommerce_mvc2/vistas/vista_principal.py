import flet as ft
from modelos import Producto

class VistaPrincipal:
    def __init__(self, pagina, controlador_principal):
        self.pagina = pagina
        self.controlador = controlador_principal
        self.carrito = {}
        self.crear_controles()

    def crear_controles(self):
        self.campo_busqueda = ft.TextField(
            label="Buscar productos...",
            width=900,
            on_submit=self.buscar_productos,
            suffix=ft.IconButton(ft.Icons.SEARCH, on_click=self.buscar_productos)
        )

        self.boton_carrito = ft.ElevatedButton(
            "🛒 Carrito (0)", 
            on_click=self.abrir_carrito
        )

        self.boton_panel_admin = ft.ElevatedButton(
            "Panel Administrador",
            on_click=self.abrir_panel_admin,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE,
                color=ft.Colors.WHITE
            ),
            visible=False
        )

        self.boton_cerrar_sesion = ft.ElevatedButton("⬅️ Cerrar Sesión", on_click=self.cerrar_sesion)

    def mostrar(self, usuario, productos, carrito=None):
        if carrito:
            self.carrito = carrito
        
        self.actualizar_contador_carrito()
        
        # Configurar visibilidad del botón de admin
        self.boton_panel_admin.visible = (usuario['tipo'] == 'administrador')

        # Crear barra superior
        botones_superiores = [
            self.boton_cerrar_sesion,
            ft.Container(width=20),
            self.campo_busqueda,
            ft.Container(width=20),
            self.boton_carrito
        ]

        if usuario['tipo'] == 'administrador':
            botones_superiores.append(ft.Container(width=20))
            botones_superiores.append(self.boton_panel_admin)

        barra_superior = ft.Row(
            controls=botones_superiores,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Crear interfaz de productos
        texto_bienvenida = ft.Text(f"¡Bienvenido {usuario['nombre']}!", size=24, weight="bold")
        texto_tipo_usuario = ft.Text(f"Tipo de cuenta: {usuario['tipo'].capitalize()}", size=16)

        # Productos destacados
        productos_destacados = [p for p in productos if p.get('destacado', False)]
        lista_destacados = [self.crear_tarjeta_producto(p) for p in productos_destacados]

        # Todos los productos
        lista_todos = [self.crear_tarjeta_producto(p) for p in productos]

        self.contenedor_principal = ft.Column(
            controls=[
                barra_superior,
                texto_bienvenida,
                texto_tipo_usuario,
                ft.Divider(),
                ft.Text("Productos Destacados", size=20, weight="bold"),
                ft.Row(lista_destacados, wrap=True, spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                ft.Text("Todos los Productos", size=20, weight="bold"),
                ft.Row(lista_todos, wrap=True, spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.pagina.clean()
        self.pagina.add(self.contenedor_principal)

    def crear_tarjeta_producto(self, producto_data):
        producto = Producto(
            id=producto_data['id'],
            nombre=producto_data['nombre'],
            precio=producto_data['precio'],
            descripcion=producto_data['descripcion'],
            marca=producto_data['marca'],
            categoria=producto_data['categoria'],
            imagen=producto_data['imagen'],
            destacado=producto_data.get('destacado', False)
        )

        tarjeta = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(producto.imagen, size=30),
                    ], alignment="center"),
                    ft.Text(producto.nombre, size=16, weight="bold"),
                    ft.Text(f"${producto.precio_base:,.2f}", size=14, color="green"),
                    ft.Text(f"{producto.marca} | {producto.categoria}", size=12, color="gray"),
                    ft.Text(producto.descripcion, size=10),
                    ft.Row([
                        ft.ElevatedButton(
                            "Ver detalles", 
                            on_click=lambda e, p=producto: self.ver_detalles_producto(p),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE_50,
                                color=ft.Colors.BLUE_700
                            )
                        ),
                    ], alignment="center")
                ], spacing=5),
                padding=10,
                width=180
            ),
        )
        return tarjeta

    def ver_detalles_producto(self, producto):
        self.controlador.mostrar_detalle_producto(producto)

    def buscar_productos(self, e):
        query = self.campo_busqueda.value.strip()
        self.controlador.buscar_productos(query)

    def abrir_carrito(self, e):
        self.controlador.mostrar_carrito(self.carrito)

    def abrir_panel_admin(self, e):
        self.controlador.mostrar_panel_administrador()

    def cerrar_sesion(self, e):
        self.controlador.cerrar_sesion()

    def actualizar_contador_carrito(self):
        total_items = sum(item['cantidad'] for item in self.carrito.values())
        self.boton_carrito.text = f"🛒 Carrito ({total_items})"
        if hasattr(self, 'pagina'):
            self.pagina.update()

    def agregar_al_carrito(self, producto):
        producto_id = str(producto['id'])
        if producto_id in self.carrito:
            self.carrito[producto_id]['cantidad'] += 1
        else:
            self.carrito[producto_id] = {
                'id': producto['id'],
                'nombre': producto['nombre'],
                'precio_base': producto['precio'],
                'precio_final': producto['precio_final'],
                'descripcion_final': producto['descripcion_final'],
                'cantidad': 1
            }
        self.actualizar_contador_carrito()

    def mostrar_mensaje(self, texto):
        self.pagina.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            duration=2000,
        )
        self.pagina.snack_bar.open = True
        self.pagina.update()