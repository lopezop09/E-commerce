import flet as ft
from datetime import datetime

class VistaGestionProductos:
    def __init__(self, pagina, controlador_vendedor, tipo_vista="editar"):
        self.pagina = pagina
        self.controlador = controlador_vendedor
        self.tipo_vista = tipo_vista  # "editar", "eliminar", "publicar"
        self.crear_interfaz()

    def crear_interfaz(self):
        # Títulos según el tipo de vista
        titulos = {
            "editar": "Editar Productos",
            "eliminar": "Eliminar Productos", 
            "publicar": "Publicar Nuevo Producto"
        }
        
        colores = {
            "editar": ft.Colors.BLUE,
            "eliminar": ft.Colors.RED,
            "publicar": ft.Colors.GREEN
        }

        # Barra superior
        barra_superior = ft.Row([
            ft.ElevatedButton("⬅️ Volver al Panel", on_click=self.volver_panel),
            ft.Container(expand=True),
            ft.Text(titulos[self.tipo_vista], size=24, weight="bold", color=colores[self.tipo_vista]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.mensaje = ft.Text("", color=ft.Colors.BLUE, size=12)

        # Inicializar self.contenido aquí
        self.contenido = None
        
        if self.tipo_vista == "publicar":
            self.crear_formulario_publicacion()
        else:
            self.crear_lista_productos()

    def crear_formulario_publicacion(self):
        # Campos del formulario
        self.campo_nombre = ft.TextField(label="Nombre del producto", width=400)
        self.campo_precio = ft.TextField(label="Precio", width=200, prefix_text="$")
        self.campo_descripcion = ft.TextField(
            label="Descripción", 
            width=400,
            multiline=True,
            max_lines=3
        )
        
        # Selectores de marca y categoría
        self.selector_marca = ft.Dropdown(
            label="Marca",
            width=200,
            options=[]
        )
        
        self.selector_categoria = ft.Dropdown(
            label="Categoría",
            width=200,
            options=[]
        )
        
        self.campo_imagen = ft.TextField(label="URL de imagen (opcional)", width=400)
        self.checkbox_destacado = ft.Checkbox(label="Producto destacado", value=False)

        # Cargar opciones de marcas y categorías
        self.cargar_opciones_selectores()

        formulario = ft.Column([
            ft.Text("Complete la información del nuevo producto:", size=16, weight="bold"),
            ft.Row([self.campo_nombre], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.campo_precio, self.selector_marca, self.selector_categoria], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.campo_descripcion], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.campo_imagen], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.checkbox_destacado], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.ElevatedButton(
                    "Publicar Producto",
                    on_click=self.publicar_producto,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            self.mensaje
        ], spacing=15)

        self.contenido = ft.Container(
            content=ft.Column([
                self.crear_barra_superior(),
                ft.Divider(),
                ft.Card(
                    content=ft.Container(
                        content=formulario,
                        padding=30
                    )
                )
            ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE),
            expand=True,
            padding=20
        )

    def crear_lista_productos(self):
        self.lista_productos = ft.Column([], scroll=ft.ScrollMode.ADAPTIVE)
        self.cargar_productos_vendedor()

        self.contenido = ft.Container(
            content=ft.Column([
                self.crear_barra_superior(),
                ft.Divider(),
                self.mensaje,
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Mis Productos", size=18, weight="bold"),
                            ft.Divider(),
                            self.lista_productos
                        ]),
                        padding=20
                    )
                )
            ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE),
            expand=True,
            padding=20
        )

    def crear_barra_superior(self):
        """Crear barra superior reutilizable"""
        titulos = {
            "editar": "Editar Productos",
            "eliminar": "Eliminar Productos", 
            "publicar": "Publicar Nuevo Producto"
        }
        
        colores = {
            "editar": ft.Colors.BLUE,
            "eliminar": ft.Colors.RED,
            "publicar": ft.Colors.GREEN
        }
        
        return ft.Row([
            ft.ElevatedButton("⬅️ Volver al Panel", on_click=self.volver_panel),
            ft.Container(expand=True),
            ft.Text(titulos[self.tipo_vista], size=24, weight="bold", color=colores[self.tipo_vista]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def cargar_opciones_selectores(self):
        marcas, categorias = self.controlador.obtener_marcas_categorias()
        
        # Limpiar opciones existentes
        self.selector_marca.options.clear()
        self.selector_categoria.options.clear()
        
        for marca in marcas:
            self.selector_marca.options.append(ft.dropdown.Option(key=marca['nombre'], text=marca['nombre']))
        
        for categoria in categorias:
            self.selector_categoria.options.append(ft.dropdown.Option(key=categoria['nombre'], text=categoria['nombre']))
        
        # Establecer valores por defecto si hay opciones
        if self.selector_marca.options:
            self.selector_marca.value = self.selector_marca.options[0].key
        if self.selector_categoria.options:
            self.selector_categoria.value = self.selector_categoria.options[0].key

    def cargar_productos_vendedor(self):
        productos = self.controlador.obtener_productos_vendedor()
        
        self.lista_productos.controls.clear()
        
        if not productos:
            self.lista_productos.controls.append(
                ft.Text("No tienes productos publicados", size=16, color="gray", text_align=ft.TextAlign.CENTER)
            )
            return
        
        for producto in productos:
            if self.tipo_vista == "editar":
                producto_card = self.crear_tarjeta_edicion(producto)
            else:  # eliminar
                producto_card = self.crear_tarjeta_eliminacion(producto)
            
            self.lista_productos.controls.append(producto_card)

    def crear_tarjeta_edicion(self, producto):
        campo_nombre = ft.TextField(
            value=producto['nombre'],
            width=200,
            height=40
        )
        
        campo_precio = ft.TextField(
            value=str(producto['precio']),
            width=120,
            height=40,
            prefix_text="$"
        )
        
        campo_descripcion = ft.TextField(
            value=producto['descripcion'],
            width=300,
            height=60,
            multiline=True
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text("Nombre:", size=12, weight="bold"),
                            campo_nombre
                        ]),
                        ft.Column([
                            ft.Text("Precio:", size=12, weight="bold"),
                            campo_precio
                        ]),
                    ]),
                    ft.Row([
                        ft.Column([
                            ft.Text("Descripción:", size=12, weight="bold"),
                            campo_descripcion
                        ], expand=True),
                    ]),
                    ft.Row([
                        ft.ElevatedButton(
                            "Guardar Cambios",
                            on_click=lambda e, id=producto['id'], nom=campo_nombre, pre=campo_precio, desc=campo_descripcion: 
                                self.editar_producto(id, nom.value, pre.value, desc.value),
                            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
                        )
                    ], alignment=ft.MainAxisAlignment.END)
                ]),
                padding=15
            )
        )

    def crear_tarjeta_eliminacion(self, producto):
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text(producto['nombre'], size=16, weight="bold"),
                        ft.Text(f"${producto['precio']:,.2f}", size=14, color="green"),
                        ft.Text(producto['descripcion'], size=12, color="gray"),
                        ft.Text(f"{producto['marca']} | {producto['categoria']}", size=11, color="blue"),
                    ], expand=True),
                    ft.IconButton(
                        ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        tooltip="Eliminar producto",
                        on_click=lambda e, id=producto['id'], nombre=producto['nombre']: self.eliminar_producto(id, nombre)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=15
            )
        )

    def publicar_producto(self, e):
        # Validar campos obligatorios
        if not self.campo_nombre.value or not self.campo_nombre.value.strip():
            self.mostrar_mensaje("❌ El nombre del producto es obligatorio", "red")
            return
            
        if not self.campo_precio.value:
            self.mostrar_mensaje("❌ El precio es obligatorio", "red")
            return
            
        if not self.selector_marca.value:
            self.mostrar_mensaje("❌ Debes seleccionar una marca", "red")
            return
            
        if not self.selector_categoria.value:
            self.mostrar_mensaje("❌ Debes seleccionar una categoría", "red")
            return

        datos = {
            'nombre': self.campo_nombre.value.strip(),
            'precio': self.campo_precio.value,
            'descripcion': self.campo_descripcion.value.strip() if self.campo_descripcion.value else "",
            'marca': self.selector_marca.value,
            'categoria': self.selector_categoria.value,
            'imagen': self.campo_imagen.value.strip() if self.campo_imagen.value else "",
            'destacado': self.checkbox_destacado.value
        }
        
        self.controlador.publicar_producto(datos)

    def editar_producto(self, producto_id, nombre, precio, descripcion):
        # Validar campos
        if not nombre or not nombre.strip():
            self.mostrar_mensaje("❌ El nombre del producto es obligatorio", "red")
            return
            
        if not precio:
            self.mostrar_mensaje("❌ El precio es obligatorio", "red")
            return

        datos = {
            'id': producto_id,
            'nombre': nombre.strip(),
            'precio': precio,
            'descripcion': descripcion.strip() if descripcion else ""
        }
        
        self.controlador.editar_producto(datos)

    def eliminar_producto(self, producto_id, nombre):
        self.controlador.eliminar_producto(producto_id, nombre)

    def mostrar_mensaje(self, mensaje, color="blue"):
        self.mensaje.value = mensaje
        self.mensaje.color = color
        self.pagina.update()

    def mostrar(self):
        if self.contenido is None:
            # Si por alguna razón no se creó el contenido, crearlo ahora
            if self.tipo_vista == "publicar":
                self.crear_formulario_publicacion()
            else:
                self.crear_lista_productos()
                
        self.pagina.clean()
        self.pagina.add(self.contenido)

    def volver_panel(self, e):
        self.controlador.volver_panel()