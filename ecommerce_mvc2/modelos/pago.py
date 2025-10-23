import uuid
from datetime import datetime

class Pago:
    def __init__(self, usuario, carrito, total):
        self.id = str(uuid.uuid4())[:8]
        self.usuario = usuario
        self.carrito = carrito
        self.total = total
        self.fecha = datetime.now().strftime("%d/%m/%Y")
        self.estado = "Pendiente"
        self.metodo_pago = "MercadoPago"
        print(f"✅ DEBUG: Pago creado - ID: {self.id}, Usuario: {self.usuario['email']}, Total: ${self.total:,.2f}")

    def to_dict(self):
        return {
            'id': self.id,
            'usuario': self.usuario,
            'carrito': self.carrito,
            'total': self.total,
            'fecha': self.fecha,
            'estado': self.estado,
            'metodo_pago': self.metodo_pago
        }