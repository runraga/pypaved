import customtkinter as ctk
import src.model.process_cluster_data as pcd
from src.controller.Controller import Controller


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # app grame
    app = ctk.CTk()
    app.title("PAVED")
    # main_frame = ctk.CTkFrame(app)
    controller = Controller(app)
    # controller.process_cluster(
    #     sim_path="/Users/jamesault/repos/python/paved-python/resources/csv/cluster_small.csv"
    # )

    app.mainloop()
