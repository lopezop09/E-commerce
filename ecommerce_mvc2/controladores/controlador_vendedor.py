import flet as ft
from datetime import datetime

class ControladorVendedor:
    def __init__(self, pagina, controlador_principal):
        self.pagina = pagina
        self.controlador_principal = controlador_principal
        # Importación diferida
        from modelos.base_de_datos import BaseDatos
        self.base_datos = BaseDatos()
        self.vista_vendedor = None
        self.vista_actual = None

    def mostrar_panel(self, usuario):
        # Importación diferida
        from vistas.vista_panel_vendedor import VistaPanelVendedor
        self.vista_vendedor = VistaPanelVendedor(self.pagina, usuario, self)
        self.vista_vendedor.mostrar()

    def obtener_notificaciones_compras(self):
        """Obtener compras de productos del vendedor actual"""
        usuario_actual = self.controlador_principal.get_usuario_actual()
        notificaciones = []
        
        try:
            with self.base_datos.obtener_conexion() as conn:
                # Obtener pedidos que contienen productos del vendedor
                cursor = conn.execute('''
                    SELECT DISTINCT p.id as pedido_id, p.fecha as fecha_pedido, p.cliente as cliente_email,
                           ip.producto_nombre, ip.cantidad, ip.subtotal, p.estado
                    FROM pedidos p
                    JOIN items_pedido ip ON p.id = ip.pedido_id
                    JOIN productos prod ON ip.producto_id = prod.id
                    WHERE p.cliente != ? AND p.estado != 'Cancelado'
                    ORDER BY p.fecha DESC
                    LIMIT 10
                ''', (usuario_actual['email'],))
                
                for row in cursor:
                    notificaciones.append({
                        'pedido_id': row['pedido_id'],
                        'fecha_pedido': row['fecha_pedido'],
                        'cliente_email': row['cliente_email'],
                        'producto_nombre': row['producto_nombre'],
                        'cantidad': row['cantidad'],
                        'subtotal': row['subtotal'],
                        'enviado': row['estado'] == 'Enviado'
                    })
                    
        except Exception as e:
            print(f"❌ Error al obtener notificaciones: {e}")
            
        return notificaciones

    def marcar_como_enviado(self, pedido_id):
        """Marcar un pedido como enviado"""
        try:
            with self.base_datos.obtener_conexion() as conn:
                conn.execute(
                    "UPDATE pedidos SET estado = 'Enviado' WHERE id = ?",
                    (pedido_id,)
                )
            
            self.vista_vendedor.mostrar_mensaje(f"✅ Pedido #{pedido_id} marcado como enviado")
            self.vista_vendedor.actualizar_notificaciones()
            
        except Exception as e:
            self.vista_vendedor.mostrar_mensaje(f"❌ Error al marcar como enviado: {e}")

    def obtener_marcas_categorias(self):
        """Obtener listas de marcas y categorías para selectores"""
        try:
            with self.base_datos.obtener_conexion() as conn:
                cursor_marcas = conn.execute("SELECT id, nombre FROM marcas ORDER BY nombre")
                marcas = [dict(row) for row in cursor_marcas]
                
                cursor_categorias = conn.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
                categorias = [dict(row) for row in cursor_categorias]
                
                return marcas, categorias
                
        except Exception as e:
            print(f"❌ Error al obtener marcas y categorías: {e}")
            return [], []

    def obtener_productos_vendedor(self):
        """Obtener productos del vendedor actual"""
        usuario_actual = self.controlador_principal.get_usuario_actual()
        productos = []
        
        try:
            with self.base_datos.obtener_conexion() as conn:
                # En una implementación real, aquí se filtraría por vendedor
                # Por ahora mostramos todos los productos
                cursor = conn.execute('''
                    SELECT p.id, p.nombre, p.precio, p.descripcion, p.imagen, p.destacado,
                           m.nombre as marca, c.nombre as categoria
                    FROM productos p
                    JOIN marcas m ON p.marca_id = m.id
                    JOIN categorias c ON p.categoria_id = c.id
                    ORDER BY p.nombre
                ''')
                
                for row in cursor:
                    productos.append({
                        'id': row['id'],
                        'nombre': row['nombre'],
                        'precio': row['precio'],
                        'descripcion': row['descripcion'],
                        'imagen': row['imagen'],
                        'destacado': bool(row['destacado']),
                        'marca': row['marca'],
                        'categoria': row['categoria']
                    })
                    
        except Exception as e:
            print(f"❌ Error al obtener productos del vendedor: {e}")
            
        return productos

    def publicar_producto(self, datos_producto):
        """Publicar un nuevo producto"""
        try:
            # Validar datos
            if not datos_producto['nombre']:
                self.mostrar_mensaje_actual("❌ El nombre del producto es obligatorio", "red")
                return
                
            if not datos_producto['precio'] or float(datos_producto['precio']) <= 0:
                self.mostrar_mensaje_actual("❌ El precio debe ser mayor a 0", "red")
                return
            
            with self.base_datos.obtener_conexion() as conn:
                # Obtener IDs de marca y categoría
                cursor_marca = conn.execute(
                    "SELECT id FROM marcas WHERE nombre = ?", 
                    (datos_producto['marca'],)
                )
                marca_id = cursor_marca.fetchone()
                if not marca_id:
                    self.mostrar_mensaje_actual("❌ Marca no válida", "red")
                    return
                
                cursor_categoria = conn.execute(
                    "SELECT id FROM categorias WHERE nombre = ?", 
                    (datos_producto['categoria'],)
                )
                categoria_id = cursor_categoria.fetchone()
                if not categoria_id:
                    self.mostrar_mensaje_actual("❌ Categoría no válida", "red")
                    return
                
                # Insertar producto
                conn.execute('''
                    INSERT INTO productos (nombre, precio, descripcion, marca_id, categoria_id, imagen, destacado)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datos_producto['nombre'],
                    float(datos_producto['precio']),
                    datos_producto['descripcion'],
                    marca_id['id'],
                    categoria_id['id'],
                    datos_producto['imagen'] or '',
                    datos_producto['destacado']
                ))
                
                # Obtener ID del producto insertado
                producto_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                
                # Insertar en inventario
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute('''
                    INSERT INTO inventario (Productos_ID, Cantidad, Stock_minimo, Fecha_actualizacion)
                    VALUES (?, ?, ?, ?)
                ''', (producto_id, 0, 0, fecha_actual))
            
            self.mostrar_mensaje_actual("✅ Producto publicado exitosamente", "green")
            
        except Exception as e:
            self.mostrar_mensaje_actual(f"❌ Error al publicar producto: {e}", "red")

    def editar_producto(self, datos_producto):
        """Editar un producto existente"""
        try:
            # Validar datos
            if not datos_producto['nombre']:
                self.mostrar_mensaje_actual("❌ El nombre del producto es obligatorio", "red")
                return
                
            if not datos_producto['precio'] or float(datos_producto['precio']) <= 0:
                self.mostrar_mensaje_actual("❌ El precio debe ser mayor a 0", "red")
                return
            
            with self.base_datos.obtener_conexion() as conn:
                conn.execute('''
                    UPDATE productos 
                    SET nombre = ?, precio = ?, descripcion = ?
                    WHERE id = ?
                ''', (
                    datos_producto['nombre'],
                    float(datos_producto['precio']),
                    datos_producto['descripcion'],
                    datos_producto['id']
                ))
            
            self.mostrar_mensaje_actual("✅ Producto actualizado exitosamente", "green")
            
        except Exception as e:
            self.mostrar_mensaje_actual(f"❌ Error al editar producto: {e}", "red")

    def eliminar_producto(self, producto_id, nombre_producto):
        """Eliminar un producto"""
        def confirmar_eliminacion(e):
            try:
                with self.base_datos.obtener_conexion() as conn:
                    conn.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
                
                self.mostrar_mensaje_actual(f"✅ Producto '{nombre_producto}' eliminado", "green")
                dialog.open = False
                self.volver_panel()
                
            except Exception as e:
                self.mostrar_mensaje_actual(f"❌ Error al eliminar producto: {e}", "red")
        
        def cancelar_eliminacion(e):
            dialog.open = False
            self.pagina.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text(f"¿Estás seguro de que quieres eliminar el producto '{nombre_producto}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar_eliminacion),
                ft.TextButton("Eliminar", on_click=confirmar_eliminacion, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
        )
        
        self.pagina.dialog = dialog
        dialog.open = True
        self.pagina.update()

    def mostrar_mensaje_actual(self, mensaje, color):
        """Mostrar mensaje en la vista actual"""
        if hasattr(self, 'vista_actual') and self.vista_actual:
            self.vista_actual.mostrar_mensaje(mensaje, color)
        else:
            # Crear un snackbar temporal
            snackbar = ft.SnackBar(content=ft.Text(mensaje), bgcolor=color)
            self.pagina.snack_bar = snackbar
            snackbar.open = True
            self.pagina.update()

    # Métodos para mostrar diferentes vistas
    def mostrar_publicar_producto(self, e):
        from vistas.vista_gestion_productos import VistaGestionProductos
        self.vista_actual = VistaGestionProductos(self.pagina, self, "publicar")
        self.vista_actual.mostrar()

    def mostrar_editar_productos(self, e):
        from vistas.vista_gestion_productos import VistaGestionProductos
        self.vista_actual = VistaGestionProductos(self.pagina, self, "editar")
        self.vista_actual.mostrar()

    def mostrar_eliminar_productos(self, e):
        from vistas.vista_gestion_productos import VistaGestionProductos
        self.vista_actual = VistaGestionProductos(self.pagina, self, "eliminar")
        self.vista_actual.mostrar()

    def mostrar_gestion_envios(self, e):
        self.vista_vendedor.mostrar_mensaje("🚚 Funcionalidad de gestión de envíos en desarrollo")

    def mostrar_estadisticas(self, e):
        self.vista_vendedor.mostrar_mensaje("📊 Funcionalidad de estadísticas en desarrollo")

    def volver_panel(self):
        usuario_actual = self.controlador_principal.get_usuario_actual()
        self.mostrar_panel(usuario_actual)

    def volver_principal(self):
        usuario_actual = self.controlador_principal.get_usuario_actual()
        carrito_actual = self.controlador_principal.get_carrito_actual()
        self.controlador_principal.mostrar_principal(usuario_actual, carrito_actual)