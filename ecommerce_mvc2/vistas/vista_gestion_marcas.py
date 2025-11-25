import flet as ft
from datetime import datetime

class VistaGestionMarcas:
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
            ft.Text("Gestión de Marcas", size=24, weight="bold", color=ft.Colors.BLUE),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Formulario para agregar marca
        self.campo_nueva_marca = ft.TextField(
            label="Nombre de la nueva marca",
            width=300,
            hint_text="Ej: MSI, Gigabyte, etc."
        )
        
        self.mensaje_marcas = ft.Text("", color=ft.Colors.BLUE, size=12)

        # Lista de marcas existentes
        self.lista_marcas = ft.Column([], scroll=ft.ScrollMode.ADAPTIVE)

        # Cargar marcas
        self.cargar_marcas()

        # Layout principal
        self.contenido = ft.Container(
            content=ft.Column([
                barra_superior,
                ft.Divider(),
                
                # Sección agregar marca
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Agregar Nueva Marca", size=18, weight="bold"),
                            ft.Row([
                                self.campo_nueva_marca,
                                ft.ElevatedButton(
                                    "Agregar Marca",
                                    on_click=self.agregar_marca,
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)
                                )
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            self.mensaje_marcas
                        ], spacing=10),
                        padding=20
                    )
                ),
                
                # Lista de marcas
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Marcas Existentes", size=18, weight="bold"),
                            ft.Divider(),
                            self.lista_marcas
                        ]),
                        padding=20
                    )
                )
            ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE),
            expand=True,
            padding=20
        )

    def cargar_marcas(self):
        with self.base_datos.obtener_conexion() as conn:
            cursor = conn.execute("SELECT id, nombre, fecha_creacion FROM marcas ORDER BY nombre")
            marcas = cursor.fetchall()
            
            self.lista_marcas.controls.clear()
            
            for marca in marcas:
                marca_card = ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(marca['nombre'], size=16, weight="bold"),
                                ft.Text(f"Creada: {marca['fecha_creacion']}", size=12, color="gray")
                            ], expand=True),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                tooltip="Eliminar marca",
                                on_click=lambda e, id=marca['id'], nombre=marca['nombre']: self.eliminar_marca(id, nombre)
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=15
                    )
                )
                self.lista_marcas.controls.append(marca_card)

    def agregar_marca(self, e):
        nombre_marca = self.campo_nueva_marca.value.strip()
        if not nombre_marca:
            self.mostrar_mensaje("Por favor ingresa un nombre para la marca", "red")
            return
        
        try:
            with self.base_datos.obtener_conexion() as conn:
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute(
                    "INSERT INTO marcas (nombre, fecha_creacion) VALUES (?, ?)",
                    (nombre_marca, fecha_actual)
                )
            
            self.mostrar_mensaje(f"✅ Marca '{nombre_marca}' agregada exitosamente", "green")
            self.campo_nueva_marca.value = ""
            self.cargar_marcas()
            self.pagina.update()
            
        except Exception as e:
            if "UNIQUE constraint" in str(e):
                self.mostrar_mensaje(f"❌ La marca '{nombre_marca}' ya existe", "red")
            else:
                self.mostrar_mensaje(f"❌ Error al agregar marca: {str(e)}", "red")

    def eliminar_marca(self, id_marca, nombre_marca):
        def confirmar_eliminacion(e):
            try:
                with self.base_datos.obtener_conexion() as conn:
                    # Verificar si hay productos usando esta marca
                    cursor = conn.execute("SELECT COUNT(*) FROM productos WHERE marca_id = ?", (id_marca,))
                    count_productos = cursor.fetchone()[0]
                    
                    if count_productos > 0:
                        self.mostrar_mensaje(f"❌ No se puede eliminar. Hay {count_productos} productos usando esta marca", "red")
                    else:
                        conn.execute("DELETE FROM marcas WHERE id = ?", (id_marca,))
                        self.mostrar_mensaje(f"✅ Marca '{nombre_marca}' eliminada", "green")
                        self.cargar_marcas()
                        self.pagina.update()
                
                dialog.open = False
                self.pagina.update()
                
            except Exception as e:
                self.mostrar_mensaje(f"❌ Error al eliminar marca: {str(e)}", "red")
        
        def cancelar_eliminacion(e):
            dialog.open = False
            self.pagina.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text(f"¿Estás seguro de que quieres eliminar la marca '{nombre_marca}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar_eliminacion),
                ft.TextButton("Eliminar", on_click=confirmar_eliminacion, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
        )
        
        self.pagina.dialog = dialog
        dialog.open = True
        self.pagina.update()

    def mostrar_mensaje(self, mensaje, color):
        self.mensaje_marcas.value = mensaje
        self.mensaje_marcas.color = color
        self.pagina.update()

    def mostrar(self):
        self.pagina.clean()
        self.pagina.add(self.contenido)

    def volver_panel(self, e):
        usuario_actual = self.controlador.controlador_principal.get_usuario_actual()
        self.controlador.mostrar_panel(usuario_actual)