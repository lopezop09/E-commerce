import tkinter as tk
from tkinter import messagebox

# OBSERVER

class Observer:
    def actualizar(self, message):
        pass

class ProductSubject:
    def __init__(self):
        self._observers = []

    def agregar(self, observer):
        self._observers.append(observer)

    def notify(self, message):
        for observer in self._observers:
            observer.actualizar(message)

# DECORATOR

class Product:
    def __init__(self, name, precio):
        self.name = name
        self.precio = precio

    def get_precio(self):
        return self.precio

    def get_descripcion(self):
        return self.name

class ProductDecorator(Product):
    def __init__(self, product):
        self._product = product

    def get_precio(self):
        return self._product.get_precio()

    def get_descripcion(self):
        return self._product.get_descripcion()


class DescuentoDecorator(ProductDecorator):
    def __init__(self, product, Descuento):
        super().__init__(product)
        self.Descuento = Descuento

    def get_precio(self):
        return self._product.get_precio() * (1 - self.Descuento)

    def get_descripcion(self):
        return f"{self._product.get_descripcion()} (Descuento {int(self.Descuento*100)}%)"


class EnvioDecorator(ProductDecorator):
    def get_precio(self):
        return self._product.get_precio() + 20000  

    def get_descripcion(self):
        return f"{self._product.get_descripcion()} + costo adicional"

# Interfaz

class ProductApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Detalle de Producto")
        self.root.geometry("500x400")
        self.root.configure(bg="white")

        
        self.product = Product("Nombre del producto", 60000)
        self.subject = ProductSubject()

        
        self.image_frame = tk.Frame(root, width=100, height=100, bg="white", relief="solid", borderwidth=1)
        self.image_frame.pack(pady=10)

        self.image_label = tk.Label(self.image_frame, text="IMAGEN", bg="white", fg="gray", font=("Arial", 9, "bold"))
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")

        
        self.name_label = tk.Label(root, text=self.product.get_descripcion(),
                                   font=("Arial", 16, "bold"), bg="white")
        self.name_label.pack(pady=10)

        
        self.precio_var = tk.StringVar(value=f"${self.product.get_precio():,.0f}")
        self.precio_label = tk.Label(root, textvariable=self.precio_var,
                                    font=("Arial", 14), fg="green", bg="white")
        self.precio_label.pack(pady=5)

        
        self.Descuento_var = tk.BooleanVar()
        self.gift_var = tk.BooleanVar()

        tk.Checkbutton(root, text="Aplicar cupon 20% descuento",
                       variable=self.Descuento_var, bg="white").pack(anchor="w", padx=20)
        tk.Checkbutton(root, text="Aplicar Envio ultra rapido (+20.000$)",
                       variable=self.gift_var, bg="white").pack(anchor="w", padx=20)

        
        tk.Button(root, text="Actualizar precio",
                  command=self.actualizar_precio, bg="blue", fg="white").pack(pady=10)

        
        tk.Button(root, text="Añadir al carrito",
                  command=self.al_carrito, bg="black", fg="white").pack(pady=10)

    
    def actualizar_precio(self):
        product = self.product
        if self.Descuento_var.get():
            product = DescuentoDecorator(product, 0.2)
        if self.gift_var.get():
            product = EnvioDecorator(product)

        new_precio = product.get_precio()
        self.precio_var.set(f"${new_precio:.2f}")
        self.name_label.config(text=product.get_descripcion())

    
    def al_carrito(self):
        self.subject.notify(f"El producto '{self.product.get_descripcion()}' fue añadido al carrito")
        messagebox.showinfo("Carrito", "Producto añadido al carrito")


if __name__ == "__main__":
    root = tk.Tk()
    app = ProductApp(root)
    root.mainloop()