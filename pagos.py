import tkinter as tk
from tkinter import messagebox

class PaymentGatewayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pasarela de Pago")
        self.root.geometry("600x300")
        self.root.configure(bg="white")

        # Detalle pedido (L)

        left_frame = tk.Frame(root, bg="#E6F2FF", padx=20, pady=20, relief="solid", borderwidth=1)
        left_frame.pack(side="left", fill="both", expand=True)

        tk.Label(left_frame, text="Importe:", font=("Arial", 14, "bold"), bg="#E6F2FF").pack(anchor="w")
        tk.Label(left_frame, text="50,000 $", font=("Arial", 18, "bold"), fg="blue", bg="#E6F2FF").pack(anchor="w", pady=5)

        detalles = [
            ("Comercio:", "Tienda Online"),
            ("Terminal:", "335255568-1"),
            ("Pedido:", "00005189416"),
            ("Fecha:", "DD/MM/AAAA 00:00"),
            ("Descripción producto:", "Pedido 5189"),
        ]

        for k, v in detalles:
            tk.Label(left_frame, text=f"{k} {v}", font=("Arial", 10), bg="#E6F2FF").pack(anchor="w", pady=2)

        # Formulario pago (R)
        # La mayoria de este codigo es interfaz

        right_frame = tk.Frame(root, bg="white", padx=20, pady=20, relief="solid", borderwidth=1)
        right_frame.pack(side="right", fill="both", expand=True)

        tk.Label(right_frame, text="PAGAR CON TARJETA", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", pady=5)

        # Nº Tarjeta
        tk.Label(right_frame, text="Nº Tarjeta:", bg="white").pack(anchor="w")
        self.num_tarjeta = tk.Entry(right_frame, width=25, font=("Arial", 12))
        self.num_tarjeta.pack(anchor="w", pady=5)

        # Caducidad
        tk.Label(right_frame, text="Caducidad (MM/AA):", bg="white").pack(anchor="w")
        self.expiracion = tk.Entry(right_frame, width=10, font=("Arial", 12))
        self.expiracion.pack(anchor="w", pady=5)

        # Código Seguridad
        tk.Label(right_frame, text="Cód. Seguridad:", bg="white").pack(anchor="w")
        self.cvv = tk.Entry(right_frame, width=5, font=("Arial", 12), show="*")
        self.cvv.pack(anchor="w", pady=5)

        # Botones
        button_frame = tk.Frame(right_frame, bg="white")
        button_frame.pack(pady=15)

        tk.Button(button_frame, text="CANCELAR", bg="gray", fg="white",
                  command=self.cancelar_pago, width=10).pack(side="left", padx=5)

        tk.Button(button_frame, text="PAGAR", bg="blue", fg="white",
                  command=self.completar_pago, width=10).pack(side="left", padx=5)

    # Botones

    def cancelar_pago(self):
        self.num_tarjeta.delete(0, tk.END)
        self.expiracion.delete(0, tk.END)
        self.cvv.delete(0, tk.END)
        messagebox.showinfo("Cancelado", "El pago fue cancelado")

    def completar_pago(self):
        card = self.num_tarjeta.get()
        expiracion = self.expiracion.get()
        cvv = self.cvv.get()

        if not card or not expiracion or not cvv:
            messagebox.showwarning("Error", "Por favor, completa todos los campos") #Error, falta informacion
        else:
            messagebox.showinfo("Pago Exitoso", f"Pago realizado con tarjeta terminada en {card[-4:]}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PaymentGatewayApp(root)
    root.mainloop()