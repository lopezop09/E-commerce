import flet as ft
import re
import os
import uuid
import webbrowser
import mercadopago
from datetime import datetime
import sqlite3
from contextlib import contextmanager

#Token de acceso para mercado pago
ACCESS_TOKEN = "APP_USR-1864674603848840-102206-3ba17bea7a073761dabe4a32e7fafa87-2939897316"

# --- BASE DE DATOS SQLite (CON NUEVAS TABLAS MARCA Y CATEGORIA) ---
class Database:
    def __init__(self):
        self.db_name = "ecommerce.db"
        self.init_database()
        print("DEBUG: Base de datos SQLite inicializada con tablas marca y categoria")

    @contextmanager
    def get_connection(self):
        """Context manager para manejar conexiones a la base de datos"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_database(self):
        """Inicializar las tablas de la base de datos - VERSIÓN CON TABLAS MARCA Y CATEGORIA"""
        with self.get_connection() as conn:
            # Tabla de usuarios
            conn.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    email TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    password TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    nombre_tienda TEXT,
                    telefono TEXT,
                    fecha_registro TEXT NOT NULL
                )
            ''')

            # Tabla: Historial de bloqueos de usuarios
            conn.execute('''
                CREATE TABLE IF NOT EXISTS bloqueos_usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_email TEXT NOT NULL,
                    bloqueado BOOLEAN NOT NULL,
                    fecha_operacion TEXT NOT NULL,
                    realizado_por TEXT NOT NULL,
                    motivo TEXT,
                    FOREIGN KEY (usuario_email) REFERENCES usuarios (email) ON DELETE CASCADE
                )
            ''')

            # NUEVA TABLA: Marcas
            conn.execute('''
                CREATE TABLE IF NOT EXISTS marcas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    fecha_creacion TEXT NOT NULL
                )
            ''')

            # NUEVA TABLA: Categorías
            conn.execute('''
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    fecha_creacion TEXT NOT NULL
                )
            ''')

            # Tabla de productos (ACTUALIZADA CON FOREIGN KEYS)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    precio REAL NOT NULL,
                    descripcion TEXT,
                    marca_id INTEGER NOT NULL,
                    categoria_id INTEGER NOT NULL,
                    imagen TEXT,
                    destacado BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (marca_id) REFERENCES marcas (id) ON DELETE CASCADE,
                    FOREIGN KEY (categoria_id) REFERENCES categorias (id) ON DELETE CASCADE
                )
            ''')

            # Tabla: Inventario
            conn.execute('''
                CREATE TABLE IF NOT EXISTS inventario (
                    Inventario_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Productos_ID INTEGER NOT NULL,
                    Cantidad INTEGER NOT NULL DEFAULT 0,
                    Stock_minimo INTEGER NOT NULL DEFAULT 0,
                    Fecha_actualizacion TEXT NOT NULL,
                    FOREIGN KEY (Productos_ID) REFERENCES productos (id) ON DELETE CASCADE
                )
            ''')

            # Tabla de pedidos (MAESTRO)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pedidos (
                    id TEXT PRIMARY KEY,
                    fecha TEXT NOT NULL,
                    cliente TEXT NOT NULL,
                    total REAL NOT NULL,
                    estado TEXT NOT NULL,
                    metodo_pago TEXT,
                    tarjeta_ultimos_digitos TEXT,
                    FOREIGN KEY (cliente) REFERENCES usuarios (email)
                )
            ''')

            # Tabla de items_pedido (DETALLE)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS items_pedido (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id TEXT NOT NULL,
                    producto_id INTEGER NOT NULL,
                    producto_nombre TEXT NOT NULL,
                    precio_unitario REAL NOT NULL,
                    cantidad INTEGER NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
                    FOREIGN KEY (producto_id) REFERENCES productos (id)
                )
            ''')

            # Insertar datos iniciales de marcas y categorías si no existen
            if not conn.execute("SELECT COUNT(*) FROM marcas").fetchone()[0]:
                self.insertar_marcas_iniciales(conn)

            if not conn.execute("SELECT COUNT(*) FROM categorias").fetchone()[0]:
                self.insertar_categorias_iniciales(conn)

            # Insertar datos iniciales de productos si no existen
            if not conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]:
                self.insertar_productos_iniciales(conn)

            # Insertar datos iniciales de inventario si no existen
            if not conn.execute("SELECT COUNT(*) FROM inventario").fetchone()[0]:
                self.insertar_inventario_inicial(conn)

    def insertar_marcas_iniciales(self, conn):
        """Insertar marcas iniciales en la base de datos"""
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        marcas_iniciales = [
            ('Intel', fecha_actual),
            ('NVIDIA', fecha_actual),
            ('Samsung', fecha_actual),
            ('Corsair', fecha_actual),
            ('ASUS', fecha_actual),
            ('Seasonic', fecha_actual),
            ('Razer', fecha_actual),
            ('AMD', fecha_actual)
        ]

        conn.executemany('''
            INSERT INTO marcas (nombre, fecha_creacion)
            VALUES (?, ?)
        ''', marcas_iniciales)
        print("DEBUG: Marcas iniciales insertadas")

    def insertar_categorias_iniciales(self, conn):
        """Insertar categorías iniciales en la base de datos"""
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        categorias_iniciales = [
            ('Procesadores', fecha_actual),
            ('Tarjetas Gráficas', fecha_actual),
            ('Almacenamiento', fecha_actual),
            ('Memoria RAM', fecha_actual),
            ('Placas Base', fecha_actual),
            ('Fuentes de Poder', fecha_actual),
            ('Monitores', fecha_actual),
            ('Periféricos', fecha_actual)
        ]

        conn.executemany('''
            INSERT INTO categorias (nombre, fecha_creacion)
            VALUES (?, ?)
        ''', categorias_iniciales)
        print("DEBUG: Categorías iniciales insertadas")

    def insertar_productos_iniciales(self, conn):
        """Insertar productos iniciales en la base de datos"""
        # Obtener IDs de marcas y categorías
        marcas = {row['nombre']: row['id'] for row in conn.execute("SELECT id, nombre FROM marcas")}
        categorias = {row['nombre']: row['id'] for row in conn.execute("SELECT id, nombre FROM categorias")}

        productos_iniciales = [
            (1, 'Procesador Intel Core i9-13900K', 2323000, 'Procesador de 24 núcleos y 32 hilos, frecuencia turbo de hasta 5.8 GHz', 
             marcas['Intel'], categorias['Procesadores'], '', True),
            (2, 'Tarjeta Gráfica NVIDIA RTX 4080', 4670000, '16GB GDDR6X, ray tracing y DLSS 3.0', 
             marcas['NVIDIA'], categorias['Tarjetas Gráficas'], '', True),
            (3, 'SSD Samsung 980 Pro 1TB', 743440, 'Velocidades de lectura hasta 7000 MB/s, PCIe 4.0 NVMe', 
             marcas['Samsung'], categorias['Almacenamiento'], '', True),
            (4, 'Memoria RAM Corsair Vengeance 32GB', 505000, 'DDR5 5600MHz, CL36, RGB', 
             marcas['Corsair'], categorias['Memoria RAM'], '', False),
            (5, 'Placa Base ASUS ROG Strix Z790-E', 2530000, 'Socket LGA1700, PCIe 5.0, WiFi 6E', 
             marcas['ASUS'], categorias['Placas Base'], '', True),
            (6, 'Fuente de Alimentación Seasonic 850W', 600000, '80 Plus Gold, modular, certificación completa', 
             marcas['Seasonic'], categorias['Fuentes de Poder'], '', False),
            (7, 'Monitor Gaming ASUS 27" 144Hz', 1250000, 'QHD, 1ms, FreeSync y G-Sync compatible', 
             marcas['ASUS'], categorias['Monitores'], '', False),
            (8, 'Teclado Mecánico Razer BlackWidow', 600000, 'Switches mecánicos Razer Green, RGB Chroma', 
             marcas['Razer'], categorias['Periféricos'], '', False),
            (9, 'Procesador AMD Ryzen 9 7950X', 2450000, '16 núcleos, 32 hilos, frecuencia hasta 5.7 GHz', 
             marcas['AMD'], categorias['Procesadores'], '', True),
            (10, 'Tarjeta Gráfica AMD Radeon RX 7900 XT', 4700000, '20GB GDDR6, arquitectura RDNA 3', 
             marcas['AMD'], categorias['Tarjetas Gráficas'], '', False)
        ]

        conn.executemany('''
            INSERT INTO productos (id, nombre, precio, descripcion, marca_id, categoria_id, imagen, destacado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', productos_iniciales)

    def insertar_inventario_inicial(self, conn):
        """Insertar datos iniciales en la tabla inventario"""
        inventario_inicial = [
            (1, 50, 5, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            (2, 30, 3, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            (3, 100, 10, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            (4, 80, 8, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            (5, 25, 2, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            (6, 40, 4, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            (7, 15, 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            (8, 60, 6, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            (9, 35, 3, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            (10, 20, 2, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ]

        conn.executemany('''
            INSERT INTO inventario (Productos_ID, Cantidad, Stock_minimo, Fecha_actualizacion)
            VALUES (?, ?, ?, ?)
        ''', inventario_inicial)
        print("DEBUG: Datos iniciales de inventario insertados")

    # --- MÉTODOS PARA GESTIÓN DE MARCAS ---
    
    def obtener_marcas(self):
        """Obtener todas las marcas"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM marcas ORDER BY nombre")
            return [dict(row) for row in cursor]

    def guardar_marca(self, nombre):
        """Guardar una nueva marca"""
        with self.get_connection() as conn:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                conn.execute('''
                    INSERT INTO marcas (nombre, fecha_creacion)
                    VALUES (?, ?)
                ''', (nombre, fecha_actual))
                return True
            except sqlite3.IntegrityError:
                return False  # Marca ya existe

    def eliminar_marca(self, marca_id):
        """Eliminar una marca"""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM marcas WHERE id = ?", (marca_id,))

    # --- MÉTODOS PARA GESTIÓN DE CATEGORÍAS ---
    
    def obtener_categorias(self):
        """Obtener todas las categorías"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM categorias ORDER BY nombre")
            return [dict(row) for row in cursor]

    def guardar_categoria(self, nombre):
        """Guardar una nueva categoría"""
        with self.get_connection() as conn:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                conn.execute('''
                    INSERT INTO categorias (nombre, fecha_creacion)
                    VALUES (?, ?)
                ''', (nombre, fecha_actual))
                return True
            except sqlite3.IntegrityError:
                return False  # Categoría ya existe

    def eliminar_categoria(self, categoria_id):
        """Eliminar una categoría"""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))

    # --- MÉTODOS PARA GESTIÓN DE INVENTARIO ---
    
    def obtener_inventario(self):
        """Obtener todo el inventario con información de productos"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT i.*, p.nombre, m.nombre as marca, c.nombre as categoria 
                FROM inventario i 
                JOIN productos p ON i.Productos_ID = p.id
                JOIN marcas m ON p.marca_id = m.id
                JOIN categorias c ON p.categoria_id = c.id
                ORDER BY i.Fecha_actualizacion DESC
            ''')
            return [dict(row) for row in cursor]

    def obtener_stock_producto(self, producto_id):
        """Obtener stock actual de un producto específico"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT Cantidad, Stock_minimo 
                FROM inventario 
                WHERE Productos_ID = ?
            ''', (producto_id,))
            resultado = cursor.fetchone()
            if resultado:
                return dict(resultado)
            return {'Cantidad': 0, 'Stock_minimo': 0}

    def actualizar_stock(self, producto_id, nueva_cantidad, stock_minimo=None):
        """Actualizar stock de un producto"""
        with self.get_connection() as conn:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Verificar si existe el registro
            cursor = conn.execute('''
                SELECT Inventario_ID FROM inventario WHERE Productos_ID = ?
            ''', (producto_id,))
            
            existe = cursor.fetchone() is not None
            
            if existe:
                # Actualizar existente
                if stock_minimo is not None:
                    conn.execute('''
                        UPDATE inventario 
                        SET Cantidad = ?, Stock_minimo = ?, Fecha_actualizacion = ?
                        WHERE Productos_ID = ?
                    ''', (nueva_cantidad, stock_minimo, fecha_actual, producto_id))
                else:
                    conn.execute('''
                        UPDATE inventario 
                        SET Cantidad = ?, Fecha_actualizacion = ?
                        WHERE Productos_ID = ?
                    ''', (nueva_cantidad, fecha_actual, producto_id))
            else:
                # Insertar nuevo
                stock_min = stock_minimo if stock_minimo is not None else 0
                conn.execute('''
                    INSERT INTO inventario (Productos_ID, Cantidad, Stock_minimo, Fecha_actualizacion)
                    VALUES (?, ?, ?, ?)
                ''', (producto_id, nueva_cantidad, stock_min, fecha_actual))
            
            print(f"DEBUG: Stock actualizado - Producto {producto_id}: {nueva_cantidad} unidades")

    def reducir_stock(self, producto_id, cantidad):
        """Reducir stock cuando se realiza una venta"""
        stock_actual = self.obtener_stock_producto(producto_id)
        nueva_cantidad = stock_actual['Cantidad'] - cantidad
        
        if nueva_cantidad < 0:
            raise ValueError(f"Stock insuficiente. Disponible: {stock_actual['Cantidad']}, Solicitado: {cantidad}")
        
        self.actualizar_stock(producto_id, nueva_cantidad)
        return nueva_cantidad

    def obtener_productos_bajo_stock(self):
        """Obtener productos con stock por debajo del mínimo"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT i.*, p.nombre, m.nombre as marca, c.nombre as categoria 
                FROM inventario i 
                JOIN productos p ON i.Productos_ID = p.id
                JOIN marcas m ON p.marca_id = m.id
                JOIN categorias c ON p.categoria_id = c.id
                WHERE i.Cantidad <= i.Stock_minimo
                ORDER BY i.Cantidad ASC
            ''')
            return [dict(row) for row in cursor]

    # --- MÉTODOS ACTUALIZADOS PARA PRODUCTOS ---
    
    def cargar_productos(self):
        """Cargar productos con información de marcas y categorías"""
        print("DEBUG: Cargando productos desde base de datos")
        with self.get_connection() as conn:
            # Cargar productos con joins para marcas y categorías
            cursor = conn.execute('''
                SELECT p.*, m.nombre as marca_nombre, c.nombre as categoria_nombre 
                FROM productos p 
                JOIN marcas m ON p.marca_id = m.id 
                JOIN categorias c ON p.categoria_id = c.id
            ''')
            productos = []
            for row in cursor:
                producto = Producto(
                    id=row['id'],
                    nombre=row['nombre'],
                    precio=row['precio'],
                    descripcion=row['descripcion'],
                    marca=row['marca_nombre'],  # Usar el nombre de la marca
                    categoria=row['categoria_nombre'],  # Usar el nombre de la categoría
                    imagen=row['imagen'],
                    destacado=bool(row['destacado'])
                )
                productos.append(producto)

            # Cargar categorías únicas desde la nueva tabla
            cursor = conn.execute("SELECT nombre FROM categorias ORDER BY nombre")
            categorias = [row['nombre'] for row in cursor]

            # Cargar marcas únicas desde la nueva tabla
            cursor = conn.execute("SELECT nombre FROM marcas ORDER BY nombre")
            marcas = [row['nombre'] for row in cursor]

            print(f"DEBUG: {len(productos)} productos cargados")
            return productos, categorias, marcas

    def guardar_producto(self, producto_data):
        """Guardar o actualizar un producto en la base de datos"""
        print(f"DEBUG: Guardando producto {producto_data['nombre']}")
        
        with self.get_connection() as conn:
            # Obtener IDs de marca y categoría
            marca_id = conn.execute("SELECT id FROM marcas WHERE nombre = ?", 
                                  (producto_data['marca'],)).fetchone()
            categoria_id = conn.execute("SELECT id FROM categorias WHERE nombre = ?", 
                                      (producto_data['categoria'],)).fetchone()
            
            if not marca_id or not categoria_id:
                raise ValueError("Marca o categoría no válida")
            
            marca_id = marca_id['id']
            categoria_id = categoria_id['id']

            if 'id' in producto_data and producto_data['id']:
                # Actualizar producto existente
                conn.execute('''
                    UPDATE productos SET 
                    nombre = ?, precio = ?, descripcion = ?, marca_id = ?, categoria_id = ?, 
                    imagen = ?, destacado = ?
                    WHERE id = ?
                ''', (
                    producto_data['nombre'], producto_data['precio'], producto_data['descripcion'],
                    marca_id, categoria_id, producto_data['imagen'],
                    producto_data.get('destacado', False), producto_data['id']
                ))
            else:
                # Insertar nuevo producto
                conn.execute('''
                    INSERT INTO productos 
                    (nombre, precio, descripcion, marca_id, categoria_id, imagen, destacado)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    producto_data['nombre'], producto_data['precio'], producto_data['descripcion'],
                    marca_id, categoria_id, producto_data['imagen'],
                    producto_data.get('destacado', False)
                ))
        print("DEBUG: Producto guardado exitosamente")

    # --- MÉTODOS PARA GESTIÓN DE BLOQUEOS ---
    
    def obtener_estado_bloqueo(self, email):
        """Obtener el estado actual de bloqueo de un usuario"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT bloqueado, fecha_operacion, realizado_por, motivo
                FROM bloqueos_usuarios 
                WHERE usuario_email = ? 
                ORDER BY fecha_operacion DESC 
                LIMIT 1
            ''', (email,))
            
            resultado = cursor.fetchone()
            if resultado:
                return {
                    'bloqueado': bool(resultado['bloqueado']),
                    'fecha_operacion': resultado['fecha_operacion'],
                    'realizado_por': resultado['realizado_por'],
                    'motivo': resultado['motivo']
                }
            return {'bloqueado': False}

    def bloquear_usuario(self, email, administrador, motivo=None):
        """Bloquear un usuario"""
        with self.get_connection() as conn:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            conn.execute('''
                INSERT INTO bloqueos_usuarios 
                (usuario_email, bloqueado, fecha_operacion, realizado_por, motivo)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, True, fecha_actual, administrador, motivo or 'Bloqueo administrativo'))
            
            print(f"DEBUG: Usuario {email} bloqueado por {administrador}")

    def desbloquear_usuario(self, email, administrador, motivo=None):
        """Desbloquear un usuario"""
        with self.get_connection() as conn:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            conn.execute('''
                INSERT INTO bloqueos_usuarios 
                (usuario_email, bloqueado, fecha_operacion, realizado_por, motivo)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, False, fecha_actual, administrador, motivo or 'Desbloqueo administrativo'))
            
            print(f"DEBUG: Usuario {email} desbloqueado por {administrador}")

    def obtener_historial_bloqueos(self, email=None):
        """Obtener historial de bloqueos (opcionalmente filtrado por usuario)"""
        with self.get_connection() as conn:
            if email:
                cursor = conn.execute('''
                    SELECT * FROM bloqueos_usuarios 
                    WHERE usuario_email = ? 
                    ORDER BY fecha_operacion DESC
                ''', (email,))
            else:
                cursor = conn.execute('''
                    SELECT * FROM bloqueos_usuarios 
                    ORDER BY fecha_operacion DESC
                ''')
            
            return [dict(row) for row in cursor]

    # --- MÉTODOS ACTUALIZADOS PARA USUARIOS ---
    
    def cargar_usuarios(self):
        """Cargar todos los usuarios con su estado de bloqueo actual"""
        print("DEBUG: Cargando usuarios desde base de datos (con estado bloqueo)")
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM usuarios")
            usuarios = {}
            
            for row in cursor:
                usuario_dict = dict(row)
                email = usuario_dict['email']
                
                # Obtener estado de bloqueo actual desde la nueva tabla
                estado_bloqueo = self.obtener_estado_bloqueo(email)
                usuario_dict['bloqueado'] = estado_bloqueo['bloqueado']
                usuario_dict['fecha_bloqueo'] = estado_bloqueo['fecha_operacion'] if estado_bloqueo['bloqueado'] else None
                usuario_dict['bloqueado_por'] = estado_bloqueo['realizado_por'] if estado_bloqueo['bloqueado'] else None
                
                usuarios[email] = usuario_dict
            
            print(f"DEBUG: {len(usuarios)} usuarios cargados")
            return usuarios

    def guardar_usuario(self, datos_usuario):
        """Guardar o actualizar un usuario en la base de datos (versión simplificada)"""
        print(f"DEBUG: Guardando usuario {datos_usuario['email']}")
        with self.get_connection() as conn:
            # Verificar si el usuario ya existe
            cursor = conn.execute("SELECT email FROM usuarios WHERE email = ?", 
                                (datos_usuario['email'],))
            existe = cursor.fetchone() is not None

            # Preparar datos básicos del usuario (sin campos de bloqueo)
            datos_basicos = {
                'email': datos_usuario['email'],
                'nombre': datos_usuario['nombre'],
                'password': datos_usuario['password'],
                'tipo': datos_usuario['tipo'],
                'nombre_tienda': datos_usuario.get('nombre_tienda'),
                'telefono': datos_usuario.get('telefono'),
                'fecha_registro': datos_usuario['fecha_registro']
            }

            if existe:
                # Actualizar usuario existente
                conn.execute('''
                    UPDATE usuarios SET 
                    nombre = ?, password = ?, tipo = ?, nombre_tienda = ?, telefono = ?, fecha_registro = ?
                    WHERE email = ?
                ''', (
                    datos_basicos['nombre'], datos_basicos['password'], datos_basicos['tipo'],
                    datos_basicos['nombre_tienda'], datos_basicos['telefono'], 
                    datos_basicos['fecha_registro'], datos_basicos['email']
                ))
            else:
                # Insertar nuevo usuario
                conn.execute('''
                    INSERT INTO usuarios 
                    (email, nombre, password, tipo, nombre_tienda, telefono, fecha_registro)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datos_basicos['email'], datos_basicos['nombre'], datos_basicos['password'],
                    datos_basicos['tipo'], datos_basicos['nombre_tienda'],
                    datos_basicos['telefono'], datos_basicos['fecha_registro']
                ))
            
        print("DEBUG: Usuario guardado exitosamente")

    def eliminar_usuario(self, email):
        """Eliminar un usuario de la base de datos"""
        print(f"DEBUG: Eliminando usuario {email}")
        with self.get_connection() as conn:
            conn.execute("DELETE FROM usuarios WHERE email = ?", (email,))
        print("DEBUG: Usuario eliminado exitosamente")

    # --- MÉTODOS PARA PEDIDOS ---
    def cargar_pedidos(self):
        """Cargar todos los pedidos de la base de datos"""
        print("DEBUG: Cargando pedidos desde base de datos")
        with self.get_connection() as conn:
            # Cargar pedidos maestros
            cursor = conn.execute("SELECT * FROM pedidos")
            pedidos = {}
            for row in cursor:
                pedido_dict = dict(row)
                pedido_id = pedido_dict['id']
                
                # Cargar items del pedido
                cursor_items = conn.execute(
                    "SELECT * FROM items_pedido WHERE pedido_id = ?", 
                    (pedido_id,)
                )
                
                productos = {}
                for item in cursor_items:
                    productos[str(item['producto_id'])] = {
                        'id': item['producto_id'],
                        'nombre': item['producto_nombre'],
                        'precio_final': item['precio_unitario'],
                        'descripcion_final': item['producto_nombre'],
                        'cantidad': item['cantidad']
                    }
                
                pedido_dict['productos'] = productos
                pedidos[pedido_id] = pedido_dict
            
            print(f"DEBUG: {len(pedidos)} pedidos cargados")
            return pedidos

    def guardar_pedido(self, pedido):
        """Guardar un pedido en la base de datos"""
        print(f"DEBUG: Guardando pedido {pedido['id']} en base de datos pura")
        
        try:
            with self.get_connection() as conn:
                # Preparar datos
                fecha_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"🔍 DIAGNÓSTICO - Guardando pedido:")
                print(f"   ID: {pedido['id']}")
                print(f"   Cliente: {pedido['cliente']}")
                print(f"   Total: ${pedido['total']:,.2f}")
                print(f"   Productos: {len(pedido['productos'])}")
                
                # 1. Insertar pedido maestro
                conn.execute('''
                    INSERT INTO pedidos 
                    (id, fecha, cliente, total, estado, metodo_pago, tarjeta_ultimos_digitos)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pedido['id'],
                    fecha_iso,
                    pedido['cliente'],
                    float(pedido['total']),
                    pedido['estado'],
                    pedido.get('metodo_pago', 'Tarjeta'),
                    pedido.get('tarjeta_ultimos_digitos', '')
                ))
                
                # 2. Insertar items del pedido
                for prod_id, item in pedido['productos'].items():
                    subtotal = item['precio_final'] * item['cantidad']
                    
                    conn.execute('''
                        INSERT INTO items_pedido 
                        (pedido_id, producto_id, producto_nombre, precio_unitario, cantidad, subtotal)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        pedido['id'],
                        int(item['id']),
                        str(item['nombre']),
                        float(item['precio_final']),
                        int(item['cantidad']),
                        float(subtotal)
                    ))
                    
                    # 3. ACTUALIZAR INVENTARIO - Reducir stock
                    try:
                        self.reducir_stock(int(item['id']), int(item['cantidad']))
                        print(f"   - Stock actualizado: {item['nombre']} -{item['cantidad']} unidades")
                    except ValueError as e:
                        print(f"   ⚠️  Advertencia stock: {e}")
                    
                    print(f"   - Producto {item['id']}: {item['nombre']} x{item['cantidad']}")
                
                # Verificar que se insertó
                cursor_pedido = conn.execute("SELECT COUNT(*) FROM pedidos WHERE id = ?", (pedido['id'],))
                count_pedido = cursor_pedido.fetchone()[0]
                
                cursor_items = conn.execute("SELECT COUNT(*) FROM items_pedido WHERE pedido_id = ?", (pedido['id'],))
                count_items = cursor_items.fetchone()[0]
                
                if count_pedido > 0 and count_items > 0:
                    print(f"✅ DIAGNÓSTICO: Pedido {pedido['id']} guardado exitosamente")
                    print(f"   - Pedido maestro: ✅")
                    print(f"   - Items guardados: {count_items} ✅")
                    print(f"   - Inventario actualizado: ✅")
                else:
                    print("❌ DIAGNÓSTICO: Pedido NO se insertó correctamente")
                    
        except Exception as e:
            print(f"❌ DIAGNÓSTICO: Error crítico al guardar pedido: {e}")
            raise e

