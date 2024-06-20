import customtkinter as ctk
from src.controller.Controller import Controller


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("PAVED")
    controller = Controller(app)

    app.mainloop()
