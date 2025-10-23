from modelos import BaseDatos
from vistas import VistaPrincipal, VistaPanelAdministrador
from .controlador_productos import ControladorProductos
from .controlador_carrito import ControladorCarrito
from .controlador_pagos import ControladorPagos
from .controlador_admin import ControladorAdmin

class ControladorPrincipal:
    def __init__(self, pagina):
        self.pagina = pagina
        self.base_datos = BaseDatos()
        self.usuario_actual = None
        self.carrito_actual = {}
        
        # Inicializar controladores
        self.controlador_productos = ControladorProductos(pagina, self)
        self.controlador_carrito = ControladorCarrito(pagina, self)
        self.controlador_pagos = ControladorPagos(pagina, self)
        self.controlador_admin = ControladorAdmin(pagina, self)
        
        # Inicializar vista principal
        self.vista_principal = VistaPrincipal(pagina, self)

    def mostrar_principal(self, usuario, carrito=None):
        self.usuario_actual = usuario
        if carrito:
            self.carrito_actual = carrito
        
        productos, categorias, marcas = self.base_datos.cargar_productos()
        self.vista_principal.mostrar(usuario, productos, self.carrito_actual)

    def mostrar_detalle_producto(self, producto):
        self.controlador_productos.mostrar_detalle(producto, self.carrito_actual)

    def mostrar_carrito(self, carrito):
        self.controlador_carrito.mostrar_carrito(self.usuario_actual, carrito)

    def mostrar_panel_administrador(self):
        self.controlador_admin.mostrar_panel(self.usuario_actual)

    def buscar_productos(self, query):
        productos, categorias, marcas = self.base_datos.cargar_productos()
        
        if not query:
            self.vista_principal.mostrar(self.usuario_actual, productos, self.carrito_actual)
            return

        query = query.lower()
        resultados = []
        
        for producto in productos:
            if (query in producto['nombre'].lower() or 
                query in producto['marca'].lower() or 
                query in producto['categoria'].lower()):
                resultados.append(producto)
        
        # Actualizar vista con resultados
        self.vista_principal.mostrar(self.usuario_actual, resultados, self.carrito_actual)

    def cerrar_sesion(self):
        from .controlador_auth import ControladorAuth
        controlador_auth = ControladorAuth(self.pagina)
        controlador_auth.set_controlador_principal(self)
        controlador_auth.mostrar_login()

    def actualizar_carrito(self, carrito):
        self.carrito_actual = carrito
        self.vista_principal.actualizar_contador_carrito()

    def get_usuario_actual(self):
        return self.usuario_actual

    def get_carrito_actual(self):
        return self.carrito_actual