import flet as ft
from datetime import datetime

class VistaInventario:
    def __init__(self, pagina, controlador_admin, tipo_vista="completo"):
        self.pagina = pagina
        self.controlador = controlador_admin
        self.base_datos = controlador_admin.base_datos
        self.tipo_vista = tipo_vista  # "completo", "bajo", "actualizar"
        self.crear_interfaz()

    def crear_interfaz(self):
        # Títulos según el tipo de vista
        titulos = {
            "completo": "Inventario Completo",
            "bajo": "Stock Bajo - Alertas",
            "actualizar": "Actualizar Stock"
        }
        
        colores = {
            "completo": ft.Colors.BLUE,
            "bajo": ft.Colors.ORANGE,
            "actualizar": ft.Colors.GREEN
        }

        # Barra superior
        barra_superior = ft.Row([
            ft.ElevatedButton("⬅️ Volver al Panel", on_click=self.volver_panel),
            ft.Container(expand=True),
            ft.Text(titulos[self.tipo_vista], size=24, weight="bold", color=colores[self.tipo_vista]),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.mensaje_inventario = ft.Text("", color=ft.Colors.BLUE, size=12)

        # Lista de productos/inventario
        self.lista_inventario = ft.Column([], scroll=ft.ScrollMode.ADAPTIVE)

        # Cargar datos
        self.cargar_inventario()

        # Layout principal
        self.contenido = ft.Container(
            content=ft.Column([
                barra_superior,
                ft.Divider(),
                self.mensaje_inventario,
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"Lista de Productos - {titulos[self.tipo_vista]}", size=18, weight="bold"),
                            ft.Divider(),
                            self.lista_inventario
                        ]),
                        padding=20
                    )
                )
            ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE),
            expand=True,
            padding=20
        )

    def cargar_inventario(self):
        try:
            with self.base_datos.obtener_conexion() as conn:
                query = '''
                    SELECT p.id, p.nombre, p.precio, m.nombre as marca, c.nombre as categoria,
                           i.Cantidad, i.Stock_minimo, i.Fecha_actualizacion
                    FROM productos p
                    JOIN marcas m ON p.marca_id = m.id
                    JOIN categorias c ON p.categoria_id = c.id
                    JOIN inventario i ON p.id = i.Productos_ID
                '''
                
                # Filtrar según el tipo de vista
                if self.tipo_vista == "bajo":
                    query += " WHERE i.Cantidad <= i.Stock_minimo"
                
                query += " ORDER BY p.nombre"
                
                cursor = conn.execute(query)
                productos = cursor.fetchall()
                
                self.lista_inventario.controls.clear()
                
                if not productos:
                    self.lista_inventario.controls.append(
                        ft.Text("No hay productos que coincidan con los criterios", size=16, color="gray")
                    )
                    return
                
                for producto in productos:
                    cantidad = producto['Cantidad']
                    stock_minimo = producto['Stock_minimo']
                    
                    # Determinar color según stock
                    color_stock = ft.Colors.GREEN
                    if cantidad <= stock_minimo:
                        color_stock = ft.Colors.RED
                    elif cantidad <= stock_minimo * 2:
                        color_stock = ft.Colors.ORANGE
                    
                    producto_card = ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Column([
                                        ft.Text(producto['nombre'], size=16, weight="bold"),
                                        ft.Text(f"{producto['marca']} | {producto['categoria']}", size=12, color="gray"),
                                        ft.Text(f"Precio: ${producto['precio']:,.2f}", size=12),
                                    ], expand=True),
                                    ft.Column([
                                        ft.Text(f"Stock: {cantidad}", size=14, weight="bold", color=color_stock),
                                        ft.Text(f"Mínimo: {stock_minimo}", size=12),
                                        ft.Text(f"Última actualización: {producto['Fecha_actualizacion']}", size=10, color="gray"),
                                    ], horizontal_alignment=ft.CrossAxisAlignment.END)
                                ]),
                                
                                # Sección para actualizar stock (solo en vista de actualización)
                                ft.Container(
                                    content=self.crear_controles_actualizacion(producto) if self.tipo_vista == "actualizar" else None
                                )
                            ]),
                            padding=15
                        )
                    )
                    self.lista_inventario.controls.append(producto_card)
                    
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error al cargar inventario: {str(e)}", "red")

    def crear_controles_actualizacion(self, producto):
        campo_cantidad = ft.TextField(
            label="Nueva cantidad",
            value=str(producto['Cantidad']),
            width=120,
            height=40
        )
        
        campo_stock_minimo = ft.TextField(
            label="Stock mínimo",
            value=str(producto['Stock_minimo']),
            width=120,
            height=40
        )
        
        return ft.Row([
            campo_cantidad,
            campo_stock_minimo,
            ft.ElevatedButton(
                "Actualizar",
                on_click=lambda e, id=producto['id'], cant=campo_cantidad, min=campo_stock_minimo: 
                    self.actualizar_stock(id, cant.value, min.value, producto['nombre']),
                style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
            )
        ], alignment=ft.MainAxisAlignment.END)

    def actualizar_stock(self, producto_id, nueva_cantidad, nuevo_minimo, nombre_producto):
        try:
            # Validar entradas
            if not nueva_cantidad.isdigit() or not nuevo_minimo.isdigit():
                self.mostrar_mensaje("❌ La cantidad y stock mínimo deben ser números válidos", "red")
                return
            
            cantidad = int(nueva_cantidad)
            minimo = int(nuevo_minimo)
            
            if cantidad < 0 or minimo < 0:
                self.mostrar_mensaje("❌ Los valores no pueden ser negativos", "red")
                return
            
            with self.base_datos.obtener_conexion() as conn:
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute('''
                    UPDATE inventario 
                    SET Cantidad = ?, Stock_minimo = ?, Fecha_actualizacion = ?
                    WHERE Productos_ID = ?
                ''', (cantidad, minimo, fecha_actual, producto_id))
            
            self.mostrar_mensaje(f"✅ Stock de '{nombre_producto}' actualizado exitosamente", "green")
            self.cargar_inventario()
            self.pagina.update()
            
        except ValueError:
            self.mostrar_mensaje("❌ Por favor ingresa números válidos", "red")
        except Exception as e:
            self.mostrar_mensaje(f"❌ Error al actualizar stock: {str(e)}", "red")

    def mostrar_mensaje(self, mensaje, color):
        self.mensaje_inventario.value = mensaje
        self.mensaje_inventario.color = color
        self.pagina.update()

    def mostrar(self):
        self.pagina.clean()
        self.pagina.add(self.contenido)

    def volver_panel(self, e):
        usuario_actual = self.controlador.controlador_principal.get_usuario_actual()
        self.controlador.mostrar_panel(usuario_actual)