# --- PATRON OBSERVER ---
class Observador:
    def actualizar(self, mensaje):
        pass

class ProductoSujeto:
    def __init__(self):
        self._observadores = []

    def agregar_observador(self, observador):
        print(f"DEBUG: Agregando observador {observador}")
        self._observadores.append(observador)

    def eliminar_observador(self, observador):
        print(f"DEBUG: Eliminando observador {observador}")
        self._observadores.remove(observador)

    def notificar_observadores(self, mensaje):
        print(f"DEBUG: Notificando a {len(self._observadores)} observadores: {mensaje}")
        for observador in self._observadores:
            observador.actualizar(mensaje)

class Producto:
    def __init__(self, id, nombre, precio, descripcion, marca, categoria, imagen, destacado=False):
        self.id = id
        self.nombre = nombre
        self.precio_base = precio
        self.descripcion = descripcion
        self.marca = marca
        self.categoria = categoria
        self.imagen = imagen
        self.destacado = destacado
        print(f"DEBUG: Producto creado: {self.nombre} (ID: {self.id})")

    def get_precio(self):
        return self.precio_base

    def get_descripcion(self):
        return self.nombre

    def productos_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': self.precio_base,
            'descripcion': self.descripcion,
            'marca': self.marca,
            'categoria': self.categoria,
            'imagen': self.imagen,
            'destacado': self.destacado
        }

