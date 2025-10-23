import re
from modelos import BaseDatos
from vistas import VistaPanelAdministrador

class ControladorAdmin:
    def __init__(self, pagina, controlador_principal):
        self.pagina = pagina
        self.controlador_principal = controlador_principal
        self.base_datos = BaseDatos()
        self.vista_admin = None

    def mostrar_panel(self, usuario):
        self.vista_admin = VistaPanelAdministrador(self.pagina, usuario, self)
        self.vista_admin.mostrar()

    def ver_estado_usuario(self, email):
        if not self.validar_email(email):
            self.vista_admin.mostrar_mensaje_gestion_usuarios("Por favor ingresa un email válido", "red")
            return
        
        usuarios = self.base_datos.cargar_usuarios()
        usuario = usuarios.get(email)
        if not usuario:
            self.vista_admin.mostrar_mensaje_gestion_usuarios("Usuario no encontrado", "red")
            return
        
        estado_bloqueo = self.base_datos.obtener_estado_bloqueo(email)
        estado = "🔒 BLOQUEADO" if estado_bloqueo['bloqueado'] else "✅ ACTIVO"
        
        mensaje_estado = f"""
Usuario: {email}
Nombre: {usuario.get('nombre', 'N/A')}
Tipo: {usuario.get('tipo', 'N/A')}
Estado: {estado}
Registro: {usuario.get('fecha_registro', 'N/A')}
"""
        
        if estado_bloqueo['bloqueado']:
            mensaje_estado += f"\nBloqueado desde: {estado_bloqueo['fecha_operacion']}"
            mensaje_estado += f"\nBloqueado por: {estado_bloqueo['realizado_por']}"
        
        self.vista_admin.mostrar_mensaje_gestion_usuarios(mensaje_estado, "blue")

    def desbloquear_usuario(self, email):
        if not self.validar_email(email):
            self.vista_admin.mostrar_mensaje_gestion_usuarios("Por favor ingresa un email válido", "red")
            return
        
        usuarios = self.base_datos.cargar_usuarios()
        usuario = usuarios.get(email)
        if not usuario:
            self.vista_admin.mostrar_mensaje_gestion_usuarios("Usuario no encontrado", "red")
            return
        
        estado_actual = self.base_datos.obtener_estado_bloqueo(email)
        if not estado_actual['bloqueado']:
            self.vista_admin.mostrar_mensaje_gestion_usuarios("La cuenta ya está activa", "blue")
            return
        
        try:
            usuario_actual = self.controlador_principal.get_usuario_actual()
            self.base_datos.desbloquear_usuario(
                email, 
                usuario_actual['email'],
                "Desbloqueo administrativo desde panel"
            )
            self.vista_admin.mostrar_mensaje_gestion_usuarios(f"✅ Cuenta de {email} desbloqueada exitosamente", "green")
        except Exception as error:
            self.vista_admin.mostrar_mensaje_gestion_usuarios(f"Error al desbloquear: {str(error)}", "red")

    def bloquear_usuario(self, email):
        if not self.validar_email(email):
            self.vista_admin.mostrar_mensaje_gestion_usuarios("Por favor ingresa un email válido", "red")
            return
        
        usuarios = self.base_datos.cargar_usuarios()
        usuario = usuarios.get(email)
        if not usuario:
            self.vista_admin.mostrar_mensaje_gestion_usuarios("Usuario no encontrado", "red")
            return
        
        # No permitir bloquear al administrador actual
        usuario_actual = self.controlador_principal.get_usuario_actual()
        if email == usuario_actual['email']:
            self.vista_admin.mostrar_mensaje_gestion_usuarios("No puedes bloquear tu propia cuenta", "red")
            return
        
        estado_actual = self.base_datos.obtener_estado_bloqueo(email)
        if estado_actual['bloqueado']:
            self.vista_admin.mostrar_mensaje_gestion_usuarios("La cuenta ya está bloqueada", "blue")
            return
        
        try:
            self.base_datos.bloquear_usuario(
                email, 
                usuario_actual['email'],
                "Bloqueo administrativo desde panel"
            )
            self.vista_admin.mostrar_mensaje_gestion_usuarios(f"🔒 Cuenta de {email} bloqueada exitosamente", "orange")
        except Exception as error:
            self.vista_admin.mostrar_mensaje_gestion_usuarios(f"Error al bloquear: {str(error)}", "red")

    def eliminar_usuario(self, email):
        if not self.validar_email(email):
            self.vista_admin.mostrar_mensaje_gestion_usuarios("Por favor ingresa un email válido", "red")
            return
        
        usuarios = self.base_datos.cargar_usuarios()
        usuario = usuarios.get(email)
        if not usuario:
            self.vista_admin.mostrar_mensaje_gestion_usuarios("Usuario no encontrado", "red")
            return
        
        # No permitir eliminar al administrador actual
        usuario_actual = self.controlador_principal.get_usuario_actual()
        if email == usuario_actual['email']:
            self.vista_admin.mostrar_mensaje_gestion_usuarios("No puedes eliminar tu propia cuenta", "red")
            return
        
        # En una implementación real, aquí iría un diálogo de confirmación
        try:
            self.base_datos.eliminar_usuario(email)
            self.vista_admin.mostrar_mensaje_gestion_usuarios(f"🗑️ Cuenta de {email} eliminada permanentemente", "red")
        except Exception as error:
            self.vista_admin.mostrar_mensaje_gestion_usuarios(f"Error al eliminar: {str(error)}", "red")

    def gestionar_marcas(self, e):
        self.vista_admin.mostrar_mensaje_global("🚧 Gestión de marcas en desarrollo")

    def gestionar_categorias(self, e):
        self.vista_admin.mostrar_mensaje_global("🚧 Gestión de categorías en desarrollo")

    def ver_inventario_completo(self, e):
        self.vista_admin.mostrar_mensaje_global("🚧 Inventario completo en desarrollo")

    def ver_stock_bajo(self, e):
        self.vista_admin.mostrar_mensaje_global("🚧 Stock bajo en desarrollo")

    def actualizar_stock_producto(self, e):
        self.vista_admin.mostrar_mensaje_global("🚧 Actualizar stock en desarrollo")

    def validar_email(self, email):
        if not email or not email.strip():
            return False
        email = email.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def volver_principal(self):
        usuario_actual = self.controlador_principal.get_usuario_actual()
        carrito_actual = self.controlador_principal.get_carrito_actual()
        self.controlador_principal.mostrar_principal(usuario_actual, carrito_actual)