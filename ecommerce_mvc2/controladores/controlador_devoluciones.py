import flet as ft
import mercadopago

class ControladorDevolucionesSimple:
    def __init__(self, pagina, controlador_principal):
        self.pagina = pagina
        self.controlador_principal = controlador_principal
        
    def mostrar_devolucion_rapida(self, usuario):
        """Interfaz simple para devolución rápida"""
        
        # Campos simples
        campo_pedido_id = ft.TextField(
            label="ID del Pedido a devolver",
            width=300,
            hint_text="Ej: ABC123"
        )
        
        campo_monto = ft.TextField(
            label="Monto a devolver",
            width=200,
            prefix_text="$",
            hint_text="0.00"
        )
        
        campo_motivo = ft.TextField(
            label="Motivo breve",
            width=400,
            hint_text="Ej: Producto defectuoso"
        )
        
        mensaje = ft.Text("", color=ft.Colors.BLUE, size=12)
        
        def procesar_devolucion(e):
            # Validaciones básicas
            if not campo_pedido_id.value:
                mensaje.value = "❌ Ingresa el ID del pedido"
                mensaje.color = ft.Colors.RED
                self.pagina.update()
                return
                
            if not campo_monto.value:
                mensaje.value = "❌ Ingresa el monto a devolver"
                mensaje.color = ft.Colors.RED
                self.pagina.update()
                return
            
            try:
                # Procesar devolución
                monto = float(campo_monto.value)
                pedido_id = campo_pedido_id.value.strip()
                motivo = campo_motivo.value or "Devolución solicitada"
                
                # Aquí iría la integración con MercadoPago
                resultado = self.procesar_reembolso_mercadopago(pedido_id, monto, motivo)
                
                if resultado["exito"]:
                    mensaje.value = f"✅ {resultado['mensaje']}"
                    mensaje.color = ft.Colors.GREEN
                    # Limpiar campos
                    campo_pedido_id.value = ""
                    campo_monto.value = ""
                    campo_motivo.value = ""
                else:
                    mensaje.value = f"❌ {resultado['mensaje']}"
                    mensaje.color = ft.Colors.RED
                    
            except ValueError:
                mensaje.value = "❌ El monto debe ser un número válido"
                mensaje.color = ft.Colors.RED
            except Exception as e:
                mensaje.value = f"❌ Error: {str(e)}"
                mensaje.color = ft.Colors.RED
                
            self.pagina.update()
        
        def volver(e):
            usuario_actual = self.controlador_principal.get_usuario_actual()
            carrito_actual = self.controlador_principal.get_carrito_actual()
            self.controlador_principal.mostrar_principal(usuario_actual, carrito_actual)
        
        # Interfaz simple
        contenido = ft.Column([
            ft.Row([
                ft.ElevatedButton("⬅️ Volver", on_click=volver),
                ft.Container(expand=True),
                ft.Text("Devolución Rápida", size=24, weight="bold", color=ft.Colors.ORANGE),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Divider(),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Devoluciones", size=18, weight="bold"),
                        ft.Text("Proceso de reembolsos", size=14, color="gray"),
                        ft.Divider(),
                        
                        ft.Row([campo_pedido_id], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([campo_monto], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([campo_motivo], alignment=ft.MainAxisAlignment.CENTER),
                        
                        ft.Container(height=20),
                        
                        ft.Row([
                            ft.ElevatedButton(
                                "Procesar Devolución",
                                on_click=procesar_devolucion,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.ORANGE,
                                    color=ft.Colors.WHITE,
                                    padding=20
                                )
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        
                        ft.Container(height=10),
                        mensaje,
                        
                        ft.Container(height=20),
                        ft.Text("💡 Esta devolución se procesará a través de MercadoPago", 
                               size=12, color="blue", text_align=ft.TextAlign.CENTER),
                        ft.Text("y el dinero será reembolsado al método de pago original", 
                               size=11, color="gray", text_align=ft.TextAlign.CENTER)
                    ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=30,
                    width=500
                )
            )
        ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        self.pagina.clean()
        self.pagina.add(contenido)
    
    def procesar_reembolso_mercadopago(self, pedido_id, monto, motivo):
        """
        Procesar reembolso simple con MercadoPago
        """
        try:
            # Configurar SDK de MercadoPago
            sdk = mercadopago.SDK("APP_USR-1864674603848840-102206-3ba17bea7a073761dabe4a32e7fafa87-2939897316")
            
            # SIMULACIÓN - En producción quitar esto:
            print(f"Procesando reembolso para pedido {pedido_id}")
            print(f" Monto: ${monto:,.2f}")
            print(f" Motivo: {motivo}")
            
            # Simular éxito
            return {
                "exito": True,
                "mensaje": f"Reembolso de ${monto:,.2f} procesado exitosamente para pedido {pedido_id}",
                "id_reembolso": f"refund_{pedido_id}",
                "monto": monto
            }
                
        except Exception as e:
            return {
                "exito": False,
                "mensaje": f"Error al procesar reembolso: {str(e)}"
            }
    
    def obtener_payment_id_por_pedido(self, pedido_id):
        """
        En producción: Buscar en tu base de datos el payment_id de MercadoPago
        asociado al pedido_id
        """
        # Por ahora retornamos un ID simulado
        return f"mp_{pedido_id}"