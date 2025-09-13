import flet as ft
import re
import json
import os
import uuid
from datetime import datetime

# --- OBSERVER PATTERN ---
class Observer:
    def actualizar(self, mensaje):
        pass

class ProductSubject:
    def __init__(self):
        self._observadores = []

    def agregar_observador(self, observador):
        self._observadores.append(observador)

    def eliminar_observador(self, observador):
        self._observadores.remove(observador)

    def notificar_observadores(self, mensaje):
        for observador in self._observadores:
            observador.actualizar(mensaje)

# --- DECORATOR PATTERN ---
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

    def get_precio(self):
        return self.precio_base

    def get_descripcion(self):
        return self.nombre

    def to_dict(self):
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

class ProductoDecorador:
    def __init__(self, producto):
        self._producto = producto

    def get_precio(self):
        return self._producto.get_precio()

    def get_descripcion(self):
        return self._producto.get_descripcion()

    def to_dict(self):
        return self._producto.to_dict()

class DescuentoDecorador(ProductoDecorador):
    def __init__(self, producto, descuento):
        super().__init__(producto)
        self.descuento = descuento

    def get_precio(self):
        return self._producto.get_precio() * (1 - self.descuento)

    def get_descripcion(self):
        return f"{self._producto.get_descripcion()} (Descuento {int(self.descuento*100)}%)"

class EnvioDecorador(ProductoDecorador):
    def get_precio(self):
        return self._producto.get_precio() + 20

    def get_descripcion(self):
        return f"{self._producto.get_descripcion()} + envío extra"

