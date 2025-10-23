from datetime import datetime

class Usuario:
    def __init__(self, email, nombre, password, tipo, fecha_registro, nombre_tienda=None, telefono=None):
        self.email = email
        self.nombre = nombre
        self.password = password
        self.tipo = tipo
        self.fecha_registro = fecha_registro
        self.nombre_tienda = nombre_tienda
        self.telefono = telefono
        self.bloqueado = False
        print(f"✅ DEBUG: Usuario creado - {self.email} ({self.tipo})")

    def to_dict(self):
        return {
            'email': self.email,
            'nombre': self.nombre,
            'password': self.password,
            'tipo': self.tipo,
            'fecha_registro': self.fecha_registro,
            'nombre_tienda': self.nombre_tienda,
            'telefono': self.telefono,
            'bloqueado': self.bloqueado
        }

    @classmethod
    def from_dict(cls, data):
        usuario = cls(
            email=data['email'],
            nombre=data['nombre'],
            password=data['password'],
            tipo=data['tipo'],
            fecha_registro=data['fecha_registro'],
            nombre_tienda=data.get('nombre_tienda'),
            telefono=data.get('telefono')
        )
        usuario.bloqueado = data.get('bloqueado', False)
        print(f"✅ DEBUG: Usuario cargado desde dict - {usuario.email}")
        return usuario