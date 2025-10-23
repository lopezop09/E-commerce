import flet as ft
from datetime import datetime
import re

class VistaRegistro:
    def __init__(self, pagina, controlador_auth):
        self.pagina = pagina
        self.controlador = controlador_auth
        self.crear_controles()

    def crear_controles(self):
        self.tipo_usuario = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="cliente", label="Cliente"),
                ft.Radio(value="vendedor", label="Vendedor")
            ]),
            value="cliente"
        )
        self.campo_nombre = ft.TextField(label="Nombre completo", width=300)
        self.campo_email = ft.TextField(label="Email", width=300)
        self.campo_password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)
        self.campo_confirmar_password = ft.TextField(label="Confirmar contraseña", password=True, can_reveal_password=True, width=300)
        self.campo_nombre_tienda = ft.TextField(label="Nombre de la tienda", width=300, visible=False)
        self.campo_telefono = ft.TextField(label="Teléfono de contacto", width=300, visible=False)
        self.boton_registrar = ft.ElevatedButton(text="Registrarse", on_click=self.registrar_usuario, width=150)
        self.boton_volver = ft.TextButton(text="Volver al login", on_click=self.volver_al_login)
        self.mensaje = ft.Text("")

        self.contenedor_registro = ft.Container(
            content=ft.Column([
                ft.Text("CREA TU CUENTA", size=24, weight="bold"),
                ft.Text("Selecciona tu tipo de cuenta:"),
                self.tipo_usuario,
                self.campo_nombre,
                self.campo_email,
                self.campo_password,
                self.campo_confirmar_password,
                self.campo_nombre_tienda,
                self.campo_telefono,
                ft.Row([self.boton_registrar], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([self.boton_volver], alignment=ft.MainAxisAlignment.CENTER),
                self.mensaje
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            width=400
        )

        self.tipo_usuario.on_change = self.activar_campos_vendedor

    def mostrar(self):
        self.pagina.clean()
        self.pagina.add(ft.Row([self.contenedor_registro], alignment=ft.MainAxisAlignment.CENTER))

    def activar_campos_vendedor(self, e):
        es_vendedor = self.tipo_usuario.value == "vendedor"
        self.campo_nombre_tienda.visible = es_vendedor
        self.campo_telefono.visible = es_vendedor
        self.pagina.update()

    def registrar_usuario(self, e):
        datos = {
            'nombre': self.campo_nombre.value.strip(),
            'email': self.campo_email.value.lower(),
            'password': self.campo_password.value,
            'tipo': self.tipo_usuario.value,
            'fecha_registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if self.tipo_usuario.value == "vendedor":
            datos['nombre_tienda'] = self.campo_nombre_tienda.value.strip()
            datos['telefono'] = self.campo_telefono.value.strip()

        self.controlador.registrar_usuario(datos)

    def volver_al_login(self, e):
        self.controlador.mostrar_login()

    def mostrar_mensaje(self, mensaje, color="red"):
        self.mensaje.value = mensaje
        self.mensaje.color = color
        self.pagina.update()

    def limpiar_campos(self):
        self.campo_nombre.value = ""
        self.campo_email.value = ""
        self.campo_password.value = ""
        self.campo_confirmar_password.value = ""
        self.campo_nombre_tienda.value = ""
        self.campo_telefono.value = ""
        self.mensaje.value = ""
        self.pagina.update()

class VistaRegistroAdmin:
    def __init__(self, pagina, controlador_auth):
        self.pagina = pagina
        self.controlador = controlador_auth
        self.crear_controles()

    def crear_controles(self):
        self.campo_nombre = ft.TextField(label="Nombre completo", width=300)
        self.campo_email = ft.TextField(label="Email", width=300)
        self.campo_password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300)
        self.campo_confirmar_password = ft.TextField(label="Confirmar contraseña", password=True, can_reveal_password=True, width=300)
        self.boton_registrar = ft.ElevatedButton(
            text="Registrar Administrador", 
            on_click=self.registrar_administrador, 
            width=200,
            style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE, color=ft.Colors.WHITE)
        )
        self.boton_volver = ft.TextButton(text="Volver al login", on_click=self.volver_al_login)
        self.mensaje = ft.Text("")

        self.contenedor_registro = ft.Container(
            content=ft.Column([
                ft.Text("REGISTRO ADMINISTRADOR", size=24, weight="bold", color=ft.Colors.ORANGE),
                ft.Text("Crear cuenta de administrador", size=16, color="gray"),
                self.campo_nombre,
                self.campo_email,
                self.campo_password,
                self.campo_confirmar_password,
                ft.Row([self.boton_registrar], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([self.boton_volver], alignment=ft.MainAxisAlignment.CENTER),
                self.mensaje
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            width=400
        )

    def mostrar(self):
        self.pagina.clean()
        self.pagina.add(ft.Row([self.contenedor_registro], alignment=ft.MainAxisAlignment.CENTER))

    def registrar_administrador(self, e):
        datos = {
            'nombre': self.campo_nombre.value.strip(),
            'email': self.campo_email.value.lower(),
            'password': self.campo_password.value,
            'tipo': 'administrador',
            'fecha_registro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.controlador.registrar_administrador(datos)

    def volver_al_login(self, e):
        self.controlador.mostrar_login()

    def mostrar_mensaje(self, mensaje, color="red"):
        self.mensaje.value = mensaje
        self.mensaje.color = color
        self.pagina.update()

    def limpiar_campos(self):
        self.campo_nombre