# --- DATABASE HANDLER ---
class JSONDatabase:
    def __init__(self):
        self.products_file = "productos.json"
        self.users_file = "usuarios.json"
        self.orders_file = "pedidos.json"
    
    def cargar_usuarios(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r', encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}
    
    def guardar_usuario(self, datos_usuario):
        users = self.cargar_usuarios()
        users[datos_usuario['email']] = datos_usuario
        with open(self.users_file, 'w', encoding="utf-8") as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
    
    def cargar_productos(self):
        if os.path.exists(self.products_file):
            with open(self.products_file, 'r', encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    productos = []
                    for p in data.get("productos", []):
                        producto_params = {
                            'id': p.get('id'),
                            'nombre': p.get('nombre'),
                            'precio': p.get('precio'),
                            'descripcion': p.get('descripcion'),
                            'marca': p.get('marca'),
                            'categoria': p.get('categoria'),
                            'imagen': p.get('imagen'),
                            'destacado': p.get('destacado', False)
                        }
                        productos.append(Producto(**producto_params))
                    return productos, data.get("categorias", []), data.get("marcas", [])
                except json.JSONDecodeError:
                    return [], [], []
        return [], [], []
    
    def guardar_pedido(self, pedido):
        orders = self.cargar_pedidos()
        order_id = str(pedido['id'])
        orders[order_id] = pedido
        with open(self.orders_file, 'w', encoding="utf-8") as f:
            json.dump(orders, f, indent=4, ensure_ascii=False)
    
    def cargar_pedidos(self):
        if os.path.exists(self.orders_file):
            with open(self.orders_file, 'r', encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}


# --- LOGIN APP ---
class IngresoApp:
    def __init__(self, page):
        self.page = page
        self.page.title = "Login E-commerce"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.db = JSONDatabase()
        self.crear_controles_ingreso()

    def crear_controles_ingreso(self):
        """Crear controles de login"""
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
        self.mensaje_login = ft.Text("", color="red")

        self.login_container = ft.Container(
            content=ft.Column([
                ft.Text("INICIAR SESIÓN", size=24, weight="bold"),
                ft.Text("Bienvenido de vuelta", size=16, color="gray"),
                self.email_login,
                self.password_login,
                self.btn_login,
                self.btn_registrar,
                self.mensaje_login
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            width=400
        )

        self.page.add(ft.Row([
            self.login_container
        ], alignment=ft.MainAxisAlignment.CENTER))

    def iniciar_sesion(self, e):
        """Manejar el evento de login"""
        email = self.email_login.value.strip().lower()
        password = self.password_login.value

        if not email:
            self.mensaje_login.value = "Por favor ingresa tu email"
            self.page.update()
            return
        if not password:
            self.mensaje_login.value = "Por favor ingresa tu contraseña"
            self.page.update()
            return

        users = self.db.cargar_usuarios()
        if email not in users:
            self.mensaje_login.value = "El usuario no existe"
            self.mensaje_login.color = "red"
            self.page.update()
            return

        user = users[email]
        if user['password'] != password:
            self.mensaje_login.value = "Contraseña incorrecta"
            self.mensaje_login.color = "red"
            self.page.update()
            return

        self.page.clean()
        AplicacionPrincipal(self.page, user)

    def ir_a_registro(self, e):
        self.page.clean()
        RegistroApp(self.page, self.db)


# --- REGISTRO APP ---
class RegistroApp:
    def __init__(self, page, db):
        self.page = page
        self.page.title = "Registro E-commerce"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.db = db
        self.control_registro()

    def control_registro(self):
        """Crear controles de registro"""
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

    def activar_campos_vendedor(self, e):
        es_vendedor = self.tipo_usuario.value == "vendedor"
        self.nombre_tienda.visible = es_vendedor
        self.telefono.visible = es_vendedor
        self.page.update()

    def validar_correo(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validar_formulario(self):
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
        return None

    def registrar_usuario(self, e):
        error = self.validar_formulario()
        if error:
            self.mensaje.value = error
            self.mensaje.color = "red"
            self.page.update()
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

    def volver_al_login(self, e):
        self.page.clean()
        IngresoApp(self.page)


# --- DETALLE PRODUCTO CON PATRONES ---
class DetalleProducto(Observer):
    def __init__(self, page, producto, carrito_callback, volver_callback):
        self.page = page
        self.producto_base = producto
        self.producto_actual = producto
        self.carrito_callback = carrito_callback
        self.volver_callback = volver_callback
        self.subject = ProductSubject()
        self.subject.agregar_observador(self)
        self.page.title = f"Detalle: {producto.nombre}"
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Elementos UI
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
        self.envio_checkbox = ft.Checkbox(label="Aplicar envío ultra rápido (+$20)", on_change=self.actualizar_precio)

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
    
    def actualizar_precio(self, e=None):
        self.producto_actual = self.producto_base
        
        if self.descuento_checkbox.value:
            self.producto_actual = DescuentoDecorador(self.producto_actual, 0.2)
        if self.envio_checkbox.value:
            self.producto_actual = EnvioDecorador(self.producto_actual)

        self.nombre_texto.value = self.producto_actual.get_descripcion()
        self.precio_texto.value = f"${self.producto_actual.get_precio():,.2f}"
        self.page.update()
    
    def al_carrito(self, e):
        producto_dict = self.producto_base.to_dict()
        producto_dict['precio_final'] = self.producto_actual.get_precio()
        producto_dict['descripcion_final'] = self.producto_actual.get_descripcion()
        
        self.carrito_callback(producto_dict)
        
        mensaje = f"'{self.producto_actual.get_descripcion()}' añadido al carrito"
        self.subject.notificar_observadores(mensaje)
    
    def actualizar(self, mensaje):
        self.mensajes.controls.append(ft.Text(mensaje, color="blue"))
        self.page.update()
    
    def volver(self, e):
        self.page.clean()
        self.volver_callback()


# --- CARRITO DE COMPRAS ---
class Carrito:
    def __init__(self, page, user, carrito, volver_callback):
        self.page = page
        self.user = user
        self.carrito = carrito
        self.volver_callback = volver_callback
        self.db = JSONDatabase()
        self.page.title = "Carrito de Compras"
        
        self.controles_carrito()
    
    def controles_carrito(self):
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
        
        self.page.clean()
        self.page.add(contenido)
    
    def actualizar_cantidad(self, producto_id, cambio):
        """Actualizar la cantidad de un producto en el carrito"""
        if producto_id in self.carrito:
            self.carrito[producto_id]['cantidad'] += cambio
            
            if self.carrito[producto_id]['cantidad'] <= 0:
                del self.carrito[producto_id]
        
        self.controles_carrito()
    
    def eliminar_producto(self, producto_id):
        if producto_id in self.carrito:
            del self.carrito[producto_id]
        
        self.controles_carrito()
    
    def procesar_pago(self, total):
        """Abrir la pasarela de pago"""
        self.page.clean()
        PasarelaPago(self.page, self.user, self.carrito, total, self.volver_callback)
    
    def volver(self, e):
        """Volver a la página principal"""
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
        self.db = JSONDatabase()
        self.page.title = "Pasarela de Pago"
        self.page.bgcolor = "white"
        
        self.crear_pasarela()
    
    def crear_pasarela(self):
        # Detalles del pedido
        order_id = str(uuid.uuid4())[:8]
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        
        detalles = [
            ("ID:", order_id),
            ("Monto:", f"${self.total:,.2f}"),
            ("Fecha:", fecha_actual),
            ("Método de pago:", "Tarjeta"),
            ("Estado del pago:", "Pendiente"),
        ]

        # Panel izquierdo: Detalles del pedido
        panel_izquierdo = ft.Container(
            content=ft.Column([
                ft.Text("Importe:", size=16, weight=ft.FontWeight.BOLD, color="black"),
                ft.Text(f"${self.total:,.2f}", size=20, weight=ft.FontWeight.BOLD, color="blue"),
                *[ft.Text(f"{k} {v}", size=12, color="black") for k, v in detalles],
                ft.Divider(),
                ft.Text("Productos:", size=14, weight=ft.FontWeight.BOLD, color="black"),
                *[ft.Text(f"- {item['descripcion_final']} x{item['cantidad']}", size=12, color="black") 
                  for item in self.carrito.values()]
            ], spacing=5, alignment="start"),
            bgcolor="#E6F2FF",
            padding=15,
            border=ft.border.all(1, "black"),
            width=280
        )

        # Panel derecho: Formulario de pago
        self.num_tarjeta = ft.TextField(label="Nº Tarjeta", width=230)
        self.expiracion = ft.TextField(label="Caducidad (MM/AA)", width=150)
        self.cvv = ft.TextField(label="Cód. Seguridad", width=100, password=True)

        def cancelar_pago(e):
            self.page.clean()
            Carrito(self.page, self.user, self.carrito, self.volver_callback)

        def completar_pago(e):
            if not self.num_tarjeta.value or not self.expiracion.value or not self.cvv.value:
                self.page.dialog = ft.AlertDialog(
                    title=ft.Text("Error"),
                    content=ft.Text("Por favor, completa todos los campos")
                )
                self.page.dialog.open = True
                self.page.update()
                return
            
            pedido = {
                'id': order_id,
                'fecha': fecha_actual,
                'cliente': self.user['email'],
                'productos': self.carrito,
                'total': self.total,
                'estado': 'Completado',
                'metodo_pago': 'Tarjeta',
                'tarjeta_ultimos_digitos': self.num_tarjeta.value[-4:]
            }
            
            self.db.guardar_pedido(pedido)
            
            self.page.dialog = ft.AlertDialog(
                title=ft.Text("Pago exitoso"),
                content=ft.Text(f"Pago realizado con tarjeta terminada en {self.num_tarjeta.value[-4:]}\nID de pedido: {order_id}"),
                actions=[
                    ft.TextButton("Aceptar", on_click=lambda e: self.finalizar_compra())
                ]
            )
            self.page.dialog.open = True
            self.page.update()

        panel_derecho = ft.Container(
            content=ft.Column([
                ft.Text("PAGAR CON TARJETA", size=14, weight=ft.FontWeight.BOLD, color="black"),
                self.num_tarjeta,
                ft.Row([self.expiracion, self.cvv]),
                ft.Row([
                    ft.ElevatedButton("CANCELAR", bgcolor="gray", color="white", on_click=cancelar_pago),
                    ft.ElevatedButton("PAGAR", bgcolor="blue", color="white", on_click=completar_pago),
                ], spacing=10)
            ], spacing=10, alignment="start"),
            bgcolor="white",
            padding=15,
            border=ft.border.all(1, "black"),
            width=280
        )

        barra_superior = ft.Row([
            ft.ElevatedButton("⬅️ Volver al carrito", on_click=cancelar_pago),
            ft.Container(expand=True),
            ft.Text("Pasarela de Pago", size=20, weight="bold")
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        contenido = ft.Column([
            barra_superior,
            ft.Divider(),
            ft.Row(
                [panel_izquierdo, panel_derecho],
                alignment="center",
                spacing=20,
            )
        ], spacing=20)

        self.page.clean()
        self.page.add(contenido)
    
    def finalizar_compra(self):
        """Finalizar la compra y volver a la página principal"""
        self.page.dialog.open = False
        self.page.clean()
        self.volver_callback({})  # Vaciar el carrito



class AplicacionPrincipal:
    def __init__(self, page, user, carrito=None):
        self.page = page
        self.user = user
        self.carrito = carrito or {}
        self.db = JSONDatabase()
        self.page.title = "E-commerce Principal"
        self.page.scroll = ft.ScrollMode.AUTO

        self.controles_PagPrincipal()

    def mostrar_mensaje(self, texto):
        """Mostrar un mensaje temporal en la parte inferior"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(texto),
            duration=2000,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def cargar_datos(self):
        """Cargar productos, categorías y marcas"""
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
        self.page.clean()
        DetalleProducto(self.page, producto, self.agregar_al_carrito, self.volver_de_detalle)

    def agregar_al_carrito(self, producto):
        """Agregar producto al carrito desde el detalle"""
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
        
        self.mostrar_mensaje(f"✅ {producto['descripcion_final']} añadido al carrito")
        self.actualizar_contador_carrito()

    def volver_de_detalle(self):
        self.controles_PagPrincipal()
        
    def actualizar_contador_carrito(self):
        total_items = sum(item['cantidad'] for item in self.carrito.values())
        self.btn_carrito.text = f"🛒 Carrito ({total_items})"
        self.page.update()

    def buscar_productos(self, query):
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
        
        return resultados

    def controles_PagPrincipal(self):
        """Crear controles de la página principal"""
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

        barra_superior = ft.Row(
            controls=[
                ft.ElevatedButton("⬅️ Cerrar Sesión", on_click=self.cerrar_sesion),
                ft.Container(width=20),
                self.campo_busqueda,
                ft.Container(width=20),
                self.btn_carrito
            ],
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

    def barra_buscar_productos(self, e):
        query = self.campo_busqueda.value.strip()
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

    def abrir_carrito(self, e):
        self.page.clean()
        Carrito(self.page, self.user, self.carrito, self.volver_de_carrito)

    def volver_de_carrito(self, carrito_actualizado):
        self.carrito = carrito_actualizado
        self.controles_PagPrincipal()
        self.actualizar_contador_carrito()

    def cerrar_sesion(self, e):
        self.page.clean()
        IngresoApp(self.page)

def main(page: ft.Page):
    page.window_width = 1200
    page.window_height = 700
    page.window_min_width = 800
    page.window_min_height = 600

    IngresoApp(page)

ft.app(target=main)