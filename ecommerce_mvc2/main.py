import flet as ft

def main(pagina: ft.Page):
    # Configuración de la ventana
    pagina.window_width = 1200
    pagina.window_height = 700
    pagina.window_min_width = 800
    pagina.window_min_height = 600
    pagina.title = "E-commerce MVC"
    
    print("🚀 DEBUG: Aplicación iniciada")
    
    # Importación directa
    from controladores.controlador_auth import ControladorAuth
    from controladores.controlador_principal import ControladorPrincipal
    
    # Inicializar controlador principal primero
    controlador_principal = ControladorPrincipal(pagina)
    
    # Inicializar controlador de autenticación
    controlador_auth = ControladorAuth(pagina)
    controlador_auth.set_controlador_principal(controlador_principal)
    
    # Mostrar login inicial
    controlador_auth.mostrar_login()

# Ejecutar la aplicación
if __name__ == "__main__":
    ft.app(target=main)