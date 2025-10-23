class Observador:
    def actualizar(self, mensaje):
        print(f"🔔 DEBUG Observador: {mensaje}")

class SujetoProducto:
    def __init__(self):
        self._observadores = []
        print("✅ DEBUG: SujetoProducto creado")

    def agregar_observador(self, observador):
        self._observadores.append(observador)
        print(f"✅ DEBUG: Observador agregado - Total: {len(self._observadores)}")

    def eliminar_observador(self, observador):
        self._observadores.remove(observador)
        print(f"✅ DEBUG: Observador eliminado - Total: {len(self._observadores)}")

    def notificar_observadores(self, mensaje):
        print(f"🔔 DEBUG: Notificando a {len(self._observadores)} observadores: {mensaje}")
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
        print(f"✅ DEBUG: Producto creado - {self.nombre} (ID: {self.id})")

    def obtener_precio(self):
        return self.precio_base

    def obtener_descripcion(self):
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

class DecoradorProducto:
    def __init__(self, producto):
        self._producto = producto
        print(f"✅ DEBUG: DecoradorProducto aplicado a {producto.nombre}")

    def __getattr__(self, name):
        return getattr(self._producto, name)

    def obtener_precio(self):
        return self._producto.obtener_precio()

    def obtener_descripcion(self):
        return self._producto.obtener_descripcion()

    def to_dict(self):
        return self._producto.to_dict()

class DecoradorDescuento(DecoradorProducto):
    def __init__(self, producto, descuento):
        super().__init__(producto)
        self.descuento = descuento
        print(f"✅ DEBUG: Descuento de {descuento*100}% aplicado a {producto.nombre}")

    def obtener_precio(self):
        precio_original = self._producto.obtener_precio()
        precio_con_descuento = precio_original * (1 - self.descuento)
        print(f"💰 DEBUG: Precio con descuento - Original: ${precio_original:,.2f}, Con descuento: ${precio_con_descuento:,.2f}")
        return precio_con_descuento

    def obtener_descripcion(self):
        return f"{self._producto.obtener_descripcion()} (Descuento {int(self.descuento*100)}%)"

class DecoradorEnvio(DecoradorProducto):
    def obtener_precio(self):
        precio_original = self._producto.obtener_precio()
        precio_con_envio = precio_original + 100000
        print(f"🚚 DEBUG: Precio con envío - Original: ${precio_original:,.2f}, Con envío: ${precio_con_envio:,.2f}")
        return precio_con_envio

    def obtener_descripcion(self):
        return f"{self._producto.obtener_descripcion()} + envío extra"