import uuid
import webbrowser
import mercadopago
from datetime import datetime
from modelos import BaseDatos, Pedido
from vistas import VistaPasarelaPago

# Token de acceso para MercadoPago (debería estar en variables de entorno)
ACCESS_TOKEN = "APP_USR-1864674603848840-102206-3ba17bea7a073761dabe4a32e7fafa87-2939897316"

class ControladorPagos:
    def __init__(self, pagina, controlador_principal):
        self.pagina = pagina
        self.controlador_principal = controlador_principal
        self.base_datos = BaseDatos()
        self.id_pedido_actual = None
        self.fecha_actual = None
        self.usuario_actual = None
        self.carrito_actual = None
        self.total_actual = None

    def mostrar_pasarela(self, usuario, carrito, total):
        self.id_pedido_actual = str(uuid.uuid4())[:8]
        self.fecha_actual = datetime.now().strftime("%d/%m/%Y")
        self.usuario_actual = usuario
        self.carrito_actual = carrito
        self.total_actual = total
        
        self.vista_pago = VistaPasarelaPago(self.pagina, usuario, carrito, total, self)
        self.vista_pago.mostrar()

    def obtener_id_pedido(self):
        return self.id_pedido_actual

    def obtener_fecha_actual(self):
        return self.fecha_actual

    def cancelar_pago(self):
        self.controlador_principal.controlador_carrito.mostrar_carrito(
            self.usuario_actual, self.carrito_actual
        )

    def procesar_pago_mercadopago(self):
        try:
            # Validar que haya productos en el carrito
            if not self.carrito_actual:
                self.vista_pago.mostrar_error("El carrito está vacío")
                return

            # 1. Guardar pedido en base de datos
            pedido = Pedido(
                id=self.id_pedido_actual,
                cliente=self.usuario_actual['email'],
                productos=self.carrito_actual,
                total=self.total_actual,
                estado="Pendiente de pago",
                metodo_pago="MercadoPago"
            )
            
            success = self.base_datos.guardar_pedido(pedido.to_dict())
            if not success:
                self.vista_pago.mostrar_error("Error al guardar el pedido. Intenta nuevamente.")
                return
            
            # 2. Crear preferencia en MercadoPago
            sdk = mercadopago.SDK(ACCESS_TOKEN)
            
            # Crear items para MercadoPago
            items = []
            for producto_id, item in self.carrito_actual.items():
                items.append({
                    "title": item['descripcion_final'],
                    "quantity": item['cantidad'],
                    "currency_id": "COP",
                    "unit_price": float(item['precio_final'])
                })
            
            # Si hay muchos productos, crear un item consolidado
            if len(items) > 10:
                items = [{
                    "title": f"Compra #{self.id_pedido_actual} - {len(self.carrito_actual)} productos",
                    "quantity": 1,
                    "currency_id": "COP", 
                    "unit_price": float(self.total_actual)
                }]
            
            preference_data = {
                "items": items,
                "payer": {
                    "email": self.usuario_actual["email"],
                    "name": self.usuario_actual["nombre"]
                },
                "back_urls": {
                    "success": "https://www.tutienda.com/success",
                    "failure": "https://www.tutienda.com/failure", 
                    "pending": "https://www.tutienda.com/pending"
                },
                "auto_return": "approved",
                "external_reference": self.id_pedido_actual,
                "notification_url": "https://www.tutienda.com/notifications",
                "statement_descriptor": "TIENDA-TECH"
            }

            preference_response = sdk.preference().create(preference_data)
            
            if preference_response["status"] in [200, 201]:
                payment_url = preference_response["response"]["init_point"]
                self.vista_pago.mostrar_redireccion(payment_url)
            else:
                error_msg = preference_response.get("response", {}).get("message", "Error desconocido")
                self.vista_pago.mostrar_error(f"Error en MercadoPago: {error_msg}")
                
        except Exception as error:
            self.vista_pago.mostrar_error(f"Error al procesar pago: {str(error)}")

    def finalizar_compra(self):
        self.controlador_principal.mostrar_principal(self.usuario_actual, {})