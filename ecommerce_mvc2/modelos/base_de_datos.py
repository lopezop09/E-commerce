import sqlite3
import time
import uuid
from datetime import datetime
from contextlib import contextmanager

class BaseDatos:
    def __init__(self):
        self.nombre_db = "ecommerce.db"
        print("🔄 DEBUG: Inicializando BaseDatos...")
        self.inicializar_base_datos()
        print("✅ DEBUG: Base de datos SQLite inicializada")

    @contextmanager
    def obtener_conexion(self):
        """Context manager mejorado para manejar bloqueos con reintentos automáticos"""
        conn = None
        max_reintentos = 10
        retraso_reintento = 0.2
        timeout = 30.0
        
        print(f"🔗 DEBUG: Intentando conexión a BD (máx {max_reintentos} reintentos)")
        
        for intento in range(max_reintentos):
            try:
                conn = sqlite3.connect(self.nombre_db, timeout=timeout)
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA foreign_keys=ON")
                conn.execute("PRAGMA busy_timeout=30000")
                print(f"✅ DEBUG: Conexión a BD exitosa (intento {intento + 1})")
                break
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower():
                    if intento < max_reintentos - 1:
                        print(f"🔄 DEBUG: Base de datos bloqueada, reintento {intento + 1}/{max_reintentos}")
                        time.sleep(retraso_reintento)
                        retraso_reintento *= 1.5
                    else:
                        print(f"❌ ERROR: No se pudo conectar después de {max_reintentos} intentos")
                        raise e
                else:
                    print(f"❌ ERROR de BD: {e}")
                    raise e
        
        try:
            yield conn
            if conn:
                conn.commit()
                print("✅ DEBUG: Transacción realizada")
        except Exception as e:
            if conn:
                conn.rollback()
                print(f"❌ ERROR en transacción: {e}")
            raise e
        finally:
            if conn:
                conn.close()
                print("🔒 DEBUG: Conexión cerrada")

    def inicializar_base_datos(self):
        """Inicializar las tablas de la base de datos"""
        print("🔄 DEBUG: Inicializando tablas de BD...")
        with self.obtener_conexion() as conn:
            # Configuraciones de rendimiento
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA cache_size = 10000")
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA temp_store = MEMORY")

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

            # Tabla: Marcas
            conn.execute('''
                CREATE TABLE IF NOT EXISTS marcas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    fecha_creacion TEXT NOT NULL
                )
            ''')

            # Tabla: Categorías
            conn.execute('''
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    fecha_creacion TEXT NOT NULL
                )
            ''')

            # Tabla de productos
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

            print("✅ DEBUG: Tablas creadas/verificadas")

            # Insertar datos iniciales si no existen
            self._insertar_datos_iniciales(conn)

    def _insertar_datos_iniciales(self, conn):
        """Insertar datos iniciales en la base de datos"""
        print("🔄 DEBUG: Verificando datos iniciales...")
        
        # Insertar marcas iniciales si no existen
        if not conn.execute("SELECT COUNT(*) FROM marcas").fetchone()[0]:
            print("🔄 DEBUG: Insertando marcas iniciales...")
            self._insertar_marcas_iniciales(conn)

        # Insertar categorías iniciales si no existen
        if not conn.execute("SELECT COUNT(*) FROM categorias").fetchone()[0]:
            print("🔄 DEBUG: Insertando categorías iniciales...")
            self._insertar_categorias_iniciales(conn)

        # Insertar productos iniciales si no existen
        if not conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]:
            print("🔄 DEBUG: Insertando productos iniciales...")
            self._insertar_productos_iniciales(conn)

        # Insertar inventario inicial si no existen
        if not conn.execute("SELECT COUNT(*) FROM inventario").fetchone()[0]:
            print("🔄 DEBUG: Insertando inventario inicial...")
            self._insertar_inventario_inicial(conn)

        # Insertar usuario admin por defecto si no existe
        if not conn.execute("SELECT COUNT(*) FROM usuarios WHERE email = 'admin@test.com'").fetchone()[0]:
            print("🔄 DEBUG: Insertando usuario admin por defecto...")
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute('''
                INSERT INTO usuarios (email, nombre, password, tipo, fecha_registro)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin@test.com', 'Administrador', 'admin123', 'administrador', fecha_actual))
            print("✅ DEBUG: Usuario admin creado: admin@test.com / admin123")

    def _insertar_marcas_iniciales(self, conn):
        """Insertar marcas iniciales"""
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
        conn.executemany('INSERT INTO marcas (nombre, fecha_creacion) VALUES (?, ?)', marcas_iniciales)
        print(f"✅ DEBUG: {len(marcas_iniciales)} marcas insertadas")

    def _insertar_categorias_iniciales(self, conn):
        """Insertar categorías iniciales"""
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
        conn.executemany('INSERT INTO categorias (nombre, fecha_creacion) VALUES (?, ?)', categorias_iniciales)
        print(f"✅ DEBUG: {len(categorias_iniciales)} categorías insertadas")

    def _insertar_productos_iniciales(self, conn):
        """Insertar productos iniciales"""
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
        ]
        conn.executemany('''
            INSERT INTO productos (id, nombre, precio, descripcion, marca_id, categoria_id, imagen, destacado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', productos_iniciales)
        print(f"✅ DEBUG: {len(productos_iniciales)} productos insertados")

    def _insertar_inventario_inicial(self, conn):
        """Insertar inventario inicial"""
        inventario_inicial = [
            (1, 50, 5, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            (2, 30, 3, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            (3, 100, 10, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            (4, 80, 8, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            (5, 25, 2, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ]
        conn.executemany('''
            INSERT INTO inventario (Productos_ID, Cantidad, Stock_minimo, Fecha_actualizacion)
            VALUES (?, ?, ?, ?)
        ''', inventario_inicial)
        print(f"✅ DEBUG: {len(inventario_inicial)} items de inventario insertados")

    def diagnosticar_usuarios(self):
        """Método para diagnosticar usuarios en la base de datos"""
        print("\n🔍 DIAGNÓSTICO DE USUARIOS:")
        try:
            with self.obtener_conexion() as conn:
                # Contar usuarios
                count = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
                print(f"📊 Total de usuarios: {count}")
                
                # Listar todos los usuarios
                cursor = conn.execute("SELECT email, nombre, tipo FROM usuarios")
                usuarios = cursor.fetchall()
                for usuario in usuarios:
                    print(f"   👤 {usuario['email']} ({usuario['nombre']}) - {usuario['tipo']}")
                    
        except Exception as e:
            print(f"❌ Error en diagnóstico: {e}")

    # Métodos para usuarios
    def cargar_usuarios(self):
        """Cargar todos los usuarios con su estado de bloqueo"""
        print("🔄 DEBUG: Cargando usuarios desde BD...")
        with self.obtener_conexion() as conn:
            cursor = conn.execute("SELECT * FROM usuarios")
            usuarios = {}
            for row in cursor:
                usuario_dict = dict(row)
                email = usuario_dict['email']
                estado_bloqueo = self.obtener_estado_bloqueo(email)
                usuario_dict['bloqueado'] = estado_bloqueo['bloqueado']
                usuarios[email] = usuario_dict
            
            print(f"✅ DEBUG: {len(usuarios)} usuarios cargados")
            return usuarios

    def guardar_usuario(self, datos_usuario):
        """Guardar o actualizar un usuario"""
        print(f"🔄 DEBUG: Guardando usuario {datos_usuario['email']}")
        with self.obtener_conexion() as conn:
            cursor = conn.execute("SELECT email FROM usuarios WHERE email = ?", (datos_usuario['email'],))
            existe = cursor.fetchone() is not None

            if existe:
                print("🔄 DEBUG: Actualizando usuario existente")
                conn.execute('''
                    UPDATE usuarios SET 
                    nombre = ?, password = ?, tipo = ?, nombre_tienda = ?, telefono = ?, fecha_registro = ?
                    WHERE email = ?
                ''', (
                    datos_usuario['nombre'], datos_usuario['password'], datos_usuario['tipo'],
                    datos_usuario.get('nombre_tienda'), datos_usuario.get('telefono'), 
                    datos_usuario['fecha_registro'], datos_usuario['email']
                ))
            else:
                print("🔄 DEBUG: Insertando nuevo usuario")
                conn.execute('''
                    INSERT INTO usuarios 
                    (email, nombre, password, tipo, nombre_tienda, telefono, fecha_registro)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datos_usuario['email'], datos_usuario['nombre'], datos_usuario['password'],
                    datos_usuario['tipo'], datos_usuario.get('nombre_tienda'),
                    datos_usuario.get('telefono'), datos_usuario['fecha_registro']
                ))
            print("✅ DEBUG: Usuario guardado exitosamente")

    def obtener_estado_bloqueo(self, email):
        """Obtener estado de bloqueo de un usuario"""
        with self.obtener_conexion() as conn:
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

    # Métodos para productos
    def cargar_productos(self):
        """Cargar productos con información de marcas y categorías"""
        print("🔄 DEBUG: Cargando productos desde BD...")
        with self.obtener_conexion() as conn:
            cursor = conn.execute('''
                SELECT p.*, m.nombre as marca_nombre, c.nombre as categoria_nombre 
                FROM productos p 
                JOIN marcas m ON p.marca_id = m.id 
                JOIN categorias c ON p.categoria_id = c.id
            ''')
            productos = []
            for row in cursor:
                producto = {
                    'id': row['id'],
                    'nombre': row['nombre'],
                    'precio': row['precio'],
                    'descripcion': row['descripcion'],
                    'marca': row['marca_nombre'],
                    'categoria': row['categoria_nombre'],
                    'imagen': row['imagen'],
                    'destacado': bool(row['destacado'])
                }
                productos.append(producto)

            cursor = conn.execute("SELECT nombre FROM categorias ORDER BY nombre")
            categorias = [row['nombre'] for row in cursor]

            cursor = conn.execute("SELECT nombre FROM marcas ORDER BY nombre")
            marcas = [row['nombre'] for row in cursor]

            print(f"✅ DEBUG: {len(productos)} productos, {len(categorias)} categorías, {len(marcas)} marcas cargados")
            return productos, categorias, marcas

    # Métodos para pedidos
    def guardar_pedido(self, pedido):
        """Guardar pedido con manejo robusto de transacciones"""
        print(f"🛒 DEBUG: Iniciando guardado de pedido {pedido['id']}")
        
        max_reintentos = 3
        for intento in range(max_reintentos):
            try:
                with self.obtener_conexion() as conn:
                    fecha_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Verificar que el pedido no exista
                    cursor_existente = conn.execute("SELECT COUNT(*) FROM pedidos WHERE id = ?", (pedido['id'],))
                    if cursor_existente.fetchone()[0] > 0:
                        print(f"⚠️  DEBUG: Pedido {pedido['id']} ya existe, omitiendo...")
                        return True
                    
                    print(f"📦 DEBUG: Guardando pedido maestro {pedido['id']}")
                    # Insertar pedido maestro
                    conn.execute('''
                        INSERT INTO pedidos 
                        (id, fecha, cliente, total, estado, metodo_pago, tarjeta_ultimos_digitos)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        pedido['id'],
                        fecha_iso,
                        pedido['cliente'],
                        float(pedido['total']),
                        pedido.get('estado', 'Pendiente'),
                        pedido.get('metodo_pago', 'MercadoPago'),
                        pedido.get('tarjeta_ultimos_digitos', '')
                    ))
                    
                    # Insertar items del pedido
                    items_guardados = 0
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
                        items_guardados += 1
                    
                    print(f"📦 DEBUG: {items_guardados} items del pedido guardados")
                    
                    # Verificar inserción
                    cursor_pedido = conn.execute("SELECT COUNT(*) FROM pedidos WHERE id = ?", (pedido['id'],))
                    count_pedido = cursor_pedido.fetchone()[0]
                    
                    cursor_items = conn.execute("SELECT COUNT(*) FROM items_pedido WHERE pedido_id = ?", (pedido['id'],))
                    count_items = cursor_items.fetchone()[0]
                    
                    if count_pedido > 0 and count_items == items_guardados:
                        print(f"✅ DEBUG: PEDIDO {pedido['id']} GUARDADO EXITOSAMENTE")
                        return True
                    else:
                        print(f"❌ DEBUG: INCONSISTENCIA - Pedido: {count_pedido}, Items: {count_items}/{items_guardados}")
                        if intento < max_reintentos - 1:
                            print(f"🔄 DEBUG: Reintentando guardado...")
                            continue
                        else:
                            return False
                            
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and intento < max_reintentos - 1:
                    print(f"🔒 DEBUG: Base de datos bloqueada, reintento {intento + 1}/{max_reintentos}")
                    time.sleep(1)
                    continue
                else:
                    print(f"❌ ERROR CRÍTICO al guardar pedido: {e}")
                    raise e
            except Exception as e:
                print(f"❌ ERROR inesperado: {e}")
                if intento < max_reintentos - 1:
                    print(f"🔄 DEBUG: Reintentando guardado...")
                    time.sleep(1)
                    continue
                else:
                    raise e
        
        return False