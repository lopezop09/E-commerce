from modelos import SujetoProducto
from vistas import VistaDetalleProducto

class ControladorProductos:
    def __init__(self, pagina, controlador_principal):
        self.pagina = pagina
        self.controlador_principal = controlador_principal
        self.sujeto_producto = SujetoProducto()

    def mostrar_detalle(self, producto, carrito_actual):
        vista_detalle = VistaDetalleProducto(self.pagina, producto, self)
        self.sujeto_producto.agregar_observador(vista_detalle)
        vista_detalle.crear_interfaz()

    def agregar_al_carrito(self, producto):
        carrito_actual = self.controlador_principal.get_carrito_actual()
        
        producto_id = str(producto['id'])
        if producto_id in carrito_actual:
            carrito_actual[producto_id]['cantidad'] += 1
        else:
            carrito_actual[producto_id] = {
                'id': producto['id'],
                'nombre': producto['nombre'],
                'precio_base': producto['precio'],
                'precio_final': producto['precio_final'],
                'descripcion_final': producto['descripcion_final'],
                'cantidad': 1
            }
        
        mensaje = f"'{producto['descripcion_final']}' añadido al carrito"
        self.sujeto_producto.notificar_observadores(mensaje)
        
        self.controlador_principal.actualizar_carrito(carrito_actual)

    def volver_principal(self):
        usuario_actual = self.controlador_principal.get_usuario_actual()
        carrito_actual = self.controlador_principal.get_carrito_actual()
        self.controlador_principal.mostrar_principal(usuario_actual, carrito_actual)