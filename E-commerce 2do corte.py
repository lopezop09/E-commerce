import flet as ft
import re
import os
import uuid
from datetime import datetime
import sqlite3
from contextlib import contextmanager

# --- BASE DE DATOS ---
class Database:
    def __init__(self):
        self.db_name = "ecommerce.db"
        self.init_database()
        self.migrar_campo_password()  # ✅ Agregar migración
        print("DEBUG: Base de datos SQLite inicializada (sin JSON)")

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
        """Inicializar las tablas de la base de datos - VERSIÓN MEJORADA"""
        with self.get_connection() as conn:
            # Tabla de usuarios - ✅ CAMBIO: password -> contraseña
            conn.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    email TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    contraseña TEXT NOT NULL,  -- ✅ CAMBIO AQUÍ
                    tipo TEXT NOT NULL,
                    nombre_tienda TEXT,
                    telefono TEXT,
                    bloqueado BOOLEAN DEFAULT FALSE,
                    fecha_registro TEXT NOT NULL,
                    fecha_bloqueo TEXT,
                    bloqueado_por TEXT,
                    fecha_desbloqueo TEXT,
                    desbloqueado_por TEXT
                )
            ''')

            # Tabla de productos
            conn.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    precio REAL NOT NULL,
                    descripcion TEXT,
                    marca TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    imagen TEXT,
                    destacado BOOLEAN DEFAULT FALSE
                )
            ''')

            # Tabla de pedidos
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

            # Tabla de items_pedido 
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

            # Insertar datos iniciales de productos si no existen
            if not conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]:
                self.insertar_productos_iniciales(conn)

    def migrar_campo_password(self):
        """Migrar datos existentes de 'password' a 'contraseña' si es necesario"""
        print("DEBUG: Verificando migración de campo password...")
        with self.get_connection() as conn:
            # Verificar si existe la columna 'password' 
            cursor = conn.execute("PRAGMA table_info(usuarios)")
            columnas = [col[1] for col in cursor.fetchall()]
            
            if 'password' in columnas and 'contraseña' not in columnas:
                print("DEBUG: Migrando datos de 'password' a 'contraseña'...")
                # Renombrar la tabla temporalmente
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS usuarios_nueva (
                        email TEXT PRIMARY KEY,
                        nombre TEXT NOT NULL,
                        contraseña TEXT NOT NULL,
                        tipo TEXT NOT NULL,
                        nombre_tienda TEXT,
                        telefono TEXT,
                        bloqueado BOOLEAN DEFAULT FALSE,
                        fecha_registro TEXT NOT NULL,
                        fecha_bloqueo TEXT,
                        bloqueado_por TEXT,
                        fecha_desbloqueo TEXT,
                        desbloqueado_por TEXT
                    )
                ''')
                
                # Copiar datos
                conn.execute('''
                    INSERT INTO usuarios_nueva 
                    SELECT email, nombre, password, tipo, nombre_tienda, telefono, 
                           bloqueado, fecha_registro, fecha_bloqueo, bloqueado_por,
                           fecha_desbloqueo, desbloqueado_por
                    FROM usuarios
                ''')
                
                # Eliminar tabla vieja y renombrar
                conn.execute('DROP TABLE usuarios')
                conn.execute('ALTER TABLE usuarios_nueva RENAME TO usuarios')
                print("DEBUG: Migración completada exitosamente")
            else:
                print("DEBUG: No se requiere migración - estructura actualizada")

    def insertar_productos_iniciales(self, conn):
        """Insertar productos iniciales en la base de datos"""
        productos_iniciales = [
            (1, 'Procesador Intel Core i9-13900K', 2323000, 'Procesador de 24 núcleos y 32 hilos, frecuencia turbo de hasta 5.8 GHz', 'Intel', 'Procesadores', '', True),
            (2, 'Tarjeta Gráfica NVIDIA RTX 4080', 4670000, '16GB GDDR6X, ray tracing y DLSS 3.0', 'NVIDIA', 'Tarjetas Gráficas', '', True),
            (3, 'SSD Samsung 980 Pro 1TB', 743440, 'Velocidades de lectura hasta 7000 MB/s, PCIe 4.0 NVMe', 'Samsung', 'Almacenamiento', '', True),
            (4, 'Memoria RAM Corsair Vengeance 32GB', 505000, 'DDR5 5600MHz, CL36, RGB', 'Corsair', 'Memoria RAM', '', False),
            (5, 'Placa Base ASUS ROG Strix Z790-E', 2530000, 'Socket LGA1700, PCIe 5.0, WiFi 6E', 'ASUS', 'Placas Base', '', True),
            (6, 'Fuente de Alimentación Seasonic 850W', 600000, '80 Plus Gold, modular, certificación completa', 'Seasonic', 'Fuentes de Poder', '', False),
            (7, 'Monitor Gaming ASUS 27" 144Hz', 1250000, 'QHD, 1ms, FreeSync y G-Sync compatible', 'ASUS', 'Monitores', '', False),
            (8, 'Teclado Mecánico Razer BlackWidow', 600000, 'Switches mecánicos Razer Green, RGB Chroma', 'Razer', 'Periféricos', '', False),
            (9, 'Procesador AMD Ryzen 9 7950X', 2450000, '16 núcleos, 32 hilos, frecuencia hasta 5.7 GHz', 'AMD', 'Procesadores', '', True),
            (10, 'Tarjeta Gráfica AMD Radeon RX 7900 XT', 4700000, '20GB GDDR6, arquitectura RDNA 3', 'AMD', 'Tarjetas Gráficas', '', False)
        ]

        conn.executemany('''
            INSERT INTO productos (id, nombre, precio, descripcion, marca, categoria, imagen, destacado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', productos_iniciales)

    # --- MÉTODOS PARA USUARIOS ---
    def cargar_usuarios(self):
        """Cargar todos los usuarios de la base de datos - CON CONTRASEÑA"""
        print("DEBUG: Cargando usuarios desde base de datos")
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM usuarios")
            usuarios = {}
            for row in cursor:
                usuario_dict = dict(row)
                # ✅ Mantener compatibilidad con el código existente
                # Mapear 'contraseña' a 'password' para el resto de la aplicación
                if 'contraseña' in usuario_dict:
                    usuario_dict['password'] = usuario_dict['contraseña']
                usuarios[row['email']] = usuario_dict
            print(f"DEBUG: {len(usuarios)} usuarios cargados")
            return usuarios

    def guardar_usuario(self, datos_usuario):
        """Guardar o actualizar un usuario en la base de datos - CON CONTRASEÑA"""
        print(f"DEBUG: Guardando usuario {datos_usuario['email']}")
        with self.get_connection() as conn:
            # Verificar si el usuario ya existe
            cursor = conn.execute("SELECT email FROM usuarios WHERE email = ?", 
                                (datos_usuario['email'],))
            existe = cursor.fetchone() is not None

            if existe:
                # Actualizar usuario existente - ✅ CAMBIO: password -> contraseña
                conn.execute('''
                    UPDATE usuarios SET 
                    nombre = ?, contraseña = ?, tipo = ?, nombre_tienda = ?, telefono = ?,
                    bloqueado = ?, fecha_registro = ?, fecha_bloqueo = ?, bloqueado_por = ?,
                    fecha_desbloqueo = ?, desbloqueado_por = ?
                    WHERE email = ?
                ''', (
                    datos_usuario['nombre'], datos_usuario['contraseña'], datos_usuario['tipo'],  # ✅ CAMBIO
                    datos_usuario.get('nombre_tienda'), datos_usuario.get('telefono'),
                    datos_usuario.get('bloqueado', False), datos_usuario['fecha_registro'],
                    datos_usuario.get('fecha_bloqueo'), datos_usuario.get('bloqueado_por'),
                    datos_usuario.get('fecha_desbloqueo'), datos_usuario.get('desbloqueado_por'),
                    datos_usuario['email']
                ))
            else:
                # Insertar nuevo usuario - ✅ CAMBIO: password -> contraseña
                conn.execute('''
                    INSERT INTO usuarios 
                    (email, nombre, contraseña, tipo, nombre_tienda, telefono, bloqueado, fecha_registro)  # ✅ CAMBIO
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datos_usuario['email'], datos_usuario['nombre'], datos_usuario['contraseña'],  # ✅ CAMBIO
                    datos_usuario['tipo'], datos_usuario.get('nombre_tienda'),
                    datos_usuario.get('telefono'), datos_usuario.get('bloqueado', False),
                    datos_usuario['fecha_registro']
                ))
        print("DEBUG: Usuario guardado exitosamente")

    def eliminar_usuario(self, email):
        """Eliminar un usuario de la base de datos"""
        print(f"DEBUG: Eliminando usuario {email}")
        with self.get_connection() as conn:
            conn.execute("DELETE FROM usuarios WHERE email = ?", (email,))
        print("DEBUG: Usuario eliminado exitosamente")

    # --- MÉTODOS PARA PRODUCTOS ---
    def cargar_productos(self):
        """Cargar productos, categorías y marcas de la base de datos"""
        print("DEBUG: Cargando productos desde base de datos")
        with self.get_connection() as conn:
            # Cargar productos
            cursor = conn.execute("SELECT * FROM productos")
            productos = []
            for row in cursor:
                producto = Producto(
                    id=row['id'],
                    nombre=row['nombre'],
                    precio=row['precio'],
                    descripcion=row['descripcion'],
                    marca=row['marca'],
                    categoria=row['categoria'],
                    imagen=row['imagen'],
                    destacado=bool(row['destacado'])
                )
                productos.append(producto)

            # Cargar categorías únicas
            cursor = conn.execute("SELECT DISTINCT categoria FROM productos")
            categorias = [row['categoria'] for row in cursor]

            # Cargar marcas únicas
            cursor = conn.execute("SELECT DISTINCT marca FROM productos")
            marcas = [row['marca'] for row in cursor]

            print(f"DEBUG: {len(productos)} productos cargados")
            return productos, categorias, marcas

    def guardar_producto(self, producto_data):
        """Guardar o actualizar un producto en la base de datos"""
        print(f"DEBUG: Guardando producto {producto_data['nombre']}")
        with self.get_connection() as conn:
            if 'id' in producto_data and producto_data['id']:
                # Actualizar producto existente
                conn.execute('''
                    UPDATE productos SET 
                    nombre = ?, precio = ?, descripcion = ?, marca = ?, categoria = ?, 
                    imagen = ?, destacado = ?
                    WHERE id = ?
                ''', (
                    producto_data['nombre'], producto_data['precio'], producto_data['descripcion'],
                    producto_data['marca'], producto_data['categoria'], producto_data['imagen'],
                    producto_data.get('destacado', False), producto_data['id']
                ))
            else:
                # Insertar nuevo producto
                conn.execute('''
                    INSERT INTO productos 
                    (nombre, precio, descripcion, marca, categoria, imagen, destacado)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    producto_data['nombre'], producto_data['precio'], producto_data['descripcion'],
                    producto_data['marca'], producto_data['categoria'], producto_data['imagen'],
                    producto_data.get('destacado', False)
                ))
        print("DEBUG: Producto guardado exitosamente")

    # --- MÉTODOS PARA PEDIDOS (SIN JSON) ---
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
        """Guardar un pedido en la base de datos - SIN JSON"""
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
        
        # VERIFICAR SI LA CUENTA ESTÁ BLOQUEADA
        if user.get('bloqueado'):
            self.mensaje_login.value = "❌ Cuenta bloqueada. Contacta al administrador."
            self.mensaje_login.color = "red"
            self.page.update()
            print(f"DEBUG: Error - Cuenta {email} bloqueada")
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
            'contraseña': self.password.value,  # ✅ CAMBIO AQUÍ
            'tipo': 'administrador',
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
                'contraseña': self.password.value,  # ✅ CAMBIO AQUÍ
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
        """Manejar el proceso de pago completo - VERSIÓN CORREGIDA"""
        print("DEBUG: Botón PAGAR presionado")
        
        # Validar campos
        if not self.validar_campos():
            print("DEBUG: Validación falló")
            return
        
        print("DEBUG: Validación exitosa")
        
        # ✅ USAR FECHA EN FORMATO CORRECTO PARA BD
        fecha_bd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Crear registro del pedido
        pedido = {
            'id': self.order_id,
            'fecha': fecha_bd,  # ✅ Formato correcto para SQLite
            'cliente': self.user['email'],
            'productos': self.carrito,
            'total': float(self.total),  # ✅ Asegurar tipo float
            'estado': 'Completado',
            'metodo_pago': 'Tarjeta',
            'tarjeta_ultimos_digitos': self.num_tarjeta.value[-4:] if self.num_tarjeta.value else ''
        }
        
        # 🔍 DIAGNÓSTICO MEJORADO
        self.mostrar_diagnostico_pedido(pedido)
        
        # Guardar pedido
        try:
            self.db.guardar_pedido(pedido)
            print("DEBUG: Pedido guardado exitosamente")
            
            # Mostrar confirmación
            self.mostrar_confirmacion()
            
        except Exception as error:
            print(f"DEBUG: Error al guardar pedido: {error}")
            self.mostrar_error(f"Error al procesar el pago: {str(error)}")
            return
    
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

        # Sección: GESTIÓN DE PRODUCTOS (placeholder por ahora)
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

        # Sección: GESTIÓN DE PAGOS (placeholder por ahora)
        seccion_pagos = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.PAYMENTS, color=ft.Colors.PURPLE),
                        ft.Text(" Gestión de Pagos", size=18, weight="bold"),
                    ]),
                    ft.Divider(),
                    ft.Column([
                        self.crear_boton_funcionalidad(
                            "📊 Historial de Pagos", 
                            "Ver historial completo de transacciones",
                            self.funcionalidad_desarrollando
                        ),
                        self.crear_boton_funcionalidad(
                            "Generar Reembolso", 
                            "Procesar reembolsos a clientes",
                            self.funcionalidad_desarrollando
                        ),
                        self.crear_boton_funcionalidad(
                            "Generar Nota de Crédito", 
                            "Emitir notas de crédito",
                            self.funcionalidad_desarrollando
                        ),
                    ], spacing=8)
                ], spacing=12),
                padding=20,
                width=350
            ),
            elevation=5
        )

        # Sección: GESTIÓN DE PLATAFORMA (placeholder por ahora)
        seccion_plataforma = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SETTINGS, color=ft.Colors.ORANGE),
                        ft.Text(" Gestión de Plataforma", size=18, weight="bold"),
                    ]),
                    ft.Divider(),
                    ft.Column([
                        self.crear_boton_funcionalidad(
                            "Configurar Descuentos", 
                            "Establecer descuentos globales y promociones",
                            self.funcionalidad_desarrollando
                        ),
                        self.crear_boton_funcionalidad(
                            "Configurar Políticas de Envío", 
                            "Gestionar costos y políticas de envío",
                            self.funcionalidad_desarrollando
                        ),
                        self.crear_boton_funcionalidad(
                            "Administrar Roles", 
                            "Asignar o eliminar roles de vendedores",
                            self.funcionalidad_desarrollando
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
                    [seccion_usuarios, seccion_productos],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
                
                ft.Container(height=15),
                
                # Segunda fila de secciones
                ft.Row(
                    [seccion_pagos, seccion_plataforma],
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
                            "Gestión de Usuarios Funcional | Otras secciones en desarrollo", 
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
        """Ver el estado actual de un usuario"""
        email = self.campo_email_usuario.value
        valido, resultado = self.validar_email(email)
        
        if not valido:
            self.mostrar_mensaje_gestion_usuarios(resultado, "red")
            return
        
        usuario = self.obtener_usuario(resultado)
        if not usuario:
            self.mostrar_mensaje_gestion_usuarios("Usuario no encontrado", "red")
            return
        
        # Mostrar información del usuario
        estado = "🔒 BLOQUEADO" if usuario.get('bloqueado') else "✅ ACTIVO"
        mensaje_estado = f"""
        Usuario: {resultado}
    Nombre: {usuario.get('nombre', 'N/A')}
    Tipo: {usuario.get('tipo', 'N/A')}
    Estado: {estado}
    Registro: {usuario.get('fecha_registro', 'N/A')}
    """
        
        if usuario.get('bloqueado'):
            mensaje_estado += f"Bloqueado desde: {usuario.get('fecha_bloqueo', 'N/A')}"
            if usuario.get('bloqueado_por'):
                mensaje_estado += f"\nBloqueado por: {usuario.get('bloqueado_por')}"
    
        self.mostrar_mensaje_gestion_usuarios(mensaje_estado, "blue")

    def desbloquear_usuario(self, e):
        email = self.campo_email_usuario.value
        valido, resultado = self.validar_email(email)
        
        if not valido:
            self.mostrar_mensaje_gestion_usuarios(resultado, "red")
            return
        
        usuario = self.obtener_usuario(resultado)
        if not usuario:
            self.mostrar_mensaje_gestion_usuarios("Usuario no encontrado", "red")
            return
        
        # Verificar si el usuario está bloqueado
        if usuario.get('bloqueado'):
            usuario['bloqueado'] = False
            usuario['fecha_desbloqueo'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            usuario['desbloqueado_por'] = self.user['email']  # Registrar quién desbloqueó
            
            # Guardar los cambios
            try:
                self.db.guardar_usuario(usuario)
                self.mostrar_mensaje_gestion_usuarios(
                    f"✅ Cuenta de {resultado} desbloqueada exitosamente. El usuario puede iniciar sesión nuevamente.", 
                    "green"
                )
                print(f"DEBUG: Usuario {resultado} desbloqueado por administrador {self.user['email']}")
            except Exception as error:
                self.mostrar_mensaje_gestion_usuarios(f"Error al desbloquear: {str(error)}", "red")
        else:
            self.mostrar_mensaje_gestion_usuarios("La cuenta ya está activa", "blue")

    def bloquear_usuario(self, e):
        """Bloquear cuenta de usuario"""
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
        
        # Bloquear usuario
        if not usuario.get('bloqueado'):
            usuario['bloqueado'] = True
            usuario['fecha_bloqueo'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            usuario['bloqueado_por'] = self.user['email']  # Registrar quién bloqueó
            
            # Guardar los cambios
            try:
                self.db.guardar_usuario(usuario)
                self.mostrar_mensaje_gestion_usuarios(
                    f"🔒 Cuenta de {resultado} bloqueada exitosamente. El usuario no podrá iniciar sesión.", 
                    "orange"
                )
                print(f"DEBUG: Usuario {resultado} bloqueado por administrador {self.user['email']}")
            except Exception as error:
                self.mostrar_mensaje_gestion_usuarios(f"Error al bloquear: {str(error)}", "red")
        else:
            self.mostrar_mensaje_gestion_usuarios("La cuenta ya está bloqueada", "blue")

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