# DECORADOR
class ProductoDecorador:
    def __init__(self, producto):
        self._producto = producto
        print(f"DEBUG: Decorador aplicado a {producto.nombre}")

    def __getattr__(self, name):
        # Delegar atributos no encontrados al producto subyacente
        return getattr(self._producto, name)

    def get_precio(self):
        return self._producto.get_precio()

    def get_descripcion(self):
        return self._producto.get_descripcion()

    def productos_dict(self):
        return self._producto.productos_dict()

class DescuentoDecorador(ProductoDecorador):
    def __init__(self, producto, descuento):
        super().__init__(producto)
        self.descuento = descuento
        print(f"DEBUG: Descuento de {descuento*100}% aplicado a {producto.nombre}")

    def get_precio(self):
        return self._producto.get_precio() * (1 - self.descuento)

    def get_descripcion(self):
        return f"{self._producto.get_descripcion()} (Descuento {int(self.descuento*100)}%)"

class EnvioDecorador(ProductoDecorador):
    def get_precio(self):
        return self._producto.get_precio() + 100000

    def get_descripcion(self):
        return f"{self._producto.get_descripcion()} + envío extra"

# --- LOGIN ---
class IngresoApp:
    def __init__(self, page):
        self.page = page
        self.page.title = "Login E-commerce"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.db = Database()
        print("DEBUG: Aplicación de ingreso inicializada")
        self.crear_controles_ingreso()

    def crear_controles_ingreso(self):
        print("DEBUG: Creando controles de ingreso")
        self.email_login = ft.TextField(
            label="Email",
            width=300,
            hint_text="tu@email.com"
        )
        self.password_login = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=300,
            hint_text="Ingresa tu contraseña"
        )
        self.btn_login = ft.ElevatedButton(
            text="Iniciar Sesión",
            on_click=self.iniciar_sesion,
            width=200
        )
        self.btn_registrar = ft.TextButton(
            text="¿No tienes cuenta? Regístrate aquí",
            on_click=self.ir_a_registro
        )
        # Nuevo botón para registro de administradores
        self.btn_registrar_admin = ft.TextButton(
            text="Registro para Administradores",
            on_click=self.ir_a_registro_admin,
            style=ft.ButtonStyle(color=ft.Colors.ORANGE)
        )
        self.mensaje_login = ft.Text("", color="red")

        self.login_container = ft.Container(
            content=ft.Column([
                ft.Text("INICIAR SESIÓN", size=24, weight="bold"),
                ft.Text("Bienvenido de vuelta", size=16, color="gray"),
                self.email_login,
                self.password_login,
                self.btn_login,
                self.btn_registrar,
                self.btn_registrar_admin,  
                self.mensaje_login
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            width=400
        )

        self.page.add(ft.Row([
            self.login_container
        ], alignment=ft.MainAxisAlignment.CENTER))
        print("DEBUG: Controles de ingreso creados")

    def iniciar_sesion(self, e):
        print("DEBUG: Intentando iniciar sesión")
        email = self.email_login.value.strip().lower()
        password = self.password_login.value

        if not email:
            self.mensaje_login.value = "Por favor ingresa tu email"
            self.page.update()
            print("DEBUG: Error - Email vacío")
            return
        if not password:
            self.mensaje_login.value = "Por favor ingresa tu contraseña"
            self.page.update()
            print("DEBUG: Error - Contraseña vacía")
            return

        users = self.db.cargar_usuarios()
        if email not in users:
            self.mensaje_login.value = "El usuario no existe"
            self.mensaje_login.color = "red"
            self.page.update()
            print(f"DEBUG: Error - Usuario {email} no existe")
            return

        user = users[email]
        
        # VERIFICAR BLOQUEO USANDO LA NUEVA TABLA
        estado_bloqueo = self.db.obtener_estado_bloqueo(email)
        if estado_bloqueo['bloqueado']:
            self.mensaje_login.value = f"❌ Cuenta bloqueada. Contacta al administrador. (Bloqueado por: {estado_bloqueo['realizado_por']})"
            self.mensaje_login.color = "red"
            self.page.update()
            print(f"DEBUG: Error - Cuenta {email} bloqueada por {estado_bloqueo['realizado_por']}")
            return
        
        if user['password'] != password:
            self.mensaje_login.value = "Contraseña incorrecta"
            self.mensaje_login.color = "red"
            self.page.update()
            print("DEBUG: Error - Contraseña incorrecta")
            return

        print(f"DEBUG: Login exitoso para {email}")
        self.page.clean()
        AplicacionPrincipal(self.page, user)

    def ir_a_registro(self, e):
        print("DEBUG: Navegando a registro de usuario")
        self.page.clean()
        RegistroApp(self.page, self.db)

    def ir_a_registro_admin(self, e):
        print("DEBUG: Navegando a registro de administrador")
        self.page.clean()
        RegistroAdminApp(self.page, self.db)

# --- REGISTRO ADMINISTRADOR ---
class RegistroAdminApp:
    def __init__(self, page, db):
        self.page = page
        self.page.title = "Registro Administrador"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.db = db
        print("DEBUG: Aplicación de registro de administrador inicializada")
        self.control_registro()

    def control_registro(self):
        """Crear controles de registro para administradores"""
        print("DEBUG: Creando controles de registro de administrador")
        
        self.nombre = ft.TextField(
            label="Nombre completo", 
            width=300,
            hint_text="Ingresa tu nombre completo"
        )
        self.email = ft.TextField(
            label="Email", 
            width=300,
            hint_text="admin@ejemplo.com"
        )
        self.password = ft.TextField(
            label="Contraseña", 
            password=True, 
            can_reveal_password=True, 
            width=300,
            hint_text="Mínimo 8 caracteres"
        )
        self.confirm_password = ft.TextField(
            label="Confirmar contraseña", 
            password=True, 
            can_reveal_password=True, 
            width=300
        )
        
        self.btn_registrar = ft.ElevatedButton(
            text="Registrar Administrador", 
            on_click=self.registrar_administrador, 
            width=200,
            style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE, color=ft.Colors.WHITE)
        )
        
        self.btn_volver_login = ft.TextButton(
            text="Volver al login", 
            on_click=self.volver_al_login
        )
        
        self.mensaje = ft.Text("")

        self.registro_container = ft.Container(
            content=ft.Column([
                ft.Text("REGISTRO ADMINISTRADOR", size=24, weight="bold", color=ft.Colors.ORANGE),
                ft.Text("Crear cuenta de administrador", size=16, color="gray"),
                self.nombre,
                self.email,
                self.password,
                self.confirm_password,
                ft.Row([self.btn_registrar], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([self.btn_volver_login], alignment=ft.MainAxisAlignment.CENTER),
                self.mensaje
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            width=400
        )

        self.page.add(ft.Row([self.registro_container], alignment=ft.MainAxisAlignment.CENTER))
        print("DEBUG: Controles de registro de administrador creados")

    def validar_correo(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validar_formulario(self):
        print("DEBUG: Validando formulario de registro de administrador")
        if not self.nombre.value.strip():
            return "El nombre es obligatorio"
        if not self.email.value.strip():
            return "El email es obligatorio"
        if not self.validar_correo(self.email.value):
            return "El formato del email no es válido"
        users = self.db.cargar_usuarios()
        if self.email.value.lower() in users:
            return "Este email ya está registrado"
        if not self.password.value:
            return "La contraseña es obligatoria"
        if len(self.password.value) < 8:
            return "La contraseña debe tener al menos 8 caracteres"
        if self.password.value != self.confirm_password.value:
            return "Las contraseñas no coinciden"
        print("DEBUG: Formulario de administrador validado correctamente")
        return None

    def registrar_administrador(self, e):
        print("DEBUG: Intentando registrar administrador")
        error = self.validar_formulario()
        if error:
            self.mensaje.value = error
            self.mensaje.color = "red"
            self.page.update()
            print(f"DEBUG: Error en registro de administrador: {error}")
            return

        datos_admin = {
            'nombre': self.nombre.value.strip(),
            'email': self.email.value.lower(),
            'password': self.password.value,
            'tipo': 'administrador',  # Tipo específico para administradores
            'fecha_registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.db.guardar_usuario(datos_admin)
        self.mensaje.value = "¡Administrador registrado exitosamente!"
        self.mensaje.color = "green"
        self.page.update()
        print(f"DEBUG: Administrador {datos_admin['email']} registrado exitosamente")

    def volver_al_login(self, e):
        print("DEBUG: Volviendo al login desde registro de administrador")
        self.page.clean()
        IngresoApp(self.page)

# --- REGISTRO USUARIO NORMAL ---
class RegistroApp:
    def __init__(self, page, db):
        self.page = page
        self.page.title = "Registro E-commerce"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.db = db
        print("DEBUG: Aplicación de registro inicializada")
        self.control_registro()

    def control_registro(self):
        """Crear controles de registro"""
        print("DEBUG: Creando controles de registro")
        self.tipo_usuario = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="cliente", label="Cliente"),
                ft.Radio(value="vendedor", label="Vendedor")
            ]),
            value="cliente"
        )
        self.nombre = ft.TextField(label="Nombre completo", width=300)
        self.email = ft.TextField(label="Email", width=300)
        self.password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)
        self.confirm_password = ft.TextField(label="Confirmar contraseña", password=True, can_reveal_password=True, width=300)
        self.nombre_tienda = ft.TextField(label="Nombre de la tienda", width=300, visible=False)
        self.telefono = ft.TextField(label="Teléfono de contacto", width=300, visible=False)
        self.btn_registrar = ft.ElevatedButton(text="Registrarse", on_click=self.registrar_usuario, width=150)
        self.btn_volver_login = ft.TextButton(text="Volver al login", on_click=self.volver_al_login)
        self.mensaje = ft.Text("")

        self.registro_container = ft.Container(
            content=ft.Column([
                ft.Text("CREA TU CUENTA", size=24, weight="bold"),
                ft.Text("Selecciona tu tipo de cuenta:"),
                self.tipo_usuario,
                self.nombre,
                self.email,
                self.password,
                self.confirm_password,
                self.nombre_tienda,
                self.telefono,
                ft.Row([self.btn_registrar], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([self.btn_volver_login], alignment=ft.MainAxisAlignment.CENTER),
                self.mensaje
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            width=400
        )

        self.tipo_usuario.on_change = self.activar_campos_vendedor
        self.page.add(ft.Row([self.registro_container], alignment=ft.MainAxisAlignment.CENTER))
        print("DEBUG: Controles de registro creados")

    def activar_campos_vendedor(self, e):
        es_vendedor = self.tipo_usuario.value == "vendedor"
        print(f"DEBUG: Campos de vendedor {'activados' if es_vendedor else 'desactivados'}")
        self.nombre_tienda.visible = es_vendedor
        self.telefono.visible = es_vendedor
        self.page.update()

    def validar_correo(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validar_formulario(self):
        print("DEBUG: Validando formulario de registro")
        if not self.nombre.value.strip():
            return "El nombre es obligatorio"
        if not self.email.value.strip():
            return "El email es obligatorio"
        if not self.validar_correo(self.email.value):
            return "El formato del email no es válido"
        users = self.db.cargar_usuarios()
        if self.email.value.lower() in users:
            return "Este email ya está registrado"
        if not self.password.value:
            return "La contraseña es obligatoria"
        if len(self.password.value) < 8:
            return "La contraseña debe tener al menos 8 caracteres"
        if self.password.value != self.confirm_password.value:
            return "Las contraseñas no coinciden"
        if self.tipo_usuario.value == "vendedor":
            if not self.nombre_tienda.value.strip():
                return "El nombre de la tienda es obligatorio"
            if not self.telefono.value.strip():
                return "El teléfono es obligatorio"
        print("DEBUG: Formulario validado correctamente")
        return None

    def registrar_usuario(self, e):
        print("DEBUG: Intentando registrar usuario")
        error = self.validar_formulario()
        if error:
            self.mensaje.value = error
            self.mensaje.color = "red"
            self.page.update()
            print(f"DEBUG: Error en registro: {error}")
            return
        else:
            datos_usuario = {
                'nombre': self.nombre.value.strip(),
                'email': self.email.value.lower(),
                'password': self.password.value,
                'tipo': self.tipo_usuario.value,
                'fecha_registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            if self.tipo_usuario.value == "vendedor":
                datos_usuario['nombre_tienda'] = self.nombre_tienda.value.strip()
                datos_usuario['telefono'] = self.telefono.value.strip()

            self.db.guardar_usuario(datos_usuario)
            self.mensaje.value = f"¡Registro exitoso! Cuenta de {self.tipo_usuario.value.capitalize()} creada"
            self.mensaje.color = "green"
            self.page.update()
            print(f"DEBUG: Usuario {datos_usuario['email']} registrado exitosamente")

    def volver_al_login(self, e):
        print("DEBUG: Volviendo al login")
        self.page.clean()
        IngresoApp(self.page)

# --- DETALLE PRODUCTO CON PATRONES ---
class DetalleProducto(Observador):
    def __init__(self, page, producto, carrito_callback, volver_callback):
        self.page = page
        self.producto_base = producto
        self.producto_actual = producto
        self.carrito_callback = carrito_callback
        self.volver_callback = volver_callback
        self.subject = ProductoSujeto()
        self.subject.agregar_observador(self)
        self.page.title = f"Detalle: {producto.nombre}"
        print(f"DEBUG: Detalle de producto inicializado: {producto.nombre}")
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        print("DEBUG: Creando interfaz de detalle de producto")
        image_box = ft.Container(
            content=ft.Text(self.producto_base.imagen, size=40),
            width=140,
            height=140,
            alignment=ft.alignment.center,
            border=ft.border.all(1, "black"),
            bgcolor="white",
        )

        self.nombre_texto = ft.Text(self.producto_actual.get_descripcion(), size=20, weight="bold")
        self.precio_texto = ft.Text(f"${self.producto_actual.get_precio():,.2f}", size=18, color="green")
        
        self.descuento_checkbox = ft.Checkbox(label="Aplicar cupón 20% descuento", on_change=self.actualizar_precio)
        self.envio_checkbox = ft.Checkbox(label="Aplicar envío ultra rápido", on_change=self.actualizar_precio)

        self.mensajes = ft.Column([], spacing=5, scroll="auto")

        barra_superior = ft.Row(
            controls=[
                ft.ElevatedButton("⬅️ Volver", on_click=self.volver),
                ft.Container(expand=True),
                ft.Text("Detalle del Producto", size=20, weight="bold")
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        contenido = ft.Column(
            [
                barra_superior,
                ft.Divider(),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Row([image_box], alignment="center"),
                                self.nombre_texto,
                                self.precio_texto,
                                ft.Text(self.producto_base.descripcion, size=12, color="gray"),
                                ft.Divider(),
                                self.descuento_checkbox,
                                self.envio_checkbox,
                                ft.Row(
                                    [
                                        ft.ElevatedButton("Añadir al carrito", on_click=self.al_carrito, bgcolor="blue", color="white"),
                                    ],
                                    alignment="center",
                                    spacing=20,
                                )
                            ],
                            horizontal_alignment="center",
                            spacing=10,
                        ),
                        padding=20,
                    ),
                ),
                ft.Text("Eventos:", size=16, weight="bold"),
                self.mensajes
            ],
            horizontal_alignment="center",
            spacing=15,
            expand=True
        )

        self.page.clean()
        self.page.add(contenido)
        print("DEBUG: Interfaz de detalle de producto creada")
    
    def actualizar_precio(self, e=None):
        print("DEBUG: Actualizando precio del producto")
        self.producto_actual = self.producto_base
        
        if self.descuento_checkbox.value:
            self.producto_actual = DescuentoDecorador(self.producto_actual, 0.2)
            print("DEBUG: Descuento aplicado")
        if self.envio_checkbox.value:
            self.producto_actual = EnvioDecorador(self.producto_actual)
            print("DEBUG: Envío aplicado")

        self.nombre_texto.value = self.producto_actual.get_descripcion()
        self.precio_texto.value = f"${self.producto_actual.get_precio():,.2f}"
        self.page.update()
        print(f"DEBUG: Precio actualizado: {self.precio_texto.value}")
    
    def al_carrito(self, e):
        print("DEBUG: Añadiendo producto al carrito")
        producto_dict = self.producto_base.productos_dict()
        producto_dict['precio_final'] = self.producto_actual.get_precio()
        producto_dict['descripcion_final'] = self.producto_actual.get_descripcion()
        
        self.carrito_callback(producto_dict)
        
        mensaje = f"'{self.producto_actual.get_descripcion()}' añadido al carrito"
        self.subject.notificar_observadores(mensaje)
        print(f"DEBUG: {mensaje}")
    
    def actualizar(self, mensaje):
        print(f"DEBUG: Observador actualizado: {mensaje}")
        self.mensajes.controls.append(ft.Text(mensaje, color="blue"))
        self.page.update()
    
    def volver(self, e):
        print("DEBUG: Volviendo desde detalle de producto")
        self.page.clean()
        self.volver_callback()

# --- CARRITO ---
class Carrito:
    def __init__(self, page, user, carrito, volver_callback):
        self.page = page
        self.user = user
        self.carrito = carrito
        self.volver_callback = volver_callback
        self.db = Database()
        self.page.title = "Carrito de Compras"
        print(f"DEBUG: Carrito inicializado con {len(carrito)} productos")
        
        self.controles_carrito()
    
    def controles_carrito(self):
        print("DEBUG: Creando controles de carrito")
        barra_superior = ft.Row(
            controls=[
                ft.ElevatedButton("⬅️ Volver", on_click=self.volver),
                ft.Container(expand=True),
                ft.Text("🛒 Carrito de Compras", size=20, weight="bold")
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        if not self.carrito:
            contenido = ft.Column([
                barra_superior,
                ft.Text("Tu carrito está vacío", size=18, color="gray"),
                ft.ElevatedButton("Seguir comprando", on_click=self.volver)
            ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            print("DEBUG: Carrito vacío")
        else:
            productos_carrito = []
            total = 0
            
            for producto_id, item in self.carrito.items():
                subtotal = item['precio_final'] * item['cantidad']
                total += subtotal
                
                productos_carrito.append(
                    ft.Row([
                        ft.Text(f"{item['descripcion_final']}", size=16, weight="bold", width=200),
                        ft.Text(f"${item['precio_final']:,.2f}", width=100),
                        ft.Row([
                            ft.IconButton(ft.Icons.REMOVE, on_click=lambda e, id=producto_id: self.actualizar_cantidad(id, -1)),
                            ft.Text(f"{item['cantidad']}", width=30, text_align=ft.TextAlign.CENTER),
                            ft.IconButton(ft.Icons.ADD, on_click=lambda e, id=producto_id: self.actualizar_cantidad(id, 1)),
                        ]),
                        ft.Text(f"${subtotal:,.2f}", width=100, color="green", weight="bold"),
                        ft.IconButton(ft.Icons.DELETE, icon_color="red", 
                                    on_click=lambda e, id=producto_id: self.eliminar_producto(id))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            
            productos_carrito.append(ft.Divider())
            productos_carrito.append(
                ft.Row([
                    ft.Text("TOTAL:", size=18, weight="bold"),
                    ft.Text(f"${total:,.2f}", size=18, color="green", weight="bold")
                ], alignment=ft.MainAxisAlignment.END)
            )
            
            botones_accion = ft.Row([
                ft.ElevatedButton(
                    "Finalizar Compra", 
                    on_click=lambda e: self.procesar_pago(total), 
                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
                    width=200
                ),
                ft.ElevatedButton(
                    "Seguir Comprando", 
                    on_click=self.volver,
                    width=200
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
            
            productos_carrito.append(botones_accion)
            
            contenido = ft.Column([
                barra_superior,
                *productos_carrito
            ], spacing=15)
            
            print(f"DEBUG: Carrito con {len(self.carrito)} productos, total: ${total:,.2f}")
        
        self.page.clean()
        self.page.add(contenido)
        print("DEBUG: Controles de carrito creados")
    
    def actualizar_cantidad(self, producto_id, cambio):
        """Actualizar la cantidad de un producto en el carrito"""
        print(f"DEBUG: Actualizando cantidad del producto {producto_id}, cambio: {cambio}")
        if producto_id in self.carrito:
            self.carrito[producto_id]['cantidad'] += cambio
            
            if self.carrito[producto_id]['cantidad'] <= 0:
                del self.carrito[producto_id]
                print(f"DEBUG: Producto {producto_id} eliminado del carrito")
        
        self.controles_carrito()
    
    def eliminar_producto(self, producto_id):
        print(f"DEBUG: Eliminando producto {producto_id} del carrito")
        if producto_id in self.carrito:
            del self.carrito[producto_id]
        
        self.controles_carrito()
    
    def procesar_pago(self, total):
        """Abrir la pasarela de pago"""
        print(f"DEBUG: Procesando pago por ${total:,.2f}")
        self.page.clean()
        PasarelaPago(self.page, self.user, self.carrito, total, self.volver_callback)
    
    def volver(self, e):
        """Volver a la página principal"""
        print("DEBUG: Volviendo a página principal desde carrito")
        self.page.clean()
        self.volver_callback(self.carrito)

# --- PASARELA DE PAGO ---
class PasarelaPago:
    def __init__(self, page, user, carrito, total, volver_callback):
        self.page = page
        self.user = user
        self.carrito = carrito
        self.total = total
        self.volver_callback = volver_callback
        self.db = Database()
        self.page.title = "Pasarela de Pago"
        self.page.bgcolor = "#1a1a1a"
        self.page.theme_mode = ft.ThemeMode.DARK
        
        # Generar ID de pedido una sola vez
        self.order_id = str(uuid.uuid4())[:8]
        self.fecha_actual = datetime.now().strftime("%d/%m/%Y")
        
        print(f"DEBUG: Pasarela de pago inicializada. Order ID: {self.order_id}, Total: ${self.total:,.2f}")
        
        self.crear_pasarela()
    
    def crear_pasarela(self):
        print("DEBUG: Creando interfaz de pasarela de pago")
        # Detalles del pedido
        detalles = [
            ("ID:", self.order_id),
            ("Monto:", f"${self.total:,.2f}"),
            ("Fecha:", self.fecha_actual),
            ("Método de pago:", "Tarjeta"),
            ("Estado del pago:", "Pendiente"),
        ]

        # Panel izquierdo: Detalles del pedido
        panel_izquierdo = ft.Container(
            content=ft.Column([
                ft.Text("Importe:", size=16, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text(f"${self.total:,.2f}", size=20, weight=ft.FontWeight.BOLD, color="#4fc3f7"),
                *[ft.Text(f"{k} {v}", size=12, color="white") for k, v in detalles],
                ft.Divider(color="#333333"),
                ft.Text("Productos:", size=14, weight=ft.FontWeight.BOLD, color="white"),
                *[ft.Text(f"- {item['descripcion_final']} x{item['cantidad']}", size=12, color="white") 
                  for item in self.carrito.values()]
            ], spacing=5, alignment="start"),
            bgcolor="#2d2d2d",
            padding=15,
            border=ft.border.all(1, "#444444"),
            border_radius=10,
            width=280
        )

        # Panel derecho: Formulario de pago
        self.num_tarjeta = ft.TextField(
            label="Nº Tarjeta", 
            width=280,
            border_color="#666666",
            color="white",
            cursor_color="white",
            label_style=ft.TextStyle(color="white"),
            bgcolor="#333333",
            hint_text="1234 5678 9012 3456",
            on_change=self.validar_tarjeta_en_tiempo_real
        )
        self.expiracion = ft.TextField(
            label="Caducidad (MM/AA)", 
            width=280,
            border_color="#666666",
            color="white",
            cursor_color="white",
            label_style=ft.TextStyle(color="white"),
            bgcolor="#333333",
            hint_text="MM/AA",
            on_change=self.validar_expiracion
        )
        self.cvv = ft.TextField(
            label="Cód. Seguridad", 
            width=280, 
            password=True,
            can_reveal_password=True,
            border_color="#666666",
            color="white",
            cursor_color="white",
            label_style=ft.TextStyle(color="white"),
            bgcolor="#333333",
            hint_text="123",
            on_change=self.validar_cvv
        )

        # Mensajes de error
        self.mensaje_error = ft.Text("", color="red", size=12, visible=False)

        # Botones de acción
        botones_accion = ft.Row([
            ft.ElevatedButton("CANCELAR", 
                            bgcolor="#d32f2f", 
                            color="white", 
                            on_click=self.cancelar_pago,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))),
            ft.ElevatedButton("PAGAR", 
                            bgcolor="#4fc3f7", 
                            color="black", 
                            on_click=self.completar_pago,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5))),
        ], spacing=10)

        panel_derecho = ft.Container(
            content=ft.Column([
                ft.Text("PAGAR CON TARJETA", size=14, weight=ft.FontWeight.BOLD, color="white"),
                self.num_tarjeta,
                self.expiracion,
                self.cvv,
                self.mensaje_error,
                botones_accion
            ], spacing=10, alignment="start"),
            bgcolor="#2d2d2d",
            padding=15,
            border=ft.border.all(1, "#444444"),
            border_radius=10,
            width=320
        )

        # Barra superior
        barra_superior = ft.Row([
            ft.ElevatedButton("⬅️ Volver al carrito", 
                            on_click=self.cancelar_pago,
                            style=ft.ButtonStyle(
                                bgcolor="#333333",
                                color="white",
                                shape=ft.RoundedRectangleBorder(radius=5)
                            )),
            ft.Container(expand=True),
            ft.Text("Pasarela de Pago", size=20, weight="bold", color="white")
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Layout principal
        contenido = ft.Column([
            barra_superior,
            ft.Divider(color="#333333"),
            ft.Row(
                [panel_izquierdo, panel_derecho],
                alignment="center",
                spacing=20,
            )
        ], spacing=20)

        self.page.clean()
        self.page.add(contenido)
        print("DEBUG: Interfaz de pasarela de pago creada")
    
    def validar_tarjeta_en_tiempo_real(self, e):
        """Validar formato de tarjeta mientras se escribe"""
        valor = self.num_tarjeta.value
        print(f"DEBUG: Validando tarjeta: {valor}")
        if valor and (not valor.isdigit() or len(valor) != 16):
            self.mostrar_error("La tarjeta debe tener 16 dígitos")
        else:
            self.ocultar_error()
    
    def validar_expiracion(self, e):
        """Validar formato de expiración""" 
        valor = self.expiracion.value
        print(f"DEBUG: Validando expiración: {valor}")
        if valor and not re.match(r'^\d{2}/\d{2}$', valor):
            self.mostrar_error("Formato MM/AA requerido")
        else:
            self.ocultar_error()
    
    def validar_cvv(self, e):
        """Validar CVV """
        valor = self.cvv.value
        print(f"DEBUG: Validando CVV: {valor}")
        if valor and (not valor.isdigit() or len(valor) not in [3, 4]):
            self.mostrar_error("CVV debe tener 3-4 dígitos")
        else:
            self.ocultar_error()
    
    def mostrar_error(self, mensaje):
        """Mostrar mensaje de error"""
        print(f"DEBUG: Mostrando error: {mensaje}")
        self.mensaje_error.value = mensaje
        self.mensaje_error.visible = True
        self.page.update()
    
    def ocultar_error(self):
        """Ocultar mensaje de error"""
        print("DEBUG: Ocultando error")
        self.mensaje_error.visible = False
        self.page.update()
    
    def cancelar_pago(self, e):
        """Volver al carrito sin completar el pago"""
        print("DEBUG: Cancelando pago, volviendo al carrito")
        self.page.clean()
        Carrito(self.page, self.user, self.carrito, self.volver_callback)
    
    def mostrar_diagnostico_pedido(self, pedido):
        """Función para diagnosticar problemas con el guardado de pedidos"""
        print(f"\n🔍 DIAGNÓSTICO DE PEDIDO:")
        print(f"   ID: {pedido['id']}")
        print(f"   Cliente: {pedido['cliente']}")
        print(f"   Total: ${pedido['total']:,.2f}")
        print(f"   Productos: {len(pedido['productos'])}")
        
        # Verificar estructura de productos
        for prod_id, producto in pedido['productos'].items():
            print(f"     - {producto['nombre']} x{producto['cantidad']}")
    
    def completar_pago(self, e):
        """Procesar el pago completo con integración a Mercado Pago"""
        
        print("DEBUG: Botón PAGAR presionado")
        
        # Validar campos
        if not self.validar_campos():
            print("DEBUG: Validación falló")
            return
        
        print("DEBUG: Validación exitosa")
        
        # ✅ Fecha con formato correcto para SQLite
        fecha_bd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Crear registro del pedido
        pedido = {
            'id': self.order_id,
            'fecha': fecha_bd,
            'cliente': self.user['email'],
            'productos': self.carrito,
            'total': float(self.total),
            'estado': 'Pendiente de pago',
            'metodo_pago': 'Mercado Pago',
            'tarjeta_ultimos_digitos': self.num_tarjeta.value[-4:] if self.num_tarjeta.value else ''
        }
        
        # 🔍 Diagnóstico
        self.mostrar_diagnostico_pedido(pedido)
        
        # --- 🟦 INTEGRACIÓN CON MERCADO PAGO ---
        try:
            print("DEBUG: Iniciando integración con Mercado Pago...")
            sdk = mercadopago.SDK(ACCESS_TOKEN)

            datos_preferencia = {
                "items": [
                    {
                        "title": "Compra en la tienda",
                        "quantity": 1,
                        "currency_id": "COP",
                        "unit_price": float(self.total)
                    }
                ],
                "payer": {"email": self.user["email"]},
                "back_urls": {
                    "success": "https://www.exito.com/success",
                    "failure": "https://www.exito.com/failure",
                    "pending": "https://www.exito.com/pending"
                },
                "auto_return": "approved"
            }

            respuesta_preferencia = sdk.preference().create(datos_preferencia)
            url_pago = respuesta_preferencia["response"]["init_point"]

            print(f"DEBUG: Preferencia creada con éxito → {url_pago}")

            # Abrir el pago dentro de la app (en una vista web)
            self.mostrar_pagina_pago(url_pago)

            # Guardar el pedido en la base de datos como "pendiente"
            self.db.guardar_pedido(pedido)
            print("DEBUG: Pedido guardado como pendiente de pago")

        except Exception as error:
            print(f"DEBUG: Error en la integración con Mercado Pago: {error}")
            self.mostrar_error(f"Error al conectar con Mercado Pago: {str(error)}")
            return     
    
    def mostrar_pagina_pago(self, url):
        """Abrir el pago de Mercado Pago en el navegador predeterminado."""
        print(f"🛒 Abriendo página de pago en navegador: {url}")
        webbrowser.open(url)

        # Mensaje informativo dentro de la app
        self.mostrar_mensaje("Se abrió la página de pago en tu navegador. Completa la transacción y vuelve a la app.")


    def validar_campos(self):
        """Validar los campos del formulario de pago"""
        print("DEBUG: Validando campos de pago")
        # Obtener valores
        tarjeta = self.num_tarjeta.value or ""
        expiracion = self.expiracion.value or ""
        cvv = self.cvv.value or ""
        
        # Validar que todos los campos estén completos
        if not tarjeta or not expiracion or not cvv:
            self.mostrar_error("Por favor, completa todos los campos")
            return False
        
        # Validar formato de tarjeta (solo números, 16 dígitos)
        if not tarjeta.isdigit() or len(tarjeta) != 16:
            self.mostrar_error("El número de tarjeta debe tener 16 dígitos")
            return False
        
        # Validar formato de expiración (MM/AA)
        if not re.match(r'^\d{2}/\d{2}$', expiracion):
            self.mostrar_error("Formato de fecha inválido. Usa MM/AA")
            return False
        
        # Validar CVV (3-4 dígitos)
        if not cvv.isdigit() or len(cvv) not in [3, 4]:
            self.mostrar_error("El CVV debe tener 3 o 4 dígitos")
            return False
        
        # Validar que la fecha no esté expirada
        try:
            mes, anio = expiracion.split('/')
            mes_actual = datetime.now().month
            anio_actual = datetime.now().year % 100  
            
            if int(anio) < anio_actual or (int(anio) == anio_actual and int(mes) < mes_actual):
                self.mostrar_error("La tarjeta está expirada")
                return False
        except:
            self.mostrar_error("Formato de fecha inválido")
            return False
        
        self.ocultar_error()
        print("DEBUG: Campos validados correctamente")
        return True
    
    def mostrar_confirmacion(self):
        """Mostrar diálogo de confirmación de pago exitoso"""
        print("DEBUG: Mostrando confirmación de pago")
        
        # Crear diálogo de forma simple y directa
        dlg = ft.AlertDialog(
            title=ft.Text("✅ Pago Exitoso"),
            content=ft.Column([
                ft.Text(f"ID de pedido: {self.order_id}"),
                ft.Text(f"Total: ${self.total:,.2f}"),
                ft.Text("¡Gracias por tu compra!"),
            ], tight=True),
            actions=[
                ft.TextButton("Continuar", on_click=self.finalizar_compra)
            ],
        )
        
        # Abrir diálogo
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
        print("DEBUG: Diálogo de confirmación mostrado")
    
    def finalizar_compra(self, e):
        """Finalizar la compra y volver a la página principal"""
        print("DEBUG: Finalizando compra desde diálogo")
        
        # Cerrar diálogo
        self.page.dialog.open = False
        self.page.update()
        
        # Volver a la página principal con carrito vacío
        self.page.clean()
        self.volver_callback({})
        print("DEBUG: Compra finalizada, volviendo a página principal")

# --- APLICACIÓN PRINCIPAL --
class AplicacionPrincipal:
    def __init__(self, page, user, carrito=None):
        self.page = page
        self.user = user
        self.carrito = carrito or {}
        self.db = Database()
        self.page.title = "E-commerce Principal"
        self.page.scroll = ft.ScrollMode.AUTO
        print(f"DEBUG: Aplicación principal inicializada para usuario {user['nombre']}")
        print(f"DEBUG: Tipo de usuario: {user['tipo']}")

        self.controles_PagPrincipal()

    def mostrar_mensaje(self, texto):
        """Mostrar un mensaje temporal en la parte inferior"""
        print(f"DEBUG: Mostrando mensaje: {texto}")
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            duration=2000,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def cargar_datos(self):
        """Cargar productos, categorías y marcas"""
        print("DEBUG: Cargando datos de productos")
        productos, categorias, marcas = self.db.cargar_productos()
        return {"productos": productos, "categorias": categorias, "marcas": marcas}

    def crear_interfaz_producto(self, producto):
        card = ft.Card(
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
        return card

    def ver_detalles_producto(self, producto):
        print(f"DEBUG: Viendo detalles de producto: {producto.nombre}")
        self.page.clean()
        DetalleProducto(self.page, producto, self.agregar_al_carrito, self.volver_de_detalle)

    def agregar_al_carrito(self, producto):
        """Agregar producto al carrito desde el detalle"""
        producto_id = str(producto['id'])
        print(f"DEBUG: Agregando producto al carrito: {producto['nombre']} (ID: {producto_id})")
        
        if producto_id in self.carrito:
            self.carrito[producto_id]['cantidad'] += 1
            print(f"DEBUG: Cantidad incrementada: {self.carrito[producto_id]['cantidad']}")
        else:
            self.carrito[producto_id] = {
                'id': producto['id'],
                'nombre': producto['nombre'],
                'precio_base': producto['precio'],
                'precio_final': producto['precio_final'],
                'descripcion_final': producto['descripcion_final'],
                'cantidad': 1
            }
            print("DEBUG: Nuevo producto añadido al carrito")
        
        self.mostrar_mensaje(f"✅ {producto['descripcion_final']} añadido al carrito")
        self.actualizar_contador_carrito()

    def volver_de_detalle(self):
        print("DEBUG: Volviendo desde detalle de producto")
        self.controles_PagPrincipal()
        
    def actualizar_contador_carrito(self):
        total_items = sum(item['cantidad'] for item in self.carrito.values())
        self.btn_carrito.text = f"🛒 Carrito ({total_items})"
        self.page.update()
        print(f"DEBUG: Contador de carrito actualizado: {total_items} items")

    def buscar_productos(self, query):
        print(f"DEBUG: Buscando productos: {query}")
        data = self.cargar_datos()
        productos = data["productos"]
        
        if not query:
            return productos
        
        query = query.lower()
        resultados = []
        
        for producto in productos:
            if (query in producto.nombre.lower() or 
                query in producto.marca.lower() or 
                query in producto.categoria.lower()):
                resultados.append(producto)
        
        print(f"DEBUG: {len(resultados)} productos encontrados")
        return resultados

    def controles_PagPrincipal(self):
        """Crear controles de la página principal"""
        print("DEBUG: Creando controles de página principal")
        data = self.cargar_datos()
        productos = data["productos"]

        self.campo_busqueda = ft.TextField(
            label="Buscar productos...",
            width=900,
            on_submit=self.barra_buscar_productos,
            suffix=ft.IconButton(ft.Icons.SEARCH, on_click=self.barra_buscar_productos)
        )

        total_items = sum(item['cantidad'] for item in self.carrito.values())
        self.btn_carrito = ft.ElevatedButton(
            f"🛒 Carrito ({total_items})", 
            on_click=self.abrir_carrito
        )

        # BOTÓN DE PANEL ADMINISTRADOR (solo visible para administradores)
        self.btn_panel_admin = ft.ElevatedButton(
            "Panel Administrador",
            on_click=self.abrir_panel_admin,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE,
                color=ft.Colors.WHITE
            ),
            visible=(self.user['tipo'] == 'administrador')  # Solo visible para admins
        )

        # Crear la barra superior con los botones
        botones_superiores = [
            ft.ElevatedButton("⬅️ Cerrar Sesión", on_click=self.cerrar_sesion),
            ft.Container(width=20),
            self.campo_busqueda,
            ft.Container(width=20),
            self.btn_carrito
        ]

        # Agregar botón de admin si el usuario es administrador
        if self.user['tipo'] == 'administrador':
            botones_superiores.append(ft.Container(width=20))
            botones_superiores.append(self.btn_panel_admin)

        barra_superior = ft.Row(
            controls=botones_superiores,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        welcome_text = ft.Text(f"¡Bienvenido {self.user['nombre']}!", size=24, weight="bold")
        user_type = ft.Text(f"Tipo de cuenta: {self.user['tipo'].capitalize()}", size=16)


        destacados = [p for p in productos if hasattr(p, 'destacado') and p.destacado]
        lista_destacados = [self.crear_interfaz_producto(p) for p in destacados]

        lista_todos = [self.crear_interfaz_producto(p) for p in productos]

        self.contenedor = ft.Column(
            controls=[
                barra_superior,
                welcome_text,
                user_type,
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

        self.page.clean()
        self.page.add(self.contenedor)
        print("DEBUG: Controles de página principal creados")

    def abrir_panel_admin(self, e):
        """Abrir el panel de administrador"""
        print("DEBUG: Abriendo panel de administrador")
        self.page.clean()
        PanelAdministrador(self.page, self.user, self.volver_de_panel_admin)

    def volver_de_panel_admin(self):
        """Volver desde el panel de administrador a la página principal"""
        print("DEBUG: Volviendo desde panel de administrador")
        self.controles_PagPrincipal()

    def barra_buscar_productos(self, e):
        query = self.campo_busqueda.value.strip()
        print(f"DEBUG: Buscando productos con query: {query}")
        resultados = self.buscar_productos(query)

        lista_resultados = [self.crear_interfaz_producto(p) for p in resultados]

        self.contenedor.controls = [
            self.contenedor.controls[0],
            self.contenedor.controls[1],
            self.contenedor.controls[2],
            ft.Divider(),
            ft.Text(f"Resultados de búsqueda para: {query}", size=20, weight="bold"),
            ft.Row(lista_resultados, wrap=True, spacing=10, alignment=ft.MainAxisAlignment.CENTER)
        ]

        self.page.update()
        print("DEBUG: Resultados de búsqueda mostrados")

    def abrir_carrito(self, e):
        print("DEBUG: Abriendo carrito de compras")
        self.page.clean()
        Carrito(self.page, self.user, self.carrito, self.volver_de_carrito)

    def volver_de_carrito(self, carrito_actualizado):
        print("DEBUG: Volviendo desde carrito")
        self.carrito = carrito_actualizado
        self.controles_PagPrincipal()
        self.actualizar_contador_carrito()

    def cerrar_sesion(self, e):
        print("DEBUG: Cerrando sesión")
        self.page.clean()
        IngresoApp(self.page)

# --- PANEL ADMINISTRADOR ---
class PanelAdministrador:
    def __init__(self, page, user, volver_callback):
        self.page = page
        self.user = user
        self.volver_callback = volver_callback
        self.db = Database()
        self.page.title = "Panel Administrador"
        self.page.scroll = ft.ScrollMode.AUTO
        print(f"DEBUG: Panel de administrador inicializado para {user['nombre']}")
        
        self.crear_panel()

    def crear_panel(self):
        print("DEBUG: Creando interfaz del panel de administrador")
        
        # Barra superior
        barra_superior = ft.Row(
            controls=[
                ft.ElevatedButton("⬅️ Volver al Inicio", on_click=self.volver),
                ft.Container(expand=True),
                ft.Text("PANEL ADMINISTRADOR", size=24, weight="bold", color=ft.Colors.ORANGE),
                ft.Container(expand=True),
                ft.Text(f"Admin: {self.user['nombre']}", size=14, color="gray")
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Sección: GESTIÓN DE USUARIOS (FUNCIONAL)
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
                        # Campo para ingresar email
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Ingresa el email del usuario:", size=12, weight="bold"),
                                self.campo_email_usuario,
                                self.mensaje_gestion_usuarios
                            ], spacing=8),
                            padding=ft.padding.only(bottom=10)
                        ),
                        # Botones de acción
                        ft.Row([
                            self.crear_boton_funcionalidad(
                                "🔍 Ver Estado", 
                                "Ver información del usuario",
                                self.ver_estado_usuario,
                                color=ft.Colors.BLUE,
                                compacto=True
                            ),
                            self.crear_boton_funcionalidad(
                                "Desbloquear", 
                                "Desbloquear cuenta",
                                self.desbloquear_usuario,
                                color=ft.Colors.GREEN,
                                compacto=True
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([
                            self.crear_boton_funcionalidad(
                                "Bloquear", 
                                "Bloquear cuenta",
                                self.bloquear_usuario,
                                color=ft.Colors.ORANGE,
                                compacto=True
                            ),
                            self.crear_boton_funcionalidad(
                                "Eliminar", 
                                "Eliminar cuenta",
                                self.eliminar_usuario,
                                color=ft.Colors.RED,
                                compacto=True
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                    ], spacing=8)
                ], spacing=12),
                padding=20,
                width=400
            ),
            elevation=5
        )

        # Sección: GESTIÓN DE MARCAS Y CATEGORÍAS (NUEVA SECCIÓN)
        seccion_marcas_categorias = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CATEGORY, color=ft.Colors.PURPLE),
                        ft.Text(" Marcas y Categorías", size=18, weight="bold"),
                    ]),
                    ft.Divider(),
                    ft.Column([
                        self.crear_boton_funcionalidad(
                            "🏷️ Gestionar Marcas", 
                            "Administrar marcas de productos",
                            self.gestionar_marcas
                        ),
                        self.crear_boton_funcionalidad(
                            "📂 Gestionar Categorías", 
                            "Administrar categorías de productos",
                            self.gestionar_categorias
                        ),
                    ], spacing=8)
                ], spacing=12),
                padding=20,
                width=350
            ),
            elevation=5
        )

        # Sección: GESTIÓN DE INVENTARIO
        seccion_inventario = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INVENTORY, color=ft.Colors.PURPLE),
                        ft.Text(" Gestión de Inventario", size=18, weight="bold"),
                    ]),
                    ft.Divider(),
                    ft.Column([
                        self.crear_boton_funcionalidad(
                            "📊 Ver Inventario", 
                            "Ver stock completo de productos",
                            self.ver_inventario_completo
                        ),
                        self.crear_boton_funcionalidad(
                            "⚠️ Stock Bajo", 
                            "Productos con stock bajo",
                            self.ver_stock_bajo
                        ),
                        self.crear_boton_funcionalidad(
                            "✏️ Actualizar Stock", 
                            "Modificar cantidades de productos",
                            self.actualizar_stock_producto
                        ),
                    ], spacing=8)
                ], spacing=12),
                padding=20,
                width=350
            ),
            elevation=5
        )

        # Sección: GESTIÓN DE PRODUCTOS
        seccion_productos = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INVENTORY_2, color=ft.Colors.GREEN),
                        ft.Text(" Gestión de Productos", size=18, weight="bold"),
                    ]),
                    ft.Divider(),
                    ft.Column([
                        self.crear_boton_funcionalidad(
                            "Aprobar Producto", 
                            "Aprobar productos pendientes de vendedores",
                            self.funcionalidad_desarrollando
                        ),
                        self.crear_boton_funcionalidad(
                            "Editar Producto", 
                            "Modificar información de productos",
                            self.funcionalidad_desarrollando
                        ),
                        self.crear_boton_funcionalidad(
                            "Publicar Producto", 
                            "Publicar nuevos productos en la plataforma",
                            self.funcionalidad_desarrollando
                        ),
                        self.crear_boton_funcionalidad(
                            "Eliminar Producto", 
                            "Eliminar productos de la plataforma",
                            self.funcionalidad_desarrollando,
                            color=ft.Colors.RED
                        ),
                    ], spacing=8)
                ], spacing=12),
                padding=20,
                width=350
            ),
            elevation=5
        )

        # Layout principal del panel
        contenido = ft.Column(
            controls=[
                barra_superior,
                ft.Divider(),
                
                # Encabezado de bienvenida
                ft.Container(
                    content=ft.Column([
                        ft.Text("Bienvenido al Panel de administracion", size=22, weight="bold"),
                        ft.Text("Gestiona todas las operaciones de la plataforma desde un solo lugar", 
                               size=14, color="gray", text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Primera fila de secciones
                ft.Row(
                    [seccion_usuarios, seccion_marcas_categorias],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
                
                ft.Container(height=15),
                
                # Segunda fila de secciones
                ft.Row(
                    [seccion_inventario, seccion_productos],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
                
                # Información del sistema
                ft.Container(
                    content=ft.Column([
                        ft.Divider(),
                        ft.Row([
                            ft.Icon(ft.Icons.INFO, size=16, color="gray"),
                            ft.Text("Panel de Administrador - Versión 1.0", size=12, color="gray"),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Text(
                            "Gestión de Usuarios, Inventario, Marcas y Categorías Funcional | Otras secciones en desarrollo", 
                            size=11, 
                            color="orange", 
                            text_align=ft.TextAlign.CENTER
                        )
                    ], spacing=5),
                    margin=ft.margin.only(top=20)
                )
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        )

        self.page.clean()
        self.page.add(contenido)
        print("DEBUG: Panel de administrador creado exitosamente")

    def crear_boton_funcionalidad(self, texto, descripcion, on_click_func, color=None, compacto=False):
        """Crear un botón de funcionalidad estilizado"""
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
                ft.Text(
                    descripcion, 
                    size=11 if compacto else 11, 
                    color="gray",
                    text_align=ft.TextAlign.CENTER
                )
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.symmetric(vertical=5)
        )

    # === FUNCIONALIDADES DE GESTIÓN DE USUARIOS ===
    
    def validar_email(self, email):
        """Validar formato de email"""
        if not email or not email.strip():
            return False, "Por favor ingresa un email"
        
        email = email.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, "Formato de email inválido"
            
        return True, email

    def obtener_usuario(self, email):
        """Obtener usuario de la base de datos"""
        usuarios = self.db.cargar_usuarios()
        return usuarios.get(email)

    def ver_estado_usuario(self, e):
        """Ver el estado actual de un usuario (versión actualizada con nueva tabla)"""
        email = self.campo_email_usuario.value
        valido, resultado = self.validar_email(email)
        
        if not valido:
            self.mostrar_mensaje_gestion_usuarios(resultado, "red")
            return
        
        usuario = self.obtener_usuario(resultado)
        if not usuario:
            self.mostrar_mensaje_gestion_usuarios("Usuario no encontrado", "red")
            return
        
        # Obtener estado de bloqueo desde la nueva tabla
        estado_bloqueo = self.db.obtener_estado_bloqueo(resultado)
        estado = "🔒 BLOQUEADO" if estado_bloqueo['bloqueado'] else "✅ ACTIVO"
        
        mensaje_estado = f"""
Usuario: {resultado}
Nombre: {usuario.get('nombre', 'N/A')}
Tipo: {usuario.get('tipo', 'N/A')}
Estado: {estado}
Registro: {usuario.get('fecha_registro', 'N/A')}
"""
        
        if estado_bloqueo['bloqueado']:
            mensaje_estado += f"Bloqueado desde: {estado_bloqueo['fecha_operacion']}\n"
            mensaje_estado += f"Bloqueado por: {estado_bloqueo['realizado_por']}"
            if estado_bloqueo['motivo']:
                mensaje_estado += f"\nMotivo: {estado_bloqueo['motivo']}"
        
        # Mostrar historial completo de bloqueos
        historial = self.db.obtener_historial_bloqueos(resultado)
        if historial:
            mensaje_estado += f"\n\n📋 Historial de bloqueos ({len(historial)} registros):"
            for registro in historial[:3]:  # Mostrar solo los 3 más recientes
                tipo = "BLOQUEO" if registro['bloqueado'] else "DESBLOQUEO"
                mensaje_estado += f"\n• {tipo} - {registro['fecha_operacion']} por {registro['realizado_por']}"
        
        self.mostrar_mensaje_gestion_usuarios(mensaje_estado, "blue")

    def desbloquear_usuario(self, e):
        """Desbloquear cuenta de usuario (versión actualizada con nueva tabla)"""
        email = self.campo_email_usuario.value
        valido, resultado = self.validar_email(email)
        
        if not valido:
            self.mostrar_mensaje_gestion_usuarios(resultado, "red")
            return
        
        usuario = self.obtener_usuario(resultado)
        if not usuario:
            self.mostrar_mensaje_gestion_usuarios("Usuario no encontrado", "red")
            return
        
        # Verificar si está bloqueado usando la nueva tabla
        estado_actual = self.db.obtener_estado_bloqueo(resultado)
        if not estado_actual['bloqueado']:
            self.mostrar_mensaje_gestion_usuarios("La cuenta ya está activa", "blue")
            return
        
        # Desbloquear usuario usando el nuevo método
        try:
            self.db.desbloquear_usuario(
                resultado, 
                self.user['email'],
                "Desbloqueo administrativo desde panel"
            )
            
            self.mostrar_mensaje_gestion_usuarios(
                f"✅ Cuenta de {resultado} desbloqueada exitosamente. El usuario puede iniciar sesión nuevamente.", 
                "green"
            )
            print(f"DEBUG: Usuario {resultado} desbloqueado por administrador {self.user['email']}")
            
        except Exception as error:
            self.mostrar_mensaje_gestion_usuarios(f"Error al desbloquear: {str(error)}", "red")

    def bloquear_usuario(self, e):
        """Bloquear cuenta de usuario (versión actualizada con nueva tabla)"""
        email = self.campo_email_usuario.value
        valido, resultado = self.validar_email(email)
        
        if not valido:
            self.mostrar_mensaje_gestion_usuarios(resultado, "red")
            return
        
        usuario = self.obtener_usuario(resultado)
        if not usuario:
            self.mostrar_mensaje_gestion_usuarios("Usuario no encontrado", "red")
            return
        
        # No permitir bloquear al administrador actual
        if resultado == self.user['email']:
            self.mostrar_mensaje_gestion_usuarios("No puedes bloquear tu propia cuenta", "red")
            return
        
        # Verificar si ya está bloqueado usando la nueva tabla
        estado_actual = self.db.obtener_estado_bloqueo(resultado)
        if estado_actual['bloqueado']:
            self.mostrar_mensaje_gestion_usuarios("La cuenta ya está bloqueada", "blue")
            return
        
        # Bloquear usuario usando el nuevo método
        try:
            self.db.bloquear_usuario(
                resultado, 
                self.user['email'],
                "Bloqueo administrativo desde panel"
            )
            
            self.mostrar_mensaje_gestion_usuarios(
                f"🔒 Cuenta de {resultado} bloqueada exitosamente. El usuario no podrá iniciar sesión.", 
                "orange"
            )
            print(f"DEBUG: Usuario {resultado} bloqueado por administrador {self.user['email']}")
            
        except Exception as error:
            self.mostrar_mensaje_gestion_usuarios(f"Error al bloquear: {str(error)}", "red")

    def eliminar_usuario(self, e):
        email = self.campo_email_usuario.value
        valido, resultado = self.validar_email(email)
        
        if not valido:
            self.mostrar_mensaje_gestion_usuarios(resultado, "red")
            return
        
        usuario = self.obtener_usuario(resultado)
        if not usuario:
            self.mostrar_mensaje_gestion_usuarios("Usuario no encontrado", "red")
            return
        
        # No permitir eliminar al administrador actual
        if resultado == self.user['email']:
            self.mostrar_mensaje_gestion_usuarios("No puedes eliminar tu propia cuenta", "red")
            return
        
        # Confirmación de eliminación
        def confirmar_eliminacion(e):
            try:
                self.db.eliminar_usuario(resultado)
                self.mostrar_mensaje_gestion_usuarios(f"🗑️ Cuenta de {resultado} eliminada permanentemente del sistema", "red")
                print(f"DEBUG: Usuario {resultado} eliminado permanentemente por administrador")
                
                # Limpiar campo de email
                self.campo_email_usuario.value = ""
                self.page.update()
                
            except Exception as error:
                self.mostrar_mensaje_gestion_usuarios(f"Error al eliminar: {str(error)}", "red")
                print(f"DEBUG: Error al eliminar usuario: {error}")
            
            self.page.dialog.open = False
            self.page.update()
        
        dialogo = ft.AlertDialog(
            title=ft.Text("⚠️ Confirmar Eliminación Permanente"),
            content=ft.Column([
                ft.Text(f"¿Estás seguro de eliminar permanentemente la cuenta de:"),
                ft.Text(f"{resultado}", weight="bold", size=16),
                ft.Text(f"Nombre: {usuario.get('nombre', 'N/A')}"),
                ft.Text(f"Tipo: {usuario.get('tipo', 'N/A')}"),
                ft.Container(height=10),
                ft.Text("❌ Esta acción NO se puede deshacer y eliminará:", size=12, color="red"),
                ft.Text("• Todos los datos del usuario", size=12, color="red"),
                ft.Text("• Historial asociado", size=12, color="red"),
                ft.Text("• Información personal", size=12, color="red"),
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(self.page.dialog, 'open', False)),
                ft.TextButton("ELIMINAR", on_click=confirmar_eliminacion, 
                             style=ft.ButtonStyle(color=ft.Colors.RED, bgcolor=ft.Colors.RED_50)),
            ],
        )
        
        self.page.dialog = dialogo
        dialogo.open = True
        self.page.update()

    # === FUNCIONALIDADES DE GESTIÓN DE MARCAS Y CATEGORÍAS ===
    
    def gestionar_marcas(self, e):
        """Interfaz para gestionar marcas"""
        print("DEBUG: Abriendo gestión de marcas")
        try:
            marcas = self.db.obtener_marcas()
            
            # Crear lista de marcas
            lista_marcas = []
            for marca in marcas:
                lista_marcas.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(f"🏷️ {marca['nombre']}", size=16, weight="bold"),
                            ft.Container(expand=True),
                            ft.Text(f"Creada: {marca['fecha_creacion']}", size=12, color="gray"),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                icon_color="red",
                                tooltip="Eliminar marca",
                                on_click=lambda e, m_id=marca['id']: self.eliminar_marca(m_id)
                            )
                        ]),
                        padding=10,
                        border=ft.border.all(1, "#e0e0e0"),
                        border_radius=5,
                        margin=ft.margin.only(bottom=5)
                    )
                )
            
            # Campo para agregar nueva marca
            self.nueva_marca = ft.TextField(
                label="Nueva marca",
                hint_text="Nombre de la marca",
                width=300
            )
            self.mensaje_marcas = ft.Text("", color="blue", size=12)
            
            contenido_dialogo = ft.Column([
                ft.Text("🏷️ Gestión de Marcas", size=20, weight="bold"),
                ft.Text(f"Total de marcas: {len(marcas)}", size=14),
                ft.Divider(),
                
                # Formulario para agregar marca
                ft.Container(
                    content=ft.Column([
                        ft.Text("Agregar nueva marca:", size=16, weight="bold"),
                        self.nueva_marca,
                        ft.ElevatedButton(
                            "Agregar Marca",
                            on_click=self.agregar_marca,
                            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)
                        ),
                        self.mensaje_marcas
                    ], spacing=10),
                    padding=10
                ),
                
                ft.Divider(),
                ft.Text("Marcas existentes:", size=16, weight="bold"),
                ft.Container(
                    content=ft.Column(lista_marcas, scroll=ft.ScrollMode.AUTO),
                    height=300,
                    width=500
                )
            ], spacing=15)
            
            dialogo = ft.AlertDialog(
                title=ft.Text("Gestión de Marcas"),
                content=contenido_dialogo,
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda e: setattr(self.page.dialog, 'open', False))
                ]
            )
            
            self.page.dialog = dialogo
            dialogo.open = True
            self.page.update()
            
        except Exception as error:
            print(f"DEBUG: Error al cargar marcas: {error}")
            self.mostrar_mensaje(f"Error al cargar marcas: {str(error)}")

    def agregar_marca(self, e):
        """Agregar una nueva marca"""
        nombre_marca = self.nueva_marca.value.strip()
        if not nombre_marca:
            self.mensaje_marcas.value = "Por favor ingresa un nombre para la marca"
            self.mensaje_marcas.color = "red"
            self.page.update()
            return
        
        try:
            if self.db.guardar_marca(nombre_marca):
                self.mensaje_marcas.value = f"✅ Marca '{nombre_marca}' agregada exitosamente"
                self.mensaje_marcas.color = "green"
                self.nueva_marca.value = ""
                # Recargar la gestión de marcas
                self.gestionar_marcas(e)
            else:
                self.mensaje_marcas.value = f"❌ La marca '{nombre_marca}' ya existe"
                self.mensaje_marcas.color = "red"
                self.page.update()
                
        except Exception as error:
            self.mensaje_marcas.value = f"Error al agregar marca: {str(error)}"
            self.mensaje_marcas.color = "red"
            self.page.update()

    def eliminar_marca(self, marca_id):
        """Eliminar una marca"""
        try:
            self.db.eliminar_marca(marca_id)
            self.mostrar_mensaje("✅ Marca eliminada exitosamente")
            # Recargar la gestión de marcas
            self.gestionar_marcas(None)
        except Exception as error:
            self.mostrar_mensaje(f"Error al eliminar marca: {str(error)}")

    def gestionar_categorias(self, e):
        """Interfaz para gestionar categorías"""
        print("DEBUG: Abriendo gestión de categorías")
        try:
            categorias = self.db.obtener_categorias()
            
            # Crear lista de categorías
            lista_categorias = []
            for categoria in categorias:
                lista_categorias.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(f"📂 {categoria['nombre']}", size=16, weight="bold"),
                            ft.Container(expand=True),
                            ft.Text(f"Creada: {categoria['fecha_creacion']}", size=12, color="gray"),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                icon_color="red",
                                tooltip="Eliminar categoría",
                                on_click=lambda e, c_id=categoria['id']: self.eliminar_categoria(c_id)
                            )
                        ]),
                        padding=10,
                        border=ft.border.all(1, "#e0e0e0"),
                        border_radius=5,
                        margin=ft.margin.only(bottom=5)
                    )
                )
            
            # Campo para agregar nueva categoría
            self.nueva_categoria = ft.TextField(
                label="Nueva categoría",
                hint_text="Nombre de la categoría",
                width=300
            )
            self.mensaje_categorias = ft.Text("", color="blue", size=12)
            
            contenido_dialogo = ft.Column([
                ft.Text("📂 Gestión de Categorías", size=20, weight="bold"),
                ft.Text(f"Total de categorías: {len(categorias)}", size=14),
                ft.Divider(),
                
                # Formulario para agregar categoría
                ft.Container(
                    content=ft.Column([
                        ft.Text("Agregar nueva categoría:", size=16, weight="bold"),
                        self.nueva_categoria,
                        ft.ElevatedButton(
                            "Agregar Categoría",
                            on_click=self.agregar_categoria,
                            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)
                        ),
                        self.mensaje_categorias
                    ], spacing=10),
                    padding=10
                ),
                
                ft.Divider(),
                ft.Text("Categorías existentes:", size=16, weight="bold"),
                ft.Container(
                    content=ft.Column(lista_categorias, scroll=ft.ScrollMode.AUTO),
                    height=300,
                    width=500
                )
            ], spacing=15)
            
            dialogo = ft.AlertDialog(
                title=ft.Text("Gestión de Categorías"),
                content=contenido_dialogo,
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda e: setattr(self.page.dialog, 'open', False))
                ]
            )
            
            self.page.dialog = dialogo
            dialogo.open = True
            self.page.update()
            
        except Exception as error:
            print(f"DEBUG: Error al cargar categorías: {error}")
            self.mostrar_mensaje(f"Error al cargar categorías: {str(error)}")

    def agregar_categoria(self, e):
        """Agregar una nueva categoría"""
        nombre_categoria = self.nueva_categoria.value.strip()
        if not nombre_categoria:
            self.mensaje_categorias.value = "Por favor ingresa un nombre para la categoría"
            self.mensaje_categorias.color = "red"
            self.page.update()
            return
        
        try:
            if self.db.guardar_categoria(nombre_categoria):
                self.mensaje_categorias.value = f"✅ Categoría '{nombre_categoria}' agregada exitosamente"
                self.mensaje_categorias.color = "green"
                self.nueva_categoria.value = ""
                # Recargar la gestión de categorías
                self.gestionar_categorias(e)
            else:
                self.mensaje_categorias.value = f"❌ La categoría '{nombre_categoria}' ya existe"
                self.mensaje_categorias.color = "red"
                self.page.update()
                
        except Exception as error:
            self.mensaje_categorias.value = f"Error al agregar categoría: {str(error)}"
            self.mensaje_categorias.color = "red"
            self.page.update()

    def eliminar_categoria(self, categoria_id):
        """Eliminar una categoría"""
        try:
            self.db.eliminar_categoria(categoria_id)
            self.mostrar_mensaje("✅ Categoría eliminada exitosamente")
            # Recargar la gestión de categorías
            self.gestionar_categorias(None)
        except Exception as error:
            self.mostrar_mensaje(f"Error al eliminar categoría: {str(error)}")

    # === FUNCIONALIDADES DE GESTIÓN DE INVENTARIO ===
    
    def ver_inventario_completo(self, e):
        """Mostrar inventario completo"""
        print("DEBUG: Mostrando inventario completo")
        try:
            inventario = self.db.obtener_inventario()
            
            if not inventario:
                self.mostrar_mensaje("No hay datos de inventario disponibles")
                return
            
            # Crear lista de items del inventario
            items_inventario = []
            
            for item in inventario:
                estado_stock = "✅ Suficiente" if item['Cantidad'] > item['Stock_minimo'] else "⚠️ Bajo Stock"
                color_estado = "green" if item['Cantidad'] > item['Stock_minimo'] else "orange"
                
                items_inventario.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"📦 {item['nombre']}", size=16, weight="bold"),
                                ft.Container(expand=True),
                                ft.Text(estado_stock, color=color_estado, weight="bold")
                            ]),
                            ft.Row([
                                ft.Text(f"Marca: {item['marca']} | Categoría: {item['categoria']}", size=12, color="gray"),
                                ft.Container(expand=True),
                                ft.Text(f"Stock: {item['Cantidad']} | Mín: {item['Stock_minimo']}", size=12)
                            ]),
                            ft.Text(f"Última actualización: {item['Fecha_actualizacion']}", size=10, color="gray")
                        ], spacing=5),
                        padding=10,
                        border=ft.border.all(1, "#e0e0e0"),
                        border_radius=5,
                        margin=ft.margin.only(bottom=5)
                    )
                )
            
            # Crear diálogo de inventario
            contenido_dialogo = ft.Column([
                ft.Text("📊 Inventario Completo", size=20, weight="bold"),
                ft.Text(f"Total de productos: {len(inventario)}", size=14),
                ft.Divider(),
                ft.Container(
                    content=ft.Column(items_inventario, scroll=ft.ScrollMode.AUTO),
                    height=400,
                    width=500
                )
            ], spacing=15)
            
            dialogo = ft.AlertDialog(
                title=ft.Text("Inventario del Sistema"),
                content=contenido_dialogo,
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda e: setattr(self.page.dialog, 'open', False))
                ]
            )
            
            self.page.dialog = dialogo
            dialogo.open = True
            self.page.update()
            
        except Exception as error:
            print(f"DEBUG: Error al cargar inventario: {error}")
            self.mostrar_mensaje(f"Error al cargar inventario: {str(error)}")

    def ver_stock_bajo(self, e):
        """Mostrar productos con stock bajo"""
        print("DEBUG: Mostrando productos con stock bajo")
        try:
            productos_bajo_stock = self.db.obtener_productos_bajo_stock()
            
            if not productos_bajo_stock:
                self.mostrar_mensaje("✅ No hay productos con stock bajo")
                return
            
            # Crear lista de productos con stock bajo
            items_stock_bajo = []
            
            for item in productos_bajo_stock:
                items_stock_bajo.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"⚠️ {item['nombre']}", size=16, weight="bold", color="orange"),
                                ft.Container(expand=True),
                                ft.Text(f"Stock: {item['Cantidad']}", color="red", weight="bold")
                            ]),
                            ft.Row([
                                ft.Text(f"Marca: {item['marca']} | Categoría: {item['categoria']}", size=12, color="gray"),
                                ft.Container(expand=True),
                                ft.Text(f"Mínimo requerido: {item['Stock_minimo']}", size=12)
                            ]),
                            ft.ProgressBar(
                                value=item['Cantidad'] / (item['Stock_minimo'] * 2) if item['Stock_minimo'] > 0 else 0,
                                color="red",
                                bgcolor="#eeeeee"
                            )
                        ], spacing=5),
                        padding=10,
                        border=ft.border.all(1, "orange"),
                        border_radius=5,
                        margin=ft.margin.only(bottom=5)
                    )
                )
            
            # Crear diálogo de stock bajo
            contenido_dialogo = ft.Column([
                ft.Text("⚠️ Productos con Stock Bajo", size=20, weight="bold", color="orange"),
                ft.Text(f"Productos que requieren atención: {len(productos_bajo_stock)}", size=14),
                ft.Divider(),
                ft.Container(
                    content=ft.Column(items_stock_bajo, scroll=ft.ScrollMode.AUTO),
                    height=300,
                    width=500
                )
            ], spacing=15)
            
            dialogo = ft.AlertDialog(
                title=ft.Text("Alertas de Stock"),
                content=contenido_dialogo,
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda e: setattr(self.page.dialog, 'open', False))
                ]
            )
            
            self.page.dialog = dialogo
            dialogo.open = True
            self.page.update()
            
        except Exception as error:
            print(f"DEBUG: Error al cargar stock bajo: {error}")
            self.mostrar_mensaje(f"Error al cargar stock bajo: {str(error)}")

    def actualizar_stock_producto(self, e):
        """Interfaz para actualizar stock de productos"""
        print("DEBUG: Abriendo interfaz para actualizar stock")
        self.mostrar_mensaje("🚧 Funcionalidad de actualización de stock en desarrollo")

    def mostrar_mensaje_gestion_usuarios(self, mensaje, color):
        self.mensaje_gestion_usuarios.value = mensaje
        self.mensaje_gestion_usuarios.color = color
        self.page.update()

    def funcionalidad_desarrollando(self, e):
        self.mostrar_mensaje("🚧 Esta funcionalidad está en desarrollo - Próximamente")

    def mostrar_mensaje(self, texto):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            duration=3000,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def volver(self, e):
        print("DEBUG: Volviendo al inicio desde panel de administrador")
        self.page.clean()
        self.volver_callback()

# --- Main ---

def main(page: ft.Page):
    page.window_width = 1200
    page.window_height = 700
    page.window_min_width = 800
    page.window_min_height = 600
    
    import logging
    logging.basicConfig(level=logging.DEBUG)
    print("DEBUG: Aplicación iniciada")
    
    IngresoApp(page)

ft.app(target=main)