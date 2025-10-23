from datetime import datetime

class Pedido:
    def __init__(self, id, cliente, productos, total, estado="Pendiente", metodo_pago="MercadoPago"):
        self.id = id
        self.fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cliente = cliente
        self.productos = productos
        self.total = total
        self.estado = estado
        self.metodo_pago = metodo_pago
        self.tarjeta_ultimos_digitos = ""
        print(f"✅ DEBUG: Pedido creado - ID: {self.id}, Cliente: {self.cliente}, Total: ${self.total:,.2f}")

    def to_dict(self):
        return {
            'id': self.id,
            'fecha': self.fecha,
            'cliente': self.cliente,
            'productos': self.productos,
            'total': self.total,
            'estado': self.estado,
            'metodo_pago': self.metodo_pago,
            'tarjeta_ultimos_digitos': self.tarjeta_ultimos_digitos
        }

class ItemPedido:
    def __init__(self, producto_id, producto_nombre, precio_unitario, cantidad):
        self.producto_id = producto_id
        self.producto_nombre = producto_nombre
        self.precio_unitario = precio_unitario
        self.cantidad = cantidad
        self.subtotal = precio_unitario * cantidad
        print(f"✅ DEBUG: ItemPedido creado - {producto_nombre} x{cantidad} = ${self.subtotal:,.2f}")

    def to_dict(self):
        return {
            'producto_id': self.producto_id,
            'producto_nombre': self.producto_nombre,
            'precio_unitario': self.precio_unitario,
            'cantidad': self.cantidad,
            'subtotal': self.subtotal
        }