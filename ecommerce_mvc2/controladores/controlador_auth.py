import re
from modelos import BaseDatos
from vistas import VistaLogin, VistaRegistro, VistaRegistroAdmin

class ControladorAuth:
    def __init__(self, pagina):
        self.pagina = pagina
        self.base_datos = BaseDatos()
        self.vista_login = VistaLogin(pagina, self)
        self.vista_registro = VistaRegistro(pagina, self)
        self.vista_registro_admin = VistaRegistroAdmin(pagina, self)
        self.controlador_principal = None

    def set_controlador_principal(self, controlador_principal):
        self.controlador_principal = controlador_principal

    def mostrar_login(self):
        self.vista_login.mostrar()

    def mostrar_registro(self):
        self.vista_registro.mostrar()

    def mostrar_registro_admin(self):
        self.vista_registro_admin.mostrar()

    def iniciar_sesion(self, email, password):
        if not email:
            self.vista_login.mostrar_error("Por favor ingresa tu email")
            return
        if not password:
            self.vista_login.mostrar_error("Por favor ingresa tu contraseña")
            return

        usuarios = self.base_datos.cargar_usuarios()
        if email not in usuarios:
            self.vista_login.mostrar_error("El usuario no existe")
            return

        usuario = usuarios[email]
        
        # Verificar bloqueo
        estado_bloqueo = self.base_datos.obtener_estado_bloqueo(email)
        if estado_bloqueo['bloqueado']:
            self.vista_login.mostrar_error(f"❌ Cuenta bloqueada. Contacta al administrador.")
            return
        
        if usuario['password'] != password:
            self.vista_login.mostrar_error("Contraseña incorrecta")
            return

        # Login exitoso
        self.vista_login.limpiar_campos()
        if self.controlador_principal:
            self.controlador_principal.mostrar_principal(usuario)

    def registrar_usuario(self, datos_usuario):
        error = self.validar_registro(datos_usuario)
        if error:
            self.vista_registro.mostrar_mensaje(error, "red")
            return

        try:
            self.base_datos.guardar_usuario(datos_usuario)
            self.vista_registro.mostrar_mensaje(
                f"¡Registro exitoso! Cuenta de {datos_usuario['tipo'].capitalize()} creada", 
                "green"
            )
            self.vista_registro.limpiar_campos()
        except Exception as e:
            self.vista_registro.mostrar_mensaje(f"Error al registrar: {str(e)}", "red")

    def registrar_administrador(self, datos_admin):
        error = self.validar_registro_admin(datos_admin)
        if error:
            self.vista_registro_admin.mostrar_mensaje(error, "red")
            return

        try:
            self.base_datos.guardar_usuario(datos_admin)
            self.vista_registro_admin.mostrar_mensaje("¡Administrador registrado exitosamente!", "green")
            self.vista_registro_admin.limpiar_campos()
        except Exception as e:
            self.vista_registro_admin.mostrar_mensaje(f"Error al registrar: {str(e)}", "red")

    def validar_registro(self, datos):
        if not datos['nombre'].strip():
            return "El nombre es obligatorio"
        if not datos['email'].strip():
            return "El email es obligatorio"
        if not self.validar_email(datos['email']):
            return "El formato del email no es válido"
        
        usuarios = self.base_datos.cargar_usuarios()
        if datos['email'] in usuarios:
            return "Este email ya está registrado"
        if not datos['password']:
            return "La contraseña es obligatoria"
        if len(datos['password']) < 8:
            return "La contraseña debe tener al menos 8 caracteres"
        
        if datos['tipo'] == "vendedor":
            if not datos.get('nombre_tienda', '').strip():
                return "El nombre de la tienda es obligatorio"
            if not datos.get('telefono', '').strip():
                return "El teléfono es obligatorio"
        
        return None

    def validar_registro_admin(self, datos):
        if not datos['nombre'].strip():
            return "El nombre es obligatorio"
        if not datos['email'].strip():
            return "El email es obligatorio"
        if not self.validar_email(datos['email']):
            return "El formato del email no es válido"
        
        usuarios = self.base_datos.cargar_usuarios()
        if datos['email'] in usuarios:
            return "Este email ya está registrado"
        if not datos['password']:
            return "La contraseña es obligatoria"
        if len(datos['password']) < 8:
            return "La contraseña debe tener al menos 8 caracteres"
        
        return None

    def validar_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None