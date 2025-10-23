import flet as ft
from modelos import BaseDatos

class VistaLogin:
    def __init__(self, pagina, controlador_auth):
        self.pagina = pagina
        self.controlador = controlador_auth
        self.base_datos = BaseDatos()
        self.crear_controles()

    def crear_controles(self):
        self.campo_email = ft.TextField(
            label="Email",
            width=300,
            hint_text="tu@email.com"
        )
        self.campo_password = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=300,
            hint_text="Ingresa tu contraseña"
        )
        self.boton_login = ft.ElevatedButton(
            text="Iniciar Sesión",
            on_click=self.iniciar_sesion,
            width=200
        )
        self.boton_registrar = ft.TextButton(
            text="¿No tienes cuenta? Regístrate aquí",
            on_click=self.ir_a_registro
        )
        self.boton_registrar_admin = ft.TextButton(
            text="Registro para Administradores",
            on_click=self.ir_a_registro_admin,
            style=ft.ButtonStyle(color=ft.Colors.ORANGE)
        )
        self.mensaje = ft.Text("", color="red")

        self.contenedor_login = ft.Container(
            content=ft.Column([
                ft.Text("INICIAR SESIÓN", size=24, weight="bold"),
                ft.Text("Bienvenido de vuelta", size=16, color="gray"),
                self.campo_email,
                self.campo_password,
                self.boton_login,
                self.boton_registrar,
                self.boton_registrar_admin,
                self.mensaje
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            width=400
        )

    def mostrar(self):
        self.pagina.clean()
        self.pagina.add(ft.Row([self.contenedor_login], alignment=ft.MainAxisAlignment.CENTER))

    def iniciar_sesion(self, e):
        email = self.campo_email.value.strip().lower()
        password = self.campo_password.value
        self.controlador.iniciar_sesion(email, password)

    def ir_a_registro(self, e):
        self.controlador.mostrar_registro()

    def ir_a_registro_admin(self, e):
        self.controlador.mostrar_registro_admin()

    def mostrar_error(self, mensaje):
        self.mensaje.value = mensaje
        self.mensaje.color = "red"
        self.pagina.update()

    def limpiar_campos(self):
        self.campo_email.value = ""
        self.campo_password.value = ""
        self.mensaje.value = ""
        self.pagina.update()