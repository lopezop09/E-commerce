from vistas import VistaCarrito, VistaPasarelaPago

class ControladorCarrito:
    def __init__(self, pagina, controlador_principal):
        self.pagina = pagina
        self.controlador_principal = controlador_principal

    def mostrar_carrito(self, usuario, carrito):
        vista_carrito = VistaCarrito(self.pagina, usuario, carrito, self)
        vista_carrito.mostrar()

    def actualizar_carrito(self, carrito):
        self.controlador_principal.actualizar_carrito(carrito)
        usuario_actual = self.controlador_principal.get_usuario_actual()
        self.mostrar_carrito(usuario_actual, carrito)

    def mostrar_pasarela_pago(self, carrito, total):
        usuario_actual = self.controlador_principal.get_usuario_actual()
        controlador_pagos = self.controlador_principal.controlador_pagos
        controlador_pagos.mostrar_pasarela(usuario_actual, carrito, total)

    def volver_principal(self, carrito):
        self.controlador_principal.actualizar_carrito(carrito)
        usuario_actual = self.controlador_principal.get_usuario_actual()
        self.controlador_principal.mostrar_principal(usuario_actual, carrito)