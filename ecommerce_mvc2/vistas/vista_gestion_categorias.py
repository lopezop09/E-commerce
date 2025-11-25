import flet as ft
from datetime import datetime

class VistaGestionCategorias:
    def __init__(self, pagina, controlador_admin):
        self.pagina = pagina
        self.controlador = controlador_admin
        self.base_datos = controlador_admin.base_datos
        self.crear_interfaz()

    def crear_interfaz(self):
        # Barra superior
        barra_superior = ft.Row([
            ft.ElevatedButton("⬅️ Volver al Panel", on_click=self.volver_panel),
            ft.Container(expand=True),
            ft.Text("Gestión de Categorías", size=24, weight="bold", color=ft.Colors.PURPLE),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Formulario para agregar categoría
        self.campo_nueva_categoria = ft.TextField(
            label="Nombre de la nueva categoría",
            width=300,
            hint_text="Ej: Teclados, Mouse, etc."
        )
        
        self.mensaje_categorias = ft.Text("", color=ft.Colors.BLUE, size=12)

        # Lista de categorías existentes
        self.lista_categorias = ft.Column([], scroll=ft.ScrollMode.ADAPTIVE)

        # Cargar categorías
        self.cargar_categorias()

        # Layout principal
        self.contenido = ft.Container(
            content=ft.Column([
                barra_superior,
                ft.Divider(),
                
                # Sección agregar categoría
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Agregar Nueva Categoría", size=18, weight="bold"),
                            ft.Row([
                                self.campo_nueva_categoria,
                                ft.ElevatedButton(
                                    "Agregar Categoría",
                                    on_click=self.agregar_categoria,
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)
                                )
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            self.mensaje_categorias
                        ], spacing=10),
                        padding=20
                    )
                ),
                
                # Lista de categorías
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Categorías Existentes", size=18, weight="bold"),
                            ft.Divider(),
                            self.lista_categorias
                        ]),
                        padding=20
                    )
                )
            ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE),
            expand=True,
            padding=20
        )

    def cargar_categorias(self):
        with self.base_datos.obtener_conexion() as conn:
            cursor = conn.execute("SELECT id, nombre, fecha_creacion FROM categorias ORDER BY nombre")
            categorias = cursor.fetchall()
            
            self.lista_categorias.controls.clear()
            
            for categoria in categorias:
                categoria_card = ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(categoria['nombre'], size=16, weight="bold"),
                                ft.Text(f"Creada: {categoria['fecha_creacion']}", size=12, color="gray")
                            ], expand=True),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                tooltip="Eliminar categoría",
                                on_click=lambda e, id=categoria['id'], nombre=categoria['nombre']: self.eliminar_categoria(id, nombre)
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=15
                    )
                )
                self.lista_categorias.controls.append(categoria_card)

    def agregar_categoria(self, e):
        nombre_categoria = self.campo_nueva_categoria.value.strip()
        if not nombre_categoria:
            self.mostrar_mensaje("Por favor ingresa un nombre para la categoría", "red")
            return
        
        try:
            with self.base_datos.obtener_conexion() as conn:
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute(
                    "INSERT INTO categorias (nombre, fecha_creacion) VALUES (?, ?)",
                    (nombre_categoria, fecha_actual)
                )
            
            self.mostrar_mensaje(f"✅ Categoría '{nombre_categoria}' agregada exitosamente", "green")
            self.campo_nueva_categoria.value = ""
            self.cargar_categorias()
            self.pagina.update()
            
        except Exception as e:
            if "UNIQUE constraint" in str(e):
                self.mostrar_mensaje(f"❌ La categoría '{nombre_categoria}' ya existe", "red")
            else:
                self.mostrar_mensaje(f"❌ Error al agregar categoría: {str(e)}", "red")

    def eliminar_categoria(self, id_categoria, nombre_categoria):
        def confirmar_eliminacion(e):
            try:
                with self.base_datos.obtener_conexion() as conn:
                    # Verificar si hay productos usando esta categoría
                    cursor = conn.execute("SELECT COUNT(*) FROM productos WHERE categoria_id = ?", (id_categoria,))
                    count_productos = cursor.fetchone()[0]
                    
                    if count_productos > 0:
                        self.mostrar_mensaje(f"❌ No se puede eliminar. Hay {count_productos} productos usando esta categoría", "red")
                    else:
                        conn.execute("DELETE FROM categorias WHERE id = ?", (id_categoria,))
                        self.mostrar_mensaje(f"✅ Categoría '{nombre_categoria}' eliminada", "green")
                        self.cargar_categorias()
                        self.pagina.update()
                
                dialog.open = False
                self.pagina.update()
                
            except Exception as e:
                self.mostrar_mensaje(f"❌ Error al eliminar categoría: {str(e)}", "red")
        
        def cancelar_eliminacion(e):
            dialog.open = False
            self.pagina.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text(f"¿Estás seguro de que quieres eliminar la categoría '{nombre_categoria}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar_eliminacion),
                ft.TextButton("Eliminar", on_click=confirmar_eliminacion, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
        )
        
        self.pagina.dialog = dialog
        dialog.open = True
        self.pagina.update()

    def mostrar_mensaje(self, mensaje, color):
        self.mensaje_categorias.value = mensaje
        self.mensaje_categorias.color = color
        self.pagina.update()

    def mostrar(self):
        self.pagina.clean()
        self.pagina.add(self.contenido)

    def volver_panel(self, e):
        usuario_actual = self.controlador.controlador_principal.get_usuario_actual()
        self.controlador.mostrar_panel(usuario_